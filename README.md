# particlemind
Self-supervised learning for clustering on HEP events. 

## Quickstart 
```sh
git clone git@github.com:mariel-pettee/particlemind.git
cd particlemind 
uv sync
source scripts/download_data.sh
uv run python scripts/train.py ### TO-DO: replace this
```

## Repository structure
```
particlemind/
├── configs/                      ### Config files (YAML) for keeping track of hyperparameters
├── data/                         ### Data goes here (raw = root files; processed = parquet)
│   ├── raw/
│   ├── processed/
├── src/                          ### Main source code 
│   └── particlemind/
│       ├── models/               ### Model architectures
│       ├── data/                 ### Data processing & loading
│       ├── training/             ### Training loops
│       ├── evaluation/           ### Evaluation metrics & testing functions
│       └── utils/                ### Helper functions
├── notebooks/                    ### Demos 
├── scripts/                      ### Scripts to e.g. train a model
└── outputs/                      ### Model checkpoints & logs
    ├── checkpoints/
    └── logs/
```
