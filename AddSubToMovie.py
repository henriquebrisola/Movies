from ast import pattern
from importlib.resources import files
import os
import sys
import subprocess
import csv

def get_operating_system():
    platforms = {
        'linux': 'Linux',
        'darwin': 'macOS',
        'win32': 'Windows'
    }
    if sys.platform in platforms:
        return platforms[sys.platform]
    else:
        return sys.platform

def get_config_file_path():
    if get_operating_system() == 'Windows':
        config_file_path = os.path.join(os.getenv('APPDATA'), 'AddSubToMovies', 'config.txt')
    elif get_operating_system() in ['Linux', 'macOS']:
        config_file_path = os.path.join("/home/user/Movies", 'config.txt')
    return config_file_path

def check_get_default_folder_path_in_config():
    config_file_path = get_config_file_path()
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                if line.startswith('default_folder_path='):
                    print(f"Default folder path found in config: {line.split('=', 1)[1].strip()}")
                    return line.split('=', 1)[1].strip()
    return None

def select_folder_path():
    if get_operating_system() == 'Windows':
        eg_text = " (e.g., D:\\Movies)"
    elif get_operating_system() in ['Linux', 'macOS']:
        eg_text = " (e.g., /home/user/Movies)"
    config_file_path = get_config_file_path()
    inputed_folder_path = input(f"Enter the new default folder path for movies {eg_text}: ").strip()
    selected_folder_path = os.path.normpath(inputed_folder_path)  # Normalize the path for Linux/macOS
    return selected_folder_path, config_file_path

def set_default_folder(default_folder_path):
    config_file_path = check_get_default_folder_path_in_config()
    if config_file_path is not None:
        if os.path.isfile(config_file_path):
            with open(config_file_path, 'r') as config_file:
                for line in config_file:
                    if line.startswith('default_folder_path='):
                        print(f"Default folder path currently set to: {line.split('=', 1)[1].strip()}")
                        return line.split('=', 1)[1].strip()
                
    if config_file_path is None or default_folder_path is None:
        selected_folder_path, config_file_path = select_folder_path()


    write_config_file(f"default_folder_path={selected_folder_path}")

def write_config_file(incomming_config):
    config_file_path = get_config_file_path()
    config_dir = os.path.dirname(config_file_path)
    outgoing_config_key_value = []
    found_config_key_in_file = False
    # Read existing config file if it exists and update the value for the incoming config key, otherwise add the new key-value pair
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                current_config_key = line.split('=')[0]
                current_config_value = line.split('=')[1]
                if current_config_key + '=' in incomming_config:
                    print(f"Config {current_config_key} currently set to: {current_config_value.strip()}")
                    outgoing_config_key_value.append(incomming_config)
                    found_config_key_in_file = True
                if current_config_key + '=' not in incomming_config:
                    outgoing_config_key_value.append(line)
            if not found_config_key_in_file:
                outgoing_config_key_value.append(incomming_config)
    # Remove trailing newline from the last line if it exists
    for index, line in enumerate(outgoing_config_key_value):
        if (index != len(outgoing_config_key_value) - 1) and not line.endswith('\n'):
             outgoing_config_key_value[index] = line + '\n'
        elif (index == len(outgoing_config_key_value) - 1) and line.endswith('\n'):
            outgoing_config_key_value[index] = line.strip('\n')
    print(f"Config to be written: {(''.join(outgoing_config_key_value))}")
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    with open(config_file_path, 'w') as config_file:
        config_file.write(''.join(outgoing_config_key_value))
    print(f"Config file created at {config_file_path} with the following content:\n{''.join(outgoing_config_key_value)}")

def get_text_codecs_config():
    config_file_path = get_config_file_path()
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                if line.startswith('text_codecs='):
                    print(f"Text codecs found in config: {line.split('=', 1)[1].strip()}")
                    return line.split('=', 1)[1].strip().split(',')
    return None

def get_languages_config():
    config_file_path = get_config_file_path()
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                if line.startswith('languages='):
                    print(f"Languages found in config: {line.split('=', 1)[1].strip()}")
                    return line.split('=', 1)[1].strip().split(',')
    return None

