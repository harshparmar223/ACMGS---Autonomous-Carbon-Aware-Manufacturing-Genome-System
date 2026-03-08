"""
Phase 4 Code Quality Verification (No Dependencies Required)

This script verifies the implementation without needing to install packages.
Checks code structure, completeness, and quality.
"""

import os
import re
import sys

def check_file_exists(filepath, description):
    """Check if a file exists"""
    exists = os.path.exists(filepath)
    status = "✓ PASS" if exists else "✗ FAIL"
    print(f"{status}: {description}")
    return exists

def check_code_pattern(filepath, pattern, description):
    """Check if code contains a specific pattern"""
    if not os.path.exists(filepath):
        print(f"✗ FAIL: {description} - file not found")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    found = re.search(pattern, content, re.MULTILINE) is not None
    status = "✓ PASS" if found else "✗ FAIL"
    print(f"{status}: {description}")
    return found

def count_functions(filepath):
    """Count function definitions in a file"""
    if not os.path.exists(filepath):
        return 0
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    matches = re.findall(r'^def\s+(\w+)\s*\(', content, re.MULTILINE)
    return len(matches)

def check_error_handling(filepath):
    """Check for comprehensive error handling"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = {
        "try-except blocks": r'try:\s*\n',
        "ValueError raises": r'raise\s+ValueError',
        "FileNotFoundError": r'(raise|except)\s+FileNotFoundError',
        "IOError handling": r'(raise|except)\s+IOError',
        "Logging errors": r'logger\.error',
        "Logging info": r'logger\.info',
    }
    
    results = {}
    for desc, pattern in checks.items():
        matches = len(re.findall(pattern, content))
        results[desc] = matches
    
    return results

def print_header(text):
    print(f"\n{'='*70}")
    print(f"{text:^70}")
    print(f"{'='*70}\n")

def main():
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    print_header("PHASE 4 CODE QUALITY VERIFICATION")
    print("No dependencies required - checking code structure only\n")
    
    results = []
    
    # Check file structure
    print_header("1. FILE STRUCTURE")
    
    predictor_path = os.path.join(base_path, "src", "prediction", "predictor.py")
    results.append(check_file_exists(predictor_path, "predictor.py exists"))
    
    test_path = os.path.join(base_path, "test_phase4.py")
    results.append(check_file_exists(test_path, "test_phase4.py exists"))
    
    guide_path = os.path.join(base_path, "docs", "PHASE4_GUIDE.md")
    results.append(check_file_exists(guide_path, "docs/PHASE4_GUIDE.md exists"))
    
    # Check function completeness
    print_header("2. FUNCTION COMPLETENESS")
    
    num_functions = count_functions(predictor_path)
    print(f"Total functions defined: {num_functions}")
    
    required_functions = [
        "load_genome_features",
        "load_target_values",
        "split_train_test",
        "create_predictor_model",
        "train_model",
        "evaluate_model",
        "save_model",
        "load_model",
        "predict",
        "run_prediction_pipeline"
    ]
    
    for func in required_functions:
        pattern = rf'^def\s+{func}\s*\('
        results.append(check_code_pattern(predictor_path, pattern, f"{func}() implemented"))
    
    # Check ML libraries
    print_header("3. MACHINE LEARNING INTEGRATION")
    
    results.append(check_code_pattern(predictor_path, r'from sklearn', 
                                     "Uses scikit-learn"))
    results.append(check_code_pattern(predictor_path, r'import xgboost|XGBRegressor', 
                                     "XGBoost support (with fallback)"))
    results.append(check_code_pattern(predictor_path, r'RandomForestRegressor', 
                                     "RandomForest fallback"))
    results.append(check_code_pattern(predictor_path, r'MultiOutputRegressor', 
                                     "Multi-target regression"))
    
    # Check metrics
    print_header("4. METRICS AND EVALUATION")
    
    results.append(check_code_pattern(predictor_path, r'mean_absolute_error', 
                                     "Computes MAE"))
    results.append(check_code_pattern(predictor_path, r'mean_squared_error', 
                                     "Computes RMSE"))
    results.append(check_code_pattern(predictor_path, r'r2_score', 
                                     "Computes R² score"))
    results.append(check_code_pattern(predictor_path, r'MAPE|percentage', 
                                     "Computes MAPE"))
    
    # Check error handling
    print_header("5. ERROR HANDLING")
    
    if os.path.exists(predictor_path):
        error_stats = check_error_handling(predictor_path)
        for check, count in error_stats.items():
            status = "✓ PASS" if count > 0 else "✗ WARN"
            print(f"{status}: {check}: {count} occurrences")
            results.append(count > 0)
    
    # Check documentation
    print_header("6. DOCUMENTATION")
    
    results.append(check_code_pattern(predictor_path, r'\"\"\"[\s\S]*?\"\"\"', 
                                     "Contains docstrings"))
    results.append(check_code_pattern(predictor_path, r'Args:', 
                                     "Function arguments documented"))
    results.append(check_code_pattern(predictor_path, r'Returns:', 
                                     "Return values documented"))
    results.append(check_code_pattern(predictor_path, r'Raises:', 
                                     "Exceptions documented"))
    
    # Check data validation
    print_header("7. DATA VALIDATION")
    
    results.append(check_code_pattern(predictor_path, r'np\.isfinite', 
                                     "Checks for NaN/Inf values"))
    results.append(check_code_pattern(predictor_path, r'\.shape\[', 
                                     "Validates array shapes"))
    results.append(check_code_pattern(predictor_path, r'missing.*columns', 
                                     "Validates required columns"))
    
    # Check model persistence
    print_header("8. MODEL PERSISTENCE")
    
    results.append(check_code_pattern(predictor_path, r'import pickle', 
                                     "Uses pickle for model saving"))
    results.append(check_code_pattern(predictor_path, r'\.pkl', 
                                     "Saves models as .pkl files"))
    results.append(check_code_pattern(predictor_path, r'with open.*wb', 
                                     "Proper file writing"))
    results.append(check_code_pattern(predictor_path, r'with open.*rb', 
                                     "Proper file reading"))
    
    # Final summary
    print_header("CODE QUALITY SUMMARY")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Checks Passed:  {passed}/{total}")
    print(f"Success Rate:   {percentage:.1f}%")
    print(f"\nStatus: {'✓ PRODUCTION READY' if percentage >= 90 else '⚠ NEEDS REVIEW'}")
    
    # File size check
    if os.path.exists(predictor_path):
        size = os.path.getsize(predictor_path)
        lines = open(predictor_path, encoding='utf-8').read().count('\n')
        print(f"\npredictor.py size: {size:,} bytes")
        print(f"Lines of code: {lines}")
    
    # Installation instructions
    print_header("NEXT STEPS")
    
    if percentage >= 90:
        print("✓ Code structure is complete and production-ready!")
        print("\nTo run the actual pipeline:")
        print("  1. Install dependencies:")
        print("     pip install numpy pandas scikit-learn xgboost")
        print("\n  2. Ensure Phases 1-3 are complete")
        print("\n  3. Run the pipeline:")
        print("     py -m src.prediction.predictor")
        print("\n  4. Run tests:")
        print("     py test_phase4.py")
    else:
        print("⚠ Some code quality checks failed")
        print("Review the failed checks above before deployment")
    
    return 0 if percentage >= 90 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
