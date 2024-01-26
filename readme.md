
# Overview

- delivery.py compiles and cleans delivery events across 3 sites
- provider_demographics compiles and cleans provider demographics across 3 sites (either self-reported or peer-reported)
- provider_linkage.py links delivery events to provider and merges provider demographics
- main.py does analysis and statistical models

```bash
conda create --yes --name access python=3.9
conda activate access
pip install -r requirements.txt

sudo apt-get install r-base
```

```bash
export DATA_DIR='/mnt/c/Users/Urrutia/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'
# export DATA_DIR='~/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'
python main.py
```

```
Rscript model.R
```