def set_default_text_codecs_in_config_if_not_exists(skip_input=False):
    if get_text_codecs_config() is None:
        text_codecs = ['subrip', 'ass', 'ssa', 'webvtt', 'mov_text', 'srt']
        write_config_file('text_codecs=' + ','.join(text_codecs))
    elif not skip_input:
        text_codecs = input("Enter the text codecs (comma-separated): ").split(',')
        write_config_file('text_codecs=' + ','.join(text_codecs))

def set_default_languages_in_config_if_not_exists(skip_input=False):
    if get_languages_config() is None:
        languages = ['eng', 'Inglês', 'English', 'en']
        write_config_file('languages=' + ','.join(languages))
    elif not skip_input:
        languages = input("Enter the languages (comma-separated): ").split(',')
        write_config_file('languages=' + ','.join(languages))

def check_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True, encoding='utf-8')
        subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, check=True, encoding='utf-8')
        return True
    except FileNotFoundError:
        return False
    
def ensure_ffmpeg_installed():
    if not check_ffmpeg_installed():
        print("FFMPEG or FFPROBE is not installed or not found in PATH.")
        print("Please install FFMPEG and ensure it's added to your system's PATH environment variable.")
        print("You can download it from: https://ffmpeg.org/download.html")
        sys.exit(1)

def process_videos_from_csv_list(csv_folder_path, skip_update_csv_list_movies=False):
    csv_file_path = os.path.join(csv_folder_path, 'movies_subtitle_status.csv')
    if not os.path.isfile(csv_file_path):
        print(f"CSV file not found at: {csv_file_path}")
        print("Creating CSV file with current movies and subtitle status in the folder...")
        export_movies_in_folder_to_csv(check_get_default_folder_path_in_config())
    elif not skip_update_csv_list_movies:
        print("CSV file found. Updating video statuses to the list...")
        export_movies_in_folder_to_csv(check_get_default_folder_path_in_config())
    else:
        print("CSV file found. Skipping update of video statuses to the list as per flag.")
    
    with open(csv_file_path, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            movie_path = row['Movie Path']
            subtitle_path = row['Subtitle Path']
            Has_English_Text_Subtitles = row['Has English Text Subtitles']
            if os.path.isfile(movie_path) and Has_English_Text_Subtitles == 'No' and os.path.isfile(subtitle_path):
                print(f"\nProcessing Movie: {movie_path} with Subtitle: {subtitle_path}")
                add_subtitle_to_video(check_get_default_folder_path_in_config(), movie_path, subtitle_path)
                continue
            if not os.path.isfile(movie_path):
                print(f"Movie file not found: {movie_path}. Skipping.")
            if subtitle_path == '':
                print(f"No subtitle path provided for movie: {movie_path}. Skipping.")
            if not os.path.isfile(subtitle_path):
                print(f"Subtitle file not found: {subtitle_path}. Skipping.")
            if Has_English_Text_Subtitles == 'Yes':
                print(f"Movie {movie_path} already have English text subtitles according to CSV. Skipping.")

    if not skip_update_csv_list_movies:
        print("Updating video statuses to the list...")
        export_movies_in_folder_to_csv(check_get_default_folder_path_in_config())

def export_movies_in_folder_to_csv(default_folder_path):
    # List folders
    folders = [f for f in os.listdir(default_folder_path)
               if os.path.isdir(os.path.join(default_folder_path, f))
               and not f.startswith('SRT-')]

    folders_movies_subtitle_status = {}

    movies_status = []
    for folder in folders:
        print("Checking folder:", folder)
        folder_path = os.path.join(default_folder_path, folder)
        movie_files = [f for f in os.listdir(folder_path)
                       if os.path.isfile(os.path.join(folder_path, f))
                       and f.endswith(('.mp4', '.mkv'))
                       and not f.startswith('SRT-')]

        has_processed_movie_in_folder = any(f.startswith('SRT-') for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)))

        for movie_file in movie_files:
            print("  Checking movie:", movie_file)
            movie_path = os.path.join(folder_path, movie_file)
            has_english_text_sub = False

            if has_processed_movie_in_folder:
                has_english_text_sub = True
            else:
                try:
                    ffprobe_command = [
                        'ffprobe',
                        '-i', movie_path,
                        '-show_streams',
                        '-select_streams', 's',
                        '-v', '0'
                    ]
                    
                    codec = None
                    language = None
                    subtitle_index = 1

                    text_codecs = get_text_codecs_config()
                    languages = get_languages_config()
                    result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True, encoding='utf-8')
                    if result.stdout:
                        for line in result.stdout.splitlines():
                            if line.startswith('codec_name='):
                                codec = line.split('=', 1)[1]
                            if line.startswith('language=') or line.startswith('TAG:language='):
                                language = line.split('=', 1)[1]
                            if language in languages and codec in text_codecs:
                                has_english_text_sub = True
                            if line == "[/STREAM]": # cleans up after each subtitle language
                                if language not in languages or codec not in text_codecs:
                                    print(f"    Found subtitle stream with codec: {codec} and language: {language} over index: {subtitle_index}, but it does not meet criteria for English text subtitles.")
                                if language in languages and codec in text_codecs:
                                    print(f"    Found subtitle stream with codec: {codec} and language: {language} over index: {subtitle_index}, it does meet criteria for English text subtitles.")
                                subtitle_index += 1
                                codec = None
                                language = None
                except subprocess.CalledProcessError:
                    # If ffprobe fails, assume no subs
                    has_english_text_sub = False
                except UnicodeDecodeError:
                    print("UnicodeDecodeError")
                except Exception as e:
                    print(f"Error occurred while checking {movie_file}: {e}")
            
            for f in os.listdir(folder_path):
                if f.endswith(('.srt')) and os.path.isfile(os.path.join(folder_path, f)):
                    subtitle_file_path = os.path.join(folder_path, f)
                    break
                else:
                    subtitle_file_path = ''
            
            # Extract movie name from folder name
            # Removes years, resolution, and other common patterns from folder names to get a cleaner movie name for the CSV output
            # identifies words that are not part of the movie name and removes them, such as years (e.g., 1999, 2005), resolutions (e.g., 1080p, 720p), and common tags (e.g., BluRay, WEBRip)
            year_pattern = []
            for year in range(1900, 2101):
                year_pattern.append(f"{year}")
            movie_name = folder.split('(')[0].split('[')[0].strip()  # Remove anything after '(' or '[' to get a cleaner movie name
            for pattern in year_pattern:
                if pattern == movie_name:
                    break
                if pattern in movie_name:
                    movie_name = movie_name.split(pattern)[0]
            movie_name = movie_name.replace('.', ' ').replace('_', ' ').strip()
            #movie_name = ' '.join(word for word in movie_name.split() if not (word.isdigit() and len(word) == 4) and word not in ['1080p', '720p', 'BluRay', 'WEBRip'])

            movies_status.append({
                'folder': folder,
                'movie_name': movie_name,
                'movie_file': movie_file,
                'MoviePath': movie_path,
                'SubtitlePath': subtitle_file_path,
                'has_english_text_sub': has_english_text_sub,
            })

    csv_path = os.path.join(default_folder_path, 'movies_subtitle_status.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Folder', 'Movie Name', 'Movie File', 'Movie Path', 'Subtitle Path', 'Has English Text Subtitles'])
        for row in movies_status:
            writer.writerow([row['folder'], row['movie_name'], row['movie_file'], row['MoviePath'], row['SubtitlePath'], 'Yes' if row['has_english_text_sub'] else 'No'])

    print(f"Results saved to {csv_path}")

    return folders_movies_subtitle_status

