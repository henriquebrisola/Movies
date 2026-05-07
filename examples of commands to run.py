from AddSubToMovie import *
import subprocess

# add_subtitle_to_video(r"E:\Videos\Kill la Kill [1080] - Copy\6\[Cleo]Kill_la_Kill_-_06_(Dual Audio_10bit_BD1080p_x265).mkv", r"E:\Videos\Kill la Kill [1080] - Copy\6\[Cleo]Kill_la_Kill_-_06_(Dual Audio_10bit_BD1080p_x265).mkv")

# for video in list_video_files_in_folder(r"E:\Videos\Kill la Kill [1080] - Copy"):
#     add_subtitle_to_video(video, video)

export_each_english_pgs_subtitles_stream_to_sup_file(r"E:\Videos\Kill la Kill [1080]")

exit()

ffprobe_command = [
    'ffprobe',
    '-i', "E:\\Videos\\Kill la Kill [1080]\\[Cleo]Kill_la_Kill_-_01_(Dual Audio_10bit_BD1080p_x265).mkv",
    '-show_entries', 'stream=index,codec_name:stream_tags=language',
    '-select_streams', 's',
    '-of', 'json',
    '-v', '0'
]
#ffprobe_command='ffprobe -i "E:\\Videos\\Kill la Kill [1080]\\[Cleo]Kill_la_Kill_-_01_(Dual Audio_10bit_BD1080p_x265).mkv" -show_streams -of json'
result = subprocess.run(ffprobe_command, capture_output=True, text=True, check=True)
subtitle_streams_info = []
if result.stdout:
    import json
    ffprobe_output = json.loads(result.stdout)
    for stream in ffprobe_output.get('streams', []):
        codec = stream.get('codec_name')
        language = stream.get('tags', {}).get('language') or stream.get('language')
        index = stream.get('index')
        subtitle_streams_info.append({'index': index, 'codec': codec, 'language': language})

print(subtitle_streams_info)
