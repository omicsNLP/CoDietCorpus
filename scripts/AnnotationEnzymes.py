"""
Created on Tue Dec  7 11:51:34 2021

@author: Wang Meiqi

Input: Processed KEGG list of enzymes & Biomedical publications in BioC format (Corpus processed by Auto-CORPus)

Output: Annotated corpus inside which the enzymes have been searched out and annotated
"""

import pandas as pd
import json
import re
import os
import time
import csv
#import argparse
import glob
import multiprocessing as mp
from datetime import datetime

#parser = argparse.ArgumentParser(prog='PROG')
#parser.add_argument('-i', '--inputDir', type=str, help="filepath for directory to run the enzyme annotator on")
#parser.add_argument('-o', '--outputDir', type=str, help="filepath for the directory to save annotated files in")

#args = parser.parse_args()
#text_folder_path = args.inputDir
#output_folder = args.outputDir if args.outputDir else os.path.join(text_folder_path,"eNzymER_annotation_output")

def para_enzyme(input_list, output_folder, process_number):

    class bold:
        BEGIN = '\033[1m'
        END = '\033[0m'

    def enzyme_ase_list(word):
        matchword = ''
        first_match = ''
        enzymes_list = []
        flag = 1  # If flag==0, search_list only has first_match.
        if re.match('(.*)synthase', word):
            first_match = 'synthase'
            flag = 0
        elif re.match('(.*)lyase', word):
            first_match = 'lyase'
            flag = 0
        elif re.match('(.*)ligase', word):
            first_match = 'ligase'
            flag = 0
        elif re.match('(.*)ease', word):
            first_match = 'ease'
            if re.match('(.*)permease', word):
                matchword = 'permease'
            elif re.match('(.*)protease', word):
                matchword = 'protease'
            else:
                matchword = 'other'
        elif re.match('(.*)lase', word):
            first_match = 'lase'
            if re.match('(.*)methylase', word):
                matchword = 'methylase'
            elif re.match('(.*)horylase', word):
                matchword = 'horylase'
            elif re.match('(.*)cyclase', word):
                matchword = 'cyclase'
            elif re.match('(.*)hydrolase', word):
                matchword = 'hydrolase'
            elif re.match('(.*)oxylase', word):
                matchword = 'oxylase'
            else:
                matchword = 'other'
        elif re.match('(.*)rase', word):
            first_match = 'rase'
            if re.match('(.*)transferase', word):
                matchword = 'transferase'
            elif re.match('(.*)saturase', word):
                matchword = 'saturase'
            else:
                matchword = 'other'
        elif re.match('(.*)tase', word):
            first_match = 'tase'
            if re.match('(.*)synthetase', word):
                matchword = 'synthetase'
            elif re.match('(.*)reductase', word):
                matchword = 'reductase'
            else:
                matchword = 'other'
        elif re.match('(.*)idase', word):
            first_match = 'idase'
            if re.match('(.*)oxidase', word):
                matchword = 'oxidase'
            elif re.match('(.*)peptidase', word):
                matchword = 'peptidase'
            else:
                matchword = 'other'
        elif re.match('(.*)nase', word):
            first_match = 'nase'
            if re.match('(.*)proteinase', word):
                matchword = 'proteinase'
            elif re.match('(.*)oxygenase', word):
                matchword = 'oxygenase'
            elif re.match('(.*)ogenase', word):
                matchword = 'ogenase'
            elif re.match('(.*)kinase', word):
                matchword = 'kinase'
            else:
                matchword = 'other'
        else:
            first_match = 'other'
            flag = 0
        if flag == 0:
            if first_match == 'other':
                flag_other = False
                for item in enzymes_dict['ase'][first_match]:
                    for part in re.split('[ ,/()]', item):
                        if part.lower() == word:  # .strip(',').strip('/').strip('(').strip(')'):
                            enzymes_list = enzymes_dict['ase'][first_match]
                            flag_other = True
                            break
                    if flag_other == True:
                        break
            else:
                enzymes_list = enzymes_dict['ase'][first_match]

        else:
            if matchword == 'other':
                flag_other = False
                for item in enzymes_dict['ase'][first_match][matchword]:
                    for part in re.split('[ ,/()]', item):
                        if part.lower() == word:  # .strip(',').strip('/').strip('(').strip(')'):
                            enzymes_list = enzymes_dict['ase'][first_match][matchword]
                            flag_other = True
                            break
                    if flag_other == True:
                        break
            else:
                enzymes_list = enzymes_dict['ase'][first_match][matchword]
        return enzymes_list


    def part_match(text, keyword, search_list, within_list_num, outside_list_num):  # search using "re"--before and after
        entity = None
        words = text.strip().split()  # re.split(' ', text.strip())
        index = 0
        text_after = ''
        #text_before = ''
        for word in words:
            if word.find(keyword) >= 0:
                # Search the words after keyword
                if word[-1] in end_word:
                    entity = word[:-
                                  1].strip('{').strip('[').strip('(').strip('(').strip('"')
                    '''
                    if entity[-1] in end_word:
                        entity = entity[:-1]
                    '''
                    text_after = ' '.join(words[index+1:]).strip()
                elif word[-4:] == 'ases':
                    entity = word.strip('{').strip('[').strip('(').strip('"')
                else:
                    entity = word.strip('{').strip('[').strip('(').strip('"')
                    text_after = ' '.join(words[index+1:]).strip()
                    pattern = re.compile(r'[(](.*?)[)]', re.I)
                    after_bracket = pattern.match(text_after)
                    if after_bracket != None and after_bracket.group().strip('(').strip(')') in list_bracket:
                        entity = entity + ' ' + after_bracket.group()
                        text_after = text_after[after_bracket.end():].strip()
                #entity = word.strip(':').strip(',').strip('!').strip('?').strip('{').strip('[').strip('(').strip('"').strip('}').strip(']').strip(')').strip('"')

                # Search the word before keyword
                index_tmp = index
                for i in range(1, 5):
                    flag = False
                    if word[0] not in end_word and index - i >= 0 and words[index-i].strip('(').strip('[').strip('"') not in nonsense_list:
                        word_before = words[index -
                                            i].strip('(').strip('[').strip('"')
                        for item in search_list:
                            parts = item.split()
                            for part in parts:
                                if part == word_before and not re.match('\d+', word_before):
                                    entity = word_before + ' ' + entity
                                    if entity[0] in end_word:
                                        entity = entity[1:]
                                    del words[index-i]
                                    index_tmp -= 1
                                    flag = True
                                    break
                            if flag == True:
                                break
                    if flag == False:
                        break
                #text_before = ' '.join(words[: index_tmp]).strip()

                break
            index += 1
        text = text_after  # text_before + ' ' + text_after

        outside_list_num += 1
        return entity, text, keyword, within_list_num, outside_list_num


    def search_ase(text, word, within_list_num, outside_list_num):
        search_list = enzyme_ase_list(word)
        flag = False  # To mark if need to do part_match.
        entity = None
        if search_list:
            maxl = 0
            phrase = ''
            for item in search_list:
                pstart = text.lower().find(item.lower())
                #words = [i.strip('{').strip('[').strip('(').strip('(').strip('"') for i in text.split()]
                # greedy
                if pstart >= 0 and item.split()[0].lower() in text.lower().split():
                    if len(item) > maxl:
                        maxl = len(item)
                        entity = text[pstart:pstart+maxl]
                        phrase = text[pstart: len(text)]
            if entity != None:
                words = phrase.split()
                parts = entity.split()
                for i in range(len(parts)):
                    if words[i] != parts[i]:
                        entity = None
                        return entity, text, 'EC numbers', within_list_num, outside_list_num
                        break
            if entity != None:
                start = text.lower().find(entity.lower())
                #entity = text[start:start + len(entity)]
                # text[0 : start].strip() + ' ' + text[(start + len(entity) + 1) : len(text)].strip() # There is least one space between two words.
                text = text[(start + len(entity) + 1):].strip()
                flag = True
                within_list_num += 1
        # we assume that enzymes are all the types (ending with existed 'ase') which can be find inside the kegg, if it not existed in the kegg, we do not use RE to check the text.
        else:
            entity = None
            flag = True
        if flag == False:
            return part_match(text, word, search_list, within_list_num, outside_list_num)
        return entity, text, 'EC numbers', within_list_num, outside_list_num


    def search_pattern(text, word, matchword, within_list_num, outside_list_num):
        if matchword == 'other':
            entity = None
            if word.lower() in enzymes_dict[matchword]:
                entity = word
                start = text.lower().find(word.lower())
                # text[0:start].strip() + ' ' + text[start+len(entity)+1:len(sentence)].strip()
                text = text[start+len(entity)+1:].strip()
            return entity, text, 'EC numbers', within_list_num, outside_list_num
        if matchword != 'ase' and matchword != 'other':
            search_list = enzymes_dict[matchword]
            entity = None
            maxl = 0
            phrase = ''
            for item in search_list:
                pstart = text.lower().find(item.lower())
                # greedy
                if pstart >= 0 and item.split()[0].lower() in text.lower().split():
                    if len(item) > maxl:
                        maxl = len(item)
                        entity = text[pstart:pstart+maxl]
                        phrase = text[pstart: len(text)]
            if entity != None:
                words = phrase.split()
                parts = entity.split()
                for i in range(len(parts)):
                    if words[i] != parts[i]:
                        entity = None
                        break
            if entity != None:
                within_list_num += 1
                start = text.lower().find(entity.lower())
                #entity = text[start:start + len(entity)]
                # text[0 : start].strip()+ ' ' + text[(start + len(entity) + 1) : len(text)].strip()
                text = text[(start + len(entity) + 1): len(text)].strip()
            return entity, text, 'EC numbers', within_list_num, outside_list_num
        else:
            return search_ase(text, word.rstrip('s'), within_list_num, outside_list_num)


    def search_enzyme(word):
        matchword = ''
        if pattern1.search(word):
            matchword = 'complex'
        elif pattern2.search(word):
            matchword = 'enzyme'
        elif pattern3.search(word):
            matchword = 'protein'
        elif pattern4.search(word):
            matchword = 'transporter'
        elif pattern5.search(word):
            matchword = 'Transferred'
        elif pattern6.search(word):
            matchword = 'doxin'
        elif pattern7.search(word):
            matchword = 'system'
        elif pattern8.search(word):
            matchword = 'cytochrome'
        elif pattern9.search(word) and pattern9.search(word).group().rstrip('s').lower() not in notase_list:
            matchword = 'ase'
        else:
            matchword = 'other'
        return matchword


    def abbre_search_enzyme(long, matchword):
        Flag = False
        if matchword != 'ase':
            for item in enzymes_dict[matchword]:
                if item.find(long) >= 0:
                    Flag = True
        else:
            word = long.split()[-1]
            if re.match('(.*)ase$', word) and enzyme_ase_list(word):
                Flag = True
        return Flag


    def abbre_enzyme_list(filename, inputDir):
        abbre_path = os.path.join(inputDir, filename.replace('bioc', 'abbreviations'))
        with open(abbre_path, 'r', encoding='utf-8') as abbre:
            abbreviation = json.load(abbre)
        abbre.close()
        enzyme_short = []
        for j in range(len(abbreviation['documents'][0]['passages'])):
            item = abbreviation['documents'][0]['passages'][j]
            matchword = search_enzyme(item['text_long_1'])
            if matchword != '' and abbre_search_enzyme(item['text_long_1'], matchword):
                enzyme_short.append(item['text_short'])
        return enzyme_short


    def annotation_dictionary():
        dict = {'text': '',
                'infons': {'identifier': '',
                           'type': 'enzyme',
                           'annotator': 'm.wang21@imperial.ac.uk',
                           'updated_at': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.localtime())
                           },
                'id': '',
                'locations': [{'length': '',
                               'offset': ''
                               }]

                }
        return dict


    def annotate_corpus(ider, entity, offset, text, section, ec_num, kw_num, id_num):
        id_num += 1
        if entity not in dict_entities:
            dict_entities[entity] = 0
        else:
            dict_entities[entity] += 1
        tmp = entity.replace('\\', '\\\\\\').replace('(', '\(').replace(')', '\)').replace(
            '[', '\[').replace('{', '\{').replace('+', '\+').replace('*', '\*')
        #print (entity)
        #print (tmp)
        #print()
        positions = [item.start()
                     for item in re.finditer(tmp, text.replace('\n', ' '))]
        try:
            try:
                offset = offset + positions[dict_entities[entity]]
            except:
                positions = [item.start()
                         for item in re.finditer(tmp, re.sub(r'[\(\)]', '', re.sub(r' +', ' ', text.replace('\n', ' '))))]
                offset = offset + positions[dict_entities[entity]]
            annotation_dict = annotation_dictionary()
            annotation_dict['text'] = entity
            annotation_dict['id'] = str(id_num)
            if ider == 'EC numbers':
                annotation_dict['infons']['identifier'] = ec_number_list[entity.lower()]
                ec_num += 1
            else:
                annotation_dict['infons']['identifier'] = ider
                kw_num += 1
            annotation_dict['locations'][0]['length'] = len(entity)
            annotation_dict['locations'][0]['offset'] = offset
            return annotation_dict, ec_num, kw_num, id_num
        except:
            print(filename)
            print(positions)
            print(dict_entities)
            print(entity)


    def annotate_abbre(abbre, text, offset, id_num):
        id_num += 1

        # Compute the position of current abbre
        if abbre not in dict_entities_abbre:
            dict_entities_abbre[abbre] = 0
        else:
            dict_entities_abbre[abbre] += 1
        position = [item.start()
                    for item in re.finditer(abbre, text.replace('\n', ' '))]
        print(abbre+' '+text[position[dict_entities_abbre[abbre]]:position[dict_entities_abbre[abbre]]+len(abbre)])
        offset = offset + position[dict_entities_abbre[abbre]]

        annotation_dict = annotation_dictionary()
        annotation_dict['text'] = abbre
        annotation_dict['id'] = str(id_num)
        annotation_dict['infons']['identifier'] = 'abbreviation_enzyme'
        annotation_dict['locations'][0]['length'] = len(abbre)
        annotation_dict['locations'][0]['offset'] = offset
        return annotation_dict, id_num

    # main code
    start_time = time.time()

    dict_ec_number = {}
    ec_number_path = ('./EnzymeLists/KEGG_EC_Enzymes.json')
    with open(ec_number_path, 'r', encoding='utf-8') as ec_number:
        ec_number_list = json.load(ec_number)
    ec_number.close()

    enzymes_path = ("./EnzymeLists/Classified_Enzyme_List.json")
    with open(enzymes_path, 'r', encoding='utf-8') as enzymes:
        enzymes_dict = json.load(enzymes)
    enzymes.close()

    print_path = (output_folder + "printnewannot-eNzymER.txt")
    w = open(print_path, 'a+', encoding='utf-8')

    bracket_path = ("./EnzymeLists/After_word.txt")
    with open(bracket_path, 'r') as bracket:
        list_bracket = bracket.readlines()
    bracket.close()
        
    # if there is a request to give the past time of a verb?
    notase_list = ['release', 'increase', 'database',
                    'base', 'disease', 'decrease', 'case']
    nonsense_list = ['or', 'to', 'in', 'the', 'a', 'on', 'of', 'for',
                        'at', 'with', 'and', 'this', 'that', 'these', 'those', 'is', 'are']
    end_word = [')', '.', ';', '?', '!', '"', ':', ']',
                '}', '(', '[', '{', ',', '/']
    # Patterns used to rematch.
    pattern1 = re.compile(r'complex', re.I)
    pattern2 = re.compile(r'enzyme', re.I)
    pattern3 = re.compile(r'protein', re.I)
    pattern4 = re.compile(r'transporter', re.I)
    pattern5 = re.compile(r'Transferred')
    pattern6 = re.compile(r'doxin', re.I)
    pattern7 = re.compile(r'system', re.I)
    pattern8 = re.compile(r'cytochrome', re.I)
    pattern9 = re.compile(r'(.*)ase$|(.*)ases$')

    file_num = 0
    enzyme_num = 0
    ec_num = 0
    kw_num = 0
    abbre_file = 0
    count_proccessed = 0
    for input_i in input_list:
        count_proccessed += 1
        filename = input_i.split('/')[-1]
        text_folder_path = '/'.join(input_i.split('/')[:-1]) + '/'
        file_path = os.path.join(text_folder_path, filename)
        # windows 10 has the 'gbk' codec problem without encoding = 'utf-8'
        with open(file_path, 'r', encoding='utf-8') as file:
            fulltext = json.load(file)
        file.close()
        file_num += 1

        # Annotate the abbreviations of enzyme
        #abbre_list = abbre_enzyme_list(filename,text_folder_path)
        #if abbre_list:
            #abbre_file += 1
        #now = datetime.now()
        #current_time = now.strftime("%d/%m/%Y, %H:%M:%S")
        #print(str(current_time) + str(' We are at row ') + str(count_proccessed) + str(' out of ') + str(len(input_list)) + str(' from proccess ') + bold.BEGIN + str(process_number) + bold.END)
        #print(str('Proccess ') + bold.BEGIN + str(process_number) + bold.END + str(' has completed ') + bold.BEGIN + str(round((float(count_proccessed)/float(len(input_list)))*100, 2)) + str('%') + bold.END)
        #print(str(current_time) + str(' Processing ') + str(filename))
        within_list_num = 0
        outside_list_num = 0
        id_num = 0
        cont = 0

        for text in fulltext['documents'][0]['passages']:
            paragraph = text['text'].split('.')
            annotation = text['annotations']
            offset = int(fulltext['documents'][0]['passages'][cont]['offset'])
            if fulltext['documents'][0]['passages'][cont]['infons'].get('iao_name_0') != None:
                section = fulltext['documents'][0]['passages'][cont]['infons']['iao_name_0']
            else:
                section = 'unknown'
            dict_entities = {}
            dict_entities_abbre = {}
            for sentence in paragraph:
                sentence = sentence.strip()
                words = re.split('[ ]', sentence)
                for word in words:
                    matchword = search_enzyme(word)
                    if matchword != '':
                        entity, content, ider, within_list_num, outside_list_num = search_pattern(sentence, word, matchword, within_list_num, outside_list_num)
                        if entity != None:
                            w.write(filename + ' ' + section +
                                    ':' + entity + ' ' + ider + '\n')
                            #id_num += 1
                            current_annotation_dict, ec_num, kw_num, id_num = annotate_corpus(ider, entity, offset, text['text'], section, ec_num, kw_num, id_num)
                            annotation.append(current_annotation_dict)
                            sentence = content
            #if abbre_list:
                #end_letter = ['.', ';', '?', '!', '"', ':', ',']
                #for word in text['text'].split():
                    #if word[-1] in end_letter:
                        #word = word[:-1]
                    #if word in abbre_list:
                        #annotation_dict, id_num = annotate_abbre(word, text['text'], offset, id_num)
                        #annotation.append(annotate_abbre(annotation_dict)

            fulltext['documents'][0]['passages'][cont]['annotations'] = annotation
            cont += 1

        enzyme_num += id_num
        writein_path = os.path.join(output_folder, (filename.rstrip('.json') + '_' + 'annotated.json'))
        writein = open(writein_path, 'w')
        json.dump(fulltext, writein, indent=4)
        writein.close()
    w.close()

    print(f'Summary of process number: {process_number}')
    print('{} files were annotated in '.format(file_num) + str(time.time() - start_time) + ' seconds.')
    print('  Of these, {} files contained abbreviations of enzymes.'.format(abbre_file))
    print('A total of {} enzymes outside_list_numhave been found, of these:'.format(enzyme_num))
    print('  {} enzymes were found via direct matching to the KEGG list.'.format(ec_num))
    print('  {} enyzmes were found using the keyword search.'.format(kw_num))
    print('  {} abbreviations were found.'.format(enzyme_num-ec_num-kw_num))