def select_movie_folder_from_folder(default_folder_path):
    # First, list folders for user to select
    folders = [f for f in os.listdir(default_folder_path) 
               if os.path.isdir(os.path.join(default_folder_path, f)) 
               and not f.startswith('SRT-')]
    
    if not folders:
        print("No folders found in the default folder.")
        return
    
    if len(folders) == 1:
        selected_folder = folders[0]
        print(f"\nAuto-selected folder: {selected_folder}")
    else:
        print("\nAvailable folders:")
        for i, f in enumerate(folders, 1):
            print(f"{i}. {f}")
        choice = int(input("\nSelect folder number: ")) - 1
        if not (0 <= choice < len(folders)):
            print("Invalid selection.")
            return
        selected_folder = folders[choice]
    
    # Now check inside selected folder for movie files
    selected_folder_path = os.path.join(default_folder_path, selected_folder)
    movie_files = [f for f in os.listdir(selected_folder_path) 
                   if os.path.isfile(os.path.join(selected_folder_path, f)) 
                   and f.endswith(('.mp4', '.mkv'))
                   and not f.startswith('SRT-')]
    
    if not movie_files:
        print(f"No movie files (.mp4, .mkv) found in {selected_folder}.")
        return
    
    if len(movie_files) == 1:
        movie_path = os.path.join(selected_folder_path, movie_files[0]).strip('"')
        print(f"\nAuto-selected: {movie_files[0]}")
        return movie_path
    
    # Multiple movie files found, prompt user to select
    print("\nAvailable movie files:")
    for i, f in enumerate(movie_files, 1):
        print(f"{i}. {f}")
    choice = int(input("\nSelect movie file number: ")) - 1
    if 0 <= choice < len(movie_files):
        movie_path = os.path.join(selected_folder_path, movie_files[choice]).strip('"')
        return movie_path
    else:
        print("Invalid selection.")
        return

