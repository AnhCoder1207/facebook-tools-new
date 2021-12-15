import os
import random
import threading
import time
import uuid
from datetime import datetime
import PySimpleGUI as sg
import clipboard
import pymongo
import pyautogui
from bson import ObjectId

from utils import click_to, click_many, check_exist, paste_text, waiting_for, deciscion,\
    get_title, scheduler_table, logger, via_shared, video_shared, group_joined
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True
pyautogui.LOG_SCREENSHOTS = False

groups = [
    "https://www.facebook.com/groups/312177843254758/",
    "https://www.facebook.com/groups/274687116922393/",
    "https://www.facebook.com/groups/2136378319728934/",
    "https://www.facebook.com/groups/725646077993653/",
    "https://www.facebook.com/groups/680120385933768/",
    "https://www.facebook.com/groups/WeldersGroup/",
    "https://www.facebook.com/groups/soldadura.estruturas.metalicas/",
    "https://www.facebook.com/groups/1218881038314391/",
    "https://www.facebook.com/groups/384520012952678/",
    "https://www.facebook.com/groups/320331992020107/",
    "https://www.facebook.com/groups/117686506236993/",
    "https://www.facebook.com/groups/561140977665034/",
    "https://www.facebook.com/groups/ayadsater/",
    "https://www.facebook.com/groups/1971605999749160/",
    "https://www.facebook.com/groups/20974732671980479"
]


def show_desktop():
    show_desktop_btn = check_exist("show_desktop_btn.PNG")
    if show_desktop_btn:
        pyautogui.click(show_desktop_btn, button="RIGHT")
        click_to("show_desktop.PNG", waiting_time=10)
    else:
        pyautogui.hotkey("windows", "d")
    time.sleep(1)
    pyautogui.moveTo(1027, 549)


def join_group(via_name):
    if not os.path.isfile("join_group.txt"):
        return False

    via_data = group_joined.find_one({"via_name": via_name})
    if via_data is None:
        groups_joined = []
        via_data = {"_id": str(ObjectId()), "via_name": via_name, "groups_joined": groups_joined}
        group_joined.insert_one(via_data)
    else:
        groups_joined = via_data['groups_joined']

    number_join = 0
    all_groups = []
    with open("join_group.txt", encoding="utf-8") as group_file:
        for line in group_file.readlines():
            if line.strip() == '':
                continue

            splitter = line.strip().split(',')
            if len(splitter) != 2:
                continue

            group_href, _ = splitter
            group_href = group_href.strip()
            all_groups.append(group_href)
    for group_href in random.sample(all_groups, k=len(all_groups)):
        if group_href not in groups_joined:
            access_group(group_href)

            buttons = ["checkpoint_1.PNG",
                       "checkpoint_2.PNG", "cookies_failed.PNG", "disabled.PNG",
                       "login_btn.PNG", "site_can_reach.PNG", 'light_logo.PNG', 'dark_logo.PNG']
            ret = deciscion(buttons, waiting_time=10)
            if ret:
                btn_x, btn_y, btn_index = ret
                if btn_index not in [6, 7]:
                    return False

            if check_exist("not_available.PNG"):
                groups_joined.append(group_href)
                group_joined.update_one({"via_name": via_name},
                                        {"$set": {"groups_joined": groups_joined}})
                continue

            buttons = ["joined.PNG", "join_group.PNG", "join_group_1.PNG",
                       "join_group_2.PNG", "join_group_3.PNG", "join_group_4.PNG",
                       "join_group_5.PNG"]
            decision = deciscion(buttons, waiting_time=10)
            if decision:
                x, y, btn_idx = decision
                if btn_idx == 0:
                    groups_joined.append(group_href)
                    group_joined.update_one({"via_name": via_name},
                                            {"$set": {"groups_joined": groups_joined}})
                else:
                    pyautogui.click(x, y)
                    buttons = ["joined.PNG", "answer_question.PNG", "how_to_join_group.PNG", "requests_gr.PNG"]
                    decision = deciscion(buttons, waiting_time=20)
                    if decision:
                        x, y, btn_idx = decision
                        if btn_idx == 0:
                            # joined
                            groups_joined.append(group_href)
                            group_joined.update_one({"via_name": via_name},
                                                    {"$set": {"groups_joined": groups_joined}})
                        elif btn_idx == 1 or btn_idx == 3:
                            pyautogui.moveTo(x, y)
                            write_an_answer = waiting_for("write_an_answer.PNG", waiting_time=10)
                            while write_an_answer:
                                pyautogui.click(write_an_answer)
                                paste_text("Yes. I'm agree")
                                pyautogui.scroll(-300)
                                write_an_answer = check_exist("write_an_answer.PNG")
                                time.sleep(1)
                            check_box_group = check_exist("check_box_group.PNG")
                            waiting_time = 0
                            while check_box_group and waiting_time < 5:
                                waiting_time += 1
                                pyautogui.click(check_box_group)
                                pyautogui.scroll(-300)
                                check_box_group = check_exist("check_box_group.PNG")
                                time.sleep(1)
                                if check_exist("submit_join.PNG"):
                                    break

                            click_many("check.PNG", duration=0.5)
                            #click_many("agree.PNG")
                            time.sleep(1)
                            submit_status = click_to("submit_join.PNG", waiting_time=10)
                            if submit_status:
                                # joined
                                groups_joined.append(group_href)

                                group_joined.update_one({"via_name": via_name},
                                                        {"$set": {"groups_joined": groups_joined}})
                        else:
                            click_to("join_group_6.PNG", waiting_time=10)
                            groups_joined.append(group_href)

                            group_joined.update_one({"via_name": via_name},
                                                    {"$set": {"groups_joined": groups_joined}})
            number_join += 1
            if number_join > 3:
                return True
    return True


