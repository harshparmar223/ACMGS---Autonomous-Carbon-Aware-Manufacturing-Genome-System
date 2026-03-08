"""
Comprehensive Test Suite for Phase 3: Batch Genome Encoder
Run this after Phase 1 and 2 are complete.

This script performs extensive validation to ensure production readiness:
- Data integrity checks
- Shape validation
- Normalization verification
- File I/O testing
- Error handling validation
- Edge case testing
"""

import sys
import os
import numpy as np

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.batch_genome.encoder import (
    run_batch_genome_pipeline, 
    get_genome_by_batch_id,
    load_genome_vectors,
    load_normalization_params,
    load_batch_data,
    load_energy_embeddings
)


def print_header(text):
    """Print a formatted header"""
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}")


def print_subheader(text):
    """Print a formatted subheader"""
    print(f"\n{'-'*70}")
    print(f"{text}")
    print(f"{'-'*70}")


def check_pass(condition, message):
    """Print test result"""
    if condition:
        print(f"✓ PASS: {message}")
        return True
    else:
        print(f"✗ FAIL: {message}")
        return False


def test_prerequisites():
    """Test if Phase 1 and 2 outputs exist"""
    print_subheader("TEST 1: Prerequisites Check")
    
    passed = 0
    total = 0
    
    # Check batch data from Phase 1
    total += 1
    try:
        df = load_batch_data()
        passed += check_pass(True, f"Phase 1 batch data exists ({df.shape[0]} batches)")
    except FileNotFoundError:
        check_pass(False, "Phase 1 batch data missing - run Phase 1 first")
        return False
    
    # Check energy embeddings from Phase 2
    total += 1
    try:
        emb = load_energy_embeddings()
        passed += check_pass(True, f"Phase 2 embeddings exist ({emb.shape})")
    except FileNotFoundError:
        check_pass(False, "Phase 2 embeddings missing - run Phase 2 first")
        return False
    
    print(f"\nPrerequisites: {passed}/{total} passed")
    return passed == total


def test_pipeline_execution():
    """Test the main pipeline execution"""
    print_subheader("TEST 2: Pipeline Execution")
    
    try:
        genome, df = run_batch_genome_pipeline(normalize=True)
        print(f"✓ PASS: Pipeline executed successfully")
        return genome, df
    except Exception as e:
        print(f"✗ FAIL: Pipeline execution failed - {e}")
        raise


def test_genome_structure(genome, df):
    """Test genome vector structure and dimensions"""
    print_subheader("TEST 3: Genome Structure Validation")
    
    passed = 0
    total = 6
    
    # Check shape
    passed += check_pass(genome.ndim == 2, f"Genome is 2D array (shape: {genome.shape})")
    passed += check_pass(genome.shape[1] == 25, f"Genome has 25 dimensions (got: {genome.shape[1]})")
    passed += check_pass(genome.shape[0] == len(df), f"Genome matches batch count ({genome.shape[0]} == {len(df)})")
    
    # Check data type
    passed += check_pass(genome.dtype == np.float64 or genome.dtype == np.float32, 
                        f"Genome is float type (got: {genome.dtype})")
    
    # Check for invalid values
    has_nan = np.any(np.isnan(genome))
    has_inf = np.any(np.isinf(genome))
    passed += check_pass(not has_nan, f"No NaN values in genome")
    passed += check_pass(not has_inf, f"No Inf values in genome")
    
    print(f"\nStructure: {passed}/{total} passed")
    return passed == total


