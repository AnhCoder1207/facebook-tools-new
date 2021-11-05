@echo off
set crop=0.93
set speed=1.05
set rotate=4
set width=1280
set heigh=1280

ffmpeg -i %1 -vf "[0:v]rotate=-%rotate%*PI/180,crop=in_w*%crop%:in_h*%crop%,scale=%width%:%height%,setpts=1/%speed%*PTS" -af "[0:a]atempo=%speed%" -preset ultrafast -crf 24 done/%1 -y