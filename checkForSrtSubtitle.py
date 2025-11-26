import os
import subprocess
import json

def has_english_subtitle(file_path):
    """Checks if a video file has at least one English subtitle track."""
    command = [
        'ffprobe',
        '-v', 'quiet',
        '-print_format', 'json',
        '-show_entries', 'stream=index,codec_name:stream_tags=language',
        '-select_streams', 's',
        file_path
    ]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        ffprobe_output = json.loads(result.stdout)
        
        for stream in ffprobe_output.get('streams', []):
            if stream.get('codec_name') == 'subrip' or stream.get('codec_name') == 'mov_text':
                if stream.get('tags', {}).get('language') == 'eng' or stream.get('tags', {}).get('language') == 'und':
                    return True
        return False
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        # Handle errors during ffprobe execution or JSON parsing
        return False

def find_videos_without_english_subtitles(folder_path):
    """Walks a directory and prints video files without English subs."""
    no_eng_sub_files = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            # You can extend this with other video file extensions if needed
            if file.endswith(('.mkv', '.mp4', '.avi')):
                file_path = os.path.join(root, file)
                if not has_english_subtitle(file_path):
                    no_eng_sub_files.append(file)
                    
    return no_eng_sub_files

# --- Example Usage ---
folder_to_scan = 'F:\\Videos\\'
files_without_subs = find_videos_without_english_subtitles(folder_to_scan)

if files_without_subs:
    print("\n--- Files without Subrip English subtitles: ---")
    for filename in files_without_subs:
        print(filename)
else:
    print("\nAll files contain Subrip English subtitles.")
