import json
import random
from datetime import datetime

import sqlalchemy as db
from selenium.webdriver.common.by import By

from helper import ChromeHelper
from models import connection, via_share
from utils import get_group_joining_data, logger
from config_btn import *


def thread_join_group(stop_joining):
    # get list group share
    groups_share = []
    join_group = get_group_joining_data("join_group").split('\n')

    results = connection.execute(db.select([via_share]).where(db.and_(
        via_share.columns.status == 'live',
        via_share.columns.share_number < 4
    ))).fetchall()

    if len(results) == 0:
        return True

    result = random.choice(results)  # get random via
    current_date = str(datetime.date(datetime.now()))
    via_data = dict(zip(result.keys(), result))

    fb_id = via_data.get("fb_id")
    logger.info(f"Start join group for via {fb_id}")
    password = via_data.get("password")
    mfa = via_data.get("mfa")
    proxy_data = via_data.get("proxy")
    group_joined = json.loads(via_data.get("group_joined"))
    chrome_worker = ChromeHelper()  # init worker
    chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
    groups_share_fixed = list(set(join_group) - set(group_joined))

    chrome_worker.driver.get("https://facebook.com")
    # check disable
    is_disable = chrome_worker.waiting_for_selector(disable_1, waiting_time=1)
    if is_disable:
        query = db.update(via_share).values(status='disable')
        query = query.where(via_share.columns.fb_id == fb_id)
        connection.execute(query)
        chrome_worker.driver.close()
        return
    is_locked = chrome_worker.waiting_for_selector(locked_1, waiting_time=1)
    if is_locked:
        query = db.update(via_share).values(status='checkpoint')
        query = query.where(via_share.columns.fb_id == fb_id)
        connection.execute(query)
        chrome_worker.driver.close()
        return

    is_login = chrome_worker.waiting_for_selector("#email", waiting_time=1)
    if is_login:
        chrome_worker.login()

    # check language
    search_facebook = chrome_worker.waiting_for_selector(search_facebook_inp)
    if search_facebook:
        if search_facebook.get_attribute('placeholder') != 'Search Facebook':
            chrome_worker.change_language()
    else:
        return

    join_number = 0
    for group in groups_share_fixed:
        if join_number >= 4:
            chrome_worker.driver.close()
            return

        splitter = group.split(',')
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

        answer_question = chrome_worker.waiting_for_text_by_css(answer_questions_label, 'answer questions', waiting_time=10)
        request_participation = chrome_worker.waiting_for_text_by_css(participation_request, 'Participation request', waiting_time=1)
        if answer_question or request_participation:
            # chrome_worker.driver.execute_script("window.scrollTo(0, window.scrollY + 200)")
            elements = chrome_worker.driver.find_elements(By.TAG_NAME, "textarea")
            for element in elements:
                if element and element.get_attribute('placeholder') == 'Write an answer...':
                    print("found text area")
                    if element.get_attribute('value') != "":
                        element.send_keys("I'm agree")

            check_box = chrome_worker.waiting_for_text_by_css("div.hpfvmrgz.h676nmdw.buofh1pr.rj1gh0hx > span", 'I agree to the group rules', waiting_time=10)
            if check_box:
                check_box.click()

            submit = chrome_worker.waiting_for_text_by_css(submit_btn, 'submit')
            if submit:
                submit.click()

        join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'joined', waiting_time=5)
        if join_group_el:
            logger.info("found joined_btn")
            group_joined.append(group)
            query = db.update(via_share).values(group_joined=json.dumps(group_joined))
            query = query.where(via_share.columns.fb_id == fb_id)
            connection.execute(query)
            continue
        join_group_el = chrome_worker.waiting_for_text_by_css(join_group_btn, 'invite', waiting_time=1)
        if join_group_el:
            logger.info("found joined_btn")
            group_joined.append(group)
            query = db.update(via_share).values(group_joined=json.dumps(group_joined))
            query = query.where(via_share.columns.fb_id == fb_id)
            connection.execute(query)

    chrome_worker.driver.close()


if __name__ == '__main__':
    thread_join_group(False)
