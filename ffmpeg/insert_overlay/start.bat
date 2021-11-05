@echo off

if not exist "done" mkdir ""done" "
for %%f in (raw/*.avi raw/*.flv raw/*.mkv raw/*.mpg raw/*.mp4) do (
	call main.bat "%%f"
)