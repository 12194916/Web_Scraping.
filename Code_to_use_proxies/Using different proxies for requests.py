#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import requests
import queue
import threading
q=queue.Queue()
valid_proxies=[]
with open("proxy_list.txt","r") as f:
    proxies=f.read().split("\n")
    for p in proxies:
        q.put(p)

def check_proxies():
    global q
    while not q.empty():
        proxy=q.get()
        try:
            res=requests.get("http://ipinfo.io/json",
                            proxies={"http":proxy,
                                    "https":proxy})
        except:
            continue
        if res.status_code==200:
            print(proxy)
for _ in range(10):
    threading.Thread(target=check_proxies).start()
    


with open("valid_proxy_list.txt",'r') as f:
    proxies=f.read().split("\n")

try:
    counter = random.randint(0, len(proxies) - 1)
    proxy = proxies[counter]
    print(f"Using the proxy: {proxy}")
    url="website url"

    # Set the proxy for Chrome
    res=requests.get(url,proxies={"http": proxies[counter],
                                    "http": proxies[counter]})
    print(res.status_code)
#     print(res.text)
except:
    print("Proxy change failed")
finally:
    counter = random.randint(1, len(proxies)-1
                             

def get_current_ip():
    try:
        response = requests.get('https://api.ipify.org?format=json')
        data = response.json()
        current_ip = data['ip']
        return current_ip
    except requests.RequestException:
        return None

# Get the current IP address
current_ip = get_current_ip()
if current_ip:
    print(f"Current IP: {current_ip}")
else:
    print("Failed to retrieve the current IP address.")

