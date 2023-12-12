import rasterio
import json
import yaml


def save_case(parameters):
    for f in parameters['filters']:
        parameters['filters'][f]['function'] = parameters['filters'][f]['function'].__name__

    path_save = parameters['paths']['case']
    with open(f'{path_save}/data.json', 'w') as fp:
        json.dump(parameters, fp,  indent=4)
    with open(f'{path_save}/data.yml', 'w') as fp:
        yaml.dump(parameters, fp, default_flow_style=False)


def save_map(raster, parameters, meta=None, name=None, type='filters'):
    path = parameters['paths'][type]
    with rasterio.open(f'{path}/{name}.tif', 'w', **meta, compress="DEFLATE") as f:
        f.write(raster, indexes=1)


def save_text(txt, name=None):
    with open(name, 'w') as f:
        f.write(txt)
