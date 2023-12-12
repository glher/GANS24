import numpy as np
import math
import fiona
import rasterio
from rasterio.mask import mask

import tls.loader as loader
import tls.saver as saver


def run(parameters):
    get_global(parameters)
    get_countries(parameters)


def get_global(parameters):
    filepath = parameters['paths']['needs']
    service_area = parameters['service area']
    tier = parameters['tier']
    power = parameters['power capacity']
    capacity_factor = parameters['capacity factor']
    tier_need_per_capita = parameters['tier need per capita']
    
    raster, _ = loader.load_map(f'{filepath}/met_needs_{power:.0f}MW_tier{tier}_{service_area}k.tif')
    pop_served = np.sum(raster)
    number_reactors = pop_served * tier_need_per_capita / (power * 8760 * capacity_factor)
    population_poverty = get_population_poverty(parameters, mode='all')
    
    raster, _ = loader.load_map(f'{filepath}/met_needs_excl10k_{power:.0f}MW_tier{tier}_{service_area}k.tif')
    pop_served_10k = np.sum(raster)
    number_reactors_10k = pop_served_10k * tier_need_per_capita / (power * 8760 * capacity_factor)
    population_poverty_10k = get_population_poverty(parameters, mode='10k')
    
    write_stats(parameters, pop_served, pop_served_10k, number_reactors, number_reactors_10k,
                population_poverty, population_poverty_10k)


def write_stats(parameters, pop_served, pop_served_10k, number_reactors, number_reactors_10k,
                population_poverty, population_poverty_10k, region='World'):
    filepath = parameters['paths']['stats']
    reactor = parameters['__type__']
    power = parameters['power capacity']
    towrite = f'STATISTICS -- {region}\n\n'
    towrite += f'Population in poverty : {population_poverty:,.0f}\n'
    towrite += f'Population served by {reactor} : {pop_served:,.0f}\n'
    towrite += f'Number of {reactor} needed ({power:.0f} MWe) : {math.ceil(number_reactors):,}\n\n'
    towrite += f'[>10km of grid] Population in poverty : {population_poverty_10k:,.0f}\n'
    towrite += f'[>10km of grid] Population served by {reactor} : {pop_served_10k:,.0f}\n'
    towrite += f'[>10km of grid] Number of {reactor} needed ({power:.0f} MWe) : {math.ceil(number_reactors_10k):,}\n'
    saver.save_text(towrite, name=f'{filepath}/stats_{region}.txt')


def get_countries(parameters):
    power = parameters['power capacity']
    capacity_factor = parameters['capacity factor']
    tier_need_per_capita = parameters['tier need per capita']
    filepath_data = parameters['paths']['data']
    filepath = parameters['paths']['needs']
    service_area = parameters['service area']
    tier = parameters['tier']
    countries = parameters['countries']
    for country in countries:
        with fiona.open(f'{filepath_data}/Geographical/countries.shp') as src:
            filtered = filter(lambda f: f['properties']['ADM0_A3'] == country, src)
            geoms = [feature["geometry"] for feature in filtered]
            
        # all
        with rasterio.open(f'{filepath}/met_needs_{power:.0f}MW_tier{tier}_{service_area}k.tif') as r:
            country_vals, _ = mask(r, geoms, crop=True, all_touched=True, nodata=0)

        pop_served = np.sum(country_vals)
        number_reactors = pop_served * tier_need_per_capita / (power * 8760 * capacity_factor)

        population_poverty = get_population_poverty(parameters, geoms=geoms, mode='all')
        
        
        # 10k
        with rasterio.open(f'{filepath}/met_needs_excl10k_{power:.0f}MW_tier{tier}_{service_area}k.tif') as r:
            country_vals, _ = mask(r, geoms, crop=True, all_touched=True, nodata=0)

        pop_served_10k = np.sum(country_vals)
        number_reactors_10k = pop_served_10k * tier_need_per_capita / (power * 8760 * capacity_factor)

        population_poverty_10k = get_population_poverty(parameters, geoms=geoms, mode='10k')
        
        
        write_stats(parameters, pop_served, pop_served_10k, number_reactors, number_reactors_10k,
                    population_poverty, population_poverty_10k, region=country)


def get_population_poverty(parameters, geoms=None, mode='all'):
    filepath = parameters['paths']['data']
    if mode == 'all':
        filename = f'{filepath}/EnergyPoverty/energypoverty2019_100pct_elecrate.tif'
    elif mode == '10k':
        filename = f'{filepath}/EnergyPoverty/energypoverty2019_100pct_elecrate_excl10k.tif'
    if not geoms:
        raster, _ = loader.load_map(filename)
        population_poverty = np.sum(raster)
    else:
        with rasterio.open(filename) as raster:
            country_vals, _ = mask(raster, geoms, crop=True, all_touched=True, nodata=0)
        population_poverty = np.sum(country_vals)
    return population_poverty
