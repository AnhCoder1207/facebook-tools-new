import os
import zipfile
import pyotp
import time
import random
import json
import sqlalchemy as db
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from models import via_share, scheduler_video, connection, joining_group


class ChromeHelper:
    def __init__(self, fb_id, password, mfa, proxy_data):
        self.fb_id = fb_id
        self.password = password
        self.mfa = mfa
        PROXY_HOST, PROXY_PORT, PROXY_USER, PROXY_PASS = proxy_data.split(":")

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
        os.makedirs("UserData", exist_ok=True)
        # dir_path = os.path.dirname(os.path.realpath(__file__))
        options.add_argument(f"user-data-dir=E:\\Chrome\\User Data")  # Path to your chrome profile
        options.add_argument(f"--profile-directory={fb_id}")
        options.add_argument("--start-maximized")
        pluginfile = f'UserData\\proxy_auth_plugin{fb_id}.zip'

        with zipfile.ZipFile(pluginfile, 'w') as zp:
            zp.writestr("manifest.json", manifest_json)
            zp.writestr("background.js", background_js)
        options.add_extension(pluginfile)
        self.driver = webdriver.Chrome('./chromedriver.exe', options=options)

    def waiting_for_id(self, id_here):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.ID, id_here))
            )
            return element
        except Exception as ex:
            print(ex)
            return False

    def waiting_for_class(self, class_here):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, class_here))
            )
            return element
        except Exception as ex:
            print(ex)
            return False

    def waiting_for_xpath(self, xpath):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
        except Exception as ex:
            print(ex)
            return False

    def waiting_for_css_selector(self, selector):
        try:
            element = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element
        except Exception as ex:
            print(ex)
            return False

    def find_by_attr(self, tag, attribute, text_compare):
        for _ in range(3):
            try:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    if element.get_attribute(attribute) == text_compare:
                        print(element.get_attribute(attribute))
                        return element
            except Exception as ex:
                print(ex)
            time.sleep(1)
        return False

    def find_by_text(self, tag, text_compare):
        """retry 3 times"""
        for _ in range(3):
            try:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    if element.text == text_compare:
                        print(element.text)
                        return element
            except Exception as ex:
                print(ex)
            time.sleep(1)
        return False

    def waiting_for_text(self, tag, text_compare):
        for _ in range(3):
            try:
                elements = self.driver.find_elements(By.TAG_NAME, tag)
                for element in elements:
                    if element.text == text_compare:
                        print(element.text)
                        return element
            except Exception as ex:
                print(ex)
            time.sleep(1)
        return False

    def login(self):
        username_xpath = """//*[@id="m_login_email"]"""
        password_xpath = """//*[@id="m_login_password"]"""
        login_btn_xpath = """//*[@id="login_password_step_element"]/button"""
        mfa_inp_xpath = """//*[@id="approvals_code"]"""
        submit_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        continue_mfa_xpath = """//*[@id="checkpointSubmitButton-actual-button"]"""
        self.driver.get("https://m.facebook.com/")
        self.driver.set_window_size(375, 812)
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

    def sharing(self, video_id, groups_share):
        # query group share able
        result = connection.execute(db.select([scheduler_video]).
                                    where(db.and_(scheduler_video.columns.video_id == video_id,
                                                  scheduler_video.columns.shared == False))).fetchone()
        if not result:
            return False

        self.driver.get(f"https://facebook.com/{video_id}")
        time.sleep(20)
        self.find_by_text("span", "Share").click()
        self.find_by_text("span", "More Options").click()
        self.find_by_text("span", "Share to a group").click()

        search_group_inp = self.find_by_attr("input", "aria-label", "Search for groups")
        search_group_inp.clear()

        video_data = dict(zip(result.keys(), result))
        groups_shared = json.loads(video_data.get("groups_shared"))
        share_number = video_data.get("share_number")
        groups_share_fixed = list(set(groups_share) - set(groups_shared))
        for group_name in groups_share_fixed:
            search_group_inp.clear()
            for _ in range(100):
                search_group_inp.send_keys(Keys.BACKSPACE)

            search_group_inp.send_keys(group_name)
            time.sleep(1)
            found_group = self.find_by_text("span", group_name)
            if found_group:
                found_group.click()
                post_description = self.find_by_attr("div", "aria-label", "Create a public post…")
                if post_description:
                    post_description.send_keys("This is the awesome videos")
                    post_btn = self.find_by_text("span", "Post")
                    if post_btn:
                        # post_btn.click()
                        groups_shared.append(group_name)
                        share_number += 1
                        if share_number <= len(groups_share):
                            query = db.update(scheduler_video).values(groups_shared=json.dumps(groups_shared),
                                                                      share_number=share_number)
                        else:
                            query = db.update(scheduler_video).values(groups_shared=json.dumps(groups_shared),
                                                                      share_number=share_number,
                                                                      shared=True)
                        query = query.where(scheduler_video.columns.video_id == video_id)
                        connection.execute(query)
                        return True
        return False
