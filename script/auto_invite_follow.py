import os
import random
import time
import pyautogui
import logging
import clipboard
from utils import logger, click_to, click_many, check_exist, waiting_for, check_exit_program

os.makedirs('uploaded', exist_ok=True)


# def random_interval():
#     return random.uniform(0.5, 2)


# def click_to(btn, confidence=0.8, region=None, waiting_time=1000, interval=None, check_close=True):
#     logger.debug(f"Click to {btn}")
#     start_count = 0
#     while start_count < waiting_time:
#         ret = pyautogui.locateOnScreen(f"btn/{btn}", confidence=confidence, region=region)
#         start_count += 1
#         if ret:
#             interval = random_interval() if interval is None else interval
#             pyautogui.click(ret, interval=interval)
#             break
#         time.sleep(0.2)
#
#
# def click_many(btn, region=None, confidence=0.8, log=True):
#     if log:
#         logger.debug(f"Click many {btn}")
#     elements = pyautogui.locateAllOnScreen(f"btn/{btn}", confidence=confidence, region=region)
#     number_element = len(list(pyautogui.locateAllOnScreen(f"btn/{btn}", confidence=0.85, region=region)))
#     for ret in elements:
#         pyautogui.click(ret, interval=random_interval())
#     return number_element
#
#
# def check_exist(btn, region=None, confidence=0.8):
#     exist = pyautogui.locateOnScreen(f"btn/{btn}", confidence=confidence, region=region)
#     logger.debug(f"Check exist {btn} result {exist}")
#     return exist
#
#
# def waiting_for(btn, region=None, confidence=0.8, waiting_time=1000):
#     logger.debug(f"Waiting for {btn}")
#     start_count = 0
#     while start_count < waiting_time:
#         start_count += 1
#         ret = pyautogui.locateCenterOnScreen(f"btn/{btn}", confidence=confidence, region=region)
#         if ret:
#             x, y = ret
#             return x, y
#         time.sleep(0.2)
#     return None


# def deciscion(btns, region=None, confidence=0.8):
#     while True:
#         for btn_index, btn in enumerate(btns):
#             logger.debug(f"Waiting for {btn}")
#             ret = pyautogui.locateCenterOnScreen(f"btn/{btn}", confidence=confidence, region=region)
#             if ret:
#                 x, y = ret
#                 return x, y, btn_index
#
#
# def typeing_text(inp_text):
#     pyautogui.typewrite(inp_text, interval=0.2)
#
#
# def paste_text(inp_text):
#     clipboard.copy(inp_text)
#     pyautogui.hotkey('ctrl', 'v', interval=0.5)


if __name__ == '__main__':
    number_invited = 0
    while number_invited < 200:
        check_exit_program()
        waiting = 0
        number_invited += click_many("invite.PNG", region=(850, 200, 800, 800))
        pyautogui.moveTo(x=1091, y=573, duration=0.5)
        pyautogui.scroll(-200)
        pyautogui.scroll(-200)
        time.sleep(1)
