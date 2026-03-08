"""
COMPREHENSIVE PHASE CHECKER
Check all phases (1-4) to verify they run properly
"""

import os
import sys

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def check_file(filepath, description):
    """Check if a file exists and show its size"""
    exists = os.path.exists(filepath)
    if exists:
        size = os.path.getsize(filepath)
        print(f"✓ {description}: {size:,} bytes")
        return True
    else:
        print(f"✗ {description}: NOT FOUND")
        return False

def check_phase1():
    """Check Phase 1: Data Simulation"""
    print_header("PHASE 1: DATA SIMULATION")
    
    results = []
    
    # Check simulator file
    simulator_path = os.path.join("src", "data_simulation", "simulator.py")
    results.append(check_file(simulator_path, "simulator.py implementation"))
    
    # Check output files
    batch_data_path = os.path.join("data", "simulated", "batch_data.csv")
    results.append(check_file(batch_data_path, "batch_data.csv"))
    
    energy_signals_path = os.path.join("data", "simulated", "energy_signals.npy")
    results.append(check_file(energy_signals_path, "energy_signals.npy"))
    
    # Try to import and check data
    try:
        import pandas as pd
        df = pd.read_csv(batch_data_path)
        num_batches = len(df)
        print(f"✓ Data loaded: {num_batches} batches")
        
        # Check required columns
        required_cols = ['temperature', 'pressure', 'speed', 
                        'yield', 'quality', 'energy_consumption']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"✗ Missing columns: {missing}")
            results.append(False)
        else:
            print(f"✓ All required columns present ({len(df.columns)} columns)")
            results.append(True)
    except Exception as e:
        print(f"⚠ Could not verify data: {e}")
        results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nPhase 1 Status: {passed}/{total} checks passed")
    return all(results)

def check_phase2():
    """Check Phase 2: Energy DNA"""
    print_header("PHASE 2: ENERGY DNA (LSTM AUTOENCODER)")
    
    results = []
    
    # Check model files
    model_path = os.path.join("src", "energy_dna", "model.py")
    results.append(check_file(model_path, "model.py implementation"))
    
    trainer_path = os.path.join("src", "energy_dna", "trainer.py")
    results.append(check_file(trainer_path, "trainer.py implementation"))
    
    # Check output files
    lstm_model_path = os.path.join("models", "saved", "lstm_autoencoder.pth")
    results.append(check_file(lstm_model_path, "lstm_autoencoder.pth"))
    
    embeddings_path = os.path.join("data", "simulated", "energy_embeddings.npy")
    results.append(check_file(embeddings_path, "energy_embeddings.npy"))
    
    # Try to load embeddings
    try:
        import numpy as np
        embeddings = np.load(embeddings_path)
        print(f"✓ Embeddings shape: {embeddings.shape}")
        if embeddings.shape[1] == 16:
            print(f"✓ Correct latent dimension (16)")
            results.append(True)
        else:
            print(f"✗ Wrong latent dimension: {embeddings.shape[1]} (expected 16)")
            results.append(False)
    except Exception as e:
        print(f"⚠ Could not load embeddings: {e}")
        results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nPhase 2 Status: {passed}/{total} checks passed")
    return all(results)

def check_phase3():
    """Check Phase 3: Batch Genome Encoding"""
    print_header("PHASE 3: BATCH GENOME ENCODING")
    
    results = []
    
    # Check encoder file
    encoder_path = os.path.join("src", "batch_genome", "encoder.py")
    results.append(check_file(encoder_path, "encoder.py implementation"))
    
    # Check if genome vectors exist
    genome_path = os.path.join("data", "processed", "genome_vectors.npy")
    # Also check old location for compatibility
    if not os.path.exists(genome_path):
        genome_path = os.path.join("data", "simulated", "genome_vectors.npy")
    genome_exists = check_file(genome_path, "genome_vectors.npy")
    
    if genome_exists:
        results.append(True)
        try:
            import numpy as np
            genomes = np.load(genome_path)
            print(f"✓ Genome shape: {genomes.shape}")
            if genomes.shape[1] == 25:
                print(f"✓ Correct genome dimension (25)")
                results.append(True)
            else:
                print(f"✗ Wrong genome dimension: {genomes.shape[1]} (expected 25)")
                results.append(False)
        except Exception as e:
            print(f"⚠ Could not load genomes: {e}")
            results.append(False)
    else:
        results.append(False)
        print("\n⚠ Genome vectors not found. Attempting to run Phase 3...")
        
        # Try to run Phase 3  
        try:
            print("\nRunning Phase 3 encoder...")
            sys.path.insert(0, os.getcwd())
            from src.batch_genome.encoder import run_batch_genome_pipeline
            
            result = run_batch_genome_pipeline()
            # Handle both tuple and dict return types
            if isinstance(result, tuple):
                genome_vectors = result[0]
            elif isinstance(result, dict):
                genome_vectors = result.get('genome_vectors', result.get('genomes'))
            else:
                genome_vectors = result
                
            print(f"✓ Phase 3 executed successfully!")
            if hasattr(genome_vectors, '__len__'):
                print(f"✓ Generated {len(genome_vectors)} genome vectors")
            results.append(True)
        except Exception as e:
            print(f"✗ Phase 3 execution failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nPhase 3 Status: {passed}/{total} checks passed")
    return all(results)

