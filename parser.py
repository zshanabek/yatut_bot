import requests
import json
subjects_url = "http://yatut.herokuapp.com/subjects.json"

response = requests.get(url=subjects_url)

data = response.json()

print(data[0]['id'])
st = {d['id']:d['name'] for d in data}


print(st)