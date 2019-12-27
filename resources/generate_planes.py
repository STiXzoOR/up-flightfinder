import csv
import os

current_dir = os.getcwd()

capacities = {"319": 134,
              "320": 150,
              "321": 185,
              "330": 293,
              "332": 225,
              "333": 283,
              "346": 342,
              "388": 525,
              "733": 148,
              "735": 140,
              "737": 210,
              "738": 175,
              "744": 416,
              "752": 228,
              "757": 240,
              "763": 210,
              "764": 243,
              "767": 174,
              "772": 313,
              "773": 370,
              "777": 300,
              "787": 267,
              "788": 325,
              '32A': 210,
              '32B': 180,
              '32S': 222,
              '73H': 160,
              '75W': 230,
              '76W': 208,
              "77W": 370,
              "AR8": 112,
              "CRK": 100,
              "CR9": 88,
              "E90": 95,
              }

missing_airplanes = {'32A': 'Airbus A320 (Sharklet)',
                     '32B': 'Airbus A321 (Sharklet)',
                     '32S': 'Airbus (A318/A318/A320/A321)',
                     '73H': 'Boeing 737-800 (73H)',
                     '75W': 'Boeing 757-200 (75W)',
                     '76W': 'Boeing 767-300ER (76W)',
                     }

with open(current_dir + '/csv_data/planes.csv', mode='r') as file:
    airplanes = [line.strip() for line in file.readlines()]

with open(current_dir + '/csv_data/planes.txt', mode='r') as input_csv, open(current_dir + '/csv_data/planes_comp.csv', mode='w') as output_csv:
    csv_reader = csv.DictReader(input_csv,
                                delimiter=',',
                                fieldnames=['name', 'iata', ' iaco'])
    csv_writer = csv.DictWriter(output_csv,
                                fieldnames=['airplane_model',
                                            'name', 'capacity'],
                                quoting=csv.QUOTE_ALL)
    for row in csv_reader:
        if row['name'] != '':
            if row['iata'] in airplanes:
                airplane_record = {'airplane_model': row['iata'],
                                   'name': row['name'],
                                   'capacity': capacities[row['iata']]}

                csv_writer.writerow(airplane_record)

    for model, name in missing_airplanes.items():
        if model in airplanes:
            airplane_record = {'airplane_model': model,
                               'name': name,
                               'capacity': capacities[model]}

            csv_writer.writerow(airplane_record)
