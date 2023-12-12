from tqdm import tqdm
import numpy as np
import glob
import shutil
import os

import tls.saver as saver
import tls.loader as loader


def combine(parameters):
    """
    pairs is a 3-tuple, with elements 1 and 2 being merged into element 3
    """
    pairs = parameters['combinations']
    path = parameters['paths']['filters']
    path_intermediary = parameters['paths']['filters intermediary']

    for l1, l2, l3 in pairs:
        raster1, _ = loader.load_map(f'{path}/{l1}.tif')
        raster2, meta = loader.load_map(f'{path}/{l2}.tif')
        raster1 = np.minimum(raster1, raster2)
        saver.save_map(raster1, parameters, meta=meta, name=l3, type='filters')
        shutil.move(f'{path}/{l1}.tif', f'{path_intermediary}/{l1}.tif')
        shutil.move(f'{path}/{l2}.tif', f'{path_intermediary}/{l2}.tif')


def make_filters(f, fl, parameters):
    for n in tqdm(fl):
        filepath = os.path.join(parameters['paths']['data'], f[n]['path'])
        condition = f[n]['condition']
        nfunc = f[n]['function']
        raster, meta = loader.load_map(filepath, meta_dtype='int32', meta_nodata=999)
        raster = nfunc(raster, condition)
        saver.save_map(raster, parameters, meta=meta, name=n, type='filters')
    try:
        del raster
    except NameError:
        pass
    combine(parameters)


def overlay_filters(parameters):
    raster = None
    path = parameters['paths']['filters']
    for filter in tqdm(glob.glob(f'{path}/*.tif')):
        raster_next, meta = loader.load_map(filter)
        try:
            raster += raster_next
        except TypeError:
            raster = raster_next
    raster[raster >= 999] = 999
    saver.save_map(raster, parameters, meta=meta, name='potential_sites', type='sites')


def potential_sites(parameters):
    filters = parameters['filters']
    filters_list = parameters['filters list']
    make_filters(filters, filters_list, parameters)
    overlay_filters(parameters)
