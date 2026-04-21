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
    if os.path.isfile(config_file_path):
        with open(config_file_path, 'r') as config_file:
            for line in config_file:
                if line.startswith('default_folder_path='):
                    print(f"Default folder path currently set to: {line.split('=', 1)[1].strip()}")
                    return line.split('=', 1)[1].strip()
                
    if default_folder_path == None:
        selected_folder_path, config_file_path = select_folder_path()

    # Get the directory name from the full path
    config_dir = os.path.dirname(config_file_path)
    # Create the directory if it doesn't exist
    if not os.path.exists(config_dir):
        os.makedirs(config_dir)
    with open(config_file_path, 'w') as config_file:
        config_file.write(f"default_folder_path={selected_folder_path}")
    print(f"Config file created at {config_file_path} with default folder path set to {selected_folder_path}")
    

def check_ffmpeg_installed():
    try:
        subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, check=True)
        subprocess.run(['ffprobe', '-version'], capture_output=True, text=True, check=True)
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
            movie_path = row['MoviePath']
            subtitle_path = row['SubtitlePath']
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

        for movie in movie_files:
            print("  Checking movie:", movie)
            movie_path = os.path.join(folder_path, movie)
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

                    text_codecs = ['subrip', 'ass', 'ssa', 'webvtt', 'mov_text', 'srt']
                    languages = ['eng', 'Inglês', 'English', 'en']
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
                    print(f"Error occurred while checking {movie}: {e}")
            
            for f in os.listdir(folder_path):
                if f.endswith(('.srt')) and os.path.isfile(os.path.join(folder_path, f)):
                    subtitle_file_path = os.path.join(folder_path, f)
                    break
                else:
                    subtitle_file_path = ''

            movies_status.append({
                'folder': folder,
                'movie': movie,
                'MoviePath': movie_path,
                'SubtitlePath': subtitle_file_path,
                'has_english_text_sub': has_english_text_sub,
            })

    csv_path = os.path.join(default_folder_path, 'movies_subtitle_status.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Folder', 'Movie', 'MoviePath', 'SubtitlePath', 'Has English Text Subtitles'])
        for row in movies_status:
            writer.writerow([row['folder'], row['movie'], row['MoviePath'], row['SubtitlePath'], 'Yes' if row['has_english_text_sub'] else 'No'])

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

if __name__ == "__main__":
    ensure_ffmpeg_installed() # Check if FFMPEG is installed before proceeding
    
    if check_get_default_folder_path_in_config() is None: # If no default folder path is set in config, prompt user to set it
        set_default_folder(None)
    
    while True: # Loop to allow user to choose different options until they choose to exit
        print("\n=== Add Subtitles to Movies Script ===")
        print("Select an option:")
        print("1. Process video with subtitles")
        print("2. Export movies in folder and their subtitle status to CSV")
        print("3. Process videos from CSV list")
        print("4. Change default folder path")
        print("5. Get default folder path")
        print("6. Exit")
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
            print("Exiting the script. Goodbye!")
            break
        else:
            print("Invalid choice.")
        input("\nPress Enter to continue...")