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
from models import via_share, scheduler_video, connection, joining_group
from helper import ChromeHelper
from utils import click_to, click_many, check_exist, paste_text, waiting_for, deciscion,\
    get_title, scheduler_table, logger, via_shared, video_shared, group_joined, get_all_titles
import sqlalchemy as db
pyautogui.PAUSE = 0.1
pyautogui.FAILSAFE = True
pyautogui.LOG_SCREENSHOTS = False


def show_desktop():
    show_desktop_btn = check_exist("show_desktop_btn.PNG")
    if show_desktop_btn:
        pyautogui.click(show_desktop_btn, button="RIGHT")
        click_to("show_desktop.PNG", waiting_time=10)
    else:
        pyautogui.hotkey("windows", "d")
    time.sleep(1)
    pyautogui.moveTo(1027, 549)


def join_one_gr(group_href):
    pyautogui.hotkey('ctrl', 't')
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
        return

    buttons = ["joined.PNG", "join_group.PNG", "join_group_1.PNG",
               "join_group_2.PNG", "join_group_3.PNG", "join_group_4.PNG",
               "join_group_5.PNG"]
    decision = deciscion(buttons, waiting_time=10)
    if decision:
        x, y, btn_idx = decision
        if btn_idx != 0:
            pyautogui.click(x, y)
            buttons = ["joined.PNG", "answer_question.PNG", "how_to_join_group.PNG", "requests_gr.PNG", 'join_anw.PNG']
            decision = deciscion(buttons, waiting_time=20)
            if decision:
                x, y, btn_idx = decision
                if btn_idx == 1 or btn_idx == 3:
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
                    time.sleep(1)
                    click_to("submit_join.PNG", waiting_time=10)
                elif btn_idx == 4:
                    pyautogui.click(x, y)
                else:
                    click_to("join_group_6.PNG", waiting_time=10)
    pyautogui.hotkey('ctrl', 'w')


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
            if group_href not in groups_joined:
                all_groups.append(group_href)

    for group_href in random.sample(all_groups, k=len(all_groups)):
        if group_href not in groups_joined and number_join < 5:
            access_group(group_href)
            number_join += 1
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
                    buttons = ["joined.PNG", "answer_question.PNG", "how_to_join_group.PNG", "requests_gr.PNG", 'join_anw.PNG']
                    decision = deciscion(buttons, waiting_time=10)
                    if decision:
                        x, y, btn_idx = decision
                        groups_joined.append(group_href)
                        group_joined.update_one({"via_name": via_name},
                                                {"$set": {"groups_joined": groups_joined}})
                        if btn_idx == 1 or btn_idx == 3:
                            pyautogui.moveTo(x, y)
                            write_an_answer = waiting_for("write_an_answer.PNG", waiting_time=10)
                            while write_an_answer:
                                pyautogui.click(write_an_answer)
                                paste_text("Yes. I'm agree")
                                pyautogui.scroll(-200)
                                write_an_answer = check_exist("write_an_answer.PNG")
                                time.sleep(1)
                            check_box_group = check_exist("check_box_group.PNG")
                            waiting_time = 0
                            while check_box_group and waiting_time < 5:
                                waiting_time += 1
                                pyautogui.click(check_box_group)
                                pyautogui.scroll(-200)
                                check_box_group = check_exist("check_box_group.PNG")
                                time.sleep(1)
                                if check_exist("submit_join.PNG"):
                                    break

                            click_many("check.PNG", duration=0.5)
                            # click_many("agree.PNG")
                            time.sleep(1)
                            submit_status = click_to("submit_join.PNG", waiting_time=10)
                        elif btn_idx == 4:
                            pyautogui.click(x, y)
                        else:
                            click_to("join_group_6.PNG", waiting_time=10)


    return True


def access_video(video_id):
    reload_bar = waiting_for("reload_bar.PNG")
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


