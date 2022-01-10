import json
import shutil
import os
import random
import time
from datetime import datetime
import PySimpleGUI as sg
import sqlalchemy as db
from bson import ObjectId
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

from helper import ChromeHelper
from utils import get_group_joining_data, logger, via_share, joining_group, scheduler_table, group_auto_approved
from config_btn import *


def start_join_group(stop_joining):
    while not stop_joining():
        try:
            chrome_worker = ChromeHelper()  # init worker
            thread_join_group(chrome_worker)
        except Exception as ex:
            raise ex
            # logger.error(f"thread_join_group error {ex}")
            # pass

        try:
            chrome_worker.driver.close()
        except Exception as ex:
            pass


def thread_join_group(chrome_worker):
    actions = ActionChains(chrome_worker.driver)  # create actions chain for chrome drive

    results = via_share.find({"status": "live", "share_number": {"$lte": 4}})
    results = list(results)
    if len(results) == 0:
        time.sleep(10)
        return

    via_data = random.choice(results)  # get random via
    fb_id = via_data.get("fb_id")
    current_date = str(datetime.date(datetime.now()))

    join_history = via_data.get("join_history", {})
    join_in_day = join_history.get(current_date, None)
    if join_in_day is None:
        join_in_day = 0
        via_share.update_one({"fb_id": fb_id}, {"$set": {"join_history": {current_date: join_in_day}}})

    if join_in_day is not None and join_in_day >= 4:
        return

    logger.info(f"Start join group for via {fb_id}")
    via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'join group'}})
    password = via_data.get("password")
    mfa = via_data.get("mfa")
    proxy_data = via_data.get("proxy")
    group_joined = via_data.get("group_joined")
    chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
    join_group = get_group_joining_data("group_join_auto").split('\n')
    groups_share_fixed = list(set(join_group) - set(group_joined))

    try:
        chrome_worker.driver.get("https://facebook.com")
    except Exception as ex:
        logger.error(f"{fb_id} can not reach internet")
        # via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
        chrome_worker.driver.close()
        return

    # check disable
    is_disable = chrome_worker.waiting_for_selector(disable_1, waiting_time=1)
    if is_disable:
        # query = db.update(via_share).values(status='disable')
        # query = query.where(via_share.columns.fb_id == fb_id)
        # connection.execute(query)
        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'disable'}})
        chrome_worker.driver.close()
        return
    is_locked = chrome_worker.waiting_for_selector(locked_1, waiting_time=1)
    if is_locked:
        # query = db.update(via_share).values(status='checkpoint')
        # query = query.where(via_share.columns.fb_id == fb_id)
        # connection.execute(query)
        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'checkpoint'}})
        chrome_worker.driver.close()
        return

    is_login = chrome_worker.waiting_for_selector("#email", waiting_time=1)
    if is_login:
        try:
            chrome_worker.login()
            chrome_worker.driver.get("https://facebook.com")
        except Exception as ex:
            chrome_worker.driver.close()
            return

    # check theme
    chrome_worker.check_dark_light()

    # check language
    search_facebook = chrome_worker.waiting_for_selector(search_facebook_inp)
    if search_facebook:
        if search_facebook.get_attribute('placeholder') != 'Search Facebook':
            chrome_worker.change_language()
    else:
        chrome_worker.driver.close()
        return

    if random.choice([1, 2, 3, 4]) == 1:
        message_selector = """#mount_0_0_gb > div > div:nth-child(1) > div > div:nth-child(4) > div.ehxjyohh.kr520xx4.poy2od1o.b3onmgus.hv4rvrfc.n7fi1qx3 > div.du4w35lb.l9j0dhe7.byvelhso.rl25f0pe.j83agx80.bp9cbjyn > div:nth-child(3) > span"""
        message_el = chrome_worker.waiting_for_css_selector(message_selector)
        if message_el:
            message_el.click()
    if random.choice([1, 2, 3, 4]) == 1:
        chrome_worker.driver.get("https://www.facebook.com/groups/feed/")
        time.sleep(10)
    if random.choice([1, 2, 3, 4]) == 1:
        chrome_worker.driver.get("https://www.facebook.com/watch/?ref=tab")
        time.sleep(10)

    join_number = 0
    join_button_enabled = True
    for group in random.sample(groups_share_fixed, len(groups_share_fixed)):
        if join_number >= 4:
            break

        splitter = group.split('|')
        if len(splitter) >= 2:
            group_url = splitter[0]
        else:
            continue

        logger.info(f"group_url {group_url}")
        try:
            chrome_worker.driver.get(group_url)
        except Exception as ex:
            continue

        # check errors:
        go_to_newsfeed = chrome_worker.waiting_for_text_by_css(join_group_btn, 'Go to News Feed', waiting_time=5)
        if go_to_newsfeed:
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
            return

        # check joined
        joined_1 = chrome_worker.waiting_for_text_by_css(join_group_btn, 'joined', waiting_time=1)
        invite_2 = chrome_worker.waiting_for_text_by_css(join_group_btn, 'invite', waiting_time=1)

        if joined_1 or invite_2:
            group_joined.append(group)
            via_share.update_one({"fb_id": fb_id}, {"$set": {"group_joined": group_joined}})
            continue

        join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'join group', waiting_time=5)
        if join_group_el:
            if join_group_el.value_of_css_property("color") == 'rgba(255, 255, 255, 0.3)':
                logger.info(f"{fb_id} button join group is not enabled")
                join_button_enabled = False
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": "can not join group"}})
                break
            logger.info("Click join button")
            join_number += 1

            # chrome_worker.driver.execute_script("arguments[0].scrollIntoView();", join_group_el)
            join_group_el.click()  # click join btn
            time.sleep(5)

            # join as page
            try:
                elements = chrome_worker.driver.find_elements(By.CSS_SELECTOR, check_background_color)
                for element in elements:
                    if element.text and element.text.lower().strip() == "join group":
                        if element.value_of_css_property("color") != 'rgba(255, 255, 255, 0.3)':
                            print(element.text)
                            element.click()
            except Exception as ex:
                raise ex

            # join_group_el = chrome_worker.waiting_for_text_by_css(check_background_color, 'join group', waiting_time=5)
            # if join_group_el:
            #     # actions.move_to_element(join_group_el).perform()
            #     join_group_el.click()  # click join btn

            join_group_anw_exist = chrome_worker.waiting_for_text_by_css(join_group_anw, 'Join Group Anyway')
            if join_group_anw_exist:
                join_group_anw_exist.click()

        disagree_with_decision = chrome_worker.waiting_for_text_by_css(join_group_limited, 'disagree with decision',
                                                                       waiting_time=1)
        if disagree_with_decision:
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
            return

        answer_question = chrome_worker.waiting_for_text_by_css(answer_questions_label, 'answer questions',
                                                                waiting_time=10)
        request_participation = chrome_worker.waiting_for_text_by_css(participation_request,
                                                                      'Participation request', waiting_time=1)
        if answer_question or request_participation:
            # chrome_worker.driver.execute_script("window.scrollTo(0, window.scrollY + 200)")
            elements = chrome_worker.driver.find_elements(By.TAG_NAME, "textarea")
            for element in elements:
                if element and element.get_attribute('placeholder') == 'Write an answer...':
                    print("found text area")
                    # actions.move_to_element(element).perform()
                    element.click()
                    element.clear()
                    element.send_keys("I'm agree")
                    time.sleep(1)

            check_box = chrome_worker.waiting_for_text_by_css("div.hpfvmrgz.h676nmdw.buofh1pr.rj1gh0hx > span",
                                                              'I agree to the group rules', waiting_time=10)
            if check_box:
                check_box.click()
            time.sleep(1)

            submit = chrome_worker.waiting_for_text_by_css(submit_btn, 'submit')
            if submit:
                # actions.move_to_element(submit).perform()
                submit.click()
            time.sleep(5)

        join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'joined', waiting_time=5)
        if join_group_el:
            logger.info("found joined_btn")
            group_joined.append(group)
            via_share.update_one({"fb_id": fb_id}, {"$set": {"group_joined": group_joined}})
            join_in_day += 1
            via_share.update_one({"fb_id": fb_id}, {"$set": {"join_history": {current_date: join_in_day}}})
            if group_auto_approved.find_one({"group": group}) is None:
                group_auto_approved.insert_one({"_id": str(ObjectId()), "group": group})
            continue
        join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'invite', waiting_time=1)
        if join_group_el:
            logger.info("found joined_btn")
            group_joined.append(group)
            via_share.update_one({"fb_id": fb_id}, {"$set": {"group_joined": group_joined}})
            join_in_day += 1
            via_share.update_one({"fb_id": fb_id}, {"$set": {"join_history": {current_date: join_in_day}}})
            if group_auto_approved.find_one({"group": group}) is None:
                group_auto_approved.insert_one({"_id": str(ObjectId()), "group": group})
            # query = db.update(via_share).values(group_joined=json.dumps(group_joined))
            # query = query.where(via_share.columns.fb_id == fb_id)
            # connection.execute(query)
    if join_button_enabled:
        # set status live
        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})

    chrome_worker.driver.close()