def test_normalization(genome):
    """Test normalization quality"""
    print_subheader("TEST 4: Normalization Verification")
    
    passed = 0
    total = 4
    
    # Check mean (should be close to 0)
    mean_overall = genome.mean()
    passed += check_pass(abs(mean_overall) < 1e-6, 
                        f"Overall mean ≈ 0 (got: {mean_overall:.6f})")
    
    # Check std (should be close to 1)
    std_overall = genome.std()
    passed += check_pass(abs(std_overall - 1.0) < 0.2, 
                        f"Overall std ≈ 1 (got: {std_overall:.6f})")
    
    # Check per-feature means
    feature_means = genome.mean(axis=0)
    max_mean_dev = np.abs(feature_means).max()
    passed += check_pass(max_mean_dev < 1e-6, 
                        f"Max feature mean deviation < 1e-6 (got: {max_mean_dev:.6e})")
    
    # Check per-feature stds
    feature_stds = genome.std(axis=0)
    std_in_range = np.all((feature_stds > 0.5) & (feature_stds < 1.5))
    passed += check_pass(std_in_range, 
                        f"All feature stds in [0.5, 1.5] (range: [{feature_stds.min():.3f}, {feature_stds.max():.3f}])")
    
    print(f"\nNormalization: {passed}/{total} passed")
    return passed == total


def test_file_outputs():
    """Test that all output files were created correctly"""
    print_subheader("TEST 5: Output File Validation")
    
    from config.settings import PROCESSED_DIR
    
    passed = 0
    total = 4
    
    expected_files = {
        "genome_vectors.npy": None,
        "genome_normalization.npz": None,
        "batch_ids.npy": None,
        "genome_metadata.csv": None
    }
    
    for filename in expected_files.keys():
        filepath = os.path.join(PROCESSED_DIR, filename)
        exists = os.path.exists(filepath)
        if exists:
            size = os.path.getsize(filepath)
            passed += check_pass(True, f"{filename} created ({size:,} bytes)")
        else:
            check_pass(False, f"{filename} missing")
    
    print(f"\nFile Outputs: {passed}/{total} passed")
    return passed == total


def test_data_loading():
    """Test loading saved data"""
    print_subheader("TEST 6: Data Loading and Retrieval")
    
    passed = 0
    total = 3
    
    # Test load_genome_vectors
    try:
        loaded_genome = load_genome_vectors()
        passed += check_pass(loaded_genome.shape == (2000, 25), 
                           f"load_genome_vectors works (shape: {loaded_genome.shape})")
    except Exception as e:
        check_pass(False, f"load_genome_vectors failed - {e}")
    
    # Test load_normalization_params
    try:
        mean, std = load_normalization_params()
        passed += check_pass(mean.shape == (25,) and std.shape == (25,), 
                           f"load_normalization_params works (shapes: {mean.shape}, {std.shape})")
    except Exception as e:
        check_pass(False, f"load_normalization_params failed - {e}")
    
    # Test get_genome_by_batch_id
    try:
        batch_genome = get_genome_by_batch_id("BATCH_0000")
        passed += check_pass(batch_genome.shape == (25,), 
                           f"get_genome_by_batch_id works (shape: {batch_genome.shape})")
    except Exception as e:
        check_pass(False, f"get_genome_by_batch_id failed - {e}")
    
    print(f"\nData Loading: {passed}/{total} passed")
    return passed == total


def test_batch_retrieval():
    """Test batch-specific genome retrieval"""
    print_subheader("TEST 7: Batch Retrieval Validation")
    
    passed = 0
    test_ids = ["BATCH_0000", "BATCH_0100", "BATCH_0999", "BATCH_1999"]
    
    for batch_id in test_ids:
        try:
            retrieved = get_genome_by_batch_id(batch_id)
            success = (retrieved.shape == (25,) and 
                      not np.any(np.isnan(retrieved)) and 
                      not np.any(np.isinf(retrieved)))
            if success:
                passed += 1
                print(f"✓ {batch_id}: OK (first 3: [{retrieved[0]:.3f}, {retrieved[1]:.3f}, {retrieved[2]:.3f}])")
            else:
                print(f"✗ {batch_id}: Invalid data")
        except Exception as e:
            print(f"✗ {batch_id}: ERROR - {e}")
    
    print(f"\nBatch Retrieval: {passed}/{len(test_ids)} passed")
    return passed == len(test_ids)


