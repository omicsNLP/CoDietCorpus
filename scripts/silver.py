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

def is_space(char):
    return char.isspace()

def adjust_spaces_on_right(text, start_offset):
    while start_offset < len(text) and is_space(text[start_offset]):
        start_offset += 1
    
    return start_offset

def adjust_spaces_on_left(text, end_offset):
    while end_offset > 0 and is_space(text[end_offset - 1]):
        end_offset -= 1
    
    return end_offset

def adjust_offsets(text, start_offset, end_offset):
    if start_offset < 0 or end_offset >= len(text) or start_offset > end_offset:
        return start_offset, end_offset
    
    original_start = start_offset
    original_end = end_offset
    
    while start_offset > 0 and text[start_offset - 1].isalpha():
        start_offset -= 1
    
    while end_offset < len(text) and text[end_offset].isalpha():
        end_offset += 1
    
    return start_offset, end_offset

def keep_only_p_dictionary_annotations(passages):
    for passage in passages:
        annotations = passage['annotations']
        filtered_annotations = []

        for annotation in annotations:
            include_annotation = True

            for filtered_annotation in filtered_annotations:
                # Check if there's an equal or overlapping span
                prev_location = filtered_annotation['locations'][0]
                curr_location = annotation['locations'][0]

                if (
                    prev_location['offset'] <= curr_location['offset'] <= prev_location['offset'] + prev_location['length']
                    or curr_location['offset'] <= prev_location['offset'] <= curr_location['offset'] + curr_location['length']
                ):
                    # Equal or overlapping span
                    if 'p_dictionary' in filtered_annotation['infons']['annotator']:
                        # The previous annotation has 'p_dictionary', keep it and exclude the current annotation
                        include_annotation = False
                        break

            if include_annotation:
                filtered_annotations.append(annotation)
        passage['annotations'] = filtered_annotations

def combine_annotations(passages):
    for passage in passages:
        annotations = passage['annotations']

        combined_annotations = {}
        annotations_to_kepp = []

        for annotation in annotations:
            annotation_type = annotation['infons']['type']
            offset = annotation['locations'][0]['offset']
            length = annotation['locations'][0]['length']

            if (annotation_type, offset, length) not in combined_annotations:
                combined_annotations[(annotation_type, offset, length)] = {'text': annotation['text'], 'annotators': []}
                annotations_to_kepp.append(annotation)
            else:
                for i in range(len(annotations_to_kepp)):
                    if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length and annotations_to_kepp[i]['infons']['type'] == annotation_type:
                        annotations_to_kepp[i]['infons']['identifier'] = str(annotations_to_kepp[i]['infons']['identifier']) + str(',') + str(annotation['infons']['identifier'])
                        annotations_to_kepp[i]['infons']['annotator'] = str(annotations_to_kepp[i]['infons']['annotator']) + str(',') + str(annotation['infons']['annotator'])
            combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotation['infons']['annotator'])

        passage['annotations'] = annotations_to_kepp

