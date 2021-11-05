import os
import time
import pyautogui
from datetime import datetime
import clipboard

from utils import logger, click_to, click_many, check_exist, waiting_for, typeing_text, get_title

os.makedirs('uploaded', exist_ok=True)


if __name__ == '__main__':
    dir_path = r"C:\code\facebook-tools\script\upload"
    while True:
        try:
            # default_date = datetime.strptime(datetime.now(), '%d/%m/%Y %H:%M')
            start_date = pyautogui.prompt(f'Nhập thời gian bắt đầu lên lịch. \nChú ý định dạng kiểu: d/m/YYYY H:M')
            # if start_date == "":
            #     start_date = default_date
            date_time_obj = datetime.strptime(start_date, '%d/%m/%Y %H:%M')
            date_time_obj_ts = date_time_obj.timestamp()
            break
        except Exception as ex:
            pyautogui.alert('Lỗi, Kiểm tra lại định dạng của thời gian bắt đầu')

    for filename in os.listdir(dir_path):
        click_to("create_new.png")
        click_to("upload_new_video.png")
        time.sleep(2)
        typeing_text(f"{dir_path}\\{filename}")
        click_to("open.PNG")
        click_to("upload_done.png")
        click_many("close_step.png")

        # paste title
        title = waiting_for("title.png")
        title_x, title_y = title
        pyautogui.click(title_x + 50, title_y)
        description = get_title()
        filename_without_ext = f"{os.path.splitext(filename)[0]}. {description} #Crafting #DIY"
        # fix title
        if 'Views-' in filename_without_ext:
            filename_without_ext = filename_without_ext.split('Views-')[1]

        filename_without_ext = filename_without_ext.replace('+outtro', '')
        typeing_text(filename_without_ext)
        pyautogui.click(title_x + 50, title_y+70)
        typeing_text(filename_without_ext)

        # set language
        click_to("chon_ngon_ngu.PNG")
        waiting_for("chon_ngon_ngu_1.PNG")
        typeing_text("Thai")
        click_to("tieng_thai.PNG")

        # len lich
        click_to("next.png")
        click_to("later.PNG", waiting_time=2)
        click_to("schedule.PNG")
        schedule_x, schedule_y = waiting_for("auto_schedule.png")

        date_obj = datetime.fromtimestamp(date_time_obj_ts)
        # change date
        pyautogui.click(schedule_x + 30, schedule_y, interval=0.5)
        date = date_obj.strftime("%d/%m/%Y")
        logger.info(f"current date {date}")
        pyautogui.typewrite(date, interval=0.2)

        # change hour
        pyautogui.click(schedule_x + 120, schedule_y, interval=0.5)
        hour = date_obj.strftime("%H")
        logger.info(f"current hour {hour}")
        pyautogui.typewrite(hour, interval=0.2)

        # change time
        pyautogui.click(schedule_x + 130, schedule_y, interval=0.5)
        minute = date_obj.strftime("%M")
        logger.info(f"current minute {minute}")
        pyautogui.typewrite(minute, interval=0.2)
        click_to("finish.png")
        waiting_for("done.png")
        click_to("close_success.PNG", region=(1000, 200, 300, 400))
        date_time_obj_ts += 7200
        move_to_uploaded = f"C:\\code\\facebook-tools\\script\\uploaded\\{filename}"
        if not os.path.isfile(move_to_uploaded):
            os.rename(f"{dir_path}\\{filename}", move_to_uploaded)