def access_video(video_id):
    # if video_id:
    #     waiting_for("dark_logo.PNG", waiting_time=20)
    reload_bar = waiting_for("reload_bar.PNG")
    # time.sleep(0.5)
    # if waiting_for("proxy_require.PNG", waiting_time=10):
    #     paste_text("huyduc399")
    #     pyautogui.press("tab")
    #     paste_text("3b4i7mMN")
    #     click_to("proxy_signin.PNG", waiting_time=5)
    if reload_bar:
        bar_x, bar_y = reload_bar
        bar_y += 0
        pyautogui.click(bar_x + 250, bar_y)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        if video_id:
            paste_text(f"fb.com/{video_id}")
        else:
            paste_text(f"fb.com")
        pyautogui.hotkey('enter')
        return True
    return False


def access_group(group_id):
    # if video_id:
    #     waiting_for("dark_logo.PNG", waiting_time=20)
    reload_bar = waiting_for("reload_bar.PNG")
    if reload_bar:
        bar_x, bar_y = reload_bar
        bar_y += 0
        pyautogui.click(bar_x + 100, bar_y)
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('backspace')
        paste_text(group_id)
        pyautogui.hotkey('enter')
        time.sleep(2)
        waiting_for("reload_bar.PNG")
        return True
    return False


def show_full_screen():
    print("Show full screen")
    # not in maximize mod
    new_tab = check_exist("new tab_btn.PNG", region=(0, 33, 1900, 1000))
    if new_tab:
        pyautogui.click(new_tab, button="right")
        time.sleep(0.5)
        click_to("maxsimize.PNG", waiting_time=15)
        return
    full_screen = check_exist("fullscreen.PNG", region=(0, 33, 1900, 1000))
    if full_screen:
        pyautogui.click(full_screen)
        return

    pyautogui.hotkey('atl', 'space')
    time.sleep(1)
    pyautogui.press('x')