def combine_annotations_priority(passages):
    for passage in passages:
        annotations = passage['annotations']

        combined_annotations = {}
        annotations_to_kepp = []

        for annotation in annotations:
            annotation_type = annotation['infons']['type']
            offset = annotation['locations'][0]['offset']
            length = annotation['locations'][0]['length']
            annotator = annotation['infons']['annotator']

            if (annotation_type, offset, length) not in combined_annotations:
                combined_annotations[(annotation_type, offset, length)] = {'text': annotation['text'], 'annotators': []}
                annotations_to_kepp.append(annotation)
            else:
                if 'p_dictionary' in annotator:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['annotator'] = 'p_dictionary@codiet.eu'
                elif 'phenobert' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] != 'p_dictionary':
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['annotator'] = 'phenobert@codiet.eu'
                elif 'microbeRT' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] not in ['phenobert', 'p_dictionary']:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['annotator'] = 'microbeRT@codiet.eu'
                elif 'MetaboLipidBERT' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] not in ['phenobert', 'microbeRT', 'p_dictionary']:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['annotator'] = 'MetaboLipidBERT@codiet.eu'
                elif 'enzyner' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] not in ['phenobert', 'microbeRT', 'MetaboLipidBERT', 'p_dictionary']:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['annotator'] = 'enzyner@codiet.eu'
                elif 'bern2' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] not in ['phenobert', 'microbeRT', 'MetaboLipidBERT', 'enzyner', 'p_dictionary']:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['annotator'] = 'bern2@codiet.eu'
                elif 'dictionary' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] not in ['phenobert', 'microbeRT', 'MetaboLipidBERT', 'enzyner', 'bern2', 'p_dictionary']:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['dictionary'] = 'bern2@codiet.eu'
                elif 'metamap' in annotator and combined_annotations[(annotation_type, offset, length)]['type'] not in ['phenobert', 'microbeRT', 'MetaboLipidBERT', 'enzyner', 'bern2', 'dict', 'p_dictionary']:
                    combined_annotations[(annotation_type, offset, length)]['type'] = annotation_type
                    combined_annotations[(annotation_type, offset, length)]['annotators'].append(annotator)
                    for i in range(len(annotations_to_kepp)):
                        if annotations_to_kepp[i]['locations'][0]['offset'] == offset and annotations_to_kepp[i]['locations'][0]['length'] == length:
                            annotations_to_kepp[i]['infons']['dictionary'] = 'metamap@codiet.eu'
        passage['annotations'] = annotations_to_kepp

def merge_overlapping_annotations(passages):
    for passage in passages:
        annotations = passage['annotations']
        merged_annotations = []

        for annotation in annotations:
            if not merged_annotations:
                merged_annotations.append(annotation)
            else:
                # Check if the 'type' is the same
                if annotation['infons']['type'] == merged_annotations[-1]['infons']['type']:
                    # Check if there's an overlap in locations
                    prev_location = merged_annotations[-1]['locations'][0]
                    curr_location = annotation['locations'][0]

                    if (prev_location['offset'] <= curr_location['offset'] <= prev_location['offset'] + prev_location['length']):
                        # There is an overlap, merge the annotations
                        merged_annotations[-1]['locations'][0]['length'] = max(
                            prev_location['offset'] + prev_location['length'],
                            curr_location['offset'] + curr_location['length']
                        ) - prev_location['offset']

                        # Update annotators and identifier
                        merged_annotations[-1]['infons']['annotator'] += ',' + annotation['infons']['annotator']
                        merged_annotations[-1]['infons']['identifier'] += ',' + annotation['infons']['identifier']
                    else:
                        merged_annotations.append(annotation)
                else:
                    merged_annotations.append(annotation)

            # Set the 'text' field to an empty string
            #merged_annotations[-1]['text'] = ''

        passage['annotations'] = merged_annotations

def merge_overlapping_annotations_final(passages):
    for passage in passages:
        annotations = passage['annotations']
        merged_annotations = []

        for annotation in annotations:
            merged = False

            for merged_annotation in merged_annotations:
                # Check if the 'type' is the same
                if annotation['infons']['type'] == merged_annotation['infons']['type']:
                    # Check if there's an overlap in locations
                    prev_location = merged_annotation['locations'][0]
                    curr_location = annotation['locations'][0]

                    if (
                        prev_location['offset'] <= curr_location['offset']
                        and prev_location['offset'] + prev_location['length'] >= curr_location['offset'] + curr_location['length']
                    ):
                        # The current annotation is completely within the previous one
                        merged_annotation['locations'].append(curr_location)
                        merged_annotation['infons']['annotator'] += ',' + annotation['infons']['annotator']
                        merged_annotation['infons']['identifier'] += ',' + annotation['infons']['identifier']
                        merged = True
                        break
                    elif (
                        curr_location['offset'] <= prev_location['offset']
                        and curr_location['offset'] + curr_location['length'] >= prev_location['offset'] + prev_location['length']
                    ):
                        # The previous annotation is completely within the current one
                        merged_annotation['text'] = annotation['text']
                        merged_annotation['locations'] = annotation['locations']
                        merged_annotation['infons']['annotator'] = annotation['infons']['annotator']
                        merged_annotation['infons']['identifier'] = annotation['infons']['identifier']
                        merged = True
                        break
                    elif (
                        prev_location['offset'] <= curr_location['offset'] <= prev_location['offset'] + prev_location['length']
                        or curr_location['offset'] <= prev_location['offset'] <= curr_location['offset'] + curr_location['length']
                    ):
                        # There is an overlap, merge the annotations
                        merged_annotation['locations'][0]['offset'] = min(prev_location['offset'], curr_location['offset'])
                        merged_annotation['locations'][0]['length'] = max(
                            prev_location['offset'] + prev_location['length'],
                            curr_location['offset'] + curr_location['length']
                        ) - merged_annotation['locations'][0]['offset']
                        merged_annotation['infons']['annotator'] += ',' + annotation['infons']['annotator']
                        merged_annotation['infons']['identifier'] += ',' + annotation['infons']['identifier']
                        merged = True
                        break

            if not merged:
                merged_annotations.append(annotation)
        passage['annotations'] = merged_annotations

