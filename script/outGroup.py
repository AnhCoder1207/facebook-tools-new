import os
import time
import pyautogui
from datetime import datetime
import clipboard

from script.utils import logger, click_to, click_many, check_exist, waiting_for, typeing_text, get_title


if __name__ == '__main__':
    time.sleep(2)
    for _ in range(100):
        click_to("da_tham_gia.PNG")
        click_to("roi_khoi_nhom_1.PNG")
        click_to("roi_khoi_nhom.PNG")
        pyautogui.click(989, 540)
        pyautogui.hotkey('ctrl', 'w')
        time.sleep(1)
