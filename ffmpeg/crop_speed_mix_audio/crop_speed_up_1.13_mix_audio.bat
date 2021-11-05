@echo off

if not exist "done" mkdir ""done" "
if not exist "mix_audio" mkdir ""mix_audio" "

for %%f in (*.avi *.flv *.mkv *.mpg *.mp4) do (
	call mix_audio.bat "%%f"
)