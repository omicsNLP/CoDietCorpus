from ParallelPyMetaMap import ppmm
import shutil

if __name__ == "__main__":
    ppmm(6, 
        '/software/public_mm/bin/metamap20', 
        path_to_directory = './output/passages_input',
        machine_output = True,
        mm_data_version = 'NLM',
        mm_data_year = '2022AB',
        ignore_stop_phrases = True,
        word_sense_disambiguation=True,
        no_derivational_variants=True,
        restrict_to_sts = ['food', 'bdsu', 'lbpr', 'inpr', 'resa']
        )

    shutil.move('./output_ParallelPyMetaMap_text_mo', './output/output_ParallelPyMetaMap_text_mo')