def select_subtitle_file_from_folder(movie_path):
    subtitle_files = [f for f in os.listdir(os.path.dirname(movie_path)) if f.endswith(('.srt', '.ass', '.vtt'))]
    if subtitle_files:
        if len(subtitle_files) == 1:
            subtitle_path = os.path.join(os.path.dirname(movie_path), subtitle_files[0]).strip('"')
            print(f"\nAuto-selected: {subtitle_files[0]}")
            return subtitle_path
        
        print("\nAvailable subtitle files:")
        for i, f in enumerate(subtitle_files, 1):
            print(f"{i}. {f}")
        choice = int(input("\nSelect subtitle file number: ")) - 1
        if 0 <= choice < len(subtitle_files):
            subtitle_path = os.path.join(os.path.dirname(movie_path), subtitle_files[choice]).strip('"')
            return subtitle_path
        else:
            print("Invalid selection.")
            return
    else:
        print("No subtitle files found in the folder.")
        return

def add_subtitle_to_video(folder_path, movie_path=None, subtitle_path=None):
    """
    Embeds a subtitle file into a video file using ffprobe and ffmpeg.

    Args:
        movie_path (str, optional): Path to the movie file.
        subtitle_path (str, optional): Path to the subtitle file.
    """

    # --- 1. Get User Input if not provided (Equivalent to Batch's 'if not defined' and 'set /p') ---
    if movie_path is None or subtitle_path is None:
        print("Please enter the file paths.")
        if movie_path is None:
            movie_path = select_movie_folder_from_folder(folder_path)
        if subtitle_path is None:
            subtitle_path = select_subtitle_file_from_folder(movie_path)
        if os.path.isfile(movie_path) and subtitle_path is None:
            subtitle_path = select_subtitle_file_from_folder(movie_path)
        if not os.path.isfile(movie_path):
            print("Invalid movie file path provided.")
            return
        if not os.path.isfile(subtitle_path):
            print("Invalid subtitle file path provided.")
            return

    # --- 2. File Path Processing (Equivalent to Batch's 'for %%F in... do set') ---
    try:
        # Get components of the movie path
        movie_folder = os.path.dirname(movie_path)
        movie_name_ext = os.path.basename(movie_path)
        movie_name, movie_ext = os.path.splitext(movie_name_ext)

        # Construct the output path
        output_movie_path = os.path.join(movie_folder, f"SRT-{movie_name}{movie_ext}")
    except Exception as e:
        print(f"Error processing file paths: {e}")
        return

    print(f"Movie Path: {movie_path}")
    print(f"Subtitle Path: {subtitle_path}")
    print(f"Output Movie Path: {output_movie_path}")
    print(f"Output Movie File Extension: {movie_ext}")
    print()

    # --- 3. Determine Audio Channels (Equivalent to ffprobe call and temp file read) ---
    number_of_audio_channels = 0
    try:
        # ffprobe -i %MoviePath% -show_entries stream=channels -select_streams a:0 -of compact=p=0:nk=1 -v 0
        ffprobe_command = [
            'ffprobe',
            '-i', movie_path,
            '-show_entries', 'stream=channels',
            '-select_streams', 'a:0',
            '-of', 'compact=p=0:nk=1',
            '-v', '0'
        ]
        # Run ffprobe and capture stdout
        result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
        
        # The output is the number of channels or an empty string if no audio stream
        audio_channels_output = result.stdout.strip()
        if audio_channels_output:
            number_of_audio_channels = int(audio_channels_output)

    except subprocess.CalledProcessError as e:
        # ffprobe might fail if the file is not a media file or the streams can't be read
        print(f"Warning: Could not determine audio channels. ffprobe error: {e.stderr.strip()}")
    except ValueError:
        # Handle case where output is not an integer
        print("Warning: ffprobe returned non-numeric audio channel count.")

    print(f"Number of Audio Channels: {number_of_audio_channels}")

    # --- 4. Set Audio Codec Parameter (Equivalent to Batch's 'IF %NumberOfAudioChannels% gtr 2') ---
    audio_codec_param = ['-c:a', 'copy']
    # The batch script's logic for gtr 2 (greater than 2) uses a different approach:
    # IF %NumberOfAudioChannels% gtr 2 ( SET "AudioCodecParam=-map 0 -map 1" )
    # This logic seems to be an attempt to force stream mapping when channels > 2 (e.g., 5.1, 7.1)
    # The Python implementation will follow the original Batch logic:
    if number_of_audio_channels > 2:
        # This maps all streams from the input file (0) and all streams from the subtitle file (1)
        # v = video, a = audio, s = subtitles.
        audio_codec_param = ['-map', '0:v', '-map', '0:a', '-map', '1:s']


    # --- 5. Construct and Execute FFMPEG Command (Equivalent to Batch's 'IF %MovieExt% == ...') ---
    base_ffmpeg_command = [
        'ffmpeg',
        '-i', movie_path,
        '-sub_charenc', 'ISO8859-9',  # Character encoding for subtitles
        '-i', subtitle_path,
        '-c:v', 'copy',              # Video: copy (no re-encoding)
        '-metadata:s:s:2', 'language=eng',  # Set subtitle language to English
        '-metadata:s:s:2', 'title="English"',  # Set subtitle title to English
        *audio_codec_param,          # Audio parameters determined above
        '-y',                         # Overwrite output file if it already exists
        output_movie_path            # Output file path
    ]

    ffmpeg_command = []

    if movie_ext.lower() == '.mp4':
        # -c:s mov_text is the standard for embedding subtitles in an MP4 container
        ffmpeg_command = base_ffmpeg_command
        ffmpeg_command.insert(9, '-c:s')
        ffmpeg_command.insert(10, 'mov_text')
    elif movie_ext.lower() == '.mkv':
        # -c:s srt might be incorrect for embedding; usually, it's 'ass', 'subrip', or 'copy',
        # but following the original Batch file's logic for a direct conversion.
        ffmpeg_command = base_ffmpeg_command
        ffmpeg_command.insert(9, '-c:s')
        ffmpeg_command.insert(10, 'srt')
    else:
        print(f"Warning: File extension {movie_ext} is not explicitly handled by the script (.mp4 or .mkv).")
        return

    # --- 6. Execute FFMPEG ---
    if ffmpeg_command:
        # Print the command (Equivalent to Batch's 'echo ffmpeg...')
        print(f"Executing command: {' '.join(ffmpeg_command)}")
        print()
        
        try:
            # Execute the command
            # The 'check=True' raises a CalledProcessError if the command fails
            subprocess.run(ffmpeg_command, check=True)
            print()
            print(f"The File {movie_name_ext} finished processing. 🎉")
        except subprocess.CalledProcessError as e:
            print(f"\nERROR: FFMPEG failed with return code {e.returncode}")
            # print(f"Error output:\n{e.stderr}")
        except FileNotFoundError:
            print("\nERROR: FFMPEG or FFPROBE command not found.")
            print("Please ensure 'ffmpeg' and 'ffprobe' are installed and accessible in your system's PATH.")

