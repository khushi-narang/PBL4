#!/usr/bin/env python3
"""
Script to import custom videos into the database.
Usage:
  1. Place your video files in the static/videos directory
  2. Update the CUSTOM_VIDEOS dictionary below with your mappings
  3. Run this script with: python scripts/import_custom_videos.py
"""
import os
import sys
from datetime import datetime

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models import SignVideo

# Define your custom videos mapping here:
# Format: 'gloss_word': 'video_filename.mp4'
# Example: 'HELLO': 'hello.mp4'
CUSTOM_VIDEOS = {
    # Add your mappings here
    # 'YOUR_GLOSS': 'your_video.mp4',
}

def import_custom_videos():
    """
    Import custom videos into the database.
    """
    videos_dir = os.path.join('static', 'videos')
    available_videos = set(os.listdir(videos_dir))
    
    print(f"Found {len(available_videos)} video files in {videos_dir}")
    
    imported_count = 0
    updated_count = 0
    skipped_count = 0
    
    with app.app_context():
        for gloss, filename in CUSTOM_VIDEOS.items():
            if filename not in available_videos:
                print(f"Warning: Video file '{filename}' not found in {videos_dir}, skipping")
                skipped_count += 1
                continue
            
            file_path = os.path.join('static', 'videos', filename)
            
            # Check if the gloss word already exists
            existing_video = SignVideo.query.filter_by(gloss_word=gloss).first()
            
            if existing_video:
                # Update the existing entry
                existing_video.file_path = file_path
                existing_video.created_at = datetime.utcnow()
                db.session.commit()
                print(f"Updated '{gloss}' to use video '{filename}'")
                updated_count += 1
            else:
                # Create a new entry
                new_video = SignVideo(
                    gloss_word=gloss,
                    file_path=file_path
                )
                db.session.add(new_video)
                db.session.commit()
                print(f"Added '{gloss}' with video '{filename}'")
                imported_count += 1
    
    print(f"\nImport summary:")
    print(f"- {imported_count} new videos added")
    print(f"- {updated_count} existing entries updated")
    print(f"- {skipped_count} entries skipped (missing video files)")

if __name__ == "__main__":
    import_custom_videos()