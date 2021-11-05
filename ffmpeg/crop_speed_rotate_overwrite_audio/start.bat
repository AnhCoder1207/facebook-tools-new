@echo off

if not exist "done" mkdir ""done" "

for %%f in (*.avi *.flv *.mkv *.mpg *.mp4) do (
	call crop_speed_up_1.13_rotate.bat "%%f"
)