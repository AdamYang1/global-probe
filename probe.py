import wiuppy
import csv
import json
from datetime import datetime

# ========================== prep for sending requests ===========================

CLIENT_ID = '65389d4cf00b37b57c037943'
TOKEN = '740408b61c018517dad0b50719715082'
API = wiuppy.WIU('65389d4cf00b37b57c037943', '740408b61c018517dad0b50719715082')
BASE_URL = 'https://router-worker.adamyang.workers.dev/transfer'
EXPORT_PATH = './data'

servers = API.servers()
server_info_dict = {}
for item in servers:
    city_name = item['name']
    # create a new entry in the dictionary with city name as the key
    server_info_dict[city_name] = {
        'latitude': item['latitude'],
        'longitude': item['longitude']
    }

server_list = [item['name'] for item in servers]
# server_list_2 = [ 'london', 'chicago' ] # for test

# ================================ end prep =======================================

# ping server ip to find out the location
# TODO ip anycast


# ========================== start sending requests ===========================
def probe(size):
    job = wiuppy.Job(API)
    job.uri = BASE_URL + '/' + str(size)
    job.tests = ['http']
    job.servers = server_list ## TODO this is where we modify test & real probe list
    job.options = {'http': {'method': 'GET'}}
    job_id = job.submit().id
    # get the API response as a python dictionary
    results = API.retrieve(job_id) # tasks will be 'in progress' until they complete
    job.retrieve(poll=True)  # query the API until all the tasks are done
    return job # job results as a python dict
    
# generate file name with timestamp & size info
def generateFileName(size):
    now = datetime.now()
    # Format the datetime object as a string in the specified format
    formatted_datetime = now.strftime("%Y-%m-%d-%H-%M")
    return '{timestamp}-s{size}'.format(timestamp=formatted_datetime, size=size )

def exportProbeAsCSV(export_data, size):
    file_name = '{path}/{fname}.csv'.format(path = EXPORT_PATH, fname = generateFileName(size) )
    with open(file_name, 'w') as f:
        # Write all the dictionary keys in a file with commas separated.
        f.write(','.join(export_data[0].keys()))
        f.write('\n') # Add a new line
        for row in export_data:
            # Write the values in a row.
            f.write(','.join(str(x) for x in row.values()))
            f.write('\n') # Add a new line

def main():
    # Parse the JSON string to a Python dict
    size = 100
    res = probe(size)
    data = json.loads(str(res))
    
    # Access the 'http' data for each city
    export_data = []
    for city, info in data['results'].items():
        # http_list = info['http']
        # Add it to our http_data dictionary
        # http_data[city] = http_list
        request_summary = info['http'][0]
        request_summary['location'] = city
        request_summary['latitude'] = server_info_dict[city]['latitude']
        request_summary['longitude'] = server_info_dict[city]['longitude']
        export_data.append(request_summary)

    exportProbeAsCSV(export_data, size)
    # print(export_data)


main()

# get the results from a previously submitted job
# print(wiuppy.Job(API, job_id).retrieve())

# ========================== end sending requests ===========================