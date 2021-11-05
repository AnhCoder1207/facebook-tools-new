@echo off
set crop=0.89
set speed=1.10
set rotate=4
set width=1280
set height=1280
Set "SrcDir=C:\Nhac"
Set "ExtLst=*.mp3"

Set "i=0"
For /F "Delims=" %%A In ('Where /R "%SrcDir%" %ExtLst%') Do (Set /A i+=1 
        Call Set "$[%%i%%]=%%A")
Set /A rand="(%Random%%%i)+1"
Echo "%rand%"

ffmpeg -i raw/%1 -i "C:\overlay.mp4" -i "%SrcDir%\%rand%.mp3" -filter_complex "[0]rotate=%rotate%*PI/180[a];[a]crop=in_w*%crop%:in_h*%crop%[b];[b]setpts=1/%speed%*PTS[c];[c]scale=%width%:%height%,setsar=1:1[d];[1]scale=160:-1[e];[d][e]overlay=main_w-(overlay_w+10):main_h-(overlay_h+10):shortest=1[f]" -map "[f]" -map 2:a -preset ultrafast -crf 24 -shortest done/%1 -y
