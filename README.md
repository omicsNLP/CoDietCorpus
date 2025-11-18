[![DOI:10.1101/2021.01.08.425887](http://img.shields.io/badge/preprint_DOI-10.1101/2025.08.29.67155-BE2536.svg)](https://doi.org/10.1101/2025.08.29.671515)
[![DOI:10.5281/zenodo.17305411](http://img.shields.io/badge/data_DOI-10.5281/zenodo.17610205-3382C4.svg)](https://zenodo.org/records/17610205)
[![Codabench](http://img.shields.io/badge/Codabench-CoDiet_Gold_benchmark-2C3F4C.svg)](https://www.codabench.org/competitions/11676/)
[![CoDiet](https://img.shields.io/badge/%F0%9F%8D%8E_a_CoDiet_study-5AA764)](https://www.codiet.eu)
<!-- [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17305411.svg)](https://doi.org/10.5281/zenodo.17305411)  
[//]: # [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17288827.svg)](https://doi.org/10.5281/zenodo.17288827)  
[//]: # [![Codabench](http://img.shields.io/badge/Codabench-microbELP_benchmark-2C3F4C.svg)](https://www.codabench.org/competitions/10913/)  
-->

---

# CoDietCorpus

Code repository for the creation and annotation of corpora in the CoDiet project. 

This project provides scripts to generate **Bronze** and **Silver** annotated test datasets for the **CoDiet** dataset. It leverages multiple pipelines, including dictionary matching, MetaMap, enzyme annotation, PhenoBERT, MicrobELP, and BERN2.

Note that the Codabench link will be made public once the manuscript is accepted. If you wish to contribute your model before this time, please contact us to receive access to a secret URL.

---

## Environment Setup

Create and activate the main Conda environment:

```bash
conda create -n CoDiet_machine
conda activate CoDiet_machine
conda install pip
pip install pandas numpy openpyxl gdown
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
python ./script/input_text.py
```

### 2️⃣ Dictionary Matching

```bash
python ./script/dictionary_matching.py
```

### 3️⃣ Priority Dictionary Matching

```bash
python ./script/priority_dictionary_matching.py
```

### 4️⃣ Enzyme Annotation

```bash
python ./script/AnnotationEnzymes.py
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
python ./script/ppmm.py
```

⚠️ Warning: Ensure MetaMap config matches the script, or update accordingly.

### 6️⃣ MicrobELP Annotation

```bash
git clone https://github.com/omicsNLP/microbELP.git
pip install ./microbELP
python ./script/parallel_microELP.py   # or
python ./script/microELP.py
```

### 7️⃣ PhenoBERT Annotation

Create a separate environment for PhenoBERT:

```bash
conda deactivate
conda create -n CoDiet_phenobert python=3.10
conda activate CoDiet_machine
conda install pip
```

Set up PhenoBERT:

```bash
git clone https://github.com/EclipseCN/PhenoBERT.git
wget https://drive.google.com/drive/folders/1jIqW19JJPzYuyUadxB5Mmfh-pWRiEopH

mv ./PhenoBERT_data/models/* ./PhenoBERT/phenobert/models/
mv ./PhenoBERT_data/embeddings/* ./PhenoBERT/phenobert/embeddings/
rm -rf ./PhenoBERT_data/
mkdir ./output/phenobert_output

cd PhenoBERT
pip install -r requirements.txt
python setup.py
cd phenobert/utils

# Install PyTorch version 2.0.1 , stanza version 1.6.1, numpy version 1.24.3 if needed
# pip install torch==2.0.1+cu117 torchvision==0.15.2+cu117 torchaudio==2.0.2 --index-url https://download.pytorch.org/whl/cu117
# pip install stanza==1.6.1 numpy==1.24.3
# You might need to install some NLTK packages as well

python ./annotate.py -i ../../../passages_input/ -o ../../../output/phenobert_output/
cd ../../..
```

### 8️⃣ BERN2 Annotation

If not already done, exit the PhenoBERT directory:

```bash
cd ../../..
```

Follow the [BERN2 README](https://github.com/dmis-lab/BERN2) to start the BERN server. Then you can run:

```bash
python ./script/bern2.py
```

### 9️⃣ Combine Predictions & Infer Metabolites to generate the Bronze dataset

```bash
python ./script/bronze.py
```

### 🔟 Bronze to Silver Conversion

```bash
python ./script/silver.py
```

---

## Used the following repositories

- [cadmus](https://github.com/biomedicalinformaticsgroup/cadmus)<a href="https://github.com/biomedicalinformaticsgroup/cadmus"><img src="https://img.shields.io/github/stars/biomedicalinformaticsgroup/cadmus.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>
- [Auto-CORPus](https://github.com/omicsNLP/Auto-CORPus)<a href="https://github.com/omicsNLP/Auto-CORPus"><img src="https://img.shields.io/github/stars/omicsNLP/Auto-CORPus.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>
- [BERN2](https://github.com/dmis-lab/BERN2)<a href="https://github.com/dmis-lab/BERN2"><img src="https://img.shields.io/github/stars/dmis-lab/BERN2.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>
- [PhenoBERT](https://github.com/EclipseCN/PhenoBERT)<a href="https://github.com/EclipseCN/PhenoBERT"><img src="https://img.shields.io/github/stars/EclipseCN/PhenoBERT.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>
- [TABoLiSTM](https://github.com/omicsNLP/MetaboliteNER)<a href="https://github.com/omicsNLP/MetaboliteNER"><img src="https://img.shields.io/github/stars/omicsNLP/MetaboliteNER.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>
- [eNzymER](https://github.com/omicsNLP/enzymeNER)<a href="https://github.com/omicsNLP/enzymeNER"><img src="https://img.shields.io/github/stars/omicsNLP/enzymeNER.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>
- [microbELP](https://github.com/omicsNLP/microbELP)<a href="https://github.com/omicsNLP/microbELP"><img src="https://img.shields.io/github/stars/omicsNLP/microbELP.svg?logo=github&label=Stars" style="vertical-align:middle;"/></a>

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
