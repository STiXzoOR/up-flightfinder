import requests

url = "https://distanceto.p.rapidapi.com/get"

querystring = {"car": "false", "foot": "false",
               "route": '[{{"t": "{}"}}, {{"t": "{}"}}]'.format('ATH', 'LCA')}

headers = {
    'x-rapidapi-host': "distanceto.p.rapidapi.com",
    'x-rapidapi-key': "d4bdcae801mshc1fcc7068884f48p161098jsnfc08a640a4bb"
}

response = requests.request(
    "GET", url, headers=headers, params=querystring).json()

print(response['steps'][0]['distance']['flight'][0]['time'])
