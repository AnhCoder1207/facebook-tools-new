@echo off

ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=width inputs/%1 >> width.txt
ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height inputs/%1 >> height.txt
FOR /f "tokens=5 delims==_" %%i in (width.txt) do @set width=%%i
FOR /f "tokens=5 delims==_" %%i in (height.txt) do @set height=%%i
echo width=%width%
echo height=%height%
del width.txt && del height.txt
ffmpeg -i inputs/%1 -f mp4 -c:v copy -crf 24 converted/%1 -y
ffmpeg -i outtro.mp4 -f mp4 -vf scale=%width%:%height% -crf 24 converted/outtro.mp4 -y
ffmpeg -safe 0 -f concat -i list.txt -c copy done/%1 -y