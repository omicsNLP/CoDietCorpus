import pandas as pd 
import numpy as np 
import re
import os 
import glob
import pickle
import zipfile
import json
import ast
from fuzzywuzzy import fuzz
from datetime import datetime, timedelta
import torch
from transformers import AutoTokenizer, AutoModelForTokenClassification
from difflib import SequenceMatcher

exclude = []

def highest_similarity(string, word_list):
    string_lower = string.lower()
    word_list_lower = [word.lower() for word in word_list]
    similarities = [SequenceMatcher(None, string_lower, word_lower).ratio() for word_lower in word_list_lower]
    # Find the highest similarity score
    max_similarity = max(similarities)
    # Find all indices with the highest similarity score
    highest_indices = [i for i, score in enumerate(similarities) if score == max_similarity]
    # Return a list of tuples with (similarity score, word) for each highest similarity word
    result = [(max_similarity, word_list[i]) for i in highest_indices]
    return result

def extract_last_level(d, parent_key='', sep='_'):
    result = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            result.update(extract_last_level(v, new_key, sep=sep))
        else:
            result[k] = v[0]  # Assuming there's always a single element in the list
    return result

def create_sublists(lst, lst2, tokens):
    sublists = []
    start_idx = None

    for i, value in enumerate(lst):
        if value == 1:
            start_idx = i
        elif value == 0 and start_idx is not None:
            end_idx = i
            while start_idx > 0 and tokens[start_idx][:2] == '##':
                start_idx -= 1
            if tokens[end_idx][:2] == '##':
                end_idx += 1
                while end_idx < len(tokens) - 1 and tokens[end_idx + 1][:2] == '##':
                    end_idx += 1
                sublists.append(lst2[start_idx:end_idx])
            else:
                sublists.append(lst2[start_idx:end_idx])
            start_idx = None

    return sublists

def find_start_end_trigger(model, tokenizer, input_text):
    # Tokenize the input text
    inputs = tokenizer(input_text, return_tensors="pt", truncation=True, return_offsets_mapping=True)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].tolist())
    offsets_mapping = inputs.pop("offset_mapping")[0].tolist()

    # Make predictions
    with torch.no_grad():
        outputs = model(**inputs)

    # Get the predicted labels
    predictions = torch.argmax(outputs.logits, dim=2)[0]
    
    # Find the start position in the original text
    start_position = -1
    for i in range(len(predictions)):
        if tokens[i] != '[PAD]':
            start_position = i
            break

    # Check if a non-padding label is found
    if start_position == -1:
        return None, None, None, None, None, None

    # Find the end position in the original text
    end_position = start_position + 1
    while end_position < len(predictions) and tokens[end_position] != '[PAD]':
        end_position += 1

    # Convert token positions to character positions
    char_start_position = tokenizer.convert_tokens_to_string(tokens[:start_position]).count(' ')
    char_end_position = tokenizer.convert_tokens_to_string(tokens[:end_position-1]).count(' ')

    # Extract the trigger text
    trigger = tokenizer.convert_tokens_to_string(tokens[start_position:end_position])

    return predictions, tokens, offsets_mapping, start_position, end_position, trigger

# Load your model and tokenizer
model_name = 'Antoinelfr/bronze_silver_GH'  # Replace with your actual model name
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

def find_similar_substring(text, substring):
    best_match = None
    best_score = -1

    # Iterate through the text and compare each substring
    for i in range(len(text)):
        for j in range(i + 1, len(text) + 1):
            candidate = text[i:j]
            score = fuzz.ratio(candidate, substring)
            
            # Adjust the score threshold as needed
            if score > best_score:
                best_score = score
                best_match = (i, j)
    if best_score > 90:
        return best_match
    else:
        return (None,None)


os.mkdir('./bronze')
all_input = glob.glob('./CoDiet-Gold-private/*')
for i in range(len(all_input)):
    all_input[i] = all_input[i].split('/')[-1].split('.')[0]
    