def get_english_pgs_subtitles_streams(movie_path):
    # get video-type substitles streams info using ffprobe and return a list of subtitle stream indexes that are in English
    pgs_codec = 'hdmv_pgs_subtitle'
    languages = get_languages_config()
    ffprobe_command = [
        'ffprobe',
        '-i', movie_path,
        '-show_entries', 'stream=index,codec_name:stream_tags=language',
        '-select_streams', 's',
        '-of', 'json',
        '-v', '0'
    ]
    try:
        result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
        subtitle_streams_info = []
        if result.stdout:
            import json
            ffprobe_output = json.loads(result.stdout)
            for stream in ffprobe_output.get('streams', []):
                codec = stream.get('codec_name')
                language = stream.get('tags', {}).get('language') or stream.get('language')
                index = stream.get('index')
                if language in languages and codec in pgs_codec:
                    subtitle_streams_info.append({'index': index, 'codec': codec, 'language': language})
        return subtitle_streams_info
    except subprocess.CalledProcessError as e:
        print(f"Error running ffprobe: {e.stderr.strip()}")
        return []
    except json.JSONDecodeError:
        print("Error decoding ffprobe output as JSON.")
        return []

def export_english_pgs_subtitles_streams_to_sup_file(movie_path):
    if os.path.isfile(movie_path):
        video_files_in_folder = [movie_path]
    else:
        video_files_in_folder = list_video_files_in_folder(movie_path)
    for movie_file_path in video_files_in_folder:
        subtitle_streams = get_english_pgs_subtitles_streams(movie_file_path)
        if not subtitle_streams:
            print(f"No English PGS subtitle streams found for {movie_file_path}.")
            continue
        # Extract the first English PGS subtitle stream to a .sup file using ffmpeg
        stream_index = subtitle_streams[0]['index']
        output_sup_path = os.path.splitext(movie_file_path)[0] + '_english_pgs_subtitles.sup'
        ffmpeg_command = [
            'ffmpeg',
            '-i', movie_file_path,
            '-map', f'0:s:{stream_index}?',
            '-c:s', 'copy',
            '-y',                         # Overwrite output file if it already exists
            output_sup_path
        ]   
        try:
            subprocess.run(ffmpeg_command, check=True)
            print(f"Extracted English PGS subtitles to {output_sup_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error extracting subtitles with ffmpeg: {e.stderr.strip()}")
        except FileNotFoundError:
            print("\nERROR: FFMPEG command not found.")
            print("Please ensure 'ffmpeg' is installed and accessible in your system's PATH.")

