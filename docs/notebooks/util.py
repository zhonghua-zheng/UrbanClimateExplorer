import intake
import numpy as np
import pandas as pd
import xarray as xr
from haversine import haversine

cesm1_catalog_url = 'https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json'
mask_path_ref = "./urban_mask.nc"

def get_dsets(experiment, frequency, variable, catalog_url=cesm1_catalog_url):
    """This is a function for getting a dictionary of aggregate xarray datasets

    Parameters
    ----------
    experiment : string
        e.g., "RCP85" (RCP 8.5 runs)
    frequency : string
        e.g., "daily" or "monthly"
    variable : a list of string
        e.g., ["TREFHT","TREFHTMX"]
    catalog_url : string, optional
        catalog URL, by default cesm1_catalog_url ('https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json')

    Returns
    -------
    dictionary
        a dictionary of aggregate xarray datasets
    """
    col = intake.open_esm_datastore(catalog_url) # open collection description file
    col_subset = col.search(experiment=experiment, 
                        frequency=frequency, 
                        variable=variable)
    dsets = col_subset.to_dataset_dict(zarr_kwargs={"consolidated": True}, storage_options={"anon": True})
    return dsets

def get_cam_clm(experiment, frequency, member_id, time, cam_ls, clm_ls, a_component="atm", l_component="lnd"):
    """This is a function for getting CAM and CLM data

    Parameters
    ----------
    experiment : string
        e.g., "RCP85" (RCP 8.5 runs)
    frequency : string
        e.g., "daily" or "monthly"
    member_id : a list of int
        e.g., [2,3]
    time : slice
        e.g., slice("2081-01-02","2100-12-31")
    cam_ls : a list of string
        CAM variables, e.g., ["TREFHT","TREFHTMX"]
    clm_ls : a list of string
        CLM variables, e.g., ["TREFMXAV_U"]
    a_component : str, optional
        component name of CAM, by default "atm"
    l_component : str, optional
        component name of CLM, by default "lnd"

    Returns
    -------
    xarray.Dataset
        CAM dataset and CLM dataset
    """
    
    dsets = get_dsets(experiment=experiment, 
                      frequency=frequency,
                      variable=(cam_ls+clm_ls))
    dsets_cam = dsets[a_component+"."+experiment+"."+frequency].sel(member_id=member_id, time=time)[cam_ls]
    dsets_clm = dsets[l_component+"."+experiment+"."+frequency].sel(member_id=member_id, time=time)[clm_ls]
    return dsets_cam, dsets_clm

def convert_lon(ds):
    """This is a function for converting longitude from (0, 360) to (-180, 180)

    Parameters
    ----------
    ds : xarray.Dataset
        a dataset with the longitude ranging from 0 to 360

    Returns
    -------
    xarray.Dataset
        a dataset with the longitude ranging from -180 to 180
    """
    ds=ds.assign_coords(lon=(((ds.lon + 180) % 360) - 180))
    ds=ds.reindex(lon=sorted(ds.lon))  
    return ds

def get_mask_cities(mask_path):
    """This is a function for getting urban mask and a list of cities' lat and lon

    Parameters
    ----------
    mask_path : string
        path to the urban mask 

    Returns
    -------
    xarray.DataArray and dict
        a xarray.DataArray of the urban mask, and a dict of cities' lat and lon
    """
    mask = xr.open_dataset(mask_path)["mask"]  # get mask
    
    df_mask = convert_lon(mask).rename("mask").to_dataframe().reset_index() # get mask dataframe
    df_mask = df_mask[df_mask["mask"]==True].reset_index(drop=True)[["lat","lon"]] # get available cities
    CitiesList = list(df_mask.transpose().to_dict().values()) # get a list of city lat/lon
    return mask, CitiesList

def closest(data, v):
    """find the nearest urban grid cell in CESM using haversine distance
    reference: https://stackoverflow.com/questions/41336756/find-the-closest-latitude-and-longitude

    Parameters
    ----------
    data : dict
        a dict of cities' lat and lon, from get_mask_cities
    v : dict
        a dict of a city's lat and lon that we are interested in , e.g., {'lat': 40.1164, 'lon': -88.2434}

    Returns
    -------
    dict
        lat and lon of the nearest grid cell in Earth System Model
    """

    # find the nearest urban grid cell in CESM using haversine distance
    return min(data, key=lambda p: haversine((v['lat'],v['lon']),(p['lat'],p['lon'])))

# get nearst point
def get_data(city_loc, experiment, frequency, member_id, time, cam_ls, clm_ls, a_component="atm", l_component="lnd", mask_path = mask_path_ref):
    """_summary_

    Parameters
    ----------
    city_loc : dict
        a dict of a city's lat and lon that we are interested in , e.g., {'lat': 40.1164, 'lon': -88.2434}
    experiment : string
        e.g., "RCP85" (RCP 8.5 runs)
    frequency : string
        e.g., "daily" or "monthly"
    member_id : a list of int
        e.g., [2,3]
    time : slice
        e.g., slice("2081-01-02","2100-12-31")
    cam_ls : a list of string
        CAM variables, e.g., ["TREFHT","TREFHTMX"]
    clm_ls : a list of string
        CLM variables, e.g., ["TREFMXAV_U"]
    a_component : str, optional
        component name of CAM, by default "atm"
    l_component : str, optional
        component name of CLM, by default "lnd"    
    mask_path : string
        path to the urban mask 

    Returns
    -------
    xarray.Dataset
        a dataset with the CESM urban grid cell nearest to the "city of interest"
    """
    
    # get city list
    mask, CitiesList = get_mask_cities(mask_path)
    COI = closest(CitiesList, city_loc)
    # get data
    dsets_cam, dsets_clm = get_cam_clm(experiment, frequency, member_id, time, cam_ls, clm_ls)
    if ((COI["lat"]!=None) & (COI["lon"]!=None)):
        ds = xr.merge([convert_lon(dsets_cam.where(mask)).sel(lat=COI["lat"],lon=COI["lon"],method="nearest"),
                       convert_lon(dsets_clm.where(mask)).sel(lat=COI["lat"],lon=COI["lon"],method="nearest")]).load()
    else:
        ds = convert_lon(xr.merge([dsets_cam,dsets_clm]).load())
        
    return ds
      
    