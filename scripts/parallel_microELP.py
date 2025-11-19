import os
import glob
from microbELP import parallel_microbELP

if __name__ == "__main__":
	
	input_list = glob.glob('./CoDiet-Gold-private/*.json')

	for i in range(len(input_list)):
		if '_bioc.json' not in input_list[i]:
			os.rename(input_list[i], input_list[i].replace('.json', '_bioc.json'))

	parallel_microbELP(
		'./CoDiet-Gold-private', #type str
		3, #type int
		output_directory='./output'
	)
