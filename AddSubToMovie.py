import os
import sys
import subprocess

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
            movie_path = input('Enter Movie File Path [ "E:\\Videos\\" ]: ')
        if subtitle_path is None:
            subtitle_path = input('Enter Subtitle File Path [ "E:\\Videos\\" ]: ')

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

    # print(f"Movie Path: {movie_path}")
    # print(f"Subtitle Path: {subtitle_path}")
    # print(f"Output Movie Path: {output_movie_path}")
    # print(f"Output Movie File Extension: {movie_ext}")
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
        audio_codec_param = ['-map', '0', '-map', '1']

    # --- 5. Determine Subtitle Channels (The batch script's method is flawed/incomplete) ---
    # The Batch script attempts to count subtitle channels but reuses the 'NumberOfAudioChannels' variable
    # and the ffmpeg command is structured in a way that is unlikely to return a count to stdout.
    # For a direct conversion, we will skip this flawed check, as the main logic doesn't depend on it
    # other than for a printout that is not actually used in the final ffmpeg call.

    # print(f"Number of Subtitle Channels: 0 (Skipped flawed check)")
    print()


    # --- 6. Construct and Execute FFMPEG Command (Equivalent to Batch's 'IF %MovieExt% == ...') ---
    base_ffmpeg_command = [
        'ffmpeg',
        '-i', movie_path,
        '-sub_charenc', 'ISO8859-9',  # Character encoding for subtitles
        '-i', subtitle_path,
        '-c:v', 'copy',              # Video: copy (no re-encoding)
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

    # --- 7. Execute FFMPEG ---
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
    # Check for command line arguments (Equivalent to Batch's '%1' and '%2')
    movie_path_arg = sys.argv[1] if len(sys.argv) > 1 else None
    subtitle_path_arg = sys.argv[2] if len(sys.argv) > 2 else None

    # Run the main function
    process_video_with_subtitles(movie_path_arg, subtitle_path_arg)