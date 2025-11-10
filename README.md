# particlemind
Self-supervised learning for clustering on HEP events. 

## Quickstart 
```sh
git clone git@github.com:mariel-pettee/particlemind.git
cd particlemind 
uv sync
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
│       ├── __init__.py
│       ├── models/               ### Model architectures
│       ├── data/                 ### Data loaders, datasets, transforms
│       ├── training/             ### Training loops, trainers
│       ├── evaluation/           ### Eval metrics, testing
│       └── utils/                ### Helper functions
├── notebooks/                    ### Demos 
├── scripts/                      ### Scripts to e.g. train a model
└── outputs/                      ### Model checkpoints, logs (add to .gitignore)
    ├── checkpoints/
    └── logs/
```
