import yt_dlp
import csv
import os
import logging
from datetime import datetime
from pathlib import Path

class YouTubeExtractor:
    def __init__(self, output_dir):
        self.output_dir = output_dir
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True
        }
        
    def extract_metadata(self, url, progress_callback=None):
        try:
            if progress_callback:
                progress_callback(f"Processing URL: {url}")
                
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                metadata = {
                    'video_id': info.get('id'),
                    'title': info.get('title'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'duration': info.get('duration'),
                    'tags': '|'.join(info.get('tags', [])),
                    'category': info.get('category'),
                    'description': info.get('description'),
                    'scrape_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # Save to CSV
                csv_path = os.path.join(self.output_dir, f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
                if progress_callback:
                    progress_callback(f"Saving metadata to: {csv_path}")
                    
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=metadata.keys())
                    writer.writeheader()
                    writer.writerow(metadata)
                
                if progress_callback:
                    progress_callback(f"Successfully processed: {url}")
                return True
                
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error processing {url}: {str(e)}")
            logging.error(f"Error processing {url}: {str(e)}")
            return False
