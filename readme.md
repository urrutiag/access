```bash
conda create --yes --name access python=3.9
conda activate access
pip install -r requirements.txt
```

```bash
# export DATA_DIR='/mnt/c/Users/Urrutia/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'
export DATA_DIR='~/Dropbox/Documents/UNC_OBGYN/kavita_access/data/'
python main.py
```

```
Rscript model.R
```