def auto_share(table_data, current_index, window, stop, enable_join_group, join_group_only_enable):
    shared_group_name = []
    time.sleep(5)
    logger.debug("start share")
    show_desktop()
    browsers = pyautogui.locateAllOnScreen(f"btn/coccoc.PNG", confidence=0.95)
    for browser in browsers:
        st = time.time()
        scheduler = scheduler_table.find({"shared": False}).sort("create_date", pymongo.ASCENDING)
        scheduler = list(scheduler)
        if len(scheduler) > 0 or join_group_only_enable:
            via_name = ""
            browserExe = "chrome.exe"
            os.system("taskkill /f /im " + browserExe)

            if waiting_for("coccoc.PNG", waiting_time=10, confidence=0.9, region=browser) is None:
                pyautogui.click(1027, 549)
                show_desktop()

            # if not check_exist("coccoc.PNG"):
            #     logger.info("Not found coc coc")
            #     show_desktop()
            for _ in range(10):
                pyautogui.click(1027, 549)
                # pyautogui.press('f5')
                # time.sleep(1)
                # pyautogui.moveTo(browser, duration=1)
                # click_to("recycle.PNG", waiting_time=10)
                # time.sleep(0.2)
                click_to("coccoc.PNG", confidence=0.9, region=browser)
                time.sleep(0.2)
                logger.info(f"click to: {browser}")
                pyautogui.press("f2")
                time.sleep(0.2)
                pyautogui.hotkey('ctrl', 'c')
                # time.sleep(0.2)
                # pyautogui.press('esc')
                time.sleep(0.2)
                via_name = clipboard.paste().strip()
                logger.info(f"via name: {via_name}")
                if "Chrome" in via_name:
                    # shared_via.append(via_name)
                    pyautogui.click(browser)
                    time.sleep(0.2)
                    pyautogui.press('enter')
                    time.sleep(1)

                    if not check_exist("reload_bar.PNG", region=(74, 41, 30, 30)):
                        # not in maximize mod
                        show_full_screen()

                    if waiting_for("reload_bar.PNG", waiting_time=10):
                        break

            # time.sleep(2)
            if check_exist("reload_bar.PNG"):
                if via_name == "fb.com" or via_name == "" or "Chrome" not in via_name:
                    pyautogui.hotkey('ctrl', 'f4')
                    continue

                # check via is shared enough on this day
                now = datetime.now().strftime("%B %d, %Y")
                via_history = via_shared.find_one({"date": now})
                if via_history:
                    via_share_number = via_history.get(via_name, 0)
                    if via_share_number >= 4 and not join_group_only_enable:
                        pyautogui.hotkey('ctrl', 'f4')
                        logger.info(f"via {via_name} da share du 4 video")
                        continue

                # pyautogui.press('enter')
                # click_to("signin.PNG", waiting_time=5)

                pyautogui.moveTo(1027, 549)
                if not check_exist("reload_bar.PNG", region=(74, 41, 30, 30)):
                    # not in maximize mod
                    show_full_screen()

                access_video(None)
                waiting_for("reload_bar.PNG", waiting_time=50)
                buttons = ["checkpoint_1.PNG",
                           "checkpoint_2.PNG", "cookies_failed.PNG", "disabled.PNG",
                           "login_btn.PNG", "site_can_reach.PNG", 'light_logo.PNG', 'dark_logo.PNG']
                ret = deciscion(buttons, waiting_time=15)
                if ret:
                    btn_x, btn_y, btn_index = ret
                    logger.info(f"found button: {buttons[btn_index]}")
                    if btn_index not in [6, 7]:
                        pyautogui.hotkey('ctrl', 'f4')
                        continue

                    if enable_join_group or join_group_only_enable:
                        join_group(via_name)

                    buttons = ["checkpoint_1.PNG",
                               "checkpoint_2.PNG", "cookies_failed.PNG", "disabled.PNG",
                               "login_btn.PNG", "site_can_reach.PNG", 'light_logo.PNG', 'dark_logo.PNG']
                    ret = deciscion(buttons, waiting_time=10)
                    if ret:
                        btn_x, btn_y, btn_index = ret
                        if btn_index not in [6, 7]:
                            pyautogui.hotkey('ctrl', 'f4')
                            continue

                    if join_group_only_enable:
                        pyautogui.hotkey('ctrl', 'f4')
                        continue

                    scheduler = scheduler[0]
                    share_number = scheduler.get("share_number", 0)
                    groups_shared = scheduler.get('groups_shared', [])
                    video_id = scheduler['video_id']
                    logger.debug(f"share video {video_id}")

                    if btn_index == 0:
                        # change theme
                        click_to("light_dropdown.PNG")
                        time.sleep(1)
                        if not check_exist("theme_btn.PNG"):
                            click_to("light_dropdown.PNG")
                        click_to("theme_btn.PNG")
                        time.sleep(1)
                        if not check_exist("confirm_change.PNG"):
                            click_to("theme_btn.PNG")
                        click_to("confirm_change.PNG")
                        click_to('dark_logo.PNG')
                        pyautogui.press('f5')
                        time.sleep(2)

                    waiting_for("reload_bar.PNG")
                    waiting_for("dark_logo.PNG")

                    if not waiting_for("search_title.PNG", waiting_time=10):
                        # change language
                        reload_bar = waiting_for("reload_bar.PNG")
                        if reload_bar:
                            bar_x, bar_y = reload_bar
                            bar_y += 0
                            pyautogui.click(bar_x + 100, bar_y)
                            pyautogui.hotkey('ctrl', 'a')
                            pyautogui.press("backspace")
                            paste_text("https://www.facebook.com/settings?tab=language")
                            pyautogui.hotkey('enter')
                            waiting_for("reload_bar.PNG")
                            for i in range(2):
                                click_to("English.PNG")
                                time.sleep(2)
                                pyautogui.press('f5')
                                waiting_for("reload_bar.PNG")
                                if check_exist("languages_and_regions.PNG"):
                                    break

                    status = access_video(video_id)
                    if status:

                        waiting_for("dark_logo.PNG")
                        waiting_for("reload_bar.PNG")
                        if not check_exist("not_available.PNG"):
                            for _ in range(20):
                                time.sleep(1)
                                playbtn = check_exist("playbtn.PNG", confidence=0.85)
                                if playbtn:
                                    pyautogui.moveTo(playbtn)
                                    pyautogui.click(playbtn)
                                playbtn = check_exist("play_btn_2.PNG", confidence=0.85)
                                if playbtn:
                                    pyautogui.moveTo(playbtn)
                                    pyautogui.click(playbtn)

                                buttons = ['share_btn_1.PNG', 'share_btn.PNG']
                                result = deciscion(buttons, confidence=0.9, waiting_time=1)
                                if not result:
                                    pyautogui.click(1484, 604)
                                    pyautogui.scroll(-100)

                            for _ in range(2):
                                # click share buttons
                                pyautogui.moveTo(1027, 549)
                                buttons = ['share_btn_1.PNG', 'share_btn.PNG']
                                result = deciscion(buttons, confidence=0.9, waiting_time=10)
                                if result:
                                    share_x, share_y, idx = result
                                    pyautogui.click(share_x, share_y)
                                else:
                                    for _ in range(3):
                                        pyautogui.scroll(-300)
                                        time.sleep(1)
                                        buttons = ['share_btn_1.PNG', 'share_btn.PNG']
                                        result = deciscion(buttons, confidence=0.9, waiting_time=10)
                                        if result:
                                            break
                                    if result:
                                        share_x, share_y, idx = result
                                        pyautogui.click(share_x, share_y)
                                    else:
                                        continue

                                # click options or share to a group
                                buttons = ["share_to_group.PNG", "options.PNG"]
                                result = deciscion(buttons, confidence=0.9)
                                if result:
                                    share_x, share_y, idx = result
                                    pyautogui.click(share_x, share_y, interval=1)
                                    if idx == 1:
                                        click_to("share_to_group.PNG", confidence=0.9)
                                else:
                                    continue

                                # check group enable
                                go_enable = scheduler.get("go", True)
                                co_khi_enable = scheduler.get("co_khi", True)
                                xay_dung_enable = scheduler.get("xay_dung", True)
                                options_enable = scheduler.get("options", True)
                                groups_share = []

                                if go_enable:
                                    with open("go.txt", encoding='utf-8') as group_file:
                                        groups_share.extend([x.strip().split(',')[1] for x in group_file.readlines() if x.strip() != '' and ',' in x])
                                if co_khi_enable:
                                    with open("co_khi.txt", encoding='utf-8') as group_file:
                                        groups_share.extend([x.strip().split(',')[1] for x in group_file.readlines() if x.strip() != '' and ',' in x])
                                if xay_dung_enable:
                                    with open("xay_dung.txt", encoding='utf-8') as group_file:
                                        groups_share.extend([x.strip().split(',')[1] for x in group_file.readlines() if x.strip() != '' and ',' in x])
                                if options_enable:
                                    with open("tuy_chon.txt", encoding='utf-8') as group_file:
                                        groups_share.extend([x.strip().split(',')[1] for x in group_file.readlines() if x.strip() != '' and ',' in x])

                                found_group_name = False
                                for group_name in groups_share:
                                    group_name = group_name.strip()
                                    if group_name not in groups_shared:
                                        # shared_group_name.append(group_name)
                                        if shared_group_name.count(group_name) > 3:
                                            # mark group shared
                                            groups_shared.append(group_name)
                                            scheduler_table.update_one({"_id": scheduler['_id']},
                                                                       {"$set": {"groups_shared": groups_shared}})
                                            break

                                        search_for_group = waiting_for("search_for_group.PNG")
                                        if search_for_group:
                                            search_x, search_y = search_for_group
                                            pyautogui.click(search_x+100, search_y)
                                            paste_text(group_name)
                                            if waiting_for("public_group.PNG", waiting_time=10):
                                                logger.info(f"found group name: {group_name}")
                                                groups_shared.append(group_name)
                                                scheduler_table.update_one({"_id": scheduler['_id']},
                                                                           {"$set": {"groups_shared": groups_shared}})
                                                click_to("public_group.PNG")
                                                found_group_name = True
                                                break
                                            else:
                                                pyautogui.hotkey('ctrl', 'a')
                                                pyautogui.press('backspace')
                                                logger.error(f"{via_name} not found group :{group_name}")

                                if found_group_name:
                                    post_btn = waiting_for("post.PNG", confidence=0.8, waiting_time=40)
                                    if post_btn:
                                        title = get_title()
                                        logger.info(title)
                                        paste_text(title)
                                        time.sleep(5)
                                        click_to("post.PNG", confidence=0.8, duration=1, interval=3, waiting_time=10)
                                        # save via shared +1
                                        now = datetime.now().strftime("%B %d, %Y")
                                        via_history = via_shared.find_one({"date": now})
                                        if via_history:
                                            via_share_number = via_history.get(via_name, 0)
                                            via_share_number += 1
                                            via_history[via_name] = via_share_number
                                            via_shared.update_one({"_id": via_history['_id']},
                                                                  {"$set": {via_name: via_share_number}})
                                        else:
                                            new_item = {"_id": str(uuid.uuid4()), "date": now, via_name: 1}
                                            via_shared.insert_one(new_item)
                                        click_to("post_success.PNG", confidence=0.8, waiting_time=10)
                                else:
                                    click_to("close_share_dialog.PNG", waiting_time=10)

                                share_number += 1
                                update_data = {"share_number": share_number}
                                if share_number >= len(groups_share):
                                    update_data['shared'] = True
                                scheduler_table.update_one({"_id": scheduler['_id']}, {"$set": update_data})
                        else:
                            scheduler_table.delete_one({"video_id": video_id})

                # window.write_event_value('-THREAD-', "not done")  # put a message into queue for GUI

                # pyautogui.hotkey('ctrl', 'f4')
                # pyautogui.click(x=1890, y=10)
                # click_to("leave.PNG", confidence=0.9, waiting_time=5)

        et = time.time()
        logger.debug(f"share done time consuming: {round((et - st)/60, 1)}")
        # show_desktop()
    # window.write_event_value('-THREAD-', "done")  # put a message into queue for GUI


