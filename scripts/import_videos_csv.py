#!/usr/bin/env python3
"""
Import sign language videos from a CSV file.

Usage:
    1. Place your CSV file in the 'data' directory
    2. Place your video files in the 'static/videos' directory
    3. Run this script: python scripts/import_videos_csv.py data/your_file.csv

CSV Format:
    The CSV file should have at least two columns:
    - Column 1: Gloss word/phrase
    - Column 2: Video filename (should be present in static/videos)

Example CSV content:
    gloss,video_file
    NAMASTE,namaste.mp4
    THANK-YOU,thankyou.mp4
    HOW,how.mp4
"""
import os
import sys
import csv
import argparse
from datetime import datetime
from pathlib import Path

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def parse_args():
    parser = argparse.ArgumentParser(description="Import sign language videos from a CSV file")
    parser.add_argument('csv_file', help="Path to the CSV file containing the video mappings")
    parser.add_argument('--has-header', action='store_true', 
                      help="Specify if the CSV file has a header row (default: True)")
    parser.add_argument('--gloss-column', type=int, default=0, 
                      help="Column index for gloss words (0-based, default: 0)")
    parser.add_argument('--video-column', type=int, default=1,
                      help="Column index for video filenames (0-based, default: 1)")
    parser.add_argument('--delimiter', default=',',
                      help="CSV delimiter character (default: ,)")
    parser.add_argument('--videos-dir', default='static/videos',
                      help="Directory containing the video files (default: static/videos)")
    return parser.parse_args()

def import_videos_from_csv(csv_file, videos_dir='static/videos', has_header=True, 
                          gloss_col=0, video_col=1, delimiter=','):
    """
    Import sign language videos from a CSV file.
    
    Args:
        csv_file: Path to the CSV file
        videos_dir: Directory containing the video files
        has_header: Whether the CSV file has a header row
        gloss_col: Column index for gloss words (0-based)
        video_col: Column index for video filenames (0-based)
        delimiter: CSV delimiter character
    """
    if not os.path.exists(csv_file):
        print(f"Error: CSV file '{csv_file}' not found")
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
    
    # Process the CSV file
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    try:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=delimiter)
            
            # Skip header row if specified
            if has_header:
                next(reader, None)
            
            with app.app_context():
                for i, row in enumerate(reader, start=1):
                    if len(row) <= max(gloss_col, video_col):
                        print(f"Warning: Row {i} has fewer columns than expected, skipping")
                        skipped_count += 1
                        continue
                    
                    gloss = row[gloss_col].strip()
                    video_filename = row[video_col].strip()
                    
                    if not gloss or not video_filename:
                        print(f"Warning: Row {i} has empty values, skipping")
                        skipped_count += 1
                        continue
                    
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
        print(f"Error importing CSV file: {str(e)}")
        return False

if __name__ == "__main__":
    args = parse_args()
    import_videos_from_csv(
        args.csv_file, 
        videos_dir=args.videos_dir,
        has_header=args.has_header, 
        gloss_col=args.gloss_column,
        video_col=args.video_column,
        delimiter=args.delimiter
    )