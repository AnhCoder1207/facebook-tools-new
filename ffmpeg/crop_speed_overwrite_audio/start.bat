@echo off

if not exist "done" mkdir ""done" "


for %%f in (*.avi *.flv *.mkv *.mpg *.mp4) do (
	call main.bat "%%f"
)