import pandas as pd
import re
import glob
import os

file_path = "./data/dictionary/computational.csv"
df = pd.read_csv(file_path)
computational = list(df.Entity)
computational_id = list(df.Identifier)

file_path = "./data/dictionary/dataType.csv"
df = pd.read_csv(file_path)
dataType = list(df.Entity)
dataType_id = list(df.Identifier)

file_path = "./data/dictionary/dietMethod.csv"
df = pd.read_csv(file_path)
dietMethod = list(df.Entity)
dietMethod_id = list(df.Identifier)

file_path = "./data/dictionary/disease.csv"
df = pd.read_csv(file_path)
disease = list(df.Entity)
disease_id = list(df.Identifier)

file_path = "./data/dictionary/foodRelated.csv"
df = pd.read_csv(file_path)
foodRelated = list(df.Entity)
foodRelated_id = list(df.Identifier)

file_path = "./data/dictionary/methodology.xlsx"
df = pd.read_excel(file_path)
df[['Entity', 'Identifier']] = pd.DataFrame(df['Entity,Identifier'].str.split(',').tolist())
methodology = list(df.Entity)
methodology_id = list(df.Identifier)

file_path = "./data/dictionary/modelOrganism.csv"
df = pd.read_csv(file_path)
modelOrganism = list(df.Entity)
modelOrganism_id = list(df.Identifier)

file_path = "./data/dictionary/populationCharacteristic.csv"
df = pd.read_csv(file_path)
populationCharacteristic = list(df.Entity)
populationCharacteristic_id = list(df.Identifier)

file_path = "./data/dictionary/sampleType.csv"
df = pd.read_csv(file_path)
sampleType = list(df.Entity)
sampleType_id = list(df.Identifier)

try:
    os.mkdir('./output/dictionary_output')
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
    matches = find_matches(data, computational, computational_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'computational', identifier])
    matches = find_matches(data, dataType, dataType_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'dataType', identifier])
    matches = find_matches(data, dietMethod, dietMethod_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'dietMethod', identifier])
    matches = find_matches(data, disease, disease_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'diseasePhenotype', identifier])
    matches = find_matches(data, foodRelated, foodRelated_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'foodRelated', identifier])
    matches = find_matches(data, methodology, methodology_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'methodology', identifier])
    matches = find_matches(data, modelOrganism, modelOrganism_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'modelOrganism', identifier])
    matches = find_matches(data, populationCharacteristic, populationCharacteristic_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'populationCharacteristic', identifier])
    matches = find_matches(data, sampleType, sampleType_id)
    for start, end, word, identifier in matches:
        annotation.append([start, end, word, 'sampleType', identifier])
    pattern = r"\b(rs\d+)\b"
    term_positions = [(match.start(), match.end()) for match in re.finditer(pattern, data)]
    terms = [match.group() for match in re.finditer(pattern, data)]
    for loc in range(len(term_positions)):
        annotation.append([term_positions[loc][0], term_positions[loc][1], terms[loc], 'geneSNP', terms[loc]])
    
    for j in range(len(annotation)):
        f = open(f"./output/dictionary_output/{input_list[i].split('/')[-1]}", "a+")
        f.write(str(annotation[j]) + '\n')
        f.close()

print('Process complete!')
