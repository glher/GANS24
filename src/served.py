# Take the needs results (pct)
# Select optimal locations --> needs between 0 and 150%
#   That 150% would depend on projected population growth

# (map of interesting feasible locations per reactor type)
#    Sites/optimal_sites.tif (%)

# For each location with needs, sum the location within the service area around
# If > 100 --> set to 100 (every population need met)
# else, < 100

# (map of needs met per reactor types)
#    Needs/met_needs_250MW_tier5_50k.tif (%)
# Translate this to people electrified with type of reactor globally and per country

import tls.loader as loader
import tls.saver as saver
import tls.convolution as conv


def optimal_locations(parameters):
    power = parameters['power capacity']
    service_area = parameters['service area']
    tier = parameters['tier']
    optimal_limit = parameters['upper optimal service']
    filepath = parameters['paths']['needs']
    optimal_sites, meta = loader.load_map(f'{filepath}/pct_needs_{power:.0f}MW_tier{tier}_{service_area}k.tif')

    optimal_sites[optimal_sites > optimal_limit] = 0

    saver.save_map(optimal_sites, parameters, meta=meta,
                   name=f'optimal_sites_{power:.0f}MW_tier{tier}_{service_area}k', type='sites')

    return optimal_sites


def service_assessment(parameters):
    # Site logical reactors (avoid unrealistic ones, where demand is not present within their service area)
    # Raster to apply the convolution
    optimal_sites = optimal_locations(parameters).astype(float)

    power = parameters['power capacity']
    service_area = parameters['service area']
    tier = parameters['tier']
    tier_need_capita = parameters['tier need per capita']
    if service_area % 2 == 0:
        service_area_val = service_area + 1
    else:
        service_area_val = service_area

    optimal_sites = conv.compute_nomask(optimal_sites, service_area_val)
    optimal_sites[optimal_sites > 1] = 1.

    filepath = parameters['paths']['data']
    needs_locations, meta = loader.load_map(f'{filepath}/EnergyNeed/energyneed2019_tier5_100pct_electrate.tif')
    # number of people (at Tier5, 3000 kWh)
    needs_locations = needs_locations / (tier_need_capita * 1e3)
    
    needs_locations = needs_locations * optimal_sites
    meta['dtype'] = 'float64'

    saver.save_map(needs_locations, parameters, meta=meta,
                   name=f'met_needs_{power:.0f}MW_tier{tier}_{service_area}k', type='needs')

    del optimal_sites
    
    mask, _ = loader.load_map(f'{filepath}/Infrastructures/Grid/grid_10k.tif')
    mask[mask > 0] = 2
    mask[mask < 1] = 1
    mask[mask > 1] = 0
    
    needs_locations[(mask == 0)] = 0
    saver.save_map(needs_locations, parameters, meta=meta,
                   name=f'met_needs_excl10k_{power:.0f}MW_tier{tier}_{service_area}k', type='needs')
