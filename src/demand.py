import numpy as np
import warnings

import tls.loader as loader
import tls.saver as saver

warnings.filterwarnings("ignore", category=RuntimeWarning)


def needs_assessment(parameters):
    power = parameters['power capacity']
    service_area = parameters['service area']
    tier = parameters['tier']
    capacity_factor = parameters['capacity factor']
    filepath = parameters['paths']['sites']
    potential_sites, _ = loader.load_map(f'{filepath}/potential_sites.tif')

    potential_sites[potential_sites > 0] = 999
    potential_sites[potential_sites < 0.1] = 1
    potential_sites[potential_sites == 999] = 0
    potential_sites = potential_sites.astype(int)

    filepath = parameters['paths']['data']
    needs, meta = loader.load_map(f'{filepath}/EnergyNeed/service_area/energyneed2019_elec100pct_tier{tier}_{service_area}k.tif')
    needs = np.where(potential_sites, needs, 0)

    saver.save_map(needs, parameters, meta=meta, name=f'needs_tier{tier}_{service_area}k', type='needs')

    # power can be modulated by CF here (transform into MWh annual)
    # needs is in MWh annual, power in MW
    energy = power * capacity_factor * 8760

    needs = energy / needs
    needs[needs == np.inf] = 0

    saver.save_map(needs, parameters, meta=meta, name=f'pct_needs_{power:.0f}MW_tier{tier}_{service_area}k', type='needs')
