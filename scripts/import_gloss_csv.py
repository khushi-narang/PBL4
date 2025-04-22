#!/usr/bin/env python3
"""
Import gloss translations from a CSV file.

Usage:
    1. Place your CSV file in the 'data' directory
    2. Run this script: python scripts/import_gloss_csv.py data/your_file.csv
    3. Restart the application for changes to take effect

CSV Format:
    The CSV file should have at least two columns: 
    - Column 1: English word/phrase
    - Column 2: ISL gloss word/phrase

Example CSV content:
    english,gloss
    hello,NAMASTE
    thank you,THANK-YOU
    how are you,HOW YOU
"""
import os
import sys
import csv
import json
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_args():
    parser = argparse.ArgumentParser(description="Import gloss translations from a CSV file")
    parser.add_argument('csv_file', help="Path to the CSV file containing the translations")
    parser.add_argument('--has-header', action='store_true', 
                      help="Specify if the CSV file has a header row (default: True)")
    parser.add_argument('--english-column', type=int, default=0, 
                      help="Column index for English words (0-based, default: 0)")
    parser.add_argument('--gloss-column', type=int, default=1,
                      help="Column index for gloss words (0-based, default: 1)")
    parser.add_argument('--delimiter', default=',',
                      help="CSV delimiter character (default: ,)")
    return parser.parse_args()

def import_gloss_from_csv(csv_file, has_header=True, english_col=0, gloss_col=1, delimiter=','):
    """
    Import gloss translations from a CSV file.
    
    Args:
        csv_file: Path to the CSV file
        has_header: Whether the CSV file has a header row
        english_col: Column index for English words/phrases (0-based)
        gloss_col: Column index for gloss words/phrases (0-based)
        delimiter: CSV delimiter character
    """
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
        return False
    
    # Create the utils directory if it doesn't exist
    utils_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils')
    os.makedirs(utils_dir, exist_ok=True)
    
    # Path to save the translation rules
    translation_file = os.path.join(utils_dir, 'translation_rules.json')
    
    # Load existing rules if file exists
    existing_rules = {}
    if os.path.exists(translation_file):
        try:
            with open(translation_file, 'r') as f:
                existing_rules = json.load(f)
            print(f"Loaded {len(existing_rules)} existing translation rules")
        except json.JSONDecodeError:
            print("Error reading existing rules, starting fresh")
    
    # Process the CSV file
    new_count = 0
    updated_count = 0
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            
            # Skip header row if specified
            if has_header:
                next(reader, None)
            
            for i, row in enumerate(reader, start=1):
                if len(row) <= max(english_col, gloss_col):
                    print(f"Warning: Row {i} has fewer columns than expected, skipping")
                    continue
                
                english = row[english_col].strip().lower()
                gloss = row[gloss_col].strip()
                
                if not english or not gloss:
                    print(f"Warning: Row {i} has empty values, skipping")
                    continue
                
                if english in existing_rules:
                    if existing_rules[english] != gloss:
                        print(f"Updating: '{english}' -> '{gloss}' (was '{existing_rules[english]}')")
                        updated_count += 1
                    else:
                        print(f"Unchanged: '{english}' -> '{gloss}'")
                else:
                    print(f"Adding: '{english}' -> '{gloss}'")
                    new_count += 1
                
                existing_rules[english] = gloss
        
        # Save the updated translation rules
        with open(translation_file, 'w') as f:
            json.dump(existing_rules, f, indent=2, sort_keys=True)
        
        print(f"\nImport completed successfully:")
        print(f"- {new_count} new translations added")
        print(f"- {updated_count} existing translations updated")
        print(f"- {len(existing_rules)} total translations in the system")
        print(f"\nSaved to: {translation_file}")
        print("Remember to restart the application for changes to take effect")
        
        return True
    
    except Exception as e:
        print(f"Error importing CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    args = parse_args()
    import_gloss_from_csv(
        args.csv_file, 
        has_header=args.has_header, 
        english_col=args.english_column,
        gloss_col=args.gloss_column,
        delimiter=args.delimiter
    )