def start_login_via(main_windows, file_input, login_existed):
    with open(file_input) as via_files:
        for via_idx, via in enumerate(via_files):
            user_data = via.strip().split('|')
            if len(user_data) != 6:
                sg.Popup(
                    f'Via Format khong dung: fb_id|password|mfa|email|email_password|ProxyIP:ProxyPORT:ProxyUsername:ProxyPassword',
                    keep_on_top=True)
                break
            fb_id, password, mfa, email, email_password, proxy_data = user_data
            mfa = mfa.replace(" ", '')
            logger.info(f"login via {via_idx} {fb_id}")
            proxy_data_split = proxy_data.split(":")
            if len(proxy_data_split) != 4:
                sg.Popup(
                    f'Via Format khong dung: fb_id|password|mfa|email|email_password|ProxyIP:ProxyPORT:ProxyUsername:ProxyPassword',
                    keep_on_top=True)
                break

            fb_id = fb_id.strip()
            via_exist = via_share.find_one({"fb_id": fb_id})
            chrome_worker = ChromeHelper()
            if not via_exist:
                chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
                try:
                    login_status = chrome_worker.login()
                    # login success
                    if login_status:
                        via_status = "live"
                    else:
                        via_status = "can not login"
                except Exception as ex:
                    via_status = "can not login"
                    logger.error(ex)
                via_share.insert_one(
                    {
                        "fb_id": fb_id,
                        "password": password,
                        "mfa": mfa,
                        "email": email,
                        "email_password": email_password,
                        "proxy": proxy_data,
                        "share_number": 0,
                        "group_joined": [],
                        "date": "",
                        "status": via_status,
                        "create_date": str(datetime.now())
                    }
                )
            if login_existed and via_exist:
                try:
                    user_data_dir = "User Data"
                    if os.path.isfile("config.txt"):
                        with open("config.txt") as config_file:
                            for line in config_file.readlines():
                                user_data_dir = line.strip()
                                break
                    if via_exist['status'] == 'live':
                        continue

                    shutil.rmtree(f"{user_data_dir}/{fb_id}")
                    chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
                    login_status = chrome_worker.login()
                    # login success
                    if login_status:
                        via_status = "live"
                    else:
                        via_status = "can not login"

                except Exception as ex:
                    via_status = "can not login"
                    logger.error(ex)
                via_share.update_one(
                    {"fb_id": fb_id},
                    {"$set": {
                        "password": password,
                        "mfa": mfa,
                        "email": email,
                        "email_password": email_password,
                        "proxy": proxy_data,
                        "status": via_status,
                        "create_date": str(datetime.now())
                    }}
                )
            try:
                chrome_worker.driver.close()
            except Exception as ex:
                logger.error(f"can not close drive")
            main_windows.write_event_value('new_via_login', "")