def watch_videos():
    logger.info("Start watch video")
    current_hour = datetime.now().hour
    # if current_hour % 2 == 0:
    #     return

    time.sleep(2)
    logger.debug("start share")
    pyautogui.click(1024, 1024)
    pyautogui.hotkey('windows', 'd')
    browsers = pyautogui.locateAllOnScreen(f"btn/coccoc.PNG", confidence=0.95)
    for browser in browsers:
        st = time.time()

        pyautogui.click(browser)
        pyautogui.press('f2')
        pyautogui.hotkey('ctrl', 'c')
        via_name = clipboard.paste()
        logger.info(f"click to: {browser}, via_name {via_name}")
        pyautogui.press('enter')
        pyautogui.press('enter')

        if waiting_for("reload_bar.PNG", waiting_time=15):
            click_to("fullscreen_btn.PNG", waiting_time=5)

        click_to("signin.PNG", waiting_time=10)

        pyautogui.moveTo(1027, 549)
        access_video(None)
        waiting_for("reload_bar.PNG")
        # check dark theme
        buttons = ['light_logo.PNG', 'dark_logo.PNG']
        decistion_result = deciscion(buttons)
        if decistion_result is None:
            pyautogui.hotkey('ctrl', 'f4')
            continue

        btn_x, btn_y, btn_index = decistion_result
        if btn_index == 0:
            # change theme
            click_to("light_dropdown.PNG")
            click_to("theme_btn.PNG")
            click_to("confirm_change.PNG")
            access_video(None)

        waiting_for("dark_logo.PNG")
        waiting_for("reload_bar.PNG")
        if not waiting_for("search_title.PNG", waiting_time=15):
            # change language
            reload_bar = waiting_for("reload_bar.PNG", waiting_time=15)
            if reload_bar:
                bar_x, bar_y = reload_bar
                bar_y += 0
                pyautogui.click(bar_x + 100, bar_y)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
                paste_text("https://www.facebook.com/settings?tab=language")
                pyautogui.hotkey('enter')
                click_to("English.PNG")
                pyautogui.press('f5')
                time.sleep(5)
                waiting_for("dark_logo.PNG")
                access_video(None)

        start_btn = waiting_for("start_btn.PNG", waiting_time=20)
        if start_btn:
            pyautogui.click(start_btn)

            for i in range(60):
                time.sleep(1)
                playbtn = check_exist("playbtn.PNG", confidence=0.85)
                if playbtn:
                    pyautogui.moveTo(playbtn)
                    pyautogui.click(playbtn)
                playbtn = check_exist("play_btn_2.PNG", confidence=0.85)
                if playbtn:
                    pyautogui.moveTo(playbtn)
                    pyautogui.click(playbtn)
            if random.choice([0, 1]):
                click_to("like_btn.PNG", confidence=0.9, interval=1, waiting_time=10)
            click_to("dark_logo.PNG", confidence=0.9, waiting_time=10)
        pyautogui.hotkey('ctrl', 'f4')
        pyautogui.hotkey('windows', 'd')


