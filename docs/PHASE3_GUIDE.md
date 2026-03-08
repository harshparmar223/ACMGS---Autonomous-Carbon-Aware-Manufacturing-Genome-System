# Phase 3: Batch Genome Encoding — Implementation Guide

## Overview
Phase 3 creates unified "genome" vectors for each production batch by combining process parameters, material properties, energy DNA embeddings, and carbon intensity into a single 25-dimensional feature vector.

## What Was Implemented

### 1. Core Module: `src/batch_genome/encoder.py`
A complete batch genome encoding system with the following components:

#### Data Loading Functions:
- `load_batch_data()` — Loads CSV from Phase 1
- `load_energy_embeddings()` — Loads embeddings from Phase 2

#### Feature Extraction:
- `extract_process_features()` — 5 process parameters
- `extract_material_features()` — 3 material properties
- `extract_carbon_intensity()` — 1 carbon value

#### Genome Construction:
- `construct_genome_vectors()` — Combines all features into 25-dim vectors

#### Normalization:
- `normalize_genome()` — Z-score normalization (mean=0, std=1)

#### Save/Load Utilities:
- `save_genome_data()` — Saves genome vectors and metadata
- `load_genome_vectors()` — Retrieves saved genomes
- `load_normalization_params()` — Loads mean/std for denormalization
- `get_genome_by_batch_id()` — Retrieves specific batch genome

#### Main Pipeline:
- `run_batch_genome_pipeline()` — Complete end-to-end execution

## Genome Structure (25 Dimensions)

```
Index  | Feature              | Source
-------|----------------------|------------------
0-4    | Process Parameters   | Phase 1 CSV
       | - temperature        |
       | - pressure           |
       | - speed              |
       | - feed_rate          |
       | - humidity           |
-------|----------------------|------------------
5-7    | Material Properties  | Phase 1 CSV
       | - material_density   |
       | - material_hardness  |
       | - material_grade     |
-------|----------------------|------------------
8-23   | Energy DNA           | Phase 2 Embeddings
       | - 16 latent features |
-------|----------------------|------------------
24     | Carbon Intensity     | Phase 1 CSV
-------|----------------------|------------------
Total: 25 dimensions
```

## Output Files

All files saved to `data/processed/`:

1. **genome_vectors.npy**
   - Shape: (2000, 25)
   - Normalized genome vectors (z-score)
   - Ready for ML model input

2. **genome_normalization.npz**
   - Contains: mean (25,) and std (25,)
   - Used to denormalize predictions

3. **batch_ids.npy**
   - Shape: (2000,)
   - Batch identifiers in same order as genome vectors

4. **genome_metadata.csv**
   - Columns: batch_id, genome_index
   - Human-readable lookup table

## How to Run

### Option 1: Run the module directly
```bash
cd /path/to/ACMGS
python -m src.batch_genome.encoder
```

### Option 2: Use the test script
```bash
python test_phase3.py
```

### Option 3: Import in your code
```python
from src.batch_genome.encoder import run_batch_genome_pipeline

# Run pipeline
genome, df = run_batch_genome_pipeline(normalize=True)

print(f"Genome shape: {genome.shape}")  # (2000, 25)
```

## Usage Examples

### Example 1: Generate Genome Vectors
```python
from src.batch_genome.encoder import run_batch_genome_pipeline

# Generate normalized genome vectors
genome, df = run_batch_genome_pipeline(normalize=True)

# Check shape
print(genome.shape)  # (2000, 25)

# Verify normalization
print(f"Mean: {genome.mean():.6f}")  # ~0.0
print(f"Std:  {genome.std():.6f}")   # ~1.0
```

### Example 2: Retrieve Specific Batch
```python
from src.batch_genome.encoder import get_genome_by_batch_id

# Get genome for a specific batch
genome_vec = get_genome_by_batch_id("BATCH_0042")

print(genome_vec.shape)  # (25,)
print(genome_vec[:5])    # First 5 features (process params)
```

### Example 3: Load Pre-computed Genomes
```python
from src.batch_genome.encoder import load_genome_vectors, load_normalization_params

# Load saved genomes
genome = load_genome_vectors()

# Load normalization params (if needed)
mean, std = load_normalization_params()

# Denormalize if needed
genome_original = genome * std + mean
```

## Integration with Other Phases

### From Phase 1 & 2 (Inputs):
- `data/simulated/batch_data.csv` — Process, material, targets, carbon
- `data/simulated/energy_embeddings.npy` — Energy DNA from LSTM

### To Phase 4 (Outputs):
- `data/processed/genome_vectors.npy` — Input features for prediction models
- Each genome vector is a complete representation of manufacturing conditions

## Validation Checks

The pipeline includes automatic validation:
- ✓ Shape verification (all inputs have same num_batches)
- ✓ Normalization check (mean ≈ 0, std ≈ 1)
- ✓ File existence checks
- ✓ Batch ID mapping consistency

## Next Steps (Phase 4)

With genome vectors ready, Phase 4 will:
1. Load genome vectors as input features (X)
2. Load targets (yield, quality, energy) as outputs (y)
3. Train multi-target prediction models
4. Enable rapid prediction for optimization (Phase 5)

## Technical Notes

### Why Normalize?
- Machine learning models (especially neural networks) perform better with normalized inputs
- Prevents features with large scales from dominating
- Ensures all features contribute equally to model learning

### Why This Genome Structure?
- **Process params**: Direct control variables in manufacturing
- **Material props**: Batch-specific material characteristics
- **Energy DNA**: Captures complex energy patterns in compact form
- **Carbon intensity**: Time-dependent environmental context

This unified representation enables the system to:
- Predict outcomes based on complete context
- Optimize across all controllable variables
- Account for energy behavior and carbon impact

## Troubleshooting

**Error: "Batch data not found"**
- Solution: Run Phase 1 first (`python -m src.data_simulation.simulator`)

**Error: "Energy embeddings not found"**
- Solution: Run Phase 2 first (`python -m src.energy_dna.trainer`)

**Error: Shape mismatch**
- Solution: Regenerate all data from Phase 1-2 with same NUM_BATCHES setting

## Summary

Phase 3 successfully:
- ✅ Combines 4 data sources into unified genome vectors
- ✅ Normalizes features for ML compatibility
- ✅ Provides save/load utilities for downstream phases
- ✅ Creates batch lookup system for traceability
- ✅ Generates 2,000 × 25 genome vectors ready for Phase 4

**Phase 3 is COMPLETE and ready for prediction model development!**
