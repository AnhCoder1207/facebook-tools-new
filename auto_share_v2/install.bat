@echo off

git pull && pip install -r requirement.txt && pyinstaller --onefile start.py
