import requests

BASE = "http://127.0.0.1:5000/"



#response = requests.put(BASE + "user/6", {"user_name": "PooPoo ButHole", "user_is_employer": 1})
#print(response.json())
#response = requests.put(BASE + "user/10", {"user_name": "Noneya Buisness", "user_is_employer": 0})
#print(response.json())

#response = requests.patch(BASE + "user/1", {"user_application": "4"})
#print(response.json())

#response = requests.put(BASE + "job/69", {"job_owner": 6, "job_title": "Quick MAffs", "job_description": "2+2 is 4 - 1 is 3"})
#print(response.json())

#response = requests.patch(BASE + "job/69", {"job_applicant": "10"})
#print(response.json())

#response = requests.get(BASE + "twittersearch", {"subject": "Machine Learning"})
#print(response.json())

#response = requests.delete(BASE + "job/1")
#print(response.json())

#input()
response = requests.get(BASE + "job/1", {"job_get_flag" : "a"})
print(response.json())