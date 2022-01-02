import os
import zipfile
from datetime import datetime, timedelta
from functools import wraps

import pyautogui
import pyotp
import time
import random
import json
import sqlalchemy as db
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from auto_share_v2.config_btn import english_select_language, disable_1, locked_1, share_button_selector, \
    more_options_selector, share_to_a_group
from models import via_share, scheduler_video, connection, joining_group
from utils import logger, get_group_joining_data, mongo_client, scheduler_table


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

    def find_by_attr(self, tag, attribute, text_compare):
        for _ in range(3):
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

    def find_by_text(self, tag, text_compare):
        """retry 3 times"""
        for _ in range(3):
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

    def waiting_for_text(self, tag, text_compare):
        for _ in range(3):
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
            logger.error(f"Can not find {selector}")
            return False

    def waiting_for_selector(self, selector, waiting_time=10):
        try:
            element = WebDriverWait(self.driver, waiting_time).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as ex:
            logger.error(f"Can not find {selector}")
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

    def login(self):
        username_xpath = """//*[@id="m_login_email"]"""
        password_xpath = """//*[@id="m_login_password"]"""
        login_btn_xpath = """//*[@id="login_password_step_element"]/button"""
        mfa_inp_xpath = """//*[@id="approvals_code"]"""
        submit_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        continue_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        self.driver.set_window_size(375, 812)
        self.driver.get("https://m.facebook.com/")
        login_btn = self.waiting_for_xpath(login_btn_xpath)
        username_inp = self.waiting_for_xpath(username_xpath)
        password_inp = self.waiting_for_xpath(password_xpath)
        if login_btn and username_inp and password_inp:
            username_inp.send_keys(self.fb_id)
            password_inp.send_keys(self.password)
            login_btn.click()
            totp = pyotp.TOTP(self.mfa)
            current_otp = totp.now()
            print("Current OTP:", current_otp)
            mfa_inp = self.waiting_for_xpath(mfa_inp_xpath)
            submit_mfa = self.waiting_for_xpath(submit_mfa_xpath)
            mfa_inp.send_keys(current_otp)
            submit_mfa.click()
            continue_mfa_btn = self.waiting_for_xpath(continue_mfa_xpath)
            continue_mfa_btn.click()

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

    def sharing(self, video_id, fb_id, via_share_number):
        # query group share able
        video_sharing = scheduler_table.find_one({"shared": False, "video_id": video_id})
        if not video_sharing:
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

        # get list group share
        groups_share = []

        if go_enable:
            groups_go = get_group_joining_data("group_go")
            groups_share.extend([x.strip() for x in groups_go.split('\n')])
        if co_khi_enable:
            groups_co_khi = get_group_joining_data("group_co_khi")
            groups_share.extend([x.strip() for x in groups_co_khi.split('\n')])
        if xay_dung_enable:
            groups_xay_dung = get_group_joining_data("group_xay_dung")
            groups_share.extend([x.strip() for x in groups_xay_dung.split('\n')])
        if options_enable:
            group_options = get_group_joining_data("group_options")
            groups_share.extend([x.strip() for x in group_options.split('\n')])

        self.driver.get(f"https://fb.com/{video_id}")

        # check disable
        is_disable = self.waiting_for_selector(disable_1, waiting_time=1)
        if is_disable:
            query = db.update(via_share).values(status='disable')
            query = query.where(via_share.columns.fb_id == fb_id)
            connection.execute(query)
            self.driver.close()
            return
        is_locked = self.waiting_for_selector(locked_1, waiting_time=1)
        if is_locked:
            query = db.update(via_share).values(status='checkpoint')
            query = query.where(via_share.columns.fb_id == fb_id)
            connection.execute(query)
            self.driver.close()
            return

        is_login = self.waiting_for_selector("#email", waiting_time=1)
        if is_login:
            self.login()

        not_login = self.waiting_for_css_selector("""div.linmgsc8.rq0escxv.cb02d2ww.clqubjjj.bjjun2dj > div > h2 > span > span""")
        if not_login and not_login.text.lower() == "not logged in":
            query = db.update(via_share).values(status="can not login")
            query = query.where(via_share.columns.fb_id == fb_id)
            connection.execute(query)
            return False

        time.sleep(20)

        self.waiting_for_text_by_css(share_button_selector, "Share").click()
        self.waiting_for_text_by_css(more_options_selector, "More Options").click()
        self.waiting_for_text_by_css(share_to_a_group, "Share to a group").click()

        search_group_inp = self.waiting_for_css_selector("div.n851cfcs.wkznzc2l.dhix69tm.n1l5q3vz > div > div > label > input")
        groups_share_fixed = list(set(groups_share) - set(groups_shared))
        for group in groups_share_fixed:
            splitter = group.split(',')
            if len(splitter) == 2:
                group_url, group_name = splitter
            elif len(splitter) > 2:
                group_url = splitter[0]
                group_name = ",".join(splitter[1:])
            else:
                logger.error(f"Can not split {group}")
                continue

            if not search_group_inp:
                search_group_inp = self.find_by_attr("input", "aria-label", "Search for groups")
                search_group_inp.click()

            for _ in range(100):
                try:
                    search_group_inp.send_keys(Keys.BACKSPACE)
                except Exception as ex:
                    raise ex

            try:
                search_group_inp.send_keys(group_name)
            except Exception as ex:
                raise ex

            time.sleep(2)  # waiting for share btn
            elements = self.driver.find_elements(
                By.CSS_SELECTOR,
                value="""div.n851cfcs.ozuftl9m.n1l5q3vz.l9j0dhe7.nqmvxvec > div > div > i"""
            )
            share_btn = None
            for el in elements:
                if "https://static.xx.fbcdn.net/rsrc.php/v3/yy/r/eD06S0y0aJL.png" in el.get_attribute('style'):
                    try:
                        el.click()
                        share_btn = True
                        break
                    except WebDriverException:
                        print("Element is not clickable")
                        break

            if share_btn:
                post_description = self.find_by_attr("div", "aria-label", "Create a public post…")
                if post_description:
                    all_titles = get_group_joining_data('share_descriptions')
                    share_title = ""
                    for idx, title in enumerate(all_titles):
                        share_title = title
                        if idx == len(all_titles) - 1:
                            title_shared = []
                            scheduler_table.update_one({"video_id": video_id},
                                                       {"$set": {"title_shared": []}})
                        if title not in title_shared:
                            title_shared.append(title)
                            scheduler_table.update_one({"video_id": video_id},
                                                       {"$set": {"title_shared": title_shared}})
                            break
                    post_description.send_keys(share_title)
                    post_btn = self.find_by_text("span", "Post")
                    if post_btn:
                        # post_btn.click()
                        time.sleep(5)
                        groups_shared.append(group)
                        share_number += 1
                        update_data = {"share_number": share_number, "groups_shared": groups_shared}
                        if share_number >= len(groups_share):
                            update_data['shared'] = True
                        scheduler_table.update_one({"video_id": video_id}, {"$set": update_data})

                        via_share_number += 1
                        query = db.update(via_share).values(status='live', share_number=via_share_number)
                        query = query.where(via_share.columns.id == fb_id)
                        connection.execute(query)
            else:
                groups_share_fixed.remove(group_name)
        return False

    @staticmethod
    def check_state(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            """A wrapper function"""

            # Extend some capabilities of func
            func()

        return wrapper

    def open_chrome(self, fb_id, password, mfa, proxy_data):
        self.in_use = True
        self.fb_id = fb_id
        self.password = password
        self.mfa = mfa
        if self.driver:
            try:
                self.driver.close()
            except Exception as ex:
                logger.error(f"can not close drive {ex}")

        self.proxy_data = proxy_data

        PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = self.proxy_data.split(":")
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
        options = webdriver.ChromeOptions()
        user_data_dir = "User Data"
        if os.path.isfile("config.txt"):
            with open("config.txt") as config_file:
                for line in config_file.readlines():
                    user_data_dir = line.strip()
                    break

        os.makedirs("Plugin", exist_ok=True)

        options.add_argument(f"user-data-dir={user_data_dir}/{self.fb_id}")  # Path to your chrome profile
        options.add_argument(f"--profile-directory={self.fb_id}")
        options.add_argument(f"--start-maximized")
        options.add_argument('--disable-gpu')
        options.add_argument("test-type=browser")
        options.add_experimental_option("detach", True)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        prefs = {"profile.default_content_setting_values.notifications": 2, "profile.name": f"{self.fb_id} - Chrome"}
        options.add_experimental_option("prefs", prefs)
        # options.add_experimental_option(
        #     "prefs", {
        #
        #         "profile": {"name": f"{self.fb_id} - Chrome"}
        #     }
        # )
        pluginfile = f'Plugin/{self.fb_id}_proxy_auth_plugin.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)

        self.driver = webdriver.Chrome(executable_path=f'chromedriver.exe', options=options)

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