def test_error_handling():
    """Test error handling for invalid inputs"""
    print_subheader("TEST 8: Error Handling Validation")
    
    passed = 0
    total = 2
    
    # Test invalid batch ID
    try:
        get_genome_by_batch_id("INVALID_ID_12345")
        check_pass(False, "Should raise error for invalid batch ID")
    except ValueError:
        passed += check_pass(True, "Correctly raises ValueError for invalid batch ID")
    except Exception as e:
        check_pass(False, f"Wrong exception type: {type(e).__name__}")
    
    # Test nonexistent batch ID
    try:
        get_genome_by_batch_id("BATCH_9999")
        check_pass(False, "Should raise error for nonexistent batch ID")
    except ValueError:
        passed += check_pass(True, "Correctly raises ValueError for nonexistent batch ID")
    except Exception as e:
        check_pass(False, f"Wrong exception type: {type(e).__name__}")
    
    print(f"\nError Handling: {passed}/{total} passed")
    return passed == total


def test_data_consistency():
    """Test consistency between different data sources"""
    print_subheader("TEST 9: Data Consistency Checks")
    
    passed = 0
    total = 3
    
    genome = load_genome_vectors()
    df = load_batch_data()
    
    # Check batch count consistency
    batch_ids = np.load(os.path.join(PROCESSED_DIR, "batch_ids.npy"))
    passed += check_pass(len(batch_ids) == len(genome) == len(df),
                        f"Batch counts consistent: genome={len(genome)}, df={len(df)}, ids={len(batch_ids)}")
    
    # Check metadata consistency
    import pandas as pd
    metadata = pd.read_csv(os.path.join(PROCESSED_DIR, "genome_metadata.csv"))
    passed += check_pass(len(metadata) == len(genome),
                        f"Metadata row count matches genome: {len(metadata)} == {len(genome)}")
    
    # Check specific batch retrieval consistency
    test_idx = 42
    genome_row = genome[test_idx]
    batch_id = batch_ids[test_idx]
    retrieved = get_genome_by_batch_id(batch_id)
    passed += check_pass(np.allclose(genome_row, retrieved),
                        f"Direct indexing matches retrieval for {batch_id}")
    
    print(f"\nData Consistency: {passed}/{total} passed")
    
    from config.settings import PROCESSED_DIR
    return passed == total


def main():
    """Run all tests"""
    print_header("COMPREHENSIVE PHASE 3 VALIDATION TEST SUITE")
    print("This script validates production readiness")
    print(f"Test Date: {os.popen('powershell Get-Date -Format yyyy-MM-dd').read().strip()}")
    
    all_passed = []
    
    try:
        # Test 1: Prerequisites
        all_passed.append(test_prerequisites())
        
        # Test 2: Pipeline execution
        genome, df = test_pipeline_execution()
        
        # Test 3: Genome structure
        all_passed.append(test_genome_structure(genome, df))
        
        # Test 4: Normalization
        all_passed.append(test_normalization(genome))
        
        # Test 5: File outputs
        all_passed.append(test_file_outputs())
        
        # Test 6: Data loading
        all_passed.append(test_data_loading())
        
        # Test 7: Batch retrieval
        all_passed.append(test_batch_retrieval())
        
        # Test 8: Error handling
        all_passed.append(test_error_handling())
        
        # Test 9: Data consistency
        all_passed.append(test_data_consistency())
        
        # Final summary
        print_header("TEST SUMMARY")
        total_tests = len(all_passed)
        passed_tests = sum(all_passed)
        
        print(f"\nTotal Test Suites: {total_tests}")
        print(f"Passed Suites:     {passed_tests}")
        print(f"Failed Suites:     {total_tests - passed_tests}")
        print(f"Success Rate:      {100*passed_tests/total_tests:.1f}%")
        
        if all(all_passed):
            print_header("✓ ALL TESTS PASSED - PRODUCTION READY")
            print("\nPhase 3 is validated and ready for:")
            print("  - Phase 4: Prediction model training")
            print("  - Real-world manufacturing deployment")
            print("  - Integration with downstream systems")
            return 0
        else:
            print_header("✗ SOME TESTS FAILED - REVIEW REQUIRED")
            print("\nPlease review failed tests before deployment")
            return 1
            
    except Exception as e:
        print_header("✗ CRITICAL ERROR")
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
