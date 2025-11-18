import glob 
import os
import json

all_dir = glob.glob('./CoDiet-Gold-private/*.json')

try:
    os.mkdir('./output')
except:
    pass

try:
    os.mkdir('./output/passages_input')
except:
    pass
    
for i in range(len(all_dir)):
    f = open(all_dir[i])
    data = json.load(f)
    f.close()
    for j in range(len(data.get('documents')[0].get('passages'))):
        f = open(f"./output/passages_input/{all_dir[i].split('/')[-1].split('.')[0]}_{j}.txt", "w", encoding="utf-8")
        f.write(data.get('documents')[0].get('passages')[j].get('text'))
        f.close()
