import intake
import numpy as np
import pandas as pd
import xarray as xr
import gc
from math import radians
from haversine import haversine
# import time as timer
# from sklearn.metrics.pairwise import haversine_distances

catalog_url_dict = {
        "CESM1": 'https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json',
        "cesm1": 'https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json',
        "CESM2": 'https://raw.githubusercontent.com/NCAR/cesm2-le-aws/main/intake-catalogs/aws-cesm2-le.json',
        "cesm2": 'https://raw.githubusercontent.com/NCAR/cesm2-le-aws/main/intake-catalogs/aws-cesm2-le.json',
    }

def haversine_dist(a, b):
    """This is a function for getting the haversine distance

    Parameters
    ----------
    a: list 
        [lat, lon]
        e.g., (45.7597, 4.8422)
    b: list 
        [lat, lon]
        e.g., (48.8567, 2.3508)
    er: 
        Earth radius, default is 6371.0088 km

    Returns
    -------
    haversine_dist
        the haversine distance between a and b
    """
    a_n = (a[0], ((a[1] + 180) % 360) - 180)
    b_n = (b[0], ((b[1] + 180) % 360) - 180)
    return haversine(a_n, b_n)

'''
def haversine_dist_sk(a, b, er = 6371.0088):
    """This is a function for getting the haversine distance, which overcomes 
    the issue that haversine can only take the value between -180 and 180
    Earth radius provided by https://github.com/mapado/haversine/blob/main/haversine/haversine.py 

    Parameters
    ----------
    a: list 
        [lat, lon]
        e.g., (45.7597, 4.8422)
    b: list 
        [lat, lon]
        e.g., (48.8567, 2.3508)
    er: 
        Earth radius, default is 6371.0088 km

    Returns
    -------
    haversine_dist
        the haversine distance between a and b
    """
    a_in_radians = [radians(_) for _ in a]
    b_in_radians = [radians(_) for _ in b]
    result = haversine_distances([a_in_radians, b_in_radians])* er
    return result[0][1]
'''

class load_clm_subgrid_info:
    """This class is used for 1D to 3D conversion, for more information:
    https://zhonghuazheng.com/UrbanClimateExplorer/notebooks/CESM2_subgrid_info.html 
    """
    def __init__(self, ds, subgrid_info):
        self.ds = ds
        self.time = self.ds.time
        self.member_id = self.ds.member_id
        self.subgrid_info = subgrid_info
        self.lat = self.subgrid_info.lat
        self.lon = self.subgrid_info.lon
        self.ixy = self.subgrid_info.land1d_ixy
        self.jxy = self.subgrid_info.land1d_jxy
        self.ltype = self.subgrid_info.land1d_ityplunit
        self.ltype_dict = {value:key for key, value in self.ds.attrs.items() if 'ltype_' in key.lower()}     
    def get3d_var(self, clm_var_mask):
        var = self.ds[clm_var_mask]
        nmember = len(self.member_id.values)
        nlat = len(self.lat.values)
        nlon = len(self.lon.values)
        ntim = len(self.time.values)
        nltype = len(self.ltype_dict)
        # create an empty array
        gridded = np.full([nmember,ntim,nltype,nlat,nlon],np.nan)
        # assign the values
        gridded[:,
                :,
                self.ltype.values.astype(int) - 1, # Fortran arrays start at 1
                self.jxy.values.astype(int) - 1,
                self.ixy.values.astype(int) - 1] = var.values
        grid_dims = xr.DataArray(gridded, dims=("member_id","time","ltype","lat","lon"))
        grid_dims = grid_dims.assign_coords(member_id=self.member_id,
                                            time=self.time,
                                            ltype=[i for i in range(self.ltype.values.min(), 
                                                                    self.ltype.values.max()+1)],
                                            lat=self.lat.values,
                                            lon=self.lon.values)
        grid_dims.name = clm_var_mask
        return grid_dims.to_dataset()

def get_dsets(model, experiment, frequency, variable, forcing_variant=None):
    """This is a function for getting a dictionary of aggregate xarray datasets

    Parameters
    ----------
    model: string
        e.g., "CESM1"
    experiment : string
        e.g., "RCP85" (RCP 8.5 runs)
    frequency : string
        e.g., "daily" or "monthly"
    variable : a list of string
        e.g., ["TREFHT","TREFHTMX"]
    forcing_variant: string
        e.g., the biomass forcing variant, "cmip6" (the default in the cmip6 runs) or "smbb" (smoothed biomass burning), by default "cmip6

    Returns
    -------
    dictionary
        a dictionary of aggregate xarray datasets
    """
    catalog_url_dict = {
        "CESM1": 'https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json',
        "cesm1": 'https://raw.githubusercontent.com/NCAR/cesm-lens-aws/main/intake-catalogs/aws-cesm1-le.json',
        "CESM2": 'https://raw.githubusercontent.com/NCAR/cesm2-le-aws/main/intake-catalogs/aws-cesm2-le.json',
        "cesm2": 'https://raw.githubusercontent.com/NCAR/cesm2-le-aws/main/intake-catalogs/aws-cesm2-le.json',
    }

    col = intake.open_esm_datastore(catalog_url_dict[model]) # open collection description file

    if (model=="cesm1") or (model=="CESM1"): 
        col_subset = col.search(experiment=experiment, 
                            frequency=frequency, 
                            variable=variable)
    elif (model=="cesm2") or (model=="CESM2"):
        col_subset = col.search(experiment=experiment, 
                            frequency=frequency, 
                            forcing_variant=forcing_variant,
                            variable=variable)
    else:
        print("please type the model name")
        return

    dsets = col_subset.to_dataset_dict(zarr_kwargs={"consolidated": True}, storage_options={"anon": True})
    return dsets

