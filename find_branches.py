import argparse
import csv
import os

from haversine import haversine
import requests
from tabulate import tabulate


class LatLngError(Exception):
    pass


def get_latlng(address):
    url = 'http://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'sensor': 'false',
    }

    try:
        response = requests.get(url, params=params)
    except requests.RequestException as e:
        raise LatLngError('Could not connect to Google Maps API')

    data = response.json()

    if data['status'] == 'OK':
        if len(data['results']) > 1:
            raise LatLngError('Multiple results returned for {}'.format(address))
        else:
            result = data['results'][0]
            location = result['geometry']['location']
            return location['lat'], location['lng']
    elif data['status'] == 'ZERO_RESULTS':
        raise LatLngError('No results returned for {}').format(address)
    else:
        message = '{} ({})'.format(data['status'], data.get('error_message', 'no specific error'))
        raise LatLngError(message)


def load_chain_records(chain):
    records = []

    with open(os.path.join('data', '{}.csv'.format(chain))) as f:
        reader = csv.reader(f)
        for row in reader:
            record = {
                'chain': chain.title(),
                'name': row[0],
                'latitude': float(row[1]),
                'longitude': float(row[2]),
            }
            records.append(record)

    return records


def load_records(chain):
    if chain is None:
        records = []
        for chain in load_chains():
            records.extend(load_chain_records(chain))
        return records
    else:
        return load_chain_records(chain)


def load_chains():
    chains = []

    for filename in os.listdir('data'):
        chain, ext = os.path.splitext(filename)
        if ext != '.csv':
            continue
        chains.append(chain)

    return chains


def make_table_data(records, include_chain):
    if include_chain:
        lists = [['branch', 'chain', 'miles']]
    else:
        lists = [['branch', 'miles']]

    for record in records:
        lst = [record['name']]
        if include_chain:
            lst.append(record['chain'])
        lst.append('{:.2f}'.format(record['distance_miles']))
        lists.append(lst)

    return lists


def run(address, chain, within_distance_miles, max_results):
    records = load_records(chain)

    try:
        lat, lng = get_latlng(address)
    except LatLngError as e:
        print(e)
        exit(1)

    for record in records:
        record['distance_miles'] = haversine((lat, lng), (record['latitude'], record['longitude']), miles=True)

    if within_distance_miles is not None:
        records = [record for record in records if record['distance_miles'] <= within_distance_miles]

    records.sort(key=lambda r: r['distance_miles'])

    if max_results is not None:
        records = records[:max_results]

    include_chain = not chain
    table_data = make_table_data(records, include_chain=include_chain)
    print(tabulate(table_data, headers='firstrow', tablefmt='orgtbl'))


def parse_args():
    parser = argparse.ArgumentParser(description='Find supermarket branches near you')
    parser.add_argument('--address', required=True)
    parser.add_argument('--chain', choices=load_chains())
    parser.add_argument('--within-distance-miles', metavar='D', type=float)
    parser.add_argument('--max-results', metavar='N', type=int)

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    run(args.address, args.chain, args.within_distance_miles, args.max_results)
