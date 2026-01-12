# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ParticleMind is a High Energy Physics (HEP) research project for self-supervised learning on particle physics collision events. It uses VQ-VAE (Vector Quantized Variational Autoencoder) models to learn discrete representations of calorimeter hit data from simulated FCC-ee collider events.

**Dataset:** Simulated e+e- → ttbar events at 365 GeV from a CLIC-like detector (CLD), processed from ROOT format (Geant4 simulations) to Parquet.

## Commands

### Setup
```bash
uv sync                  # Install dependencies
```

### Data Pipeline
```bash
# Download dataset from Zenodo (~22GB)
source scripts/1_download_data.sh

# Convert ROOT files to Parquet (use --parallel for speed)
uv run python src/particlemind/data/root_to_parquet.py --parallel \
    -i data/raw/p8_ee_tt_ecm365/ \
    -o data/processed/p8_ee_tt_ecm365/
```

### Training
```bash
# Train VQ-VAE tokenizer
uv run python src/particlemind/training/train_vqvae.py --train_embedder

# With custom parameters
uv run python src/particlemind/training/train_vqvae.py --train_embedder \
    --hidden_dim 128 --latent_dim 16 --num_codes 512 --max_epochs 50
```

### Code Quality
```bash
pre-commit run --all-files    # Run Black formatter + nbdev clean
```

**Formatting:** Black with 120 character line length, Python 3.11.

## Architecture

### Data Layer (`src/particlemind/data/`)
- `root_to_parquet.py`: Converts ROOT files (HEP standard) to Parquet format
- `processing.py`: Physics data transformations - extracts calorimeter hits, tracker hits, and particle features (pT, eta, phi)
- `datasets.py`: `CLDHits` IterableDataset streams Parquet files during training
- `arrays.py`: Utilities for Awkward arrays (variable-length nested data structures common in HEP)

### Model Layer (`src/particlemind/models/`)
- `vqvae.py`: VQ-VAE implementations including `VQVAENormFormer` (current default) with Normformer-based encoder/decoder and `VQVAELightning` wrapper for training
- `backbone.py`: Downstream task heads for next-token prediction and classification
- `classifiers.py`: `ParticleFlow` and `ParticleTransformer` classifiers
- `gpt_model.py`: Transformer/attention primitives

### Training Layer (`src/particlemind/training/`)
- `train_vqvae.py`: Main training script using PyTorch Lightning with WandB logging

### Key Dependencies
- **PyTorch Lightning**: Training orchestration, checkpointing, distributed training
- **Awkward Arrays + Uproot**: HEP data handling (variable-length nested structures)
- **VQTorch**: Vector quantization library (from GitHub)
- **FastJet**: Jet clustering algorithms
- **Weights & Biases**: Experiment tracking

## Key Patterns

- Models use PyTorch Lightning's `LightningModule` with `training_step`/`validation_step`/`configure_optimizers`
- Data loading uses `IterableDataset` to stream large Parquet files
- Physics features are stored as Awkward arrays with variable-length dimensions (different events have different numbers of hits)
- VQ-VAE model input is 4-dimensional per hit (relative pT, eta, phi, + layer info)