if __name__ == "__main__":
    try:
        os.mkdir('./output/enzyme_annotated')
    except:
        pass
    numbers_of_cores = 1

    if numbers_of_cores >= mp.cpu_count():
        print('The number of cores you want to use is equal or greater than the numbers of cores in your machine. We stop the script now')
        exit()
    else:
        par_core = numbers_of_cores
        
    input_bioc = glob.glob('./CoDiet-Gold-private/*.json')
    for i in range(len(input_bioc)):
        if '_bioc.json' not in input_bioc[i]:
            os.rename(input_bioc[i], input_bioc[i].replace('.json', '_bioc.json'))
    input_bioc = glob.glob('./CoDiet-Gold-private/*.json')

    if len(input_bioc) < par_core:
            par_core = len(input_bioc)

    if par_core > 1:
        data = []
        for i in range(par_core):
            if i == 0:
                current_data = (input_bioc[:round(len(input_bioc)/par_core)], './output/enzyme_annotated/', i+1)
                data.append(current_data)
            elif i > 0 and i+1 != par_core:
                current_data = (input_bioc[(round(len(input_bioc)/par_core))*i:(round(len(input_bioc)/par_core))*(i+1)], './output/enzyme_annotated/', i+1)
                data.append(current_data)
            else:
                current_data = (input_bioc[round(len(input_bioc)/par_core)*i:], './output/enzyme_annotated/', i+1)
                data.append(current_data)
    else:
        data = [(input_bioc, './output/enzyme_annotated/', 1)]


    with mp.Pool(numbers_of_cores) as pool:
        pool.starmap(para_enzyme, data)

    now = datetime.now()
    current_time = now.strftime("%d/%m/%Y, %H:%M:%S")
    print(str(current_time) + str(' Process complete'))
