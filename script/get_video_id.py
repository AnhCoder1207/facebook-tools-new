import os
import random
import time
import uuid
from datetime import datetime

import pyautogui
import logging
import clipboard
from utils import logger, click_to, click_many, check_exist, waiting_for, scheduler_table

exist_number = 0


def get_videos():
    global exist_number
    uploaded_videos = pyautogui.locateAllOnScreen("btn/da_dang.PNG", confidence=0.8)
    for uploaded_video in uploaded_videos:
        left, top, width, height = uploaded_video
        pyautogui.moveTo(left - 100, top, duration=1)
        time.sleep(1)
        drop_down = waiting_for("drop_down.PNG", region=(left - 100, top, 100, 100))
        if drop_down:
            pyautogui.click(drop_down)
            click_to("copy_video_id.PNG")
            video_id = clipboard.paste()
            try:
                video_id = int(video_id)
                exist_scheduler = scheduler_table.find_one(
                    {
                        "video_id": str(video_id)
                    }
                )
                if exist_scheduler:
                    if exist_number > 10:
                        # stop get ids
                        return False
                    else:
                        exist_number += 1
                    print(f"exist video id: {video_id}")
                elif not exist_scheduler:
                    exist_number = 0
                    new_scheduler = {
                        "_id": str(uuid.uuid4()),
                        "video_id": str(video_id),
                        "scheduler_time": datetime.now().timestamp(),
                        "create_date": datetime.now().timestamp(),
                        "shared": False,
                        "share_number": 2
                    }
                    result = scheduler_table.insert_one(new_scheduler)
                    print(f"new video id: {video_id}")
            except Exception as ex:
                pass
    return True


if __name__ == '__main__':
    pyautogui.click(x=1078, y=193)
    # time.sleep(3)
    waiting_for("da_dang.PNG")
    while True:
        status = get_videos()
        if not status:
            break
        pyautogui.scroll(-500)
        time.sleep(5)
        # pyautogui.scroll(-500)
        # time.sleep(1)
        # pyautogui.scroll(-150)
