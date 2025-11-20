import requests
import time
import glob
import os

try:
    os.mkdir('./output/bern2_output')
except:
    pass

def query_plain(text, url="http://localhost:8888/plain"):
    return requests.post(url, json={'text': text}).json()


input_list = glob.glob('./output/passages_input/*.txt')
for i in range(len(input_list)):
    input_list[i] = input_list[i].split('/')[-1]


done = glob.glob('./output/bern2_output/*.txt')
for i in range(len(done)):
    done[i] = done[i].split('/')[-1]



to_do = []
for i in range(len(input_list)):
    if input_list[i] in done:
        pass
    else:
        to_do.append(input_list[i])

try:
    test = query_plain('BERN2 is setup')
except:
    time.sleep(60)

for i in range(len(to_do)):
    if len(to_do) > 100:
        if i % (len(to_do) // 10) == 0:
            print(f'Processing index: {i} of {len(to_do)}')
    f = open(f"./output/passages_input/{to_do[i]}", "r")
    data = f.read()
    f.close()
    f = open(f"./output/bern2_output/{to_do[i]}", "w")
    f.write(str(query_plain(data)))
    f.close()
    time.sleep(0.1)
