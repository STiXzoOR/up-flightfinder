import csv
import os
import glob
from pathlib import Path

current_dir = os.getcwd()


# def convert_to_binary_data(filename):
#     with open(filename, 'rb') as file:
#         binaryData = file.read()
#     return binaryData


with open(current_dir + '/csv_data/airlines.csv', mode='r') as file:
    airlines = [line.strip() for line in file.readlines()]

# logos = sorted(glob.glob(current_dir + '/csv_data/airline_logos/*.png'))
# logos = {k: v for (k, v) in zip(airlines, logos)}

with open(current_dir + '/csv_data/airlines_all.csv', mode='r') as input_csv, open(current_dir + '/csv_data/airlines_comp.csv', mode='w') as output_csv:
    csv_reader = csv.DictReader(input_csv,
                                delimiter=';',
                                fieldnames=['airline_code', 'airline_name'])
    csv_writer = csv.DictWriter(output_csv,
                                fieldnames=['airline_code',
                                            'airline_name'],
                                quoting=csv.QUOTE_ALL)

    for row in csv_reader:
        if row['airline_code'] != '':
            if row['airline_code'] in airlines:
                airline_record = {'airline_code': row['airline_code'],
                                  'airline_name': row['airline_name']
                                  }
                csv_writer.writerow(airline_record)
