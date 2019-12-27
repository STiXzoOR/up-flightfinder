import csv
import os
import re
import json
import requests
import time
from datetime import datetime, timedelta
from collections import defaultdict
from bs4 import BeautifulSoup

current_dir = os.getcwd()
durations = defaultdict(dict)


def get_time_through_api(source='', dest=''):
    url = "https://distanceto.p.rapidapi.com/get"

    headers = {'x-rapidapi-host': "distanceto.p.rapidapi.com",
               'x-rapidapi-key': "your-rapid-api-key"
               }

    route = '[{{"t": "{from_code}"}}, {{"t": "{to_code}"}}]'.format(from_code=source,
                                                                    to_code=dest)

    querystring = {"car": "false", "foot": "false", "route": route}
    response = requests.request("GET", url,
                                headers=headers,
                                params=querystring).json()

    time = response['steps'][0]['distance']['flight'][0]['time']

    return time


def get_time_through_soup(source='', dest=''):
    url = 'https://www.distance.to/{from_code}/{to_code}'.format(from_code=source,
                                                                 to_code=dest)

    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    contents = soup.find(class_="label flight").contents

    return contents[len(contents)-1].strip()


with open(current_dir + '/csv_data/routes_minimal.csv', mode='r') as input_csv, open(current_dir + '/csv_data/routes_durations.json', mode='w') as output_json:
    csv_reader = csv.DictReader(input_csv,
                                delimiter=';',
                                fieldnames=['from', 'to'])

    for row in csv_reader:
        if row['from'] != '':
            source = row['from']
            dest = row['to']

            time = get_time_through_soup(source=source, dest=dest)
            time = re.sub(r'[\(\)]', '', time)

            time = time.replace('h ', ':').replace('min', '')
            time_obj = datetime.strptime(time, '%H:%M').time()

            durations[source].update({dest: str(time_obj)})

    json.dump(durations, output_json)
