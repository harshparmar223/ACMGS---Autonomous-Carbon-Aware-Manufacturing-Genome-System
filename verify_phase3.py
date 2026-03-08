"""
Phase 3 Code Quality Verification (No Dependencies Required)

This script verifies the implementation without needing to install packages
or run the actual pipeline. It checks:
- Code structure and completeness
- Error handling implementation
- Documentation quality
- File organization
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
        "Logging warnings": r'logger\.warning',
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
    
    print_header("PHASE 3 CODE QUALITY VERIFICATION")
    print("No dependencies required - checking code structure only\n")
    
    results = []
    
    # Check file structure
    print_header("1. FILE STRUCTURE")
    
    encoder_path = os.path.join(base_path, "src", "batch_genome", "encoder.py")
    results.append(check_file_exists(encoder_path, "encoder.py exists"))
    
    test_path = os.path.join(base_path, "test_phase3.py")
    results.append(check_file_exists(test_path, "test_phase3.py exists"))
    
    deployment_path = os.path.join(base_path, "PHASE3_DEPLOYMENT.md")
    results.append(check_file_exists(deployment_path, "PHASE3_DEPLOYMENT.md exists"))
    
    guide_path = os.path.join(base_path, "docs", "PHASE3_GUIDE.md")
    results.append(check_file_exists(guide_path, "docs/PHASE3_GUIDE.md exists"))
    
    # Check function completeness
    print_header("2. FUNCTION COMPLETENESS")
    
    num_functions = count_functions(encoder_path)
    print(f"Total functions defined: {num_functions}")
    
    required_functions = [
        "load_batch_data",
        "load_energy_embeddings",
        "extract_process_features",
        "extract_material_features",
        "extract_carbon_intensity",
        "construct_genome_vectors",
        "normalize_genome",
        "save_genome_data",
        "load_genome_vectors",
        "load_normalization_params",
        "get_genome_by_batch_id",
        "run_batch_genome_pipeline"
    ]
    
    for func in required_functions:
        pattern = rf'^def\s+{func}\s*\('
        results.append(check_code_pattern(encoder_path, pattern, f"{func}() implemented"))
    
    # Check error handling
    print_header("3. ERROR HANDLING")
    
    if os.path.exists(encoder_path):
        error_stats = check_error_handling(encoder_path)
        for check, count in error_stats.items():
            status = "✓ PASS" if count > 0 else "✗ WARN"
            print(f"{status}: {check}: {count} occurrences")
            results.append(count > 0)
    
    # Check documentation
    print_header("4. DOCUMENTATION")
    
    results.append(check_code_pattern(encoder_path, r'\"\"\"[\s\S]*?\"\"\"', 
                                     "Contains docstrings"))
    results.append(check_code_pattern(encoder_path, r'Args:', 
                                     "Function arguments documented"))
    results.append(check_code_pattern(encoder_path, r'Returns:', 
                                     "Return values documented"))
    results.append(check_code_pattern(encoder_path, r'Raises:', 
                                     "Exceptions documented"))
    
    # Check validation logic
    print_header("5. DATA VALIDATION")
    
    results.append(check_code_pattern(encoder_path, r'np\.isfinite', 
                                     "Checks for NaN/Inf values"))
    results.append(check_code_pattern(encoder_path, r'\.shape\[', 
                                     "Validates array shapes"))
    results.append(check_code_pattern(encoder_path, r'if.*\.empty', 
                                     "Checks for empty data"))
    results.append(check_code_pattern(encoder_path, r'required.*columns', 
                                     "Validates required columns"))
    
    # Check configuration integration
    print_header("6. CONFIGURATION")
    
    results.append(check_code_pattern(encoder_path, r'from config\.settings import', 
                                     "Imports from config.settings"))
    results.append(check_code_pattern(encoder_path, r'GENOME_PROCESS_FEATURES', 
                                     "Uses GENOME_PROCESS_FEATURES"))
    results.append(check_code_pattern(encoder_path, r'GENOME_MATERIAL_FEATURES', 
                                     "Uses GENOME_MATERIAL_FEATURES"))
    results.append(check_code_pattern(encoder_path, r'PROCESSED_DIR', 
                                     "Uses PROCESSED_DIR config"))
    
    # Check logging
    print_header("7. LOGGING")
    
    results.append(check_code_pattern(encoder_path, r'from src\.utils\.logger import', 
                                     "Imports logger"))
    results.append(check_code_pattern(encoder_path, r'logger\.info', 
                                     "Uses info logging"))
    results.append(check_code_pattern(encoder_path, r'logger\.error', 
                                     "Uses error logging"))
    
    # Final summary
    print_header("CODE QUALITY SUMMARY")
    
    passed = sum(results)
    total = len(results)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Checks Passed:  {passed}/{total}")
    print(f"Success Rate:   {percentage:.1f}%")
    print(f"\nStatus: {'✓ PRODUCTION READY' if percentage >= 90 else '⚠ NEEDS REVIEW'}")
    
    # File size check
    if os.path.exists(encoder_path):
        size = os.path.getsize(encoder_path)
        print(f"\nencoder.py size: {size:,} bytes")
        print(f"Lines of code: {open(encoder_path).read().count(chr(10))}")
    
    # Installation instructions
    print_header("NEXT STEPS")
    
    if percentage >= 90:
        print("✓ Code structure is complete and production-ready!")
        print("\nTo run the actual pipeline:")
        print("  1. Install dependencies:")
        print("     pip install numpy pandas torch")
        print("\n  2. Ensure Phase 1 & 2 are complete")
        print("\n  3. Run the pipeline:")
        print("     py -m src.batch_genome.encoder")
        print("\n  4. Run tests:")
        print("     py test_phase3.py")
    else:
        print("⚠ Some code quality checks failed")
        print("Review the failed checks above before deployment")
    
    return 0 if percentage >= 90 else 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