def merge_select_annotator_priority(passages):
    for passage in passages:
        annotations = passage['annotations']
        annotator_priority_order = [
            'p_dictionary', 'phenobert', 'microbeRT', 'MetaboLipidBERT', 'enzyner', 'bern2', 'dictionary', 'metamap'
        ]

        merged_annotations = []

        for annotation in annotations:
            merged = False

            for merged_annotation in merged_annotations:
                # Check if there's an overlap in locations
                prev_location = merged_annotation['locations'][0]
                curr_location = annotation['locations'][0]

                if (
                    prev_location['offset'] == curr_location['offset']
                    and prev_location['length'] == curr_location['length']
                ):
                    # The annotations have the same offset and length
                    if (
                        annotation['infons']['type'] != merged_annotation['infons']['type']
                        and 'annotator' in annotation['infons']
                        and 'annotator' in merged_annotation['infons']
                    ):
                        # Different types, select based on annotator priority
                        for annotator in annotator_priority_order:
                            if annotator in annotation['infons']['annotator']:
                                merged_annotation['text'] = annotation['text']
                                merged_annotation['locations'] = annotation['locations']
                                merged_annotation['infons']['annotator'] = annotation['infons']['annotator']
                                merged_annotation['infons']['identifier'] = annotation['infons']['identifier']
                                merged_annotation['infons']['type'] = annotation['infons']['type']
                                merged = True
                                break

                        if not merged:
                            # If none of the specified annotators is present, choose the first annotator available
                            merged_annotation['text'] = annotation['text']
                            merged_annotation['locations'] = annotation['locations']
                            merged_annotation['infons']['annotator'] = annotation['infons']['annotator']
                            merged_annotation['infons']['identifier'] = annotation['infons']['identifier']
                            merged_annotation['infons']['type'] = annotation['infons']['type']
                            merged = True

                        break

            if not merged:
                merged_annotations.append(annotation)
        passage['annotations'] = merged_annotations

def keep_longest_overlapping_annotations(passages):
    for passage in passages:
        # Sort annotations by length in descending order
        sorted_annotations = sorted(passage['annotations'], key=lambda x: x['locations'][0]['length'], reverse=True)

        # Filter annotations, keeping only the longest when there is an overlap and annotators are the same
        filtered_annotations = []
        for annotation in sorted_annotations:
            keep_annotation = True
            for filtered_annotation in filtered_annotations:
                if (
                    annotation['locations'][0]['offset'] < filtered_annotation['locations'][0]['offset'] + filtered_annotation['locations'][0]['length']
                    and annotation['locations'][0]['offset'] + annotation['locations'][0]['length'] > filtered_annotation['locations'][0]['offset']
                    and annotation['infons']['annotator'] == filtered_annotation['infons']['annotator']
                ):
                    # There is an overlap and annotators are the same, keep only the longest
                    keep_annotation = False
                    break
            if keep_annotation:
                filtered_annotations.append(annotation)
        passage['annotations'] = filtered_annotations

try:
    os.mkdir('./silver')
except:
    pass

all_input = glob.glob('./bronze/*json')
for i in range(len(all_input)):
    all_input[i] = all_input[i].split('/')[-1].split('.')[0]
    
