import json
import random
import time
from datetime import datetime
import PySimpleGUI as sg
import sqlalchemy as db
from bson import ObjectId
from selenium.webdriver.common.by import By

from helper import ChromeHelper
from utils import get_group_joining_data, logger, via_share, joining_group, scheduler_table, group_auto_approved
from config_btn import *


def thread_join_group(stop_joining):
    # get list group share
    groups_share = []
    while not stop_joining():
        # results = connection.execute(db.select([via_share]).where(db.and_(
        #     via_share.columns.status == 'live',
        #     via_share.columns.share_number < 4
        # ))).fetchall()
        results = via_share.find({"status": "live", "share_number": {"$lte": 4}})
        results = list(results)
        if len(results) == 0:
            time.sleep(10)
            continue

        via_data = random.choice(results)  # get random via
        fb_id = via_data.get("fb_id")
        current_date = str(datetime.date(datetime.now()))

        join_history = via_data.get("join_history", {})
        join_in_day = join_history.get(current_date, None)
        if join_in_day is None:
            join_in_day = 0
            via_share.update_one({"fb_id": fb_id}, {"$set": {"join_history": {current_date: join_in_day}}})

        if join_in_day is not None and join_in_day > 10:
            continue

        logger.info(f"Start join group for via {fb_id}")
        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'join group'}})
        password = via_data.get("password")
        mfa = via_data.get("mfa")
        proxy_data = via_data.get("proxy")
        group_joined = via_data.get("group_joined")
        chrome_worker = ChromeHelper()  # init worker
        chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
        join_group = get_group_joining_data("group_join_auto").split('\n')
        groups_share_fixed = list(set(join_group) - set(group_joined))

        try:
            chrome_worker.driver.get("https://facebook.com")
        except Exception as ex:
            logger.error(f"{fb_id} can not reach internet")
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
            chrome_worker.driver.close()
            continue

        # check disable
        is_disable = chrome_worker.waiting_for_selector(disable_1, waiting_time=1)
        if is_disable:
            # query = db.update(via_share).values(status='disable')
            # query = query.where(via_share.columns.fb_id == fb_id)
            # connection.execute(query)
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'disable'}})
            chrome_worker.driver.close()
            continue
        is_locked = chrome_worker.waiting_for_selector(locked_1, waiting_time=1)
        if is_locked:
            # query = db.update(via_share).values(status='checkpoint')
            # query = query.where(via_share.columns.fb_id == fb_id)
            # connection.execute(query)
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'checkpoint'}})
            chrome_worker.driver.close()
            continue

        is_login = chrome_worker.waiting_for_selector("#email", waiting_time=1)
        if is_login:
            chrome_worker.login()

        # check language
        search_facebook = chrome_worker.waiting_for_selector(search_facebook_inp)
        if search_facebook:
            if search_facebook.get_attribute('placeholder') != 'Search Facebook':
                chrome_worker.change_language()
        else:
            continue

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
        for group in random.sample(groups_share_fixed, len(groups_share_fixed)):
            if join_number >= 4:
                break

            splitter = group.split('|')
            if len(splitter) >= 2:
                group_url = splitter[0]
            else:
                continue

            logger.info(f"group_url {group_url}")
            chrome_worker.driver.get(group_url)
            join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'join group', waiting_time=5)
            if join_group_el:
                logger.info("Click join button")
                join_number += 1
                join_group_el.click()  # click join btn

                join_group_anw_exist = chrome_worker.waiting_for_text_by_css(join_group_anw, 'Join Group Anyway')
                if join_group_anw_exist:
                    join_group_anw_exist.click()

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
                        if element.get_attribute('value') != "":
                            element.send_keys("I'm agree")

                check_box = chrome_worker.waiting_for_text_by_css("div.hpfvmrgz.h676nmdw.buofh1pr.rj1gh0hx > span",
                                                                  'I agree to the group rules', waiting_time=10)
                if check_box:
                    check_box.click()

                submit = chrome_worker.waiting_for_text_by_css(submit_btn, 'submit')
                if submit:
                    submit.click()
                time.sleep(5)

            join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'joined', waiting_time=5)
            if join_group_el:
                logger.info("found joined_btn")
                group_joined.append(group)
                # query = db.update(via_share).values(group_joined=json.dumps(group_joined))
                # query = query.where(via_share.columns.fb_id == fb_id)
                # connection.execute(query)
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

            # via_exist = connection.execute(db.select([via_share]).where(via_share.columns.fb_id == fb_id.strip())).fetchone()
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
                        "status": via_status
                    }
                )
            if login_existed and via_exist:
                try:
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
                        "status": via_status
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
        groups_share = video_sharing.get("groups_remaining", [])
        groups_shared = video_sharing.get("groups_shared", [])
        logger.info(f"Share video : {video_sharing_id}")

        results = via_share.find({"status": 'live', "share_number": {"$lte": 4}})
        results = list(results)
        if len(results) == 0:
            continue

        via_data = random.choice(results)
        current_date = str(datetime.date(datetime.now()))
        # via_data = dict(zip(result.keys(), result))
        group_joined = via_data.get("group_joined", [])
        groups_share_fixed = list(set(groups_share) - set(groups_shared))

        founded = False
        for group_share_fixed in groups_share_fixed:
            if group_share_fixed in group_joined:
                founded = True
                break
        if not founded:
            # via not join this group break
            continue

        share_date = via_data.get("date")
        fb_id = via_data.get("fb_id")
        password = via_data.get("password")
        mfa = via_data.get("mfa")
        proxy_data = via_data.get("proxy")
        via_share_number = via_data.get("share_number")
        # reset via share counting
        if share_date != current_date:
            # query = db.update(via_share).values(date=current_date, share_number=0)
            # query = query.where(via_share.columns.fb_id == fb_id)
            # connection.execute(query)
            via_share.update_one({"fb_id": fb_id}, {"$set": {"date": current_date, "share_number": 0}})

        # mark via running
        # query = db.update(via_share).values(status='sharing')
        # query = query.where(via_share.columns.fb_id == fb_id)
        # connection.execute(query)
        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'sharing'}})
        # start sharing
        chrome_worker = ChromeHelper()
        chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
        try:
            share_status = chrome_worker.sharing(video_sharing_id, fb_id, via_share_number)
        except Exception as ex:
            # raise ex
            logger.error(f"share video errors {ex}")
        finally:
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
            # query = db.update(via_share).values(status='live')
            # query = query.where(via_share.columns.fb_id == fb_id)
            # connection.execute(query)
            main_window.write_event_value('-THREAD-', "")

        try:
            chrome_worker.driver.close()
        except Exception as ex:
            pass


if __name__ == '__main__':
    thread_join_group(False)
