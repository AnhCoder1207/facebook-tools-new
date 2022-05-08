import os
import zipfile
from datetime import datetime, timedelta
from functools import wraps
import requests
import pyotp
import time
import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from config_btn import drop_down_menu_xpath, language_selector
from utils import logger, get_group_joining_data, scheduler_table, via_share, random_sleep, validate_string


class ChromeHelper:
    def __init__(self):
        self.fb_id = None
        self.password = None
        self.mfa = None
        self.driver = None
        self.proxy_data = None
        self.in_use = False
        self.last_active = datetime.now()

    def waiting_for_id(self, id_here):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, id_here))
            )
            return element
        except Exception as ex:
            # print(ex)
            logger.error(f"Can not find {id_here}")
            return False

    def waiting_for_class(self, class_here):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_here))
            )
            return element
        except Exception as ex:
            logger.error(f"Can not find {class_here}")
            return False

    def waiting_for_xpath(self, xpath):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception as ex:
            logger.error(f"Can not find {xpath}")
            return False

    def waiting_for_css_selector(self, selector):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as ex:
            # print(ex)
            return False

    def find_by_attr(self, tag, attribute, text_compare, waiting_time=3):
        for _ in range(waiting_time):
            try:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    if element and element.get_attribute(attribute) and \
                            element.get_attribute(attribute).lower().strip() == text_compare.lower().strip():
                        print(element.get_attribute(attribute))
                        return element
            except Exception as ex:
                logger.error(f"Can not find {text_compare}")
            time.sleep(2)
        return False

    def find_attr_by_css(self, css_selector, attribute, text_compare, waiting_time=3):
        for _ in range(waiting_time):
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, css_selector)
                for element in elements:
                    if element and element.get_attribute(attribute) and \
                            element.get_attribute(attribute).lower().strip() == text_compare.lower().strip():
                        print(element.get_attribute(attribute))
                        return element
            except Exception as ex:
                logger.error(f"Can not find {text_compare}")
            time.sleep(2)
        return False

    def find_by_text(self, tag, text_compare, waiting_time=3):
        """retry 3 times"""
        for _ in range(waiting_time):
            try:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    if element.text and element.text.lower().strip() == text_compare.lower().strip():
                        print(element.text)
                        return element
            except Exception as ex:
                logger.error(f"Can not find {text_compare}")
            time.sleep(2)
        return False

    def waiting_for_text(self, tag, text_compare, waiting_time=3):
        for _ in range(waiting_time):
            try:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    if element.text and element.text.lower().strip() == text_compare.lower().strip():
                        print(element.text)
                        return element
            except Exception as ex:
                logger.error(f"Can not find {text_compare}")
            time.sleep(2)
        return False

    def find_by_css_selector(self, selector):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as ex:
            pass
            # logger.error(f"Can not find {selector}")
            return False

    def find_by_xpath(self, xpath):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception as ex:
            pass
            # logger.error(f"Can not find {selector}")
            return False

    def waiting_for_selector(self, selector, waiting_time=10):
        try:
            element = WebDriverWait(self.driver, waiting_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as ex:
            pass
            # logger.error(f"Can not find {selector}")
            return False

    def waiting_for_text_by_css(self, selector, text_compare, waiting_time=3):
        for _ in range(waiting_time):
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.text and element.text.lower().strip() == text_compare.lower().strip():
                        print(element.text)
                        return element
            except Exception as ex:
                logger.error(f"Can not find {text_compare}")
            time.sleep(1)
        return False

    def check_dark_light(self):
        drop_down_menu_el = self.find_by_xpath(drop_down_menu_xpath)
        if drop_down_menu_el:
            print(drop_down_menu_el.value_of_css_property("background-color"))

    def check_comunity_spams(self):
        # data - nt = "NT:BOX_3_CHILD"
        ids = self.waiting_for_text_by_css("div", "You can't use this URL")
        community_standards = self.waiting_for_text_by_css("div", "This post goes against our Community Standards on spam")
        if ids or community_standards:
            try:
                span_elements = self.driver.find_elements(By.CSS_SELECTOR, "span")
                for btn in span_elements:
                    try:
                        #data-nt="NT:BOX"
                        img = btn.find_element(By.CSS_SELECTOR, 'img')
                        attribute = img.get_attribute("data-nt")
                        style = img.get_attribute("style")
                        if attribute == "NT:IMAGE" and style == 'object-fit: inherit; width: 20px; height: 20px; max-width: 20px; max-height: 20px;':
                            btn.click()
                            time.sleep(5)
                            self.driver.get("https://m.facebook.com")
                    except Exception as ex:
                        logger.error(f"check_comunity_spams {ex}")
            except Exception as ex:
                logger.error(f"check_comunity_spams {ex}")

    def login(self):
        username_xpath = """//*[@id="m_login_email"]"""
        password_xpath = """//*[@id="m_login_password"]"""
        login_btn_xpath = """//*[@id="login_password_step_element"]/button"""
        mfa_inp_xpath = """//*[@id="approvals_code"]"""
        submit_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        continue_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        homepage = "#search_jewel > a > span._7iz_"
        self.driver.set_window_size(375, 812)
        try:
            self.driver.get("https://m.facebook.com/")
        except Exception as ex:
            logger.error(f"{self.fb_id} can not reach internet")
        # check via is ok

        notifications = self.find_by_attr("div", 'data-sigil', 'messenger_icon')
        if notifications:
            logger.info(f"{self.fb_id} passed")
            return True

        search_header = self.waiting_for_css_selector(homepage)
        if search_header:
            logger.info(f"{self.fb_id} passed")
            return True

        choose_your_account_selector = """#root > div > div > div > p"""
        choose_your_account = self.waiting_for_text_by_css(choose_your_account_selector, "Choose Your Account")
        if choose_your_account:
            # login exited account
            # data-sigil="login_profile_form"
            login_profile_form = self.find_by_attr("div", "data-sigil", "login_profile_form", waiting_time=1)
            if login_profile_form:
                login_profile_form.click()
                # placeholder="Password"
                password_inp = self.find_by_attr("input", "placeholder", "Password")
                password_inp.send_keys(self.password)
                # data-sigil="touchable password_login_button"
                password_login_button = self.find_by_attr("button", "data-sigil", "touchable password_login_button")
                if password_login_button:
                    password_login_button.click()
                    self.input_mfa()

        else:
            # login normal
            login_btn = self.waiting_for_xpath(login_btn_xpath)
            username_inp = self.waiting_for_xpath(username_xpath)
            password_inp = self.waiting_for_xpath(password_xpath)
            if login_btn and username_inp and password_inp:
                if username_inp.get_attribute("placeholder") != "Mobile number or email address":
                    english_uk = self.waiting_for_text_by_css(language_selector, "English (UK)")
                    try:
                        english_uk.click()
                        time.sleep(5)
                        login_btn = self.waiting_for_xpath(login_btn_xpath)
                        username_inp = self.waiting_for_xpath(username_xpath)
                        password_inp = self.waiting_for_xpath(password_xpath)
                        if not login_btn:
                            return False
                    except:
                        pass

                username_inp.click()
                username_inp.clear()
                password_inp.click()
                password_inp.clear()
                username_inp.send_keys(self.fb_id)
                time.sleep(1)
                password_inp.send_keys(self.password)
                time.sleep(1)
                login_btn.click()
                time.sleep(5)

                self.input_mfa()

        login_with_one_tab = self.find_by_text("h3", "Log In With One Tap", waiting_time=1)
        if login_with_one_tab:
            not_now = self.waiting_for_text_by_css("div > a > span", "Not now", waiting_time=1)
            if not_now:
                not_now.click()
                time.sleep(5)
        # nux - nav - button
        nux_nav_button = self.waiting_for_id("nux-nav-button")
        if nux_nav_button:
            nux_nav_button.click()

        self.driver.get("https://m.facebook.com")
        notifications = self.find_by_attr("div", 'data-sigil', 'messenger_icon')
        if notifications:
            logger.info(f"{self.fb_id} passed")
            return True
        else:
            self.check_comunity_spams()
            notifications = self.find_by_attr("div", 'data-sigil', 'messenger_icon')
            if notifications:
                logger.info(f"{self.fb_id} passed")
                return True

        search_header = self.waiting_for_css_selector(homepage)
        if search_header:
            logger.info(f"{self.fb_id} passed")
            return True

        return False

    # def login(self):
    #     self.driver.get("https://mbasic.facebook.com/")
    #     user_name = self.waiting_for_id("m_login_email")
    #     password = self.waiting_for_css_selector("#password_input_with_placeholder > input")
    #     submit_btn = self.find_attr_by_css("input", "name", "login")
    #     if user_name and password and submit_btn:
    #
    #         user_name.click()
    #         user_name.clear()
    #         for item in self.fb_id:
    #             user_name.send_keys(item)
    #             time.sleep(0.05)
    #
    #         password.click()
    #         password.clear()
    #         for item in self.password:
    #             password.send_keys(item)
    #             time.sleep(0.05)
    #
    #         submit_btn.click()
    #
    #     approvals_code = self.waiting_for_id("approvals_code")
    #
    #     if approvals_code:
    #         totp = pyotp.TOTP(self.mfa)
    #         current_otp = totp.now()
    #         approvals_code.send_keys(current_otp)
    #
    #         for _ in range(5):
    #             checkpointSubmitButton = self.waiting_for_id("checkpointSubmitButton")
    #             if not checkpointSubmitButton:
    #                 break
    #
    #             checkpointSubmitButton.click()
    #             time.sleep(2)
    #
    #     fb_logo = self.find_by_attr("img", "alt", "Facebook logo")
    #     if fb_logo:
    #         return True
    #     return False

    def input_mfa(self):
        mfa_inp_xpath = """//*[@id="approvals_code"]"""
        submit_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        continue_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        mfa_inp = self.waiting_for_xpath(mfa_inp_xpath)

        if mfa_inp:
            totp = pyotp.TOTP(self.mfa)
            current_otp = totp.now()
            print("Current OTP:", current_otp)
            submit_mfa = self.waiting_for_xpath(submit_mfa_xpath)
            mfa_inp.click()
            mfa_inp.clear()
            mfa_inp.send_keys(current_otp)
            submit_mfa.click()
            continue_mfa_btn = self.waiting_for_xpath(continue_mfa_xpath)
            continue_mfa_btn.click()

        for _ in range(5):
            continue_mfa_btn = self.waiting_for_xpath(continue_mfa_xpath)
            if continue_mfa_btn:
                continue_mfa_btn.click()
            else:
                break

    def check_language(self):
        search_bar = """#search_jewel > a > span"""
        search_bar_el = self.waiting_for_text_by_css(search_bar, "Search")
        if not search_bar_el:
            self.driver.get("https://m.facebook.com/language/")
            english_us_selector = """span"""
            english_select = self.find_by_text(english_us_selector, "English (US)")
            if english_select:
                english_select.click()
                time.sleep(5)
                self.driver.get("https://m.facebook.com")
    
    def watch_live(self):
        element = self.find_by_attr("a", "aria-label", "Watch")
        if element:
            element.click()
            html = self.driver.find_element(By.TAG_NAME, 'html')
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            html.send_keys(Keys.PAGE_DOWN)
            time.sleep(3)
            html.send_keys(Keys.PAGE_DOWN)

    def check_notification(self):
        element1 = self.find_by_attr("a", "aria-label", "Notifications")
        element2 = self.find_by_text("span", "See all")
        element3 = self.find_by_text("span", "Confirm")
        [el.click() for el in [element1, element2, element3] if el]

    def sharing(self, video_id, fb_id, via_share_number, found_group_name):
        # query group share able
        video_sharing = scheduler_table.find_one({"shared": False, "video_id": video_id})
        if not video_sharing:
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
            return False

        video_sharing_id = video_sharing.get("video_id", "")
        groups_shared = video_sharing.get("groups_shared", [])
        title_shared = video_sharing.get("title_shared", [])
        share_number = video_sharing.get("share_number", 0)
        shared = video_sharing.get("shared", False)
        go_enable = video_sharing.get("go_enable", False)
        co_khi_enable = video_sharing.get("co_khi_enable", False)
        xay_dung_enable = video_sharing.get("xay_dung_enable", False)
        options_enable = video_sharing.get("options_enable", False)
        groups_remaining = video_sharing.get("groups_remaining", [])
        share_descriptions = video_sharing.get("share_descriptions", [])
        video_custom_share_links = video_sharing.get("video_custom_share_links", [])

        share_link = f"https://m.facebook.com/{video_id}"
        if len(video_custom_share_links) > 0:
            share_link = random.choice(video_custom_share_links)
            share_link = share_link.replace("www", "m")
        total_groups = []

        if go_enable:
            groups_go = get_group_joining_data("group_go")
            total_groups.extend([x.strip() for x in groups_go.split('\n')])
        if co_khi_enable:
            groups_co_khi = get_group_joining_data("group_co_khi")
            total_groups.extend([x.strip() for x in groups_co_khi.split('\n')])
        if xay_dung_enable:
            groups_xay_dung = get_group_joining_data("group_xay_dung")
            total_groups.extend([x.strip() for x in groups_xay_dung.split('\n')])
        if options_enable:
            group_options = get_group_joining_data("group_options")
            total_groups.extend([x.strip() for x in group_options.split('\n')])

        groups_share_fixed = list(set(groups_remaining) - set(groups_shared))
        # groups_share_fixed.append(found_group_name)

        self.driver.get("https://m.facebook.com")

        # check account restricted
        text_compare = "Your account is restricted"
        try:
            if self.driver.find_element(By.ID, "MChromeHeader"):
                elements = self.driver.find_elements(By.TAG_NAME, "div")
                for element in elements:
                    if element.text and text_compare.lower().strip() in element.text.lower().strip():
                        print(element.text)
                        day_restrict = [int(i) for i in element.text.split() if i.isdigit()]
                        if len(day_restrict) > 0:
                            day_restrict = int(time.time()) + day_restrict[0]*86400
                            via_share.update_one(
                                {"fb_id": fb_id},
                                {"$set": {"block_share": day_restrict, "status": 'restricted'}}
                            )
                            return False
                            # account restricted
        except Exception as ex:
            logger.error(f"Can not find {text_compare}")

        # check die proxy
        # try:
        #     any_tag = self.driver.find_element(By.TAG_NAME, "div")
        # except Exception as ex:
        #     via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
        #     logger.error(f"Proxy die {self.fb_id}")
        #     return

        # check log in needed
        self.check_language()

        # close community standard
        # data-nt="NT:IMAGE"


        # check logged
        newsfeed = self.find_by_attr("div", 'data-sigil', 'messenger_icon')
        if not newsfeed:
            login_status = False
            try:
                login_status = self.login()
            except Exception as ex:
                print(ex)

            self.driver.get("https://m.facebook.com")
            # check again
            # check logged

            if self.find_by_text("h1", "Your account has been disabled", waiting_time=1):
                logger.info(f"Via {fb_id} Disabled")
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'disable'}})
                return
            # check logged
            if self.find_by_attr("button", "value", "Get started", waiting_time=1):
                logger.info(f"Via {fb_id} Checkpoint")
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'checkpoint'}})
                return

            # newsfeed = self.find_by_attr("div", 'data-sigil', 'messenger_icon', waiting_time=1)
            # if login_status and not newsfeed:
            #     via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
            #     return
            # < div
            # id = "checkpoint_title" > Isaac, Login
            # approval
            # needed < / div >
            # check point
            try:
                checkpoint_title = self.driver.find_element(By.ID, "checkpoint_title")
                if checkpoint_title:
                    logger.info(f"Via {fb_id} Checkpoint")
                    via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'checkpoint'}})
                    return
            except Exception as ex:
                logger.error(f"get checkpoint_title errors")
                pass

            if not newsfeed:
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
                return

        if random.choice([1, 2]) == 1:
            message_el = self.find_by_attr("a", "name", "Friend Requests", waiting_time=1)
            if message_el:
                message_el.click()
                # confirm_friend = self.waiting_for_text_by_css(confirm_friend_request, "Confirm")
                # if confirm_friend: confirm_friend.click()
                # add_friend = self.waiting_for_text_by_css(add_friend_button, "Add Friend")
                # if add_friend: add_friend.click()
            random_sleep()
        if random.choice([1, 2]) == 1:
            message_el = self.find_by_attr("a", "name", "Notifications", waiting_time=1)
            if message_el: message_el.click()
            random_sleep()

        # Get scroll height
        i = 0
        while i < 5:
            i += 1
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            random_sleep(1)

        random_sleep(5)
        # self.driver.get(share_link)

        # check content not found
        # if self.find_by_text("a", "Content Not Found", waiting_time=2):
        #     logger.error(f"Video die errors {fb_id}")
        #     scheduler_table.update_one({"video_id": video_id}, {"$set": {"shared": True}})
        #     via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
        #     return

        # scheduler_table.update_one({"video_id": video_id}, {"$set": {"shared": False}})
        # play_button = self.find_by_attr("div", "data-sigil", "m-video-play-button playInlineVideo")
        # if play_button: play_button.click()
        # random_sleep(5, 10)

        # i = 0
        # while i < 10:
        #     i += 1
        #     # Scroll down to bottom
        #     self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        #     # Wait to load page
        #     time.sleep(1)

        # check disable
        # is_disable = self.waiting_for_selector(disable_1, waiting_time=5)
        # if is_disable:
        #     # query = db.update(via_share).values(status='disable')
        #     # query = query.where(via_share.columns.fb_id == fb_id)
        #     # connection.execute(query)
        #     via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'disable'}})
        #     self.driver.quit()
        #     return False
        # is_locked = self.waiting_for_selector(locked_1, waiting_time=5)
        # if is_locked:
        #     # query = db.update(via_share).values(status='checkpoint')
        #     # query = query.where(via_share.columns.fb_id == fb_id)
        #     # connection.execute(query)
        #     via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'checkpoint'}})
        #     self.driver.quit()
        #     return False

        # is_login = self.waiting_for_selector("#m_login_email", waiting_time=1)
        # if is_login:
        #     self.login()
        not_found_time = 0
        found_group = False
        # group_join_auto = random.sample(get_group_joining_data('group_join_auto').split('\n'), k = 5)
        for group in random.sample(groups_share_fixed, k=len(groups_share_fixed)):
            group = group.strip()
            if group == "":
                continue

            logger.info(f"share group: {group}")
            splitter = group.split('|')
            if len(splitter) == 2:
                group_url, group_name = splitter
            elif len(splitter) > 2:
                group_url = splitter[0]
                group_name = ",".join(splitter[1:])
            elif len(splitter) == 1:
                group_url = group
            else:
                logger.error(f"Can not split {group}")
                continue
            if 'www' in group_url:
                group_url = group_url.replace("www", "m")

            # group_url = "https://m.facebook.com/groups/2701287196753908/"
            self.driver.get(group_url)

            # check logged
            if self.find_by_text("h1", "Your account has been disabled", waiting_time=1):
                logger.info(f"Via {fb_id} Disabled")
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'disable'}})
                return
            # check logged
            if self.find_by_attr("button", "value", "Get started", waiting_time=1):
                logger.info(f"Via {fb_id} Checkpoint")
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'checkpoint'}})
                return

            # check logged
            if self.waiting_for_text_by_css("#MBackNavBar > a", "Content Not Found", waiting_time=1):
                logger.error(f"Group {group} not found")
                continue

            if self.waiting_for_text_by_css("#MBackNavBar > a", "You’re Temporarily Blocked", waiting_time=1):
                logger.error(f"{fb_id} You’re Temporarily Blocked")
                share_per_day = os.environ.get("SHARE_PER_DAY", 10)
                share_per_day = int(share_per_day)
                via_share.update_one({"fb_id": fb_id}, {"$set": {"share_number": share_per_day}})
                return False

            self.driver.get(group_url)
            write_something = None  # init write el
            try:
                write_something_els = self.driver.find_elements(By.CLASS_NAME, "_5xu4")
                for el in write_something_els:
                    if el.text == "Write something...":
                        write_something = el
            except Exception as ex:
                logger.error(f"errors : Write something... not found")
                continue

            # join group private
            if not write_something:
                # check join group
                join_group_btn = self.find_attr_by_css("button", "label",
                                                       "Join Group", waiting_time=1)
                if join_group_btn:

                    # check join in day
                    via_data = via_share.find_one({"fb_id": fb_id})
                    current_date = str(datetime.date(datetime.now()))
                    join_history = via_data.get("join_history", {})
                    join_in_day = join_history.get(current_date, None)

                    if join_in_day is None:
                        join_in_day = 0
                        via_share.update_one({"fb_id": fb_id}, {"$set": {"join_history": {current_date: join_in_day}}})

                    if join_in_day is not None and join_in_day >= 5:
                        continue

                    join_group_btn.click()
                    time.sleep(10)
                    pending_request = self.find_attr_by_css("button", "label", "Submit")
                    try:
                        if pending_request:
                            all_questions = self.driver.find_elements(By.TAG_NAME, "textarea")
                            for question in all_questions:
                                question.click()
                                question.send_keys("I'm agree")
                                time.sleep(1)

                            # submit button
                            submit_btn = self.find_attr_by_css("button", "label",
                                                               "Submit")
                            if submit_btn:
                                submit_btn.click()
                        join_in_day += 1
                        via_share.update_one({"fb_id": fb_id},
                                             {"$set": {"join_history": {current_date: join_in_day}}})
                        continue
                    except:
                        pass
                else:
                    logger.error(f"errors : Can not find button join group")
                    continue
            # continue
            else:
                # scroll page
                for _ in range(5):
                    # Scroll down to bottom
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    # Wait to load page
                    random_sleep(1, 3)

            self.driver.get(group_url)
            try:
                write_something_els = self.driver.find_elements(By.CLASS_NAME, "_5xu4")
                for el in write_something_els:
                    if el.text == "Write something...":
                        el.click()
                        random_sleep(1, 3)
            except Exception as ex:
                logger.error(f"errors : Write something... not found")
                continue

            # write_something = self.waiting_for_text("div > div", "Write something...", waiting_time=1)
            # if not write_something:
            #     logger.error(f"errors : Write something... not found")
            #     continue

            # check group is shared
            video_sharing_tmp = scheduler_table.find_one({"video_id": video_id})
            groups_shared = video_sharing_tmp.get("groups_shared", [])
            title_shared = video_sharing_tmp.get("title_shared", [])
            groups_remaining = video_sharing_tmp.get("groups_remaining", [])
            share_number = video_sharing_tmp.get("share_number", 0)
            if group in groups_shared:
                continue

            post_area = self.find_by_attr("textarea", "aria-label", "What's on your mind?", waiting_time=2)
            if not post_area:
                logger.error(f"errors : What's on your mind?")
                continue

            post_area.click()
            post_area.clear()
            post_area.send_keys(share_link)
            random_sleep(1, 3)

            close_link_button = self.find_by_attr("a", "data-sigil", "close-link-preview-button", waiting_time=3)
            if not close_link_button:
                not_found_time += 1
                if not_found_time > 5:
                    scheduler_table.update_one({"video_id": video_id}, {"$set": {"shared": True}})
                    break
                continue

            random_sleep(1, 3)
            # title share
            all_titles = share_descriptions
            if len(share_descriptions) == 0:
                all_titles = get_group_joining_data('share_descriptions').split("\n")

            share_title = ""
            for idx, title in enumerate(all_titles):
                share_title = validate_string(title)
                if idx == len(all_titles) - 1:
                    title_shared = []
                    scheduler_table.update_one({"video_id": video_id},
                                               {"$set": {"title_shared": []}})
                if title not in title_shared:
                    title_shared.append(title)
                    scheduler_table.update_one({"video_id": video_id},
                                               {"$set": {"title_shared": title_shared}})
                    break

            # share_title += " #DIY #handmade #lifehack"
            post_area.click()
            post_area.clear()
            post_area.send_keys(share_title)
            logger.info(f"send {share_title}")
            time.sleep(1)
            elements = self.driver.find_elements(By.TAG_NAME, "button")
            attribute = "data-sigil"
            text_compare = "submit_composer"
            for element in elements:
                if element and element.get_attribute(attribute) and \
                        element.get_attribute(attribute).lower().strip() == text_compare.lower().strip():
                    if element.text == "Post":
                        logger.info(f"Found post button")
                        video_sharing_tmp = scheduler_table.find_one({"video_id": video_id})
                        groups_shared = video_sharing_tmp.get("groups_shared", [])
                        if group in groups_shared:
                            break
                        if not video_sharing_tmp['shared']:
                            element.click()
                            time.sleep(2)
                            if self.waiting_for_text_by_css("#MBackNavBar > a", "You Can't Use This Feature Right Now",
                                                            waiting_time=1):
                                logger.error(f"{fb_id} You Can't Use This Feature Right Now")
                                share_per_day = os.environ.get("SHARE_PER_DAY", 10)
                                share_per_day = int(share_per_day)
                                via_share.update_one({"fb_id": fb_id}, {"$set": {"share_number": share_per_day, "status": "live"}})
                                return False
                            if self.waiting_for_text_by_css("#MBackNavBar > a", "You can't use this feature at the moment",
                                                            waiting_time=1):
                                # You can't use this feature at the moment
                                logger.error(f"{fb_id} You Can't Use This Feature Right Now")
                                share_per_day = os.environ.get("SHARE_PER_DAY", 10)
                                share_per_day = int(share_per_day)
                                via_share.update_one({"fb_id": fb_id}, {"$set": {"share_number": share_per_day, "status": "live"}})
                                return False
                            video_sharing = scheduler_table.find_one({"video_id": video_id})
                            via_shares = video_sharing.get("via_shares", [])
                            via_shares.append({
                                "group_id": group,
                                "via_id": fb_id
                            })
                            scheduler_table.update_one({"video_id": video_id}, {"$set": {"via_shares": via_shares}})
                            break

            video_sharing_tmp = scheduler_table.find_one({"video_id": video_id})
            groups_shared = video_sharing_tmp.get("groups_shared", [])
            share_number = video_sharing_tmp.get("share_number", 0)
            groups_remaining = video_sharing_tmp.get("groups_remaining", [])
            if group not in groups_shared:
                groups_shared.append(group)
            if group in groups_remaining:
                groups_remaining.remove(group)
            logger.info(f"{video_id} Share done")
            found_group = True
            break

        if not found_group:
            # update video metadata
            video_sharing_tmp = scheduler_table.find_one({"video_id": video_id})
            groups_shared = video_sharing_tmp.get("groups_shared", [])
            share_number = video_sharing_tmp.get("share_number", 0)
            groups_remaining = video_sharing_tmp.get("groups_remaining", [])

        share_number += 1
        update_data = {
            "share_number": share_number,
            "groups_shared": groups_shared,
            "groups_remaining": groups_remaining
        }
        if len(groups_remaining) == 0 or share_number >= len(total_groups):
            update_data['shared'] = True
        scheduler_table.update_one({"video_id": video_id}, {"$set": update_data})
        via_share_number += 1
        via_share.update_one(
            {
                "fb_id": fb_id
            },
            {
                "$set": {
                    "status": "live",
                    "share_number": via_share_number
                }
            }
        )
        time.sleep(10)
        return True

    @staticmethod
    def check_state(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """A wrapper function"""

            # Extend some capabilities of func
            func()

        return wrapper

    def scroll_down(self):
        SCROLL_PAUSE_TIME = 1

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        for _ in range(10):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(2)

        # Calculate new scroll height and compare with last scroll height
        # new_height = self.driver.execute_script("return document.body.scrollHeight")
        # if new_height == last_height:
        #     break
        # last_height = new_height

    def check_video_ids(self):
        SCROLL_PAUSE_TIME = 3

        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(SCROLL_PAUSE_TIME)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

            try:
                videos = self.driver.find_elements(By.CSS_SELECTOR, "div._53mw")
                for video in videos:
                    if video.get_attribute("aria-label") == "Video":
                        data_store = video.get_attribute("data-store")
                        video_id = data_store['videoID']
                        print(video_id)
            except Exception as ex:
                logger.error(f"Get video id errors: {ex}")

    def click_approve(self, page_auto_approved):
        page_auto_approved = [x.lower().strip() for x in page_auto_approved]
        # self.driver.execute_script("window.scrollTo(0, 0);")
        for _ in range(10):
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            time.sleep(5)

            try:
                articles = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.lzcic4wl"))
                )
            except Exception as ex:
                return

            # articles = self.driver.find_elements(By.CSS_SELECTOR, "div.lzcic4wl")
            for article in reversed(articles):
                try:
                    role = article.get_attribute('role')
                    if role and role == "article":
                        all_page_name = article.find_elements(By.CSS_SELECTOR, "h4 > span > a > strong > span")
                        for page_name in all_page_name:
                            if page_name.text.lower().strip() in page_auto_approved:
                                # click approve
                                approved_buttons = article.find_elements(By.TAG_NAME, "div")
                                for btn in approved_buttons:
                                    # aria-label="Decline"
                                    # role="button"
                                    aria_label = btn.get_attribute('aria-label')
                                    if aria_label == "Approve":
                                        self.driver.execute_script(f"window.scrollTo(0, {article.location['y']});")
                                        time.sleep(5)
                                        btn.click()
                                        print(page_name.text)
                                        break
                except Exception as ex:
                    print(ex)

    def check_views(self, group_id, video_id, fb_id):
        group_id = group_id.replace("m.facebook.com", "www.facebook.com")
        if not group_id.endswith("/"):
            group_id += "/"

        # check posted content
        for status in ["my_pending_content", "my_posted_content", "my_declined_content", "my_removed_content"]:
            self.driver.get(group_id + status)
            time.sleep(5)
            selector = "div.i09qtzwb.pmk7jnqg.dpja2al7.pnx7fd3z.e4zzj2sf.k4urcfbm.tghn160j.bp9cbjyn.jeutjz8y.j83agx80.btwxx1t3 > div > span > span > span > a"
            permalinks_selector = "div.rq0escxv.l9j0dhe7.du4w35lb.cbu4d94t.d2edcug0.hpfvmrgz.rj1gh0hx.buofh1pr.g5gj957u.j83agx80.dp1hu0rb > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > div > a"
            try:
                el = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                if not el:
                    continue

                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                permalinks = self.driver.find_elements(By.CSS_SELECTOR, permalinks_selector)

                for el_idx, element in enumerate(elements):
                    if element.get_attribute("aria-label") == "Enlarge":
                        href = element.get_attribute("href")
                        href_split = href.split("/")
                        if len(href_split) >= 5:
                            extracted_video_id = href_split[5]
                            if extracted_video_id == video_id:
                                video_data = scheduler_table.find_one({"video_id": video_id})
                                via_shares = video_data.get("via_shares", [])
                                for idx, item in enumerate(via_shares):
                                    tmp_group_id = item.get("group_id")
                                    tmp_group_id = tmp_group_id.replace("m.facebook.com", "www.facebook.com")
                                    if not tmp_group_id.endswith("/"):
                                        tmp_group_id += "/"
                                    tmp_via_id = item.get("via_id")
                                    if tmp_group_id.split('/')[5] == group_id.split('/')[5] and tmp_via_id == fb_id:
                                        via_shares[idx]['status'] = status
                                        video_permalink = ""
                                        if status == 'my_posted_content':
                                            video_permalink = permalinks[el_idx].get_attribute("href")
                                        via_shares[idx]['video_permalink'] = video_permalink

                                        logger.info(f"found {video_id} {status}")
                                        if video_permalink.strip() != "":
                                            like = None
                                            try:
                                                self.driver.get(video_permalink)
                                                article = self.driver.find_element(By.CSS_SELECTOR,
                                                                                   "div.du4w35lb.k4urcfbm.l9j0dhe7.sjgh65i0 > div > div > div > div")
                                                if article:
                                                    like = article.find_element(By.CSS_SELECTOR,
                                                                                "div.bp9cbjyn.j83agx80.buofh1pr.ni8dbmo4.stjgntxs > div > span > div > span.gpro0wi8.cwj9ozl2.bzsjyuwj.ja2t1vim > span > span")
                                            except Exception as ex:
                                                pass
                                            like = like.text if like else "0"
                                            via_shares[idx]['like'] = like
                                        scheduler_table.update_one({"video_id": video_id},
                                                                   {"$set": {"via_shares": via_shares}})
                                        break
            except Exception as ex:
                pass

    def open_chrome(self, fb_id, password, mfa, proxy_data, proxy_enable=True):
        self.in_use = True
        self.fb_id = fb_id
        self.password = password
        self.mfa = mfa
        if self.driver:
            try:
                self.driver.quit()
            except Exception as ex:
                logger.error(f"can not close drive {ex}")

        self.proxy_data = proxy_data

        options = webdriver.ChromeOptions()
        user_data_dir = "User Data"
        if os.path.isfile("config.txt"):
            with open("config.txt") as config_file:
                for line in config_file.readlines():
                    user_data_dir = line.strip()
                    break

        os.makedirs("Plugin", exist_ok=True)
        os.makedirs(user_data_dir, exist_ok=True)
        options.add_argument(f"user-data-dir={user_data_dir}/{self.fb_id}")  # Path to your chrome profile
        options.add_argument(f"--profile-directory=Default")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-3d-apis")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-notifications')
        options.add_argument('--disable-bundled-ppapi-flash')
        options.add_argument('--disable-prompt-on-repost')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-webrtc-hw-decoding')
        options.add_argument('--disable-webrtc-hw-vp8-encoding')
        options.add_argument('--disable-webrtc-multiple-routes')
        options.add_argument('--disable-rtc-smoothness-algorithm')
        options.add_argument('--enable-blink-features=ShadowDOMV0')
        options.add_argument('--enforce-webrtc-ip-permission-check')
        options.add_argument('--force-webrtc-ip-handling-policy')
        options.add_argument('--no-first-run')
        options.add_argument('--disable-sync')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-webgl')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--mute-audio')
        # options.add_argument('--headless')
        options.add_argument('disable-infobars')
        options.add_argument('--no-sandbox')
        options.add_argument('--no-first-run')
        options.add_argument('--no-service-autorun')
        options.add_argument('--password-store=basic')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-popup-blocking')
        options.add_argument("test-type=webdriver")
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.binary_location = "chrome-win/chrome.exe"
        options.add_argument("--window-size=375,667")
        options.add_argument("--flag-switches-begin")
        options.add_argument("--flag-switches-end data:,")
        options.add_argument("--app=https://m.facebook.com")
        if proxy_data != "" and proxy_enable:

            PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = self.proxy_data.split(":")

            # check proxy
            proxies = {"http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"}

            try:
                # check internet connection
                r = requests.get("http://www.google.com/")
                if r.status_code == 200:
                    try:
                        # check proxy connection
                        r = requests.get("http://www.google.com/", proxies=proxies)
                    except Exception as ex:
                        logger.error(f"proxy die: {self.fb_id}")
                        via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
                        return False
            except Exception as ex:
                pass
                # return False

            manifest_json = """
                {
                    "version": "1.0.0",
                    "manifest_version": 2,
                    "name": "Chrome Proxy",
                    "permissions": [
                        "proxy",
                        "tabs",
                        "unlimitedStorage",
                        "storage",
                        "<all_urls>",
                        "webRequest",
                        "webRequestBlocking"
                    ],
                    "background": {
                        "scripts": ["background.js"]
                    },
                    "minimum_chrome_version":"22.0.0"
                }
                """
            background_js = """
                var config = {
                        mode: "fixed_servers",
                        rules: {
                        singleProxy: {
                            scheme: "http",
                            host: "%s",
                            port: parseInt(%s)
                        },
                        bypassList: ["localhost"]
                        }
                    };
    
                chrome.proxy.settings.set({value: config, scope: "regular"}, function() {});
    
                function callbackFn(details) {
                    return {
                        authCredentials: {
                            username: "%s",
                            password: "%s"
                        }
                    };
                }
    
                chrome.webRequest.onAuthRequired.addListener(
                            callbackFn,
                            {urls: ["<all_urls>"]},
                            ['blocking']
                );
                """ % (PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS)

            pluginfile = f'Plugin/{self.fb_id}_proxy_auth_plugin.zip'

            with zipfile.ZipFile(pluginfile, 'w') as zp:
                zp.writestr("manifest.json", manifest_json)
                zp.writestr("background.js", background_js)
            options.add_extension(pluginfile)
        if not proxy_enable:
            pluginfile = f'Plugin/{self.fb_id}_proxy_auth_plugin.zip'
            if os.path.isfile(pluginfile):
                try:
                    os.remove(pluginfile)
                except:
                    logger.error("Can not remove plugin files.")
            options.add_argument("--disable-extensions")

        if os.name == "posix":
            self.driver = webdriver.Chrome(executable_path=f'./chromedriver', options=options)
        else:
            self.driver = webdriver.Chrome(executable_path=f'chromedriver.exe', options=options)
        # self.driver.get("https://m.facebook.com/groups/1514416682242976")
        # self.driver.execute_script("window.onbeforeunload = function() {};")
        # while True:
        #
        #     print(self.driver.switchTo().alert().getText())
        #     time.sleep(1)
        # self.driver.set_window_size(390, 844)
        # self.driver.quit()
        return True

    def change_language(self):
        self.driver.get("https://www.facebook.com/settings/?tab=language")
        iframe = self.driver.find_element(By.CSS_SELECTOR, "div.rq0escxv.l9j0dhe7.du4w35lb.cbu4d94t.d2edcug0.hpfvmrgz.rj1gh0hx.buofh1pr.g5gj957u.j83agx80.dp1hu0rb > div > div > iframe")
        self.driver.switch_to.frame(iframe)
        languages = self.driver.find_elements(By.CSS_SELECTOR, 'ul > li > a')
        for item in languages:
            print(item.text)
            if 'English' in item.get_attribute('title'):
                item.click()
                time.sleep(5)
                self.driver.switch_to.default_content()
                self.driver.get("https://www.facebook.com")
                break
