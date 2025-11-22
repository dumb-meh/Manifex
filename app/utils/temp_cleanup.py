import os
import time
import asyncio
from pathlib import Path

async def start_cleanup_service():
    """Clean temp audio files every 6 hours"""
    while True:
        try:
            cleanup_temp_files()
            await asyncio.sleep(6 * 3600)  # Wait 6 hours
        except Exception as e:
            print(f"Cleanup error: {e}")
            await asyncio.sleep(3600)  # Wait 1 hour on error

def cleanup_temp_files():
    """Delete audio files older than 6 hours from temp_audio directory"""
    temp_dir = Path("temp_audio")
    
    if not temp_dir.exists():
        print("temp_audio directory does not exist, creating it...")
        temp_dir.mkdir(exist_ok=True)
        return
    
    cutoff_time = time.time() - (6 * 3600)  # 6 hours ago
    deleted = 0
    
    for file_path in temp_dir.glob("*.mp3"):
        if file_path.stat().st_mtime < cutoff_time:
            try:
                file_path.unlink()
                deleted += 1
                print(f"Deleted old audio file: {file_path}")
            except OSError as e:
                print(f"Failed to delete {file_path}: {e}")
    
    if deleted > 0:
        print(f"Cleanup completed: {deleted} old audio files deleted")
    else:
        print("No old audio files to clean up")