for uyi in range(len(all_input)):
    if len(all_input) > 100:
        if uyi % (len(all_input) // 10) == 0:
            print(f'Processing index: {uyi} of {len(all_input)}')
    f = open(f'./bronze/{all_input[uyi]}.json')
    data = json.load(f)
    total = 1

    print(all_input[uyi])
    for i in range(len(data['documents'][0]['passages'])):
        for j in range(len(data['documents'][0]['passages'][i]['annotations'])):
            if len(data['documents'][0]['passages'][i]['annotations'][j]['infons']['identifier'].split(',')) > 15:
                data['documents'][0]['passages'][i]['annotations'][j]['infons']['identifier'] = 'TOO_LONG_' + ','.join(data['documents'][0]['passages'][i]['annotations'][j]['infons']['identifier'].split(',')[:10])

    for i in range(len(data['documents'][0]['passages'])):
        text = data['documents'][0]['passages'][i]['text']
        current_offset = data['documents'][0]['passages'][i]['offset']
        for j in range(len(data['documents'][0]['passages'][i]['annotations'])):
            start_index = data['documents'][0]['passages'][i]['annotations'][j]['locations'][0]['offset'] - current_offset
            end_index = data['documents'][0]['passages'][i]['annotations'][j]['locations'][0]['offset'] + data['documents'][0]['passages'][i]['annotations'][j]['locations'][0]['length'] - current_offset
            start_index2 = adjust_spaces_on_right(text, start_index)
            end_index2 = adjust_spaces_on_left(text, end_index)
            adjusted_start, adjusted_end = adjust_offsets(text, start_index2, end_index2)
            if adjusted_start != start_index or end_index != adjusted_end:
                data['documents'][0]['passages'][i]['annotations'][j]['text'] = text[adjusted_start:adjusted_end]
                data['documents'][0]['passages'][i]['annotations'][j]['locations'][0]['offset'] = adjusted_start + current_offset
                data['documents'][0]['passages'][i]['annotations'][j]['locations'][0]['length'] = adjusted_end - adjusted_start

    keep_only_p_dictionary_annotations(data.get('documents')[0].get('passages'))
    combine_annotations(data.get('documents')[0].get('passages'))
    combine_annotations_priority(data.get('documents')[0].get('passages'))
    merge_overlapping_annotations(data.get('documents')[0].get('passages'))
    merge_overlapping_annotations_final(data.get('documents')[0].get('passages'))
    merge_select_annotator_priority(data.get('documents')[0].get('passages'))
    keep_longest_overlapping_annotations(data.get('documents')[0].get('passages'))
    keep_only_p_dictionary_annotations(data.get('documents')[0].get('passages'))
    for i in range(len(data.get('documents')[0].get('passages'))):
        for j in range(len(data.get('documents')[0].get('passages')[i]['annotations'])):
            data['documents'][0]['passages'][i]['annotations'][j]['text'] = data.get('documents')[0].get('passages')[i]['text'][int(data.get('documents')[0].get('passages')[i]['annotations'][j]['locations'][0]['offset']) - int(data.get('documents')[0].get('passages')[i]['offset']):int(data.get('documents')[0].get('passages')[i]['annotations'][j]['locations'][0]['offset']) - int(data.get('documents')[0].get('passages')[i]['offset']) + int(data.get('documents')[0].get('passages')[i]['annotations'][j]['locations'][0]['length'])]
        for j in range(len(data.get('documents')[0].get('passages')[i]['annotations'])):
            data['documents'][0]['passages'][i]['annotations'][j]['locations'] = [data['documents'][0]['passages'][i]['annotations'][j]['locations'][0]]
    filtered_data = []
    for i in range(len(data.get('documents')[0].get('passages'))):
        try:
            if data['documents'][0]['passages'][i]['infons']['iao_id_0'] == 'IAO:0000320':
                pass
            else:
                filtered_data.append(data['documents'][0]['passages'][i])
        except:
            filtered_data.append(data['documents'][0]['passages'][i])
    data['documents'][0]['passages'] = filtered_data
    with open(f'./silver/{all_input[uyi]}.json', 'w', encoding="utf-8") as fp:
        json.dump(data, fp, indent = 2, ensure_ascii=False)