def check_phase4():
    """Check Phase 4: Prediction Models"""
    print_header("PHASE 4: PREDICTION MODELS")
    
    results = []
    
    # Check predictor file
    predictor_path = os.path.join("src", "prediction", "predictor.py")
    results.append(check_file(predictor_path, "predictor.py implementation"))
    
    # Check if model exists
    model_path = os.path.join("models", "saved", "predictor.pkl")
    model_exists = check_file(model_path, "predictor.pkl")
    
    if model_exists:
        results.append(True)
        print("✓ Trained model found")
    else:
        results.append(False)
        print("\n⚠ Trained model not found. Attempting to run Phase 4...")
        
        # Try to run Phase 4
        try:
            print("\nRunning Phase 4 predictor...")
            sys.path.insert(0, os.getcwd())
            from src.prediction.predictor import run_prediction_pipeline
            
            model, metrics, X_test, y_test, y_pred = run_prediction_pipeline()
            print(f"✓ Phase 4 executed successfully!")
            print(f"\nPrediction Performance:")
            print(f"  Overall R² Score: {metrics['overall']['R2']:.4f}")
            print(f"  Yield R²:         {metrics['yield']['R2']:.4f}")
            print(f"  Quality R²:       {metrics['quality']['R2']:.4f}")
            
            # Check for energy key (may be 'energy' or 'energy_consumption')
            energy_key = 'energy_consumption' if 'energy_consumption' in metrics else 'energy'
            print(f"  Energy R²:        {metrics[energy_key]['R2']:.4f}")
            
            # Check if performance meets standards
            if metrics['overall']['R2'] > 0.80:
                print(f"✓ Performance meets standards (R² > 0.80)")
                results.append(True)
            else:
                print(f"⚠ Performance below standard (R² = {metrics['overall']['R2']:.4f})")
                results.append(False)
                
        except Exception as e:
            print(f"✗ Phase 4 execution failed: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    passed = sum(results)
    total = len(results)
    print(f"\nPhase 4 Status: {passed}/{total} checks passed")
    return all(results)

def main():
    print_header("ACMGS PHASE VALIDATION")
    print("Checking all phases (1-4) for proper execution\n")
    
    # Track overall results
    phase_results = {}
    
    # Check each phase
    phase_results['Phase 1'] = check_phase1()
    phase_results['Phase 2'] = check_phase2()
    phase_results['Phase 3'] = check_phase3()
    phase_results['Phase 4'] = check_phase4()
    
    # Final summary
    print_header("OVERALL SUMMARY")
    
    for phase, result in phase_results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {phase}")
    
    total_passed = sum(phase_results.values())
    total_phases = len(phase_results)
    
    print(f"\n{'='*70}")
    print(f"Total: {total_passed}/{total_phases} phases operational")
    
    if total_passed == total_phases:
        print("✓ ALL PHASES OPERATIONAL - SYSTEM READY")
    else:
        print("⚠ SOME PHASES NEED ATTENTION")
        print("\nTo fix issues:")
        print("  1. Install dependencies: pip install numpy pandas torch scikit-learn xgboost")
        print("  2. Run failed phases individually")
        print("  3. Check logs/ directory for error details")
    
    return 0 if total_passed == total_phases else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