def start_share(table_data, current_index, window, stop, enable_join_group, join_group_only_enable):
    logger.debug("Start share")
    try:
        auto_share(table_data, current_index, window, stop, enable_join_group, join_group_only_enable)
        logger.debug("Done share")
    except Exception as ex:
        logger.error(ex)
        raise ex


def start_watch():
    logger.debug("Start watch")
    try:
        watch_videos()
        logger.debug("Done watch")
    except Exception as ex:
        logger.error(ex)
        raise ex


def mapping_table(item):
    return [
        item.get('video_id', ''),
        len(item.get('groups_shared', [])),
        item.get('shared', False),
        item.get('go', False),
        item.get('co_khi', False),
        item.get('xay_dung', False),
        item.get('options', False),
    ]


if __name__ == '__main__':
    # time.sleep(2)
    # print(pyautogui.position())

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    headings = ['video_id', 'share group', 'share done', "Gỗ", "Cơ Khí", "Xây Dựng", "Tùy Chọn"]  # the text of the headings
    table_default = scheduler_table.find(
        {
            "shared": False
        },
        {
            "video_id": 1,
            "groups_shared": 1,
            "shared": 1,
            "go": 1,
            "co_khi": 1,
            "xay_dung": 1,
            "options": 1,
        }
    ).sort("create_date", pymongo.ASCENDING)
    table_default = list(map(mapping_table, list(table_default)))
    layout = [[sg.Text('Video ID'), sg.Multiline(size=(30, 5), key="video_id"), sg.Button('Add')],
              [
                  sg.Checkbox(
                      'Gỗ', key='groups.go', enable_events=False, default=True),
                  sg.Checkbox(
                      'Cơ Khí', key='groups.co_khi', enable_events=False, default=True),
                  sg.Checkbox(
                      'Xây Dựng', key='groups.xay_dung', enable_events=False, default=True),
                  sg.Checkbox(
                      'Tùy Chọn', key='groups.options', enable_events=False, default=True),
                  sg.Checkbox(
                      'Join group when sharing video', key='join_group', enable_events=False, default=False),
                  sg.Checkbox(
                      'Join group only', key='join_group_only', enable_events=False, default=False)
              ],
              [
                  sg.Table(values=table_default,
                        headings=headings,
                        display_row_numbers=True,
                        justification='right',
                        auto_size_columns=False,
                        col_widths=[20, 20, 15],
                        vertical_scroll_only=False,
                        num_rows=24, key='table')
              ],
              [
                  sg.Button('Start'),
                  sg.Button('Remove'),
                  sg.Button('Exit'),
                  sg.Button('Kill Chrome')]
              ]

    # Create the Window
    window = sg.Window('Auto Share', layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        print(f'{event} You entered {values}')
        print('event', event)
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            # browserExe = "chrome.exe"
            # os.system("taskkill /f /im " + browserExe)
            break
        elif event == 'Kill Chrome':
            browserExe = "chrome.exe"
            os.system("taskkill /f /im " + browserExe)
        elif event == 'Start':
            browserExe = "chrome.exe"
            os.system("taskkill /f /im " + browserExe)
            window.Element('Start').Update(text="Sharing")
            stop_threads = False
            current_index = 0
            if len(values['table']) > 0:
                current_index = values['table'][0]
            table_data = window.Element('table').Get()
            thread = threading.Thread(target=start_share,
                                      args=(table_data, current_index, window,
                                            lambda: stop_threads, values.get("join_group", False),
                                            values.get("join_group_only", False)),
                                      daemon=True)
            thread.start()
        elif event == 'Remove':
            removed = values['table']
            table_data = window.Element('table').Get()
            for item in reversed(removed):
                video_id = table_data[item][0]
                print(video_id)
                results = scheduler_table.delete_one({"video_id": str(video_id.strip())})
                table_data.pop(item)
            window.Element('table').Update(values=table_data)
        elif event == '-THREAD-':
            table_default = scheduler_table.find({"shared": False, "share_number": {"$lt": 30}},
                                                 {
                                                     "video_id": 1,
                                                     "groups_shared": 1,
                                                     "shared": 1,
                                                     "go": 1,
                                                     "co_khi": 1,
                                                     "xay_dung": 1,
                                                     "options": 1
                                                 })
            table_default = list(map(mapping_table, list(table_default)))
            window.Element('table').Update(values=table_default)
        elif event == 'Add':
            video_ids = str(values['video_id']).strip().split('\n')
            for video_id in video_ids:
                if video_id != "":
                    exist_scheduler = scheduler_table.delete_one({"video_id": video_id})
                    # if exist_scheduler:
                    #     scheduler_table.update_one({"_id": exist_scheduler['_id']},
                    #                                {"$set": {"shared": False, "share_number": 30, "title": text_seo}})
                    #     sg.Popup('Them that bai, video da co', keep_on_top=True)
                    # else:
                    new_scheduler = {
                        "_id": str(uuid.uuid4()),
                        "video_id": video_id,
                        "scheduler_time": datetime.now().timestamp(),
                        "create_date": datetime.now().timestamp(),
                        "shared": False,
                        "share_number": 0,
                        "go": values.get("groups.go", False),
                        "co_khi": values.get("groups.co_khi", False),
                        "xay_dung": values.get("groups.xay_dung", False),
                        "options": values.get("groups.options", False)
                    }

                    result = scheduler_table.insert_one(new_scheduler)
            table_default = scheduler_table.find(
                {
                    "shared": False
                },
                {
                    "video_id": 1,
                    "groups_shared": 1,
                    "shared": 1,
                    "go": 1,
                    "co_khi": 1,
                    "xay_dung": 1,
                    "options": 1,
                }
            ).sort("create_date", pymongo.ASCENDING)
            table_default = list(map(mapping_table, list(table_default)))
            window.Element('table').Update(values=table_default)
            sg.Popup('Them thanh cong', keep_on_top=True)
            # else:
            #     sg.Popup('Them that bai', keep_on_top=True)
    window.close()
