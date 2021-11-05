@echo off

Set "SrcDir=C:\Nhac"
Set "ExtLst=*.mp3"

Set "i=0"
For /F "Delims=" %%A In ('Where /R "%SrcDir%" %ExtLst%') Do (Set /A i+=1 
        Call Set "$[%%i%%]=%%A")
Set /A rand="(%Random%%%i)+1"
Echo "%rand%"
ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=width %1 >> width.txt
ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=height %1 >> height.txt
FOR /f "tokens=5 delims==_" %%i in (width.txt) do @set width=%%i
FOR /f "tokens=5 delims==_" %%i in (height.txt) do @set height=%%i
echo width=%width%
echo height=%height%
del width.txt && del height.txt
ffmpeg -i %1 -i "%SrcDir%\%rand%.mp3" -vf "[0:v]crop=in_w*0.95:in_h*0.95,scale=%width%:%height%,setpts=1/1.05*PTS" -af "[1:a]atempo=1.05" -map "0:0" -map "1:0" -preset ultrafast -crf 24 -shortest done/%1 -y