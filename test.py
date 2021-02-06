import requests

BASE = "http://127.0.0.1:5000/"



#response = requests.put(BASE + "user/1", {"user_name": "Felix Wawrosz", "user_is_employer": 0})
#print(response.json())

response = requests.patch(BASE + "user/1", {"user_application": "4"})
print(response.json())








#response = requests.get(BASE + "twittersearch", {"subject": "Machine Learning"})
#print(response.json())