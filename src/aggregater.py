import math
import rasterio
import tls.loader as loader

def get_data(l):
    for line in l:
        if line.startswith('Population in poverty'):
            pp = int(line.split(':')[-1].replace(',', ''))
        elif line.startswith('Population served by'):
            ps = int(line.split(':')[-1].replace(',', ''))
        elif line.startswith('Number of'):
            nr = math.ceil(float(line.split(':')[-1].replace(',', '')))
        if '(' in line:
            p = line.split('(')[-1].split()[0]
    return pp, ps, nr, p


def get_data_10k(l):
    for line in l:
        if line.startswith('[>10km of grid] Population in poverty'):
            pp = int(line.split(':')[-1].replace(',', ''))
        elif line.startswith('[>10km of grid] Population served by'):
            ps = int(line.split(':')[-1].replace(',', ''))
        elif line.startswith('[>10km of grid] Number of'):
            nr = math.ceil(float(line.split(':')[-1].replace(',', '')))
        if '(' in line:
            p = line.split('(')[-1].split()[0]
    return pp, ps, nr, p

def stat_writer(parameters, reactor_types):
    countries = parameters['countries']
    cooling_modes = parameters['cooling_modes']
    cooling_name = parameters['cooling_name']
    case = parameters['case']
    
    towrite = ''
    for c in ['World'] + countries:
        title = f'| REGION: {c} |\n'
        embel = '+' + (len(title) - 3) * '-' + '+\n'
        towrite += '\n\n' + embel + title + embel + '\n'
        col1 = 'Reactor'
        col2 = 'Power'
        col3 = 'Population in Poverty (n)'
        col4 = 'Population Served (n)'
        col5 = 'Population Served (%)'
        col6 = 'Number of Reactors'
        mycols = [col1, col2, col3, col4, col5, col6]
        for cooling in cooling_modes:
            table_text = ' | '.join(mycols) + ' |\n'
            # reactors = [r for r in reactor_types if cooling in r]
            reactors = reactor_types
            towrite += f'\nCooling Method: {cooling_name[cooling]}\n'
            
            towrite += f'\n\nAll population\n'
            for r in reactors:
                with open(f'res/case{case}/{r}/Stats/stats_{c}.txt', 'r') as sf:
                    lines = sf.readlines()
                population_poverty, population_served, number_reactors, power = get_data(lines)
                try:
                    population_served_pct = 100. * population_served / population_poverty
                except ZeroDivisionError:
                    population_served_pct = 0
                reactor_name = r.split('_')[0]
                table_text += f'{reactor_name:{len(col1)}} | {power:{len(col2)}} | {population_poverty:{len(col3)},.0f} | {population_served:{len(col4)},.0f} | {population_served_pct:{len(col5)}.2f} | {number_reactors:{len(col6)},.0f} |\n'
            table_text += '\n'
            towrite += table_text
            
            
            table_text = ' | '.join(mycols) + ' |\n'
            # reactors = [r for r in reactor_types if cooling in r]
            reactors = reactor_types
            towrite += f'\n\nPopulation outside of 10km of transmission lines\n'
            for r in reactors:
                with open(f'res/case{case}/{r}/Stats/stats_{c}.txt', 'r') as sf:
                    lines = sf.readlines()
                population_poverty, population_served, number_reactors, power = get_data_10k(lines)
                try:
                    population_served_pct = 100. * population_served / population_poverty
                except ZeroDivisionError:
                    population_served_pct = 0
                reactor_name = r.split('_')[0]
                table_text += f'{reactor_name:{len(col1)}} | {power:{len(col2)}} | {population_poverty:{len(col3)},.0f} | {population_served:{len(col4)},.0f} | {population_served_pct:{len(col5)}.2f} | {number_reactors:{len(col6)},.0f} |\n'
            table_text += '\n'
            towrite += table_text
            
        towrite += '\n\n\n\n'

    with open(f'res/case{case}/results.txt', 'w') as res:
        res.write(towrite)


def combine_sites(parameters, reactors):
    # This assumes that LWR sites include MMR sites
    powers = parameters['powers']
    reactors = sorted(powers.keys(), key=powers.get)
    # reactors = [f'{r}_CT' for r in reactors]
    case = parameters['case']
    composite = None
    for i, r in enumerate(reactors):
        
        if i == 0:
            raster, meta = loader.load_map(f'res/case{case}/{r}/Sites/potential_sites.tif')
            raster[raster < 999] *= 10
            raster[raster == 0] = 1
            composite = raster
            continue
        
        raster, _ = loader.load_map(f'res/case{case}/{r}/Sites/potential_sites.tif')
        composite[raster == 0] += 1

    with rasterio.open(f'res/case{case}/potential_sites.tif',
                        'w', **meta, compress="DEFLATE") as f:
        f.write(composite, indexes=1)