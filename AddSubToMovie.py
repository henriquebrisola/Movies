from importlib.resources import files
import os
import sys
import subprocess
import csv

default_folder_path = "F:\\Videos\\"

def list_movies_in_folder_to_csv(default_folder_path):
    # List folders
    folders = [f for f in os.listdir(default_folder_path)
               if os.path.isdir(os.path.join(default_folder_path, f))
               and not f.startswith('SRT-')]

    folders_movies_subtitle_status = {}
    text_codecs = ['subrip', 'ass', 'ssa', 'webvtt', 'mov_text', 'srt']

    for folder in folders:
        print("Checking folder:", folder)
        folder_path = os.path.join(default_folder_path, folder)
        movie_files = [f for f in os.listdir(folder_path)
                       if os.path.isfile(os.path.join(folder_path, f))
                       and f.endswith(('.mp4', '.mkv'))
                       and not f.startswith('SRT-')]

        has_srt_in_folder = any(f.startswith('SRT-') for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f)))

        movies_status = []
        for movie in movie_files:
            print("  Checking movie:", movie)
            movie_path = os.path.join(folder_path, movie)
            has_english_text_sub = False

            if has_srt_in_folder:
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
                    result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
                    codec = None
                    if result.stdout:
                        for line in result.stdout.splitlines():
                            if line.startswith('codec_name='):
                                codec = line.split('=', 1)[1]
                            elif line.startswith('language=') and codec:
                                lang = line.split('=', 1)[1]
                                if lang == 'eng' and codec in text_codecs:
                                    has_english_text_sub = True
                                    break
                except subprocess.CalledProcessError:
                    # If ffprobe fails, assume no subs
                    has_english_text_sub = False
                except Exception as e:
                    print(f"Error occurred while checking {movie}: {e}")

            movies_status.append({
                'movie': movie,
                'has_english_text_sub': has_english_text_sub
            })

        folders_movies_subtitle_status[folder] = movies_status

    csv_path = os.path.join(default_folder_path, 'movies_subtitle_status.csv')
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Folder', 'Movie', 'Has English Text Subtitles'])
        for folder, movies in folders_movies_subtitle_status.items():
            for item in movies:
                writer.writerow([folder, item['movie'], 'Yes' if item['has_english_text_sub'] else 'No'])

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


def process_video_with_subtitles(movie_path=None, subtitle_path=None):
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
            movie_path = select_movie_folder_from_folder(default_folder_path)
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

    # --- 8. Wait for user input before closing (Equivalent to Batch's 'pause') ---
    input("\nPress Enter to exit...")


if __name__ == "__main__":
    print("Select an option:")
    print("1. Process video with subtitles")
    print("2. List movies in folder and their subtitle status to CSV")
    choice = input("Enter choice (1 or 2): ").strip()
    if choice == '1':
        # Check for command line arguments (Equivalent to Batch's '%1' and '%2')
        movie_path_arg = sys.argv[1] if len(sys.argv) > 1 else None
        subtitle_path_arg = sys.argv[2] if len(sys.argv) > 2 else None
        # Run the main function
        process_video_with_subtitles(movie_path_arg, subtitle_path_arg)
    elif choice == '2':
        list_movies_in_folder_to_csv(default_folder_path)
    else:
        print("Invalid choice.")