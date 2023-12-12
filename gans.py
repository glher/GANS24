import sys
import os
import time
import datetime
import yaml
import src.setup as setup
import tls.saver as saver
import src.finder as finder
import src.demand as demand
import src.served as served
import src.stats as stats
import src.aggregater as aggregater


def run(casefile):
    case = CASE
    for reactor in casefile['REACTORS']:
        print(reactor)
        start_run = time.time()
        parameters = setup.run(casefile, case, reactor)
        parameters['paths']['data'] = casefile['DATA']

        if casefile['DEBUG']:
            print('The code will:')
            print('\tFind Potential Sites (using the constraints associated with the case file)')
            print('\tAssess the local need (based on the electricity needs given in the constraints file)')
            print('\tMatch the potential to the need (based on service area information in the constraints file)')
            print('\tObtain the statistics (globally and per country listed in the case constraints file)')
        else:
            finder.potential_sites(parameters)
            demand.needs_assessment(parameters)
            served.service_assessment(parameters)
            stats.run(parameters)
            parameters['runtime'] = str(datetime.timedelta(seconds=time.time() - start_run))
            saver.save_case(parameters)
    if casefile['MODE'] == 'sweep':
        parameters = setup.run(casefile, case, 'all')
        if casefile['DEBUG']:
            print('We are in a sweep mode. The code will combine different scales of reactor power potential.')
        else:
            aggregater.stat_writer(parameters, casefile['REACTORS'])
            aggregater.combine_sites(parameters, casefile['REACTORS'])


if __name__ == "__main__":
    
    CASE = sys.argv[1]
    
    print(f'\n\n\nCase {CASE}\n')
    if not os.path.exists(f'cases/case{CASE}.yml'):
        raise ValueError(f'Case {CASE} does not exist in the cases folder')
    with open(f'cases/case{CASE}.yml', 'r') as s:
        try:
            case_file = yaml.safe_load(s)
        except yaml.YAMLError as e:
            print(e)
    run(case_file)
