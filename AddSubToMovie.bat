@echo off &:: does not print command
if not defined in_subprocess (cmd /k set in_subprocess=y ^& %0 %*) & exit )
set MoviePath=%1
set SubtitlePath=%2

if not [%1]==[] if not [%2]==[] goto skip
	:: checks if positional arguments were provided
	set /p "MoviePath=Enter Movie File Path [ "E:\Videos\" ]: " &:: asks for movie path
	set /p "SubtitlePath=Enter Subtitle File Path [ "E:\Videos\" ]: " &:: asks for subtitle path
:skip

for %%F in (%MoviePath%) do set "MovieName=%%~nxF" &:: gets Movie File Name
for %%F in (%MoviePath%) do set "MovieFolder=%%~dpF" &:: gets Movie Folder
for %%F in (%MoviePath%) do set "MovieExt=%%~xF" &:: gets Movie File Extension
set "OutputMoviePath=%MovieFolder%SRT-%MovieName%"

echo:
::echo Movie Path: %MovieFolder%%MovieName%
::echo Subtitle Path: %SubtitlePath%
::echo Output Movie Path: %OutputMoviePath%
::echo Output Movie File Extension: %MovieExt%

SET "NumberOfAudioChannels=0"
ffprobe -i %MoviePath% -show_entries stream=channels -select_streams a:0 -of compact=p=0:nk=1 -v 0 > temp
set /p NumberOfAudioChannels= < temp
del temp

echo Number of Audio Channels: %NumberOfAudioChannels%
SET "AudioCodecParam=-c:a copy"
IF %NumberOfAudioChannels% gtr 2 (
	SET "AudioCodecParam=-map 0 -map 1"
)

SET "NumberOfSubtitleChannels=0"
ffmpeg -i %MoviePath% -c copy -map 0:s:0 -frames:s 1 -f null - -v 0 -hide_banner > temp
set /p NumberOfAudioChannels= < temp
del temp
echo Number of Subtitle Channels: %NumberOfSubtitleChannels%

echo:

IF %MovieExt% == .mp4 (
	echo ffmpeg -i %MoviePath% -i %SubtitlePath% -c:s mov_text -c:v copy %AudioCodecParam% "%OutputMoviePath%"
	echo:
	ffmpeg -i %MoviePath% -sub_charenc ISO8859-9 -i %SubtitlePath% -c:s mov_text -c:v copy %AudioCodecParam% "%OutputMoviePath%"
)
IF %MovieExt% == .mkv (
	echo ffmpeg -i %MoviePath% -sub_charenc ISO8859-9 -i %SubtitlePath% -c:s srt -c:v copy %AudioCodecParam% "%OutputMoviePath%"
	echo:
	ffmpeg -i %MoviePath% -sub_charenc ISO8859-9 -i %SubtitlePath% -c:s srt -c:v copy %AudioCodecParam% "%OutputMoviePath%"
	::ffmpeg -i %MoviePath% -sub_charenc utf-8 -i %SubtitlePath% -c:s srt -c:v copy %AudioCodecParam% "%OutputMoviePath%"
	echo:
)

echo:
echo The File %MovieName% finished processing.
echo:

pause :: keeps prompt open