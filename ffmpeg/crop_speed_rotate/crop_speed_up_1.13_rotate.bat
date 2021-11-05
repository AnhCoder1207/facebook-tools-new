@echo off
set crop=0.93
set speed=1.05
set rotate=4
ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=width %1 >> width.txt
ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height %1 >> height.txt
FOR /f "tokens=5 delims==_" %%i in (width.txt) do @set width=%%i
FOR /f "tokens=5 delims==_" %%i in (height.txt) do @set height=%%i
echo width=%width%
echo height=%height%
del width.txt && del height.txt
ffmpeg -i %1 -vf "[0:v]rotate=-%rotate%*PI/180,crop=in_w*%crop%:in_h*%crop%,scale=%width%:%height%,setpts=1/%speed%*PTS" -af "[0:a]atempo=%speed%" -preset ultrafast -crf 24 done/%1 -y