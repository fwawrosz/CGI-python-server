import requests

BASE = "http://127.0.0.1:5000/"


response = requests.get(BASE + "twittersearch", {"subject": "Machine Learning"})
print(response.json())