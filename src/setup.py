import os

# import src.case as case_information
import importlib


def create_architecture(paths, debug=True):
    for p in paths:
        if not os.path.exists(paths[p]):
            if debug:
                print(f'Path to be created: {paths[p]}')
            else:
                os.makedirs(paths[p])


def parameters(case_info, r):
    rtype = r.split('_')[0]
    param = {}
    param['__type__'] = r
    param['filters'] = case_info.filters[r]
    param['filters list'] = case_info.filters_list[rtype]
    param['combinations'] = case_info.combinations
    param['power capacity'] = case_info.powers[rtype]
    param['service area'] = case_info.service_areas[rtype]
    param['capacity factor'] = case_info.capacity_factors[rtype]
    param['tier'] = case_info.tier
    param['tier need per capita'] = case_info.tier_need_per_capita[case_info.tier]
    param['upper optimal service'] = case_info.upper_service
    param['countries'] = case_info.countries
    
    param['reactor'] = r
    return param


def get_paths(c, r):
    dict_paths = {}
    dirpath = f'res/case{c}/{r}'
    dict_paths['filters'] = f'{dirpath}/Filters'
    dict_paths['case'] = f'{dirpath}/Case'
    dict_paths['sites'] = f'{dirpath}/Sites'
    dict_paths['needs'] = f'{dirpath}/Needs'
    dict_paths['stats'] = f'{dirpath}/Stats'
    dict_paths['filters intermediary'] = f'{dirpath}/Filters/intermediary'
    return dict_paths


def run(casefile, case, reactor):
    case_information = importlib.import_module(f'cases.constraints.{casefile["INPUTS"]}')
    if reactor == 'all':
        params = {}
        params['powers'] = case_information.powers
        params['cooling_modes'] = case_information.cooling_modes
        params['cooling_name'] = case_information.cooling_name
        params['countries'] = case_information.countries
    else:
        paths = get_paths(case, reactor)
        create_architecture(paths, debug=casefile['DEBUG'])
        params = parameters(case_information, reactor)
        params['paths'] = paths
    params['case'] = case
    return params
