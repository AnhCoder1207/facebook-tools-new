import os
import zipfile
from datetime import datetime
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

from config_btn import drop_down_menu_xpath, confirm_friend_request, add_friend_button, language_selector
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

        notifications = self.find_by_attr("div", 'data-sigil', 'messenger_icon')
        if notifications:
            logger.info(f"{self.fb_id} passed")
            return True

        search_header = self.waiting_for_css_selector(homepage)
        if search_header:
            logger.info(f"{self.fb_id} passed")
            return True

        return False

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
        groups_share_fixed.append(found_group_name)

        self.driver.get("https://m.facebook.com")

        # check die proxy
        # try:
        #     any_tag = self.driver.find_element(By.TAG_NAME, "div")
        # except Exception as ex:
        #     via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
        #     logger.error(f"Proxy die {self.fb_id}")
        #     return

        # check log in needed
        self.check_language()

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

            newsfeed = self.find_by_attr("div", 'data-sigil', 'messenger_icon', waiting_time=1)
            if login_status and not newsfeed:
                via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'die proxy'}})
                return

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

        time.sleep(5)
        self.driver.get(share_link)

        # check content not found
        if self.find_by_text("a", "Content Not Found", waiting_time=2):
            scheduler_table.update_one({"video_id": video_id}, {"$set": {"shared": True}})
            via_share.update_one({"fb_id": fb_id}, {"$set": {"status": 'live'}})
            return

        play_button = self.find_by_attr("div", "data-sigil", "m-video-play-button playInlineVideo")
        if play_button: play_button.click()
        random_sleep(5, 10)

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
        for group in random.sample(groups_share_fixed, len(groups_share_fixed)):
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
            else:
                logger.error(f"Can not split {group}")
                continue

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
            write_something = self.waiting_for_text("div > div", "Write something...", waiting_time=1)
            if not write_something:
                logger.error(f"errors : Write something... not found")
                continue

            i = 0
            while i < 10:
                i += 1
                # Scroll down to bottom
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # Wait to load page
                time.sleep(2)

            self.driver.get(group_url)
            write_something = self.waiting_for_text("div > div", "Write something...", waiting_time=2)
            if not write_something:
                logger.error(f"errors : Write something... not found")
                continue

            write_something.click()
            random_sleep(1, 3)

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
            random_sleep(5, 10)

            close_link_button = self.find_by_attr("a", "data-sigil", "close-link-preview-button", waiting_time=2)
            if not close_link_button:
                not_found_time += 1
                if not_found_time > 2:
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
                                via_share.update_one({"fb_id": fb_id}, {"$set": {"share_number": share_per_day}})
                                return False
                            if self.waiting_for_text_by_css("#MBackNavBar > a", "You can't use this feature at the moment",
                                                            waiting_time=1):
                                # You can't use this feature at the moment
                                logger.error(f"{fb_id} You Can't Use This Feature Right Now")
                                share_per_day = os.environ.get("SHARE_PER_DAY", 10)
                                share_per_day = int(share_per_day)
                                via_share.update_one({"fb_id": fb_id}, {"$set": {"share_number": share_per_day}})
                                return False
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
        options.add_argument(f"--profile-directory={self.fb_id}")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-background-networking')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-client-side-phishing-detection')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-prompt-on-repost')
        options.add_argument('--disable-rtc-smoothness-algorithm')
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
        options.add_argument("test-type=webdriver")
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        # options.binary_location = "chrome-win/chrome.exe"
        options.add_argument("--window-size=390,844")

        if proxy_data != "" and proxy_enable:

            PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = self.proxy_data.split(":")

            # check proxy
            proxies = {"http": f"http://{PROXY_USER}:{PROXY_PASS}@{PROXY_HOST}:{PROXY_PORT}"}

            try:
                r = requests.get("http://www.google.com/", proxies=proxies)
            except Exception as ex:
                logger.error(f"proxy die: {self.fb_id}")
                return False

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

        self.driver = webdriver.Chrome(executable_path=f'chromedriver.exe', options=options)
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
