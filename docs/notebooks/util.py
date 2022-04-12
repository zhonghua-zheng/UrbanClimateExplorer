import intake
import numpy as np
import pandas as pd
import xarray as xr
import time as timer
from haversine import haversine

cesm1_catalog_url = 'https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json'

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

def lon_to_180(ds):
    """This is a function for converting longitude from (0, 360) to (-180, 180)
    ref: https://gis.stackexchange.com/questions/201789/verifying-formula-that-will-convert-longitude-0-360-to-180-to-180/201793

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

def lon_to_360(lon):
    """This is a function for converting input city's lon from (-180, 180) to (0, 360)
    ref: https://gis.stackexchange.com/questions/201789/verifying-formula-that-will-convert-longitude-0-360-to-180-to-180/201793
    
    Parameters
    ----------
    lon : float
        longitude ranges from -180 to 180

    Returns
    -------
    float
        longitude ranges from 0 to 360
    """
    return lon*1.0%360

def get_time_invariant_urban_mask(dsets, var, idx=0, arr_name="mask"):
    """This is a function for creating a time invariant urban mask.
    If we use 2006-01-01, given the that is not available, we should use 1 for the idx.
    We are interested in lat and lon only, e.g., 
    ["time", "lat", "lon"] if time is considered.

    Parameters
    ----------
    dsets : xarray.DataArray
        _description_
    var : variable that we are interested in
        _description_
    idx : int, optional
        index of other dimensions, by default 0
    arr_name : str, optional
        name of the mask, by default "mask"

    Returns
    -------
    xarray.DataArray
        urban mask
    """
    da = dsets[var]
    for dim in da.dims:
        if dim not in ["lat","lon"]:
            da = da.isel({dim:idx}).squeeze().drop(dim)
            # or da = da.sel({dim:da[dim][idx]}).squeeze().drop(dim)
    return da.rename(arr_name).notnull().load()

def get_mask_cities(mask):
    """This is a function for getting urban mask and a list of cities' lat and lon

    Parameters
    ----------
    mask : xarray.DataArray
        urban mask

    Returns
    -------
    dict
        a dict of cities' lat and lon
    """
    
    # pad a new mask for periodic in longitude
    mask_pad = mask.sel(lon=slice(0,180))
    mask_pad = mask_pad.assign_coords(lon = mask_pad.indexes['lon']+360)
    mask_w_pad = xr.concat([mask, mask_pad], dim="lon")
    
    # get mask dataframe
    df_mask = mask_w_pad.to_dataframe().reset_index() 
    df_mask = df_mask[df_mask["mask"]==True].reset_index(drop=True)[["lat","lon"]] # get available cities
    CitiesList = list(df_mask.transpose().to_dict().values()) # get a list of city lat/lon
    return CitiesList

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
def get_data(city_loc, experiment, frequency, member_id, time, cam_ls, clm_ls, clm_var_mask, a_component="atm", l_component="lnd"):
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

    Returns
    -------
    xarray.Dataset
        a dataset with the CESM urban grid cell nearest to the "city of interest"
    """

    # get data
#     t0 = timer.time()
    dsets_cam, dsets_clm = get_cam_clm(experiment, frequency, member_id, time, cam_ls, clm_ls)
#     print(timer.time()-t0,": get data from AWS")

    # get urban mask based on dsets_clm, use the first element of clm_ls if not specified
#     t0 = timer.time()
    if clm_var_mask is None:
        clm_var_mask = clm_ls[0]
    mask = get_time_invariant_urban_mask(dsets_clm, clm_var_mask, idx=0, arr_name="mask")
#     print(timer.time()-t0,": get urban mask")

    # get city list
#     t0 = timer.time()
    CitiesList = get_mask_cities(mask)
#     print(timer.time()-t0,": get city list")

    # get nearest urban grid cell in CESM
#     t0 = timer.time()
    COI = closest(CitiesList, city_loc)
    COI["lon"] = lon_to_360(COI["lon"])
#     print(timer.time()-t0,": get nearest gridcell")

    # apply the mask and get data
#     t0 = timer.time()
    if ((COI["lat"]!=None) & (COI["lon"]!=None)):
        ds = xr.merge([dsets_cam.where(mask).sel(lat=COI["lat"],lon=COI["lon"],method="nearest"),
                       dsets_clm.where(mask).sel(lat=COI["lat"],lon=COI["lon"],method="nearest")]).load()
    else:
        ds = xr.merge([dsets_cam.where(mask),dsets_clm.where(mask)].load())
#     print(timer.time()-t0,": apply mask and get data")
    
    return ds
      
    