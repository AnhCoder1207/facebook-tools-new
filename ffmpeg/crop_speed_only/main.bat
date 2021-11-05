@echo off
set crop=0.85
set speed=1.05
set rotate=4
set width=1080
set height=1080

for /f "tokens=*" %%a in ('ffprobe -show_format -i %1 ^| find "duration"') do set _duration=%%a
set _duration=%_duration:~9%
for /f "delims=. tokens=1*" %%b in ('echo %_duration%') do set /a "_durS=%%b"
for /f "delims=. tokens=2*" %%c in ('echo %_duration%') do set "_durMS=%%c"
rem following line is seconds to cut
set /a "_durS-=60"
set "_newduration=%_durS%.%_durMS%"
set "_output=%~n1"

ffmpeg -ss 60 -i %1 -t %_newduration% -vf "crop=in_w*%crop%:in_h*%crop%:in_w*((1-%crop%)/2):in_h*(1-%crop%),scale=%width%:%height%,setsar=1:1,setpts=1/%speed%*PTS" -af "[0:a]atempo=%speed%" -preset ultrafast -crf 24 done/%1 -y