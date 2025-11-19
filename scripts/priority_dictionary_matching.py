import pandas as pd
import re
import glob
import os

file_path = "./data/priority_dictionary/p_protein.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_protein = list(df.Entity)
p_protein_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_foodRelated.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_foodRelated = list(df.Entity)
p_foodRelated_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_metabolite.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_metabolite = list(df.Entity)
p_metabolite_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_computational.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_compu = list(df.Entity)
p_compu_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_dietMethod.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_diet = list(df.Entity)
p_diet_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_disease.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_disease = list(df.Entity)
p_disease_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_populationCharacteristic.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_popu = list(df.Entity)
p_popu_id = list(df.Identifier)

file_path = "./data/priority_dictionary/p_sampleType.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
p_sample = list(df.Entity)
p_sample_id = list(df.Identifier)

try:
    os.mkdir('./output/priority_dictionary_output')
except:
    pass

def find_matches(text, word_list, id_list):
    # Create a case-insensitive regular expression pattern that matches any word from the list
    pattern = r'\b(?:' + '|'.join(re.escape(word) for word in word_list) + r')\b'
    
    # Find all matches in the text
    matches = []
    for match in re.finditer(pattern, text, re.IGNORECASE):
        word = match.group().lower()
        if word in word_list:
            index = word_list.index(word)
            matches.append((match.start(), match.end(), word, id_list[index]))
    
    return matches

input_list = glob.glob('./output/passages_input/*.txt')

for i in range(len(input_list)):
    if len(input_list) > 100:
        if i % (len(input_list) // 10) == 0:
            print(f'Processing index: {i} of {len(input_list)}')
    f = open(f"{input_list[i]}", "r")
    data = f.read()
    f.close()
    
    annotation = []
    matches = find_matches(data, p_foodRelated, p_foodRelated_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'foodRelated', identifier])
    matches = find_matches(data, p_protein, p_protein_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'proteinEnzyme', identifier])
    matches = find_matches(data, p_metabolite, p_metabolite_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'metabolite', identifier]) 
    matches = find_matches(data, p_compu, p_compu_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'computational', identifier])
    matches = find_matches(data, p_diet, p_diet_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'dietMethod', identifier])  
    matches = find_matches(data, p_disease, p_disease_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'diseasePhenotype', identifier])
    matches = find_matches(data, p_popu, p_popu_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'populationCharacteristic', identifier])
    matches = find_matches(data, p_sample, p_sample_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'sampleType', identifier])
    
    for j in range(len(annotation)):
        f = open(f"./output/priority_dictionary_output/{input_list[i].split('/')[-1]}", "a+")
        f.write(str(annotation[j]) + '\n')
        f.close()
