@echo off

if not exist "done" mkdir ""done" "


for %%f in (*.avi *.flv *.mkv *.mpg *.mp4) do (
  ffmpeg -i "%%f" -i "C:\RockTheCity.mp3" -map "0:0" -map "1:0" -preset ultrafast -crf 24 -shortest done/"%%f" -y
)