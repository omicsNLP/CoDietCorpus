[![DOI:10.1101/2021.01.08.425887](http://img.shields.io/badge/preprint_DOI-10.1101/2025.09.04.673740-BE2536.svg)](https://doi.org/10.1101/2025.09.04.673740)
[![DOI:10.5281/zenodo.17305411](http://img.shields.io/badge/data_DOI-10.5281/zenodo.17610205-3382C4.svg)](https://zenodo.org/records/17610205)
[![Codabench](http://img.shields.io/badge/Codabench-CoDiet_Gold_benchmark-2C3F4C.svg)](https://www.codabench.org/competitions/11676/)
[![CoDiet](https://img.shields.io/badge/%F0%9F%8D%8E_a_CoDiet_study-5AA764)](https://www.codiet.eu)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17305411.svg)](https://doi.org/10.5281/zenodo.17305411)  
[//]: # [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17288827.svg)](https://doi.org/10.5281/zenodo.17288827)  
[//]: # [![Codabench](http://img.shields.io/badge/Codabench-microbELP_benchmark-2C3F4C.svg)](https://www.codabench.org/competitions/10913/)  
-->

---

# CoDietCorpus

Code repository for the annotation of silver and bronze corpora related to the CoDiet project.

This repository provides the scripts required to generate Bronze and Silver annotated test sets for the CoDiet dataset. The annotation process integrates multiple pipelines, including dictionary-based matching, MetaMap, enzyme annotation, PhenoBERT, MicrobELP, and BERN2.

Please note that the Codabench link will be made public once the manuscript is accepted. If you would like to contribute your model prior to publication, feel free to contact us to obtain access to a private URL.

---

## Environment Setup

Create and activate the main Conda environment:

```bash
conda create -n CoDiet_machine
conda activate CoDiet_machine
conda install pip
pip install pandas numpy openpyxl
```

---

## Collect the codebase

```bash
git clone https://github.com/omicsNLP/CoDietCorpus.git
cd CoDietCorpus
```

---

## Download the Data

```bash
wget https://zenodo.org/records/17610205/files/CoDiet-Gold-private.zip
unzip ./CoDiet-Gold-private.zip
```

---

## Run the Annotation Scripts

### 1️⃣ Input Text Processing

```bash
python ./scripts/input_text.py
```

### 2️⃣ Dictionary Matching

```bash
python ./scripts/dictionary_matching.py
```

### 3️⃣ Priority Dictionary Matching

```bash
python ./scripts/priority_dictionary_matching.py
```

### 4️⃣ Enzyme Annotation

```bash
python ./scripts/AnnotationEnzymes.py
```

⚠️ Note: This script is an adaptation of another library [eNzymER](https://github.com/omicsNLP/enzymeNER).

### 5️⃣ MetaMap-based Annotation

MetaMap must be installed and configured properly.
If the Metamap instance is not running, start the MetaMap instance from the correct folder:

```bash
./bin/skrmedpostctl start
./bin/wsdserverctl start
```

Then run:

```bash
git clone https://github.com/biomedicalinformaticsgroup/ParallelPyMetaMap.git
pip install ./ParallelPyMetaMap
python ./scripts/ppmm.py
```

⚠️ Warning: Ensure MetaMap config matches the script, or update accordingly.

### 6️⃣ MicrobELP Annotation

```bash
git clone https://github.com/omicsNLP/microbELP.git
pip install ./microbELP
```

Using the single-core CPU:

```bash
python ./scripts/microELP.py
```

or the multiprocessing implementation:

```bash
python ./scripts/parallel_microELP.py
```

### 7️⃣ PhenoBERT Annotation

Create a separate environment for PhenoBERT:

```bash
conda deactivate
conda create -n CoDiet_phenobert python=3.10
conda activate CoDiet_phenobert
conda install pip
pip install gdown
```

Set up PhenoBERT:

```bash
git clone https://github.com/EclipseCN/PhenoBERT.git
gdown --folder "https://drive.google.com/drive/folders/1jIqW19JJPzYuyUadxB5Mmfh-pWRiEopH"

mv ./PhenoBERT_data/models/* ./PhenoBERT/phenobert/models/
mv ./PhenoBERT_data/embeddings/* ./PhenoBERT/phenobert/embeddings/
rm -rf ./PhenoBERT_data/
mkdir ./output/phenobert_output

cd PhenoBERT
pip install -r requirements.txt
python setup.py
pip install torch==2.0.1+cu117 torchvision==0.15.2+cu117 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117
pip install stanza==1.6.1 numpy==1.24.3
python -c "import nltk; nltk.download('averaged_perceptron_tagger_eng')"

cd phenobert/utils
python ./annotate.py -i ../../../output/passages_input/ -o ../../../output/phenobert_output/
cd ../../..
conda deactivate
```

### 8️⃣ BERN2 Annotation

If not already done, exit the PhenoBERT directory:

```bash
cd ../../..
```

⚠️ Note: This set of instructions is an adaptation of the official README from the original library [BERN2 README](https://github.com/dmis-lab/BERN2).

⚠️ **Prerequisites**: This installation requires:
- ~70GB of free disk space
- For GPU: ≥63.5GB RAM and ≥5GB GPU memory
- Linux or WSL (Windows Subsystem for Linux)

1. Create environment and install dependencies
```bash
conda create -n CoDiet_bern2 python=3.7
conda activate CoDiet_bern2
conda install pytorch==1.9.0 cudatoolkit=10.2 -c pytorch
conda install faiss-gpu libfaiss-avx2 -c conda-forge
pip install gdown
```

2. Download BERN2
```bash
git clone https://github.com/dmis-lab/BERN2.git
cd BERN2
pip install -r requirements.txt

gdown --folder "https://drive.google.com/file/d/147b3OhU4IdQi121ZBUSqO1XKdKoXE5DK"
tar -zxvf resources_v1.1.b.tar.gz
md5sum resources_v1.1.b.tar.gz
# make sure the md5sum is 'c0db4e303d1ccf6bf56b42eda2fe05d0'
rm resources_v1.1.b.tar.gz
```

3. Install CRF (required for GNormPlus)
```bash
cd resources/GNormPlusJava
tar -zxvf CRF++-0.58.tar.gz
mv CRF++-0.58 CRF
cd CRF
./configure --prefix="$HOME"
make
make install
cd ../../..
```

4. Start the BERN2 server
   
**GPU (Linux/WSL)**
```bash
export CUDA_VISIBLE_DEVICES=0
cd scripts
nohup bash run_bern2.sh &
cd ../..
```

**CPU**
```bash
cd scripts
nohup bash run_bern2_cpu.sh &
cd ../..
```

5. Run inference
```bash
python ./scripts/bern2.py
bash ./BERN2/scripts/stop_bern2.sh 
conda deactivate
```

### 9️⃣ Combine Predictions & Infer Metabolites to generate the Bronze dataset

```bash
conda activate CoDiet_machine
python ./scripts/bronze.py
```

### 🔟 Bronze to Silver Conversion

```bash
python ./scripts/silver.py
```

---

## ⚠️ Important - Please Read!

Published literature can be subject to copyright with restrictions on redistribution. Users need to be mindful of the data storage requirements and how the derived products are presented and shared. Many publishers provide guidance on the use of content for redistribution and use in research.

---

## Used the following repositories

<div align="center">

<div align="center">

| GitHub repository | Paper | 
|:-----------------:|:-----:|
| [cadmus](https://github.com/biomedicalinformaticsgroup/cadmus) <a href="https://github.com/biomedicalinformaticsgroup/cadmus"><img src="https://img.shields.io/github/stars/biomedicalinformaticsgroup/cadmus.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | n/a |
| [Auto-CORPus](https://github.com/omicsNLP/Auto-CORPus) <a href="https://github.com/omicsNLP/Auto-CORPus"><img src="https://img.shields.io/github/stars/omicsNLP/Auto-CORPus.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | [Paper](https://www.frontiersin.org/journals/digital-health/articles/10.3389/fdgth.2022.788124/full) |
| [BERN2](https://github.com/dmis-lab/BERN2) <a href="https://github.com/dmis-lab/BERN2"><img src="https://img.shields.io/github/stars/dmis-lab/BERN2.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | [Paper](https://arxiv.org/abs/2201.02080) |
| [PhenoBERT](https://github.com/EclipseCN/PhenoBERT) <a href="https://github.com/EclipseCN/PhenoBERT"><img src="https://img.shields.io/github/stars/EclipseCN/PhenoBERT.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | [Paper](https://ieeexplore.ieee.org/document/9763337) |
| [TABoLiSTM](https://github.com/omicsNLP/MetaboliteNER) <a href="https://github.com/omicsNLP/MetaboliteNER"><img src="https://img.shields.io/github/stars/omicsNLP/MetaboliteNER.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | [Paper](https://www.mdpi.com/2218-1989/12/4/276) |
| [eNzymER](https://github.com/omicsNLP/enzymeNER) <a href="https://github.com/omicsNLP/enzymeNER"><img src="https://img.shields.io/github/stars/omicsNLP/enzymeNER.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | [Paper](https://pubs.acs.org/doi/10.1021/acs.jproteome.3c00367) |
| [microbELP](https://github.com/omicsNLP/microbELP) <a href="https://github.com/omicsNLP/microbELP"><img src="https://img.shields.io/github/stars/omicsNLP/microbELP.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a> | [Paper](https://www.biorxiv.org/content/10.1101/2025.08.29.671515v1.full) |

</div>


</div>

---

## 👥 Code Contributors

<p align="center">
  <kbd>
    <a href="https://github.com/Antoinelfr">
      <img src="https://drive.google.com/uc?id=1FH6XRJuam6eMuCzwWXBAIdDacIw8PFiu" width="90" height="90" style="border-radius:50%;">
    </a><br>
    👉 <strong><a href="https://github.com/Antoinelfr" style="text-decoration:none; color:inherit;">Antoine</a></strong>
  </kbd>
  &nbsp;&nbsp;
  <kbd>
    <a href="https://github.com/jmp111">
      <img src="https://drive.google.com/uc?id=1kgEK2yqJG-eQnHGYDUH7mL2QeLtar2ZC" width="90" height="90" style="border-radius:50%;">
    </a><br>
    👉 <strong><a href="https://github.com/jmp111" style="text-decoration:none; color:inherit;">Joram</a></strong>
  </kbd>
</p>

---
