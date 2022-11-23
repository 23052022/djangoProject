import requests


resp = requests.post('http://127.0.0.1:8000/route/review', {'id_route': 1})
print(resp.status_code, resp.text)