def start_share(main_window, stop_thread):
    # Step 1 query all via live
    print("start share")
    while not stop_thread():
        video_sharing = scheduler_table.find_one({"shared": False})
        if not video_sharing:
            time.sleep(10)
            continue

        video_sharing_id = video_sharing.get("video_id", "")
        groups_remaining = video_sharing.get("groups_remaining", [])
        groups_shared = video_sharing.get("groups_shared", [])
        logger.info(f"Share video : {video_sharing_id}")

        results = via_share.find({"status": 'live', "share_number": {"$lt": 4}})
        results = list(results)

        if len(results) == 0:
            continue

        groups_share_fixed = list(set(groups_remaining) - set(groups_shared))
        current_date = str(datetime.date(datetime.now()))
        via_data = None
        founded = False
        found_group_name = ""
        for via_data in results:
            group_joined = via_data.get("group_joined", [])
            for group_share_fixed in random.sample(groups_share_fixed, k=len(groups_share_fixed)):
                if group_share_fixed in group_joined:
                    founded = True
                    found_group_name = group_share_fixed
                    break
            if founded:
                # found group joined
                break

        if not founded:
            # not found any via have joined this group in the remaining groups
            scheduler_table.update_one({"video_id": video_sharing_id}, {"$set": {"shared": True}})
            continue

        share_date = via_data.get("date")
        fb_id = via_data.get("fb_id")
        password = via_data.get("password")
        mfa = via_data.get("mfa")
        proxy_data = via_data.get("proxy")
        via_share_number = via_data.get("share_number")
        # reset via share counting
        if share_date != current_date:
            via_share.update_one({"fb_id": fb_id}, {"$set": {"date": current_date, "share_number": 0}})

        # mark via running
        # query = db.update(via_share).values(status='sharing')
        # query = query.where(via_share.columns.fb_id == fb_id)
        # connection.execute(query)
        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'sharing'}})
        # start sharing
        chrome_worker = ChromeHelper()
        logger.info(f"{fb_id}, {password}, {mfa}, {proxy_data}")
        chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
        try:
            chrome_worker.sharing(video_sharing_id, fb_id, via_share_number, found_group_name)
        except Exception as ex:
            # raise ex
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
            logger.error(f"share video errors {ex}")

        main_window.write_event_value('-THREAD-', "")

        try:
            chrome_worker.driver.close()
        except Exception as ex:
            pass


# if __name__ == '__main__':
#     all_via = via_share.find()
#     # print(list(all_via))
#     for via in all_via:
#         exist = via_share.find({"fb_id": via['fb_id']})
#         exist = list(exist)
#         if len(exist) > 1:
#             via_share.delete_one({"_id": exist[0]['_id']})
#