def auto_share(table_data, current_index, window, stop, enable_join_group, join_group_only_enable, force_to_share):
    # query via live
    st = time.time()

    while True:
        scheduler = scheduler_table.find({"shared": False}).sort("create_date", pymongo.ASCENDING)
        scheduler = list(scheduler)
        if len(scheduler) == 0 and not join_group_only_enable:
            return

        results = connection.execute(db.select([via_share]).where(db.and_(
            db.or_(via_share.columns.status == 'sharing', via_share.columns.status == 'live',),
            via_share.columns.share_number < 4
        ))).fetchall()
        if len(results) == 0:
            return True

        result = random.choice(results)
        current_date = str(datetime.date(datetime.now()))
        via_data = dict(zip(result.keys(), result))

        share_date = via_data.get("date")
        fb_id = via_data.get("fb_id")
        password = via_data.get("password")
        mfa = via_data.get("mfa")
        proxy_data = via_data.get("proxy")
        via_share_number = via_data.get("share_number")

        if share_date != current_date:
            query = db.update(via_share).values(date=current_date, share_number=0).where(via_share.columns.fb_id == fb_id)
            connection.execute(query)

        # mark via running
        #query = db.update(via_share).values(status='sharing').where(via_share.columns.fb_id == fb_id)
        #connection.execute(query)
        # start sharing
        chrome_worker = ChromeHelper(fb_id, password, mfa, proxy_data)

        via_name = ""
        access_video(None)
        waiting_for("reload_bar.PNG", waiting_time=50)
        buttons = ['accept_1.PNG', 'accept_2.PNG']
        ret = deciscion(buttons, waiting_time=5)
        if ret:
            btn_x, btn_y, btn_index = ret
            pyautogui.click(btn_x, btn_y)

        buttons = ["checkpoint_1.PNG",
                   "checkpoint_2.PNG", "cookies_failed.PNG", "disabled.PNG",
                   "login_btn.PNG", "site_can_reach.PNG", 'home_light.PNG', 'home_dark.PNG', "disabled_1.PNG", "disabled_2.PNG"]
        ret = deciscion(buttons, waiting_time=10)
        if ret:
            btn_x, btn_y, btn_index = ret
            logger.info(f"found button: {buttons[btn_index]}")
            if btn_index not in [6, 7]:
                query = db.update(via_share).values(status='checkpoint').where(via_share.columns.fb_id == fb_id)
                connection.execute(query)
                chrome_worker.driver.close()
                continue

            if btn_index == 5:
                query = db.update(via_share).values(status='die proxy').where(via_share.columns.fb_id == fb_id)
                connection.execute(query)
                chrome_worker.driver.close()
                continue

            buttons = ["checkpoint_1.PNG",
                       "checkpoint_2.PNG", "cookies_failed.PNG", "disabled.PNG",
                       "login_btn.PNG", "site_can_reach.PNG", 'light_logo.PNG', 'dark_logo.PNG']
            ret = deciscion(buttons, waiting_time=10)
            if ret:
                btn_x, btn_y, btn_index = ret
                if btn_index not in [6, 7]:
                    query = db.update(via_share).values(status='checkpoint').where(via_share.columns.fb_id == fb_id)
                    connection.execute(query)
                    chrome_worker.driver.close()
                    continue

            scheduler = scheduler[0] if len(scheduler) != 0 else dict()
            share_number = scheduler.get("share_number", 0)
            groups_shared = scheduler.get('groups_shared', [])
            title_shared = scheduler.get('title_shared', [])
            video_id = scheduler.get('video_id', '')
            logger.debug(f"share video {video_id}")

            if btn_index == 6:
                # change theme
                click_to("light_dropdown.PNG", confidence=0.9)
                time.sleep(1)
                if not check_exist("theme_btn.PNG", confidence=0.9):
                    click_to("light_dropdown.PNG", confidence=0.9)
                click_to("theme_btn.PNG", confidence=0.9)
                time.sleep(1)
                if not check_exist("confirm_change.PNG", confidence=0.9):
                    click_to("theme_btn.PNG", confidence=0.9)
                click_to("confirm_change.PNG", confidence=0.9)
                click_to('dark_logo.PNG', confidence=0.9)
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
                    for i in range(10):
                        pyautogui.scroll(-300)
                        click_to("English.PNG")
                        time.sleep(2)
                        pyautogui.press('f5')
                        waiting_for("reload_bar.PNG")
                        if check_exist("search_title.PNG"):
                            break

            if enable_join_group or join_group_only_enable:
                join_group(fb_id)

            if join_group_only_enable:
                chrome_worker.driver.close()
                continue

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
                        found_share_btn = False
                        result = deciscion(buttons, confidence=0.9)
                        if result:
                            share_x, share_y, idx = result
                            pyautogui.click(share_x, share_y, interval=1)
                            if idx == 1:
                                found_share_btn = click_to("share_to_group.PNG", confidence=0.9)

                        if not found_share_btn:
                            break

                        # check group enable
                        go_enable = scheduler.get("go", True)
                        co_khi_enable = scheduler.get("co_khi", True)
                        xay_dung_enable = scheduler.get("xay_dung", True)
                        options_enable = scheduler.get("options", True)
                        groups_share = []

                        if go_enable:
                            with open("go.txt", encoding='utf-8') as group_file:
                                groups_share.extend([x.strip() for x in group_file.readlines() if x.strip() != '' and ',' in x])
                        if co_khi_enable:
                            with open("co_khi.txt", encoding='utf-8') as group_file:
                                groups_share.extend([x.strip() for x in group_file.readlines() if x.strip() != '' and ',' in x])
                        if xay_dung_enable:
                            with open("xay_dung.txt", encoding='utf-8') as group_file:
                                groups_share.extend([x.strip() for x in group_file.readlines() if x.strip() != '' and ',' in x])
                        if options_enable:
                            with open("tuy_chon.txt", encoding='utf-8') as group_file:
                                groups_share.extend([x.strip() for x in group_file.readlines() if x.strip() != '' and ',' in x])

                        via_data = group_joined.find_one({"via_name": fb_id})
                        groups_joined = via_data.get("groups_joined", [])
                        found_group_name = False
                        for group_share in groups_share:
                            split_data = group_share.split(',')

                            if len(split_data) == 0:
                                continue

                            group_hef = split_data[0].strip()
                            group_name = ",".join(split_data[1:]).strip()

                            if group_hef not in groups_joined:
                                continue

                            # join_one_gr(group_hef)
                            if group_name not in groups_shared:
                                search_for_group = waiting_for("search_for_group.PNG")
                                if search_for_group:
                                    search_x, search_y = search_for_group
                                    pyautogui.click(search_x+100, search_y)
                                    paste_text(group_name)
                                    buttons = ['not_found_group.PNG', "public_group.PNG"]
                                    ret = deciscion(buttons, waiting_time=10)
                                    if ret:
                                        _, _, ret_idx = ret
                                        if ret_idx == 1:
                                            logger.info(f"found group name: {group_name}")
                                            groups_shared.append(group_name)
                                            scheduler_table.update_one({"_id": scheduler['_id']},
                                                                       {"$set": {"groups_shared": groups_shared}})
                                            click_to("public_group.PNG")
                                            found_group_name = True
                                            break
                                        if ret_idx == 0:
                                            groups_share.remove(group_share)
                                            logger.error(f"{via_name} not found group :{group_name}")
                                            # join_one_gr(group_hef)
                                            pyautogui.click(search_x + 100, search_y)
                                            pyautogui.hotkey('ctrl', 'a')
                                            pyautogui.press('backspace')
                                            # logger.info("Join group success")
                                            # break

                        if found_group_name:
                            post_btn = waiting_for("post.PNG", confidence=0.8, waiting_time=40)
                            if post_btn:
                                all_titles = get_all_titles()
                                title = ""
                                for idx, title in enumerate(all_titles):
                                    if idx == len(all_titles) - 1:
                                        title_shared = []
                                        scheduler_table.update_one({"_id": scheduler['_id']},
                                                                   {"$set": {"title_shared": []}})
                                    if title not in title_shared:
                                        title_shared.append(title)
                                        scheduler_table.update_one({"_id": scheduler['_id']},
                                                                   {"$set": {"title_shared": title_shared}})
                                        break

                                logger.info(title)
                                paste_text(title)
                                time.sleep(5)
                                click_to("post.PNG", confidence=0.8, duration=1, interval=3, waiting_time=10)
                                # save via shared +1
                                now = datetime.now().strftime("%B %d, %Y")
                                via_share_number += 1
                                query = db.update(via_share).values(status='live',
                                                                    share_number=via_share_number)
                                query = query.where(via_share.columns.fb_id == fb_id)
                                connection.execute(query)
                                click_to("post_success.PNG", confidence=0.8, waiting_time=10)
                                if force_to_share:
                                    share_number += 1
                                    update_data = {"share_number": share_number}
                                    if share_number >= len(groups_share):
                                        update_data['shared'] = True
                                    scheduler_table.update_one({"_id": scheduler['_id']}, {"$set": update_data})
                        else:
                            click_to("close_share_dialog.PNG", waiting_time=10)
                            #pyautogui.press('f5')
                            #waiting_for("reload_bar.PNG")
                        if not force_to_share:
                            share_number += 1
                            update_data = {"share_number": share_number}
                            if share_number >= len(groups_share):
                                update_data['shared'] = True
                            scheduler_table.update_one({"_id": scheduler['_id']}, {"$set": update_data})
                else:
                    scheduler_table.delete_one({"video_id": video_id})

            window.write_event_value('-THREAD-', "not done")  # put a message into queue for GUI
        chrome_worker.driver.close()

    et = time.time()
    logger.debug(f"share done time consuming: {round((et - st)/60, 1)}")
    # show_desktop()
    window.write_event_value('-THREAD-', "done")  # put a message into queue for GUI


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