def list_video_files_in_folder(folder_path):
    if not folder_path:
        folder_path = input("Enter the folder path to list video files: ").strip()
    if not os.path.isdir(folder_path):
        print(f"Invalid folder path: {folder_path}")
        return []
    video_extensions = ('.mp4', '.mkv')
    video_files = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            if f.endswith(video_extensions):
                video_files.append(os.path.join(root, f))
    return video_files

if __name__ == "__main__":
    #export_english_pgs_subtitles_streams_to_sup_file(r"E:\Videos\Kill la Kill [1080] - Copy")

    ensure_ffmpeg_installed() # Check if FFMPEG is installed before proceeding
    
    if check_get_default_folder_path_in_config() is None: # If no default folder path is set in config, prompt user to set it
        set_default_folder(None)
    
    set_default_text_codecs_in_config_if_not_exists(skip_input=True) # If no text codecs are set in config, prompt user to set default text codecs
    set_default_languages_in_config_if_not_exists(skip_input=True) # If no languages are set in config, prompt user to set default languages
    
    while True: # Loop to allow user to choose different options until they choose to exit
        print("\n=== Add Subtitles to Movies Script ===")
        print("Select an option:")
        print("1. Process video with subtitles")
        print("2. Export movies in folder and their subtitle status to CSV")
        print("3. Process videos from CSV list")
        print("4. Change default folder path")
        print("5. Get default folder path")
        print("6. Set default text codecs in config")
        print("7. Set default languages in config")
        print("8. Exit")
        choice = input("Enter choice number: ").strip()
        if choice == '1':
            # Check for command line arguments (Equivalent to Batch's '%1' and '%2')
            movie_path_arg = sys.argv[1] if len(sys.argv) > 1 else None
            subtitle_path_arg = sys.argv[2] if len(sys.argv) > 2 else None
            # Run the main function
            add_subtitle_to_video(check_get_default_folder_path_in_config(), movie_path_arg, subtitle_path_arg)
        elif choice == '2':
            export_movies_in_folder_to_csv(check_get_default_folder_path_in_config())
        elif choice == '3':
            process_videos_from_csv_list(check_get_default_folder_path_in_config())
        elif choice == '4':
            set_default_folder(None)
        elif choice == '5':
            default_folder_path = check_get_default_folder_path_in_config()
            if default_folder_path:
                print(f"Current default folder path: {default_folder_path}")
            else:
                print("No default folder path set.")
        elif choice == '6':
            set_default_text_codecs_in_config_if_not_exists()
        elif choice == '7':
            set_default_languages_in_config_if_not_exists()
        elif choice == '8':
            print("Exiting the script. Goodbye!")
            break
        else:
            print("Invalid choice.")
        input("\nPress Enter to continue...")