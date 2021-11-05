echo chcp 65001 >nul
if not exist converted mkdir converted
if not exist done mkdir done

for %%f in ("inputs/*") do (
  (echo file 'converted/%%f' & echo file 'converted/outtro.mp4') > list.txt
  call core.bat "%%f"
)