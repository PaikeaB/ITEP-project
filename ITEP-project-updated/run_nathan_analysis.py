"""
Master script to run all of Nathan's analysis tasks in sequence.
Run this single file to complete all tasks.
"""

import subprocess
import sys
import os

def run_script(script_name, description):
    """Run a Python script and report status."""
    print("\n" + "="*70)
    print(f"RUNNING: {description}")
    print("="*70)
    try:
        result = subprocess.run([sys.executable, script_name], 
                                check=True, 
                                capture_output=False)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error running {script_name}: {e}")
        return False

def main():
    print("\n" + "#"*70)
    print("# NATHAN'S COMPLETE ANALYSIS PIPELINE")
    print("#"*70)
    
    scripts = [
        ("create_sample_data.py", "Creating sample coded data"),
        ("calculate_irr.py", "Calculating inter-rater reliability"),
        ("create_consensus.py", "Creating consensus dataset"),
        ("analyze_framing.py", "Analyzing framing distribution"),
        ("extract_examples.py", "Extracting representative examples")
    ]
    
    results = []
    
    for script, description in scripts:
        if os.path.exists(script):
            success = run_script(script, description)
            results.append((description, success))
        else:
            print(f"\n✗ Script not found: {script}")
            results.append((description, False))
    
    # Final summary
    print("\n" + "="*70)
    print("ANALYSIS COMPLETE - SUMMARY")
    print("="*70)
    
    for description, success in results:
        status = "✓ SUCCESS" if success else "✗ FAILED"
        print(f"{status}: {description}")
    
    print("\n" + "="*70)
    print("OUTPUT FILES GENERATED:")
    print("="*70)
    
    output_files = [
        "metadata/nathan_coded_passages.csv",
        "metadata/paikea_coded_passages.csv",
        "metadata/disagreements_to_resolve.csv",
        "metadata/final_coded_passages.csv",
        "reports/irr_report.txt",
        "reports/framing_summary.txt",
        "reports/framing_examples.md",
        "visualizations/irr_confusion_matrix.png",
        "visualizations/framing_distribution.png",
        "visualizations/framing_by_platform.png",
        "visualizations/framing_pie_chart.png"
    ]
    
    for filepath in output_files:
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            print(f"✓ {filepath} ({size:,} bytes)")
        else:
            print(f"✗ {filepath} (not found)")
    
    print("\n" + "#"*70)
    print("# ALL TASKS COMPLETE")
    print("#"*70 + "\n")

if __name__ == "__main__":
    main()