def get_cam_clm(model, experiment, frequency, member_id, time, cam_ls, clm_ls, forcing_variant=None, urban_type=None, a_component="atm", l_component="lnd"):
    """This is a function for getting CAM and CLM data

    Parameters
    ----------
    model: string
        e.g., "CESM1"
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
    forcing_variant: string
        e.g., the biomass forcing variant, "cmip6" (the default in the cmip6 runs) or "smbb" (smoothed biomass burning), by default "cmip6
    urban_type: string
        e.g., "tbd" (Tall Building District), "hd" (High Density), and "md" (Medium Density)
    a_component : str, optional
        component name of CAM, by default "atm"
    l_component : str, optional
        component name of CLM, by default "lnd"

    Returns
    -------
    xarray.Dataset
        CAM dataset and CLM dataset
    """

    subgrid_info_path = "./CESM2_subgrid_info.nc"
    clm_var = clm_ls[0] # CESM2 can only work on a single variable at this point. 
    urban_type_dict = {"tbd":7, "hd":8, "md":9}


    """
    Tall Building District (tbd)
    High Density (hd) Residential/Commerical/Industrial
    Medium Density (md) Residential
    """    

    if (model=="cesm1") or (model=="CESM1"): 
        dsets = get_dsets(model, 
                          experiment=experiment, 
                          frequency=frequency,
                          variable=(cam_ls+clm_ls))
        dsets_cam = dsets[a_component+"."+experiment+"."+frequency].sel(member_id=member_id, time=time)[cam_ls]
        dsets_clm = dsets[l_component+"."+experiment+"."+frequency].sel(member_id=member_id, time=time)[clm_ls]

    elif (model=="cesm2") or (model=="CESM2"):
        dsets = get_dsets(model, 
                          experiment=experiment, 
                          frequency=frequency, 
                          forcing_variant=forcing_variant,
                          variable=(cam_ls+clm_ls))
        
        dsets_cam = dsets[a_component+"."+experiment+"."+frequency+"."+forcing_variant]\
                         .sel(member_id=member_id, time=time)[cam_ls] 
        dsets_clm_load = dsets[l_component+"."+experiment+"."+frequency+"."+forcing_variant]\
                         .sel(member_id=member_id, time=time)[clm_ls]

        # add the subgrid info
        subgrid_info = xr.open_dataset(subgrid_info_path) 
        
        if np.array_equal(dsets_cam.lon, subgrid_info.lon) is False:
            print("different lon between CAM and CLM subgrid info, adjust subgrid info's lon")
            subgrid_info = subgrid_info.assign_coords(lon = dsets_cam.indexes['lon'])
        if np.array_equal(dsets_cam.lat, subgrid_info.lat) is False:
            print("different lat between CAM and CLM subgrid info, adjust subgrid info's lat")
            subgrid_info = subgrid_info.assign_coords(lat = dsets_cam.indexes['lat'])
        
        dsets_clm_subgrid = load_clm_subgrid_info(dsets_clm_load, subgrid_info)
        del dsets_clm_load, subgrid_info
        gc.collect()

        # select the urban type
        dsets_clm = dsets_clm_subgrid.get3d_var(clm_var).sel(ltype=urban_type_dict[urban_type]).drop("ltype")
        
        # need to select "lev[-1]"" and drop "lev"
        if ("lev" in dsets_cam.dims):
            return dsets_cam.isel({"lev":-1}).drop("lev"), dsets_clm
        
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
    dsets : xarray.DataSets
        _description_
    var : variable that we are interested in
        e.g., TREFMXAV_U for CESM1
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
    
    # get mask dataframe
    df_mask = mask.to_dataframe().reset_index() 
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
        a dict of a city's lat and lon that we are interested in, e.g., {'lat': 40.1164, 'lon': -88.2434}

    Returns
    -------
    dict
        lat and lon of the nearest grid cell in Earth System Model
    """

    # find the nearest urban grid cell in CESM using haversine distance
    return min(data, key=lambda p: haversine_dist([v['lat'],v['lon']],[p['lat'],p['lon']]))

# get nearst point
def get_data(model, city_loc, experiment, frequency, member_id, time, cam_ls, clm_ls, clm_var_mask=None, forcing_variant=None, urban_type=None, a_component="atm", l_component="lnd"):
    """_summary_

    Parameters
    ----------
    model: string
        e.g., "CESM1"
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
    dsets_cam, dsets_clm = get_cam_clm(model, experiment, frequency, member_id, time, cam_ls, clm_ls, forcing_variant, urban_type, a_component, l_component)
    # check if lat and lon are the same
    assert np.array_equal(dsets_cam.lon, dsets_clm.lon)
    assert np.array_equal(dsets_cam.lat, dsets_clm.lat)
#     print(timer.time()-t0,": get data from AWS")

    # get urban mask based on dsets_clm, use the first element of clm_ls if not specified
#     t0 = timer.time()
    # if clm_var_mask is not defined
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
      
    