#!/usr/bin/env python3
"""
Script to customize the gloss translation rules.
This allows you to define custom mappings from English words to ISL gloss.

Usage:
  1. Update the CUSTOM_TRANSLATIONS dictionary below with your mappings
  2. Run this script with: python scripts/update_gloss_translations.py
  3. Restart the application to apply changes
"""
import os
import sys
import json

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Define your custom translations mapping here:
# Format: 'english_word': 'ISL_GLOSS_WORD'
# Example: 'hello': 'HELLO'
CUSTOM_TRANSLATIONS = {
    # Add your mappings here
    # 'english': 'ISL_GLOSS',
}

def update_translation_rules():
    """
    Update the translation rules file with custom mappings.
    """
    utils_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'utils')
    translation_file = os.path.join(utils_dir, 'translation_rules.json')
    
    # Load existing rules if file exists, or create new empty rules
    if os.path.exists(translation_file):
        try:
            with open(translation_file, 'r') as f:
                translation_rules = json.load(f)
            print(f"Loaded existing translation rules with {len(translation_rules)} entries")
        except json.JSONDecodeError:
            print("Error reading existing rules, creating new rules file")
            translation_rules = {}
    else:
        print("No existing rules file found, creating new rules file")
        translation_rules = {}
    
    # Update with custom translations
    added_count = 0
    updated_count = 0
    
    for english, gloss in CUSTOM_TRANSLATIONS.items():
        if english in translation_rules:
            old_gloss = translation_rules[english]
            translation_rules[english] = gloss
            print(f"Updated rule for '{english}': '{old_gloss}' -> '{gloss}'")
            updated_count += 1
        else:
            translation_rules[english] = gloss
            print(f"Added new rule: '{english}' -> '{gloss}'")
            added_count += 1
    
    # Write the updated rules back to the file
    os.makedirs(utils_dir, exist_ok=True)
    with open(translation_file, 'w') as f:
        json.dump(translation_rules, f, indent=2, sort_keys=True)
    
    print(f"\nUpdate summary:")
    print(f"- {added_count} new translation rules added")
    print(f"- {updated_count} existing rules updated")
    print(f"- Total: {len(translation_rules)} translation rules in the system")
    print(f"\nTranslation rules saved to: {translation_file}")
    print("Remember to restart the application for changes to take effect")

if __name__ == "__main__":
    update_translation_rules()