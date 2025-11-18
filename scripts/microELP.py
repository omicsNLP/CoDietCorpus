import os
import glob

input_list = glob.glob('./CoDiet-Gold-private/*.json')
for i in range(len(input_list)):
	if '_bioc.json' not in input_list[i]:
		os.rename(input_list[i], input_list[i].replace('.json', '_bioc.json'))

from microbELP import microbELP

microbELP('./CoDiet-Gold-private', output_directory='./output') #type str