all_input_2 = glob.glob('./bronze/*')
for i in range(len(all_input_2)):
    all_input_2[i] = all_input_2[i].split('/')[-1].split('.')[0]
        
for uyi in range(len(all_input)):
    if all_input[uyi] in all_input_2:
        pass
    else:
        if len(all_input) > 100:
            if uyi % (len(all_input) // 10) == 0:
                print(f'Processing index: {uyi} of {len(all_input)}')
        f = open(f'./CoDiet-Gold-private/{all_input[uyi]}.json')
        all_data = json.load(f)
        f = open(f'./output/enzyme_annotated/{all_input[uyi]}_annotated.json')
        enzyme_data = json.load(f)
        f = open(f'./output/microbELP_result/{all_input[uyi]}.json')
        microbiome_data = json.load(f)
        total = 1

        print(all_input[uyi])
        for ycf in range(len(all_data.get('documents')[0].get('passages'))):
            data = all_data.get('documents')[0].get('passages')[ycf].get('text')
            current_offset = all_data.get('documents')[0].get('passages')[ycf].get('offset')
            start_pheno = []
            len_pheno = []
            id_pheno = []
            trigger_pheno = []
            try:
                f = open(f'./output/phenobert_output/{all_input[uyi]}_{ycf}.txt', "r")
                data_pheno = f.read()
                f.close()

                temporary = data_pheno.split('\n')
                data_split = []
                for i in range(len(temporary)):
                    if temporary[i] != '':
                        data_split.append(temporary[i].replace('\t', ' '))
                for i in range(len(data_split)):
                    start_pheno.append(current_offset + int(data_split[i].split()[0]))
                    len_pheno.append(int(data_split[i].split()[1]) - int(data_split[i].split()[0]))
                    trigger_pheno.append(data[int(data_split[i].split()[0]):int(data_split[i].split()[1])])
                    id_pheno.append(str('HP:' + str(data_split[i].split('HP:')[-1].split()[0])))
            except:
                pass

            start_bern = []
            len_bern = []
            id_bern = []
            trigger_bern = []
            cat_bern = []
            try:
                f = open(f'./output/bern2_output/{all_input[uyi]}_{ycf}.txt', "r")
                data_bern = f.read()
                f.close()
                res = ast.literal_eval(data_bern)
                diff = 2 * (len(data) - len(res.get('text')))
                if diff > 50:
                    pass
                else:
                    for i in range(len(res.get('annotations'))):
                        if res.get('annotations')[i].get('span').get('begin') < 10 + diff:
                            start, end = find_similar_substring(data[:int(res.get('annotations')[i].get('span').get('end')) + 10 + diff], res.get('text')[:int(res.get('annotations')[i].get('span').get('end')) + 10])
                            if start != None:
                                id_bern.append(str(res.get('annotations')[i].get('id')).replace("['", '').replace("', '", ',').replace("']", ''))
                                cat_bern.append(str(res.get('annotations')[i].get('obj')))
                                start_bern.append(current_offset + start)
                                len_bern.append(end - start - 10)
                                trigger_bern.append(data[start:end-10])
                            else:
                                pass
                        elif res.get('annotations')[i].get('span').get('end') > len(res.get('text')) - 10 - diff:
                            previous = int(res.get('annotations')[i].get('span').get('begin')) - 10 - diff
                            start, end = find_similar_substring(data[int(res.get('annotations')[i].get('span').get('begin')) - 10 - diff:], res.get('text')[int(res.get('annotations')[i].get('span').get('begin')) - 10:int(res.get('annotations')[i].get('span').get('end'))])
                            if start:
                                id_bern.append(str(res.get('annotations')[i].get('id')).replace("['", '').replace("', '", ',').replace("']", ''))
                                cat_bern.append(str(res.get('annotations')[i].get('obj')))
                                start_bern.append(current_offset + previous + start + 10)
                                len_bern.append(end - (start +10))
                                trigger_bern.append(data[previous + start + 10:previous+end])
                            else:
                                pass
                        else:
                            previous = int(res.get('annotations')[i].get('span').get('begin')) - 10 - diff
                            start, end = find_similar_substring(data[int(res.get('annotations')[i].get('span').get('begin')) - 10 - diff:int(res.get('annotations')[i].get('span').get('end')) + 10 + diff], res.get('text')[int(res.get('annotations')[i].get('span').get('begin')) - 10:int(res.get('annotations')[i].get('span').get('end')) + 10])
                            if start:
                                id_bern.append(str(res.get('annotations')[i].get('id')).replace("['", '').replace("', '", ',').replace("']", ''))
                                cat_bern.append(str(res.get('annotations')[i].get('obj')))
                                start_bern.append(current_offset + previous + start + 10)
                                len_bern.append((end - 10) - (start + 10))
                                trigger_bern.append(data[previous+start+10:previous+end-10])
                            else:
                                pass
            except:
                pass

            start_dict = []
            len_dict = []
            id_dict = []
            trigger_dict = []
            cat_dict = []
            try:
                f = open(f'./output/dictionary_output/{all_input[uyi]}_{ycf}.txt', "r")
                data_dict = f.read()
                f.close()
                data_dict = data_dict.split('\n')
                final_data_dict = []
                for i in range(len(data_dict)-1):
                    final_data_dict.append(ast.literal_eval(data_dict[i]))
                single_final_data_dict = []
                for i in range(len(final_data_dict)):
                    if final_data_dict[i] not in single_final_data_dict:
                        single_final_data_dict.append(final_data_dict[i])
                for i in range(len(single_final_data_dict)):
                    start_dict.append(current_offset + single_final_data_dict[i][0])
                    len_dict.append(single_final_data_dict[i][1] - single_final_data_dict[i][0])
                    id_dict.append(single_final_data_dict[i][-1])
                    cat_dict.append(single_final_data_dict[i][3])
                    trigger_dict.append(data[single_final_data_dict[i][0]:(single_final_data_dict[i][0]) + (single_final_data_dict[i][1] - single_final_data_dict[i][0])])
            except:
                pass

            start_pdict = []
            len_pdict = []
            id_pdict = []
            trigger_pdict = []
            cat_pdict = []
            try:
                f = open(f'./output/priority_dictionary_output/{all_input[uyi]}_{ycf}.txt', "r")
                data_dict = f.read()
                f.close()
                data_dict = data_dict.split('\n')
                final_data_dict = []
                for i in range(len(data_dict)-1):
                    final_data_dict.append(ast.literal_eval(data_dict[i]))
                single_final_data_dict = []
                for i in range(len(final_data_dict)):
                    if final_data_dict[i] not in single_final_data_dict:
                        single_final_data_dict.append(final_data_dict[i])
                for i in range(len(single_final_data_dict)):
                    start_pdict.append(current_offset + single_final_data_dict[i][0])
                    len_pdict.append(single_final_data_dict[i][1] - single_final_data_dict[i][0])
                    id_pdict.append(single_final_data_dict[i][-1])
                    cat_pdict.append(single_final_data_dict[i][3])
                    trigger_pdict.append(data[single_final_data_dict[i][0]:(single_final_data_dict[i][0]) + (single_final_data_dict[i][1] - single_final_data_dict[i][0])])
            except:
                pass

            start_enzyme = []
            len_enzyme = []
            id_enzyme = []
            trigger_enzyme = []
            cat_enzyme = []

            for i in range(len(enzyme_data.get('documents')[0].get('passages')[ycf].get('annotations'))):
                start_enzyme.append(enzyme_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['locations'][0]['offset'])
                len_enzyme.append(enzyme_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['locations'][0]['length'])
                id_enzyme.append(enzyme_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['infons']['identifier'])
                trigger_enzyme.append(enzyme_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['text'])
                cat_enzyme.append('proteinEnzyme')

            start_microbiome = []
            len_microbiome = []
            id_microbiome = []
            trigger_microbiome = []
            cat_microbiome = []

            for i in range(len(microbiome_data.get('documents')[0].get('passages')[ycf].get('annotations'))):
                start_microbiome.append(microbiome_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['locations']['offset'])
                len_microbiome.append(microbiome_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['locations']['length'])
                id_microbiome.append(microbiome_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['infons']['identifier'])
                trigger_microbiome.append(microbiome_data.get('documents')[0].get('passages')[ycf].get('annotations')[i]['text'])
                cat_microbiome.append('microbiome')

            current_offset = all_data.get('documents')[0].get('passages')[ycf].get('offset')
            # Input text
            input_text = all_data.get('documents')[0].get('passages')[ycf]['text']
            # Find start and end positions and trigger
            # Chunk size
            chunk_size = 512
            chunks = [input_text[i:i + chunk_size] for i in range(0, len(input_text), chunk_size)]

            # Initialize lists to store metadata
            start_meta = []
            len_meta = []
            id_meta = []
            trigger_meta = []
            cat_meta = []
            accumulated_offset = 0

            # Process each chunk
            for chunk in chunks:
                # Find start and end positions and trigger for the current chunk
                predictions, tokens, offsets_mapping, start_position, end_position, trigger = find_start_end_trigger(model, tokenizer, chunk)
                to_identify = create_sublists(predictions, offsets_mapping, tokens)

                # Populate metadata lists for the current chunk
                for i in range(len(to_identify)):
                    start_meta.append(current_offset + accumulated_offset + to_identify[i][0][0])
                    len_meta.append(to_identify[i][-1][1] - to_identify[i][0][0])
                    trigger_meta.append(input_text[accumulated_offset + to_identify[i][0][0]:(accumulated_offset + to_identify[i][0][0]) + (to_identify[i][-1][1] - to_identify[i][0][0])])
                    cat_meta.append('metabolites')
                    id_meta.append('')

                # Accumulate offset for the next chunk
                accumulated_offset += len(chunk)

            start_ppmm = []
            len_ppmm = []
            id_ppmm = []
            trigger_ppmm = []
            cat_ppmm = []
            try:    
                try:
                    archive_ppmm = zipfile.ZipFile(f'./output/output_ParallelPyMetaMap_text_mo/txt_files_input/{all_input[uyi]}_{ycf}.txt.zip', 'r')
                    data_ppmm = archive_ppmm.read(f'{all_input[uyi]}_{ycf}.txt').decode()
                except:
                    f = open(f'./output/output_ParallelPyMetaMap_text_mo/txt_files_input/{all_input[uyi]}_{ycf}.txt', "r")
                    data_ppmm = f.read()
                    f.close()
                with zipfile.ZipFile(f'./output/output_ParallelPyMetaMap_text_mo/annotated_json/{all_input[uyi]}_{ycf}.json.zip', "r") as z:
                    for filename in z.namelist():
                        with z.open(filename) as f:
                            d = f.read()
                            content = json.loads(d)
                f.close()
                z.close()
                keys_id = list(content.keys())
                diff = 2 * abs(len(data) - len(data_ppmm))
                if diff > 50:
                    pass
                else:
                    keys_id = list(content.keys())

                    for i in range(len(keys_id)):
                        for j in range(len(content.get(f'{keys_id[i]}').get('pos_info'))):
                            if int(content.get(f'{keys_id[i]}').get('score')[j]) > 849 or int(content.get(f'{keys_id[i]}').get('score')[j]) < -849:
                                if int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[1]) > 2:
                                    if int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) < 10 + diff:
                                        start, end = find_similar_substring(data[:(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) + int(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[-1]))) + 10 + diff], data_ppmm[:(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) + int(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[-1]))) + 10])
                                        if start != None:
                                            id_ppmm.append(keys_id[i])
                                            cat_ppmm.append(content.get(f'{keys_id[i]}').get('full_semantic_type_name')[0])
                                            start_ppmm.append(current_offset + start)
                                            len_ppmm.append(end - start - 10)
                                            trigger_ppmm.append(data[start:end-10])
                                        else:
                                            pass


                                    elif int(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) + int(int(content.get(f'{keys_id[i]}').get('pos_info')[0][0].split('/')[-1]))) > len(data_ppmm) - 10 - diff:
                                        previous = int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) - 10 - diff
                                        start, end = find_similar_substring(data[int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) - 10 - diff:], data_ppmm[int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) - 10:(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) + int(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[-1])))])
                                        if start:
                                            id_ppmm.append(keys_id[i])
                                            cat_ppmm.append(content.get(f'{keys_id[i]}').get('full_semantic_type_name')[0])
                                            start_ppmm.append(current_offset + previous + start + 10)
                                            len_ppmm.append(end - (start +10))
                                            trigger_ppmm.append(data[previous + start + 10:previous+end])
                                        else:
                                            pass


                                    else:
                                        previous = int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) - 10 - diff
                                        start, end = find_similar_substring(data[int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) - 10 - diff:(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) + int(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[-1]))) + 10 + diff], data_ppmm[int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) - 10:(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[0]) + int(int(content.get(f'{keys_id[i]}').get('pos_info')[j][0].split('/')[-1]))) + 10])
                                        if start:
                                            id_ppmm.append(keys_id[i])
                                            cat_ppmm.append(content.get(f'{keys_id[i]}').get('full_semantic_type_name')[0])
                                            start_ppmm.append(current_offset + previous + start + 10)
                                            len_ppmm.append((end - 10) - (start + 10))
                                            trigger_ppmm.append(data[previous+start+10:previous+end-10])
                                        else:
                                            pass
            except:
                pass

            codiet_ppmm = []
            for i in range(len(cat_ppmm)):
                if cat_ppmm[i] == 'Food':
                    codiet_ppmm.append('foodRelated')
                elif cat_ppmm[i] == 'Research Activity':
                    codiet_ppmm.append('methodology')
                elif cat_ppmm[i] == 'Laboratory Procedure':
                    codiet_ppmm.append('dataType')
                elif cat_ppmm[i] == 'Body Substance': #Body Substance
                    codiet_ppmm.append('sampleType')
                else:
                    pass


            final_start_bern = []
            final_len_bern = []
            final_id_bern = []
            final_trigger_bern = []
            final_cat_bern = []
            final_codiet_bern = []
            for i in range(len(cat_bern)):
                if cat_bern[i] == 'disease':
                    final_start_bern.append(start_bern[i])
                    final_len_bern.append(len_bern[i])
                    final_id_bern.append(id_bern[i])
                    final_trigger_bern.append(trigger_bern[i])
                    final_cat_bern.append(cat_bern[i])
                    final_codiet_bern.append('diseasePhenotype')
                if cat_bern[i] == 'species':
                    final_start_bern.append(start_bern[i])
                    final_len_bern.append(len_bern[i])
                    final_id_bern.append(id_bern[i])
                    final_trigger_bern.append(trigger_bern[i])
                    final_cat_bern.append(cat_bern[i])
                    final_codiet_bern.append('modelOrganism')
                if cat_bern[i] == 'gene':
                    final_start_bern.append(start_bern[i])
                    final_len_bern.append(len_bern[i])
                    final_id_bern.append(id_bern[i])
                    final_trigger_bern.append(trigger_bern[i])
                    final_cat_bern.append(cat_bern[i])
                    final_codiet_bern.append('geneSNP')


            annotations = []
            current_date = datetime.now() 
            formatted_date = current_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            for i in range(len(start_pdict)):    
                try:
                    annotations.append({
                        'id' : str(total),
                        'infons': {'type': cat_pdict[i],
                               'identifier': id_pdict[i],
                               'annotator': 'p_dictionary@codiet.eu',
                               'updated_at': f'{formatted_date}'},
                        'text': trigger_pdict[i],
                        'locations': [{'offset': start_pdict[i], 'length': len_pdict[i]}]
                    })
                    total += 1
                except:
                    pass
            for i in range(len(start_pheno)):    
                try:
                    annotations.append({
                        'id' : str(total),
                        'infons': {'type': 'diseasePhenotype',
                               'identifier': id_pheno[i],
                               'annotator': 'phenobert@codiet.eu',
                               'updated_at': f'{formatted_date}'},
                        'text': trigger_pheno[i],
                        'locations': [{'offset': start_pheno[i], 'length': len_pheno[i]}]
                    })
                    total += 1
                except:
                    pass
            for i in range(len(start_dict)):    
                try:
                    if id_dict[i] not in exclude:
                        annotations.append({
                            'id' : str(total),
                            'infons': {'type': cat_dict[i],
                                   'identifier': id_dict[i],
                                   'annotator': 'dictionary@codiet.eu',
                                   'updated_at': f'{formatted_date}'},
                            'text': trigger_dict[i],
                            'locations': [{'offset': start_dict[i], 'length': len_dict[i]}]
                        })
                    total += 1
                except:
                    pass
            for i in range(len(start_meta)):    
                try:
                    annotations.append({
                        'id' : str(total),
                        'infons': {'type': cat_meta[i],
                               'identifier': id_meta[i],
                               'annotator': 'MetaboLipidBERT@codiet.eu',
                               'updated_at': f'{formatted_date}'},
                        'text': trigger_meta[i],
                        'locations': [{'offset': start_meta[i], 'length': len_meta[i]}]
                    })
                    total += 1
                except:
                    pass

            for i in range(len(start_enzyme)):    
                try:
                    annotations.append({
                        'id' : str(total),
                        'infons': {'type': cat_enzyme[i],
                               'identifier': id_enzyme[i],
                               'annotator': 'enzyner@codiet.eu',
                               'updated_at': f'{formatted_date}'},
                        'text': trigger_enzyme[i],
                        'locations': [{'offset': start_enzyme[i], 'length': len_enzyme[i]}]
                    })
                    total += 1
                except:
                    pass

            for i in range(len(start_microbiome)):    
                try:
                    annotations.append({
                        'id' : str(total),
                        'infons': {'type': cat_microbiome[i],
                                'identifier': str(id_microbiome[i]).replace("['", "").replace("', '", ',').replace("']", ""),
                               'annotator': 'microbeRT@codiet.eu',
                               'updated_at': f'{formatted_date}'},
                        'text': trigger_microbiome[i],
                        'locations': [{'offset': start_microbiome[i], 'length': len_microbiome[i]}]
                    })
                    total += 1
                except:
                    pass

            for i in range(len(start_ppmm)):    
                try:
                    if id_ppmm[i] not in exclude:
                        annotations.append({
                            'id' : str(total),
                            'infons': {'type': codiet_ppmm[i],
                                   'identifier': id_ppmm[i],
                                   'annotator': 'metamap@codiet.eu',
                                   'updated_at': f'{formatted_date}'},
                            'text': trigger_ppmm[i],
                            'locations': [{'offset': start_ppmm[i], 'length': len_ppmm[i]}]
                        })
                    total += 1
                except:
                    pass
            for i in range(len(final_start_bern)):    
                try:
                    annotations.append({
                        'id' : str(total),
                        'infons': {'type': final_codiet_bern[i],
                               'identifier': final_id_bern[i],
                               'annotator': 'bern2@codiet.eu',
                               'updated_at': f'{formatted_date}'},
                        'text': final_trigger_bern[i],
                        'locations': [{'offset': final_start_bern[i], 'length': final_len_bern[i]}]
                    })
                    total += 1
                except:
                    pass

            all_data['documents'][0]['passages'][ycf]['annotations'] = annotations

            #print(id_ppmm)

        with open(f'./bronze/{all_input[uyi]}.json', 'w', encoding="utf-8") as fp:
            json.dump(all_data, fp, indent = 2, ensure_ascii=False)