def start_share(table_data, current_index, window, stop, enable_join_group, join_group_only_enable, force_to_share):
    logger.debug("Start share")
    try:
        auto_share(table_data, current_index, window, stop, enable_join_group, join_group_only_enable, force_to_share)
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
                      'Join group only', key='join_group_only', enable_events=False, default=False),
                  sg.Checkbox(
                      'Ignore group if not found', key='force_to_share', enable_events=False, default=False)
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
            # browserExe = "chrome.exe"
            # os.system("taskkill /f /im " + browserExe)
            window.Element('Start').Update(text="Sharing")
            stop_threads = False
            current_index = 0
            if len(values['table']) > 0:
                current_index = values['table'][0]
            table_data = window.Element('table').Get()
            thread = threading.Thread(target=start_share,
                                      args=(table_data, current_index, window,
                                            lambda: stop_threads, values.get("join_group", False),
                                            values.get("join_group_only", False),
                                            values.get("force_to_share", False)),
                                      daemon=True)
            thread.start()
        elif event == 'Remove':
            removed = values['table']
            table_data = window.Element('table').Get()
            for item in reversed(removed):
                video_id = table_data[item][0]
                print(video_id)
                update_data = {"shared": True}
                scheduler_table.update_one({"video_id": str(video_id.strip())}, {"$set": update_data})
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
                    exist_scheduler = scheduler_table.find_one({"video_id": video_id})
                    if exist_scheduler:
                        scheduler_table.update_one({"_id": exist_scheduler['_id']}, {"$set": {
                            "shared": False,
                            "go": values.get("groups.go", False),
                            "co_khi": values.get("groups.co_khi", False),
                            "xay_dung": values.get("groups.xay_dung", False),
                            "options": values.get("groups.options", False)
                        }})
                        continue

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
