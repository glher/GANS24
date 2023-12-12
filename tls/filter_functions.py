def avoidance_condition(raster, condition):
    raster[raster <= condition] = 0
    raster[raster > condition] = 1
    raster = raster.astype('int32')
    return raster


def invert_condition(raster, condition):
    raster[raster <= condition] = -1
    raster[raster > condition] = 0
    raster[raster < 0] = 1
    raster = raster.astype('int32')
    return raster


def get_land(raster, condition):
    raster[raster <= condition] = -1
    raster[raster > condition] = 0
    raster[raster < 0] = 999
    raster = raster.astype('int32')
    return raster


def get_seismic(raster, condition):
    # This function translates from 475 RP to 2475 RP
    raster = raster * (2475. / 475.) ** (0.478 - 0.431 * raster)
    raster[raster <= condition] = 0
    raster[raster > condition] = 1
    raster = raster.astype('int32')
    return raster
