import rasterio


def load_map(filepath, meta_dtype=None, meta_nodata=None):
    raster = rasterio.open(filepath)
    meta = raster.meta
    raster = raster.read(1)
    if meta_dtype:
        meta['dtype'] = meta_dtype
    if meta_nodata:
        meta['nodata'] = meta_nodata
    return raster, meta


def load_internal_map(filepath, meta_dtype=None, meta_nodata=None):
    raster = rasterio.open(filepath)
    meta = raster.meta
    raster = raster.read(1)
    if meta_dtype:
        meta['dtype'] = meta_dtype
    if meta_nodata:
        meta['nodata'] = meta_nodata
    return raster, meta
