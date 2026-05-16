import requests
import time

virus_total_api_scan_file_url = "https://www.virustotal.com/api/v3/files"
virus_total_api_scan_link_url = "https://www.virustotal.com/api/v3/urls"
virus_total_api_key = ""
with open("key.txt") as f:
    virus_total_api_key = f.readlines()[1]

def upload_link_for_scan(link):
    response = requests.post(url=virus_total_api_scan_link_url, headers={'x-apikey': virus_total_api_key}, data={'url':link})
    response = response.json()
    print(response)
    return response['data']['id']  # return analysis id


def scan(to_scan, type): #TODO: change parameter for document in bytes and adjust func
    print(f"Scanning {type}: ")
    if type == 'file':
        analysis_id = upload_file_for_scan(to_scan)
    elif type == 'link':
        analysis_id = upload_link_for_scan(to_scan)
    else:
        return "Unknown"
    print(f"File uploaded for scanning. Analysis ID: {analysis_id}")
    # TODO: send http get request with the analysis id to get the scan results

    header = {'x-apikey': virus_total_api_key, "accept": "application/json"}
    suc = True
    data = {}
    while suc:
        time.sleep(10)
        result = requests.get(url=f"https://www.virustotal.com/api/v3/analyses/{analysis_id}",headers=header)
        print(result.text)
        data = result.json()
        print(data)
        status = data["data"]["attributes"]["status"]
        print(status)
        if status == "completed":
            suc = False
    print(data["data"]['attributes']["stats"])




def upload_file_for_scan(file_bytes): #TODO: change parameter for document in bytes and adjust func
    response = requests.post(url=virus_total_api_scan_file_url, headers={'x-apikey': virus_total_api_key}, files={'file': file_bytes})
    response = response.json()
    print(response)
    return response['data']['id'] # return analysis id

#with open("chat.db", 'rb') as f:
 #   s = f.read()
  #  print(s)
   # scan_file(s)

scan(virus_total_api_scan_file_url, "link")