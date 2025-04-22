#!/usr/bin/env python3
"""
Import data from Excel files (.xlsx format)

This script can:
1. Import gloss translations from Excel
2. Import video mappings from Excel

Usage:
    1. Upload your Excel file to data/uploads
    2. Run this script: 
       python scripts/import_excel.py data/uploads/your_file.xlsx --type [gloss|videos]
    3. Restart the application for changes to take effect

Example:
    python scripts/import_excel.py data/uploads/ISL_CSLRT_Corpus_details.xlsx --type videos
"""
import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_args():
    parser = argparse.ArgumentParser(description="Import data from Excel files (.xlsx format)")
    parser.add_argument('excel_file', help="Path to the Excel file containing the data")
    parser.add_argument('--type', choices=['gloss', 'videos'], required=True,
                      help="Type of data to import: 'gloss' for translations or 'videos' for video mappings")
    parser.add_argument('--sheet-name', help="Name of the Excel sheet to use (default: first sheet)")
    parser.add_argument('--english-column', help="Column name for English words (for gloss imports)")
    parser.add_argument('--gloss-column', help="Column name for gloss words")
    parser.add_argument('--video-column', help="Column name for video filenames (for video imports)")
    parser.add_argument('--videos-dir', default='static/videos',
                      help="Directory containing the video files (default: static/videos)")
    return parser.parse_args()

def import_gloss_from_excel(excel_file, sheet_name=None, english_column=None, gloss_column=None):
    """
    Import gloss translations from an Excel file.
    
    Args:
        excel_file: Path to the Excel file
        sheet_name: Name of the Excel sheet to use (default: first sheet)
        english_column: Column name for English words
        gloss_column: Column name for gloss words
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas is required for Excel import. Installing...")
        os.system("pip install pandas openpyxl")
        import pandas as pd
    
    if not os.path.exists(excel_file):
        print(f"Error: Excel file '{excel_file}' not found")
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
    
    try:
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_file)
        
        print(f"Read Excel file with {len(df)} rows")
        
        # If column names are not provided, try to guess them
        if not english_column:
            # Look for column names that might contain English words
            for col in df.columns:
                if 'english' in str(col).lower() or 'word' in str(col).lower() or 'text' in str(col).lower():
                    english_column = col
                    print(f"Auto-detected English column: '{english_column}'")
                    break
            
            if not english_column:
                english_column = df.columns[0]
                print(f"Using first column as English column: '{english_column}'")
        
        if not gloss_column:
            # Look for column names that might contain gloss words
            for col in df.columns:
                if 'gloss' in str(col).lower() or 'sign' in str(col).lower() or 'isl' in str(col).lower():
                    gloss_column = col
                    print(f"Auto-detected gloss column: '{gloss_column}'")
                    break
            
            if not gloss_column:
                gloss_column = df.columns[1]
                print(f"Using second column as gloss column: '{gloss_column}'")
        
        # Process the Excel data
        new_count = 0
        updated_count = 0
        skipped_count = 0
        
        for _, row in df.iterrows():
            if english_column not in row or gloss_column not in row:
                print(f"Warning: Row is missing required columns, skipping")
                skipped_count += 1
                continue
            
            english = str(row[english_column]).strip().lower()
            gloss = str(row[gloss_column]).strip()
            
            if not english or not gloss or english == 'nan' or gloss == 'nan':
                skipped_count += 1
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
        print(f"- {skipped_count} rows skipped")
        print(f"- {len(existing_rules)} total translations in the system")
        print(f"\nSaved to: {translation_file}")
        print("Remember to restart the application for changes to take effect")
        
        return True
    
    except Exception as e:
        print(f"Error importing Excel file: {str(e)}")
        return False

def import_videos_from_excel(excel_file, videos_dir='static/videos', sheet_name=None, 
                           gloss_column=None, video_column=None):
    """
    Import sign language videos from an Excel file.
    
    Args:
        excel_file: Path to the Excel file
        videos_dir: Directory containing the video files
        sheet_name: Name of the Excel sheet to use (default: first sheet)
        gloss_column: Column name for gloss words
        video_column: Column name for video filenames
    """
    try:
        import pandas as pd
    except ImportError:
        print("pandas is required for Excel import. Installing...")
        os.system("pip install pandas openpyxl")
        import pandas as pd
    
    if not os.path.exists(excel_file):
        print(f"Error: Excel file '{excel_file}' not found")
        return False
    
    if not os.path.exists(videos_dir):
        print(f"Error: Videos directory '{videos_dir}' not found")
        return False
    
    try:
        # Import necessary modules from the app
        from app import app, db
        from models import SignVideo
    except ImportError as e:
        print(f"Error importing app modules: {str(e)}")
        print("Make sure you're running this script from the project root directory")
        return False
    
    # Get list of available video files
    available_videos = set(os.listdir(videos_dir))
    print(f"Found {len(available_videos)} video files in {videos_dir}")
    
    try:
        # Read the Excel file
        if sheet_name:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
        else:
            df = pd.read_excel(excel_file)
        
        print(f"Read Excel file with {len(df)} rows")
        
        # If column names are not provided, try to guess them
        if not gloss_column:
            # Look for column names that might contain gloss words
            for col in df.columns:
                if 'gloss' in str(col).lower() or 'sign' in str(col).lower() or 'isl' in str(col).lower():
                    gloss_column = col
                    print(f"Auto-detected gloss column: '{gloss_column}'")
                    break
            
            if not gloss_column:
                gloss_column = df.columns[0]
                print(f"Using first column as gloss column: '{gloss_column}'")
        
        if not video_column:
            # Look for column names that might contain video filenames
            for col in df.columns:
                if 'video' in str(col).lower() or 'file' in str(col).lower() or 'path' in str(col).lower():
                    video_column = col
                    print(f"Auto-detected video column: '{video_column}'")
                    break
            
            if not video_column:
                video_column = df.columns[1]
                print(f"Using second column as video column: '{video_column}'")
        
        # Process the Excel data
        added_count = 0
        updated_count = 0
        skipped_count = 0
        
        with app.app_context():
            for _, row in df.iterrows():
                if gloss_column not in row or video_column not in row:
                    print(f"Warning: Row is missing required columns, skipping")
                    skipped_count += 1
                    continue
                
                gloss = str(row[gloss_column]).strip()
                video_filename = str(row[video_column]).strip()
                
                if not gloss or not video_filename or gloss == 'nan' or video_filename == 'nan':
                    skipped_count += 1
                    continue
                
                # Check if the video file exists
                if video_filename not in available_videos:
                    print(f"Warning: Video file '{video_filename}' not found in {videos_dir}, skipping")
                    skipped_count += 1
                    continue
                
                file_path = os.path.join(videos_dir, video_filename)
                
                # Check if the gloss word already exists
                existing_video = SignVideo.query.filter_by(gloss_word=gloss).first()
                
                if existing_video:
                    # Update the existing entry
                    existing_video.file_path = file_path
                    existing_video.created_at = datetime.utcnow()
                    db.session.commit()
                    print(f"Updated: '{gloss}' -> '{video_filename}'")
                    updated_count += 1
                else:
                    # Create a new entry
                    new_video = SignVideo(
                        gloss_word=gloss,
                        file_path=file_path
                    )
                    db.session.add(new_video)
                    db.session.commit()
                    print(f"Added: '{gloss}' -> '{video_filename}'")
                    added_count += 1
        
        print(f"\nImport completed successfully:")
        print(f"- {added_count} new videos added")
        print(f"- {updated_count} existing entries updated")
        print(f"- {skipped_count} entries skipped")
        
        return True
    
    except Exception as e:
        print(f"Error importing Excel file: {str(e)}")
        return False

if __name__ == "__main__":
    args = parse_args()
    
    if args.type == 'gloss':
        import_gloss_from_excel(
            args.excel_file, 
            sheet_name=args.sheet_name,
            english_column=args.english_column,
            gloss_column=args.gloss_column
        )
    elif args.type == 'videos':
        import_videos_from_excel(
            args.excel_file,
            videos_dir=args.videos_dir,
            sheet_name=args.sheet_name,
            gloss_column=args.gloss_column,
            video_column=args.video_column
        )