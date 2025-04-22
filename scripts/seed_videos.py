#!/usr/bin/env python3
"""
Script to seed the database with video data from the static/videos directory.
"""

import os
import sys
from pathlib import Path

# Add the project root directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.append(project_root)

# Import the Flask app and database models
from app import app, db
from models import SignVideo

def main():
    """
    Scan the videos directory and add entries to the SignVideo model.
    """
    # Path to the videos directory
    videos_dir = os.path.join(project_root, 'static', 'videos')
    
    if not os.path.exists(videos_dir):
        print(f"Error: Videos directory does not exist at {videos_dir}")
        return
    
    # Get all mp4 files in the directory
    video_files = [f for f in os.listdir(videos_dir) if f.endswith('.mp4')]
    
    if not video_files:
        print("No MP4 video files found in the directory")
        return
    
    print(f"Found {len(video_files)} video files")
    
    # Create application context for database operations
    with app.app_context():
        added_count = 0
        for video_file in video_files:
            # Extract the gloss word from the filename (remove the .mp4 extension)
            gloss_word = os.path.splitext(video_file)[0].lower()
            
            # Check if this gloss word already exists in the database
            existing_video = SignVideo.query.filter_by(gloss_word=gloss_word).first()
            
            if existing_video:
                print(f"Skipping {gloss_word}, already exists in database")
                continue
            
            # Create a new SignVideo record
            video_path = f'videos/{video_file}'
            new_video = SignVideo(
                gloss_word=gloss_word,
                file_path=video_path
            )
            
            db.session.add(new_video)
            added_count += 1
            print(f"Added {gloss_word} to database")
        
        # Commit all changes
        if added_count > 0:
            db.session.commit()
            print(f"Successfully added {added_count} videos to database")
        else:
            print("No new videos added to database")

if __name__ == "__main__":
    main()