import random
from datetime import datetime
import string
import time
import uuid

import clipboard
import pyautogui
import pyotp

from auto_via.utils import cookies_table, waiting_for, get_fb_id, \
    click_to, check_exist, deciscion, via_share_table, \
    logger, paste_text, get_code, get_exist_phone, get_new_phone, get_out_look, get_email, click_many, cancel_session, \
    get_email_cenationtshirt, get_emails, logger


class AutoVia:
    def __init__(self, fb_id, old_password, old_email_outlook, old_email_password, old_secret_key):
        self.fb_id = fb_id
        self.phone_number = ''
        self.old_email_outlook = old_email_outlook
        self.old_email_password = old_email_password
        self.old_secret_key = old_secret_key
        self.old_password = old_password
        self.new_email_outlook = old_email_outlook
        self.new_email_password = old_email_password
        self.new_secret_key = ''
        self.new_password = ''

    def show_meta_data(self):
        print(f"{self.fb_id}|{self.new_password}|{self.new_secret_key}|{self.new_email_outlook}|{self.new_email_password}\n")

    @staticmethod
    def change_ip():
        hma_x, hma_y = waiting_for("hma_app.PNG")
        pyautogui.moveTo(hma_x, hma_y)
        pyautogui.click(hma_x, hma_y, button='right', interval=3)
        click_to("change_ip_address.png", interval=3)
        waiting_for("change_ip_success.PNG")
        # time.sleep(20)
        click_to("google.PNG")

    def log_in(self):
        click_to("home_page.PNG")
        click_to("EnglishUS.PNG")
        waiting_for("sign_in_btn.PNG")
        click_to("email_or_phone.PNG")
        paste_text(self.fb_id)
        pyautogui.press('tab')
        paste_text(self.old_password)
        click_to("sign_in_btn.PNG", confidence=0.9)

        if waiting_for("wrong_credentials.PNG", waiting_time=10):
            return False

        click_to("EnglishUS_1.PNG")
        if not waiting_for("continue.PNG", waiting_time=10):
            click_to("EnglishUS_1.PNG", confidence=0.8)

        secret_key = self.old_secret_key.strip().replace(' ', '')
        click_to('sign_in_code.PNG')
        totp = pyotp.TOTP(secret_key).now()
        paste_text(totp)
        click_to("continue.PNG", waiting_time=10)
        click_to("continue.PNG", waiting_time=10)
        click_to("continue.PNG", waiting_time=10)
        click_to("itme.PNG", waiting_time=10)
        click_to("continue.PNG", waiting_time=10)
        if waiting_for("dark_logo.PNG", waiting_time=20, confidence=0.9):
            click_to("dark_drop_down.PNG", confidence=0.9)
            click_to("dark_theme.PNG")
            click_to("off_dark_theme.PNG")

        # if waiting_for("locked.PNG", waiting_time=10):
        #     self.new_password = self.old_password
        #     self.new_secret_key = self.old_secret_key
        #     self.new_email_outlook = self.old_email_outlook
        #     self.new_email_password = self.old_email_password
        #     self.save_results()
        #     return False

        if waiting_for("accept_cookies_title.PNG", waiting_time=10):
            click_to("accept_cookies.PNG")

        click_to("settings_page.PNG")
        if waiting_for("locked.PNG", waiting_time=10):
            self.new_password = self.old_password
            self.new_secret_key = self.old_secret_key
            self.new_email_outlook = self.old_email_outlook
            self.new_email_password = self.old_email_password
            self.save_results()
            return False

        click_to("change_language_1.PNG", confidence=0.8)
        if waiting_for("login_approved.PNG", waiting_time=10):
            return False
        if waiting_for("facebook_logo.PNG", waiting_time=10):
            return False
        if waiting_for("cookies_alive_1.PNG", waiting_time=10) or waiting_for("dark_logo.PNG", waiting_time=10):
            return True
        return False

    @staticmethod
    def check_dark_light_theme():
        if waiting_for("dark_drop_down.PNG", waiting_time=2, confidence=0.95):
            click_to("dark_drop_down.PNG", confidence=0.95)
            click_to("dark_theme.PNG")
            click_to("off_dark_theme.PNG")

    @staticmethod
    def change_language():
        click_to("change_language_1.PNG", confidence=0.8)
        pyautogui.click(x=951, y=725)
        waiting_for("cookies_alive_1.PNG")
        if not check_exist("is_english.PNG"):
            click_to("EnglishUS_1.PNG")
            pyautogui.press("f5")
        waiting_for("cookies_alive_1.PNG")

    def change_email(self):
        while True:
            click_to("settings_page.PNG", confidence=0.85)
            if waiting_for("settings_title.PNG", waiting_time=10):
                break
        self.new_email_outlook, self.new_email_password, account_outlook = get_email()
        print(self.new_email_outlook, self.new_email_password)
        contact = waiting_for("contact.PNG")
        if contact:
            contact_x, contact_y = waiting_for("contact.PNG")
            click_to("modify_phone.PNG", region=(contact_x + 780, contact_y - 20, 200, 40), confidence=0.7, check_close=False)
            click_to("add_phone_btn.PNG", confidence=0.7)
            click_to("new_email_inp.PNG")
            paste_text(self.new_email_outlook)
            click_to("add_new_email.PNG")
            waiting_for("add_other_email.PNG", waiting_time=100)
            waiting_for("add_other_email.PNG")
            href, otp = get_out_look(self.new_email_outlook, self.new_email_password, account_outlook)
            pyautogui.click(x=1738, y=517)
            pyautogui.hotkey('ctrl', 't', interval=1)
            paste_text(href)
            pyautogui.press('enter')
            time.sleep(10)
            pyautogui.hotkey('ctrl', 'w')
            pyautogui.press('f5')
            waiting_for("cookies_alive_1.PNG")
            return True
        return False

    @staticmethod
    def remove_old_contact():
        while True:
            click_to("settings_page.PNG", confidence=0.85)
            if waiting_for("settings_title.PNG", waiting_time=10):
                break
        contact = waiting_for("contact.PNG")
        if contact:
            contact_x, contact_y = contact
            time.sleep(1)
            click_to("modify_phone.PNG", region=(contact_x + 780, contact_y - 20, 200, 40), confidence=0.7,
                     check_close=False)
            click_many("remove_old_email.PNG", confidence=0.95)
            pyautogui.press('f5')

    def change_2fa_code(self):
        click_to('2fa_page.PNG', confidence=0.9)

        click_to("manage_2fa.PNG")
        waiting_for("2fa_title.PNG")
        # Xác thực 2 yếu tố đang bật
        if check_exist("turn_off_2fa.PNG"):
            click_to("turn_off_2fa.PNG")
            click_to("turn_off_confirm.PNG")
            time.sleep(2)
            if check_exist("enter_password.PNG"):
                paste_text(self.old_password)
                pyautogui.press('enter')
        if waiting_for("login_approved.PNG", waiting_time=10):
            self.new_secret_key = self.old_secret_key
            self.new_email_outlook = self.old_email_outlook
            self.new_email_password = self.old_email_password
            self.save_results()
            return False
        click_to("use_authenticator_app.PNG")
        waiting_for("next_btn_otp.PNG")
        pyautogui.moveTo(989, 540)
        pyautogui.dragTo(1183, 610, 1, button='left')
        pyautogui.hotkey('ctrl', 'c')
        self.new_secret_key = clipboard.paste().strip().replace(' ', '')
        try:
            totp = pyotp.TOTP(self.new_secret_key)
            print("Current OTP:", totp.now())
        except Exception as ex:
            return False
        click_to("next_btn_otp.PNG", check_close=False)
        waiting_for("enter_2fa_code.PNG")
        paste_text(totp.now())
        waiting_for("2fa_enabled.PNG")
        return True

    def change_password(self):
        click_to("security_page.PNG", confidence=0.8)
        waiting_for("account_proteted_title.PNG", confidence=0.7)

        change_password = waiting_for("use_change_password.PNG")
        if not change_password:
            return False

        use_2fa_x, use_2fa_y = change_password
        click_to("edit_btn.PNG", region=(use_2fa_x + 500, use_2fa_y - 20, 400, 100))
        time.sleep(5)
        click_to("current_password.PNG")
        pyautogui.hotkey('ctrl', 'a')
        paste_text(self.old_password)
        pyautogui.press("tab")
        self.new_password = "ThinhMinh1234@"
        print(f"new_password {self.new_password}")
        paste_text(self.new_password)
        pyautogui.press("tab")
        paste_text(self.new_password)
        pyautogui.press('enter')
        # click_to("save_password.PNG")
        waiting_for("tiep_tuc.PNG", waiting_time=15)
        # pyautogui.hotkey('ctrl', 'w')
        return True

    @staticmethod
    def clear_browser():
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'h')
        click_to('clear_brower_data.PNG')
        click_many("check_box.PNG")
        click_to("start_clear_data.PNG", confidence=0.9)
        pyautogui.hotkey('ctrl', 'w')
        pyautogui.hotkey('ctrl', 'w')

    def save_results(self):
        with open("via-share-output.txt", 'a', encoding='utf-8') as output_file:
            output_file.write(f"{self.fb_id}|{self.old_password}|{self.old_secret_key}|{self.old_email_outlook}|{self.old_email_password}\n")
            output_file.close()

        insert_dict = {
            "_id": str(uuid.uuid4()),
            "fb_id": self.fb_id,
            "password": self.old_password,
            "secret_key": self.old_secret_key,
            "email": self.old_email_outlook,
            "email_password": self.old_email_password,
            "phone_number": '',
            "created_date": datetime.now()
        }
        via_share_table.insert_one(insert_dict)

    def start_job(self):
        worker.change_ip()
        # worker.show_meta_data()
        # get cookies
        logged = worker.log_in()
        if not logged:
            return False
        # worker.show_meta_data()
        # worker.change_language()
        # worker.show_meta_data()

        # update current email
        # status = worker.change_email()
        # if not status:
        #     return False
        # worker.show_meta_data()
        # worker.remove_old_contact()
        # status = worker.change_password()
        # if not status:
        #     return False
        # worker.show_meta_data()
        # status = worker.change_2fa_code()
        # if not status:
        #     return False
        worker.show_meta_data()
        worker.save_results()
        # worker.clear_browser()
        return True


if __name__ == '__main__':
    # while True:
    with open("3.csv", encoding='utf-8') as vias:
        for via in vias.readlines():
            via = via.strip().split(',')
            # 1164660951|satthu111|ON64EQWAJJBCSO7CPIBXV56NRWEDCIHI|rttvakelsey@hotmail.com|flEanxd6jrw
            fb_id, old_password, old_secret_key, old_email_outlook, old_email_password = via
            print(fb_id, old_password, old_secret_key, old_email_outlook, old_email_password)
            st = time.time()

            exist = via_share_table.find_one({"fb_id": fb_id.strip(), "password": {"$ne": old_password}})
            if not exist:
                pyautogui.click(989, 540)
                pyautogui.hotkey('ctrl', 'shift', 'n')
                worker = AutoVia(
                    fb_id=fb_id.strip(),
                    old_password=old_password.strip(),
                    old_secret_key=old_secret_key.strip(),
                    old_email_outlook=old_email_outlook.strip(),
                    old_email_password=old_email_password.strip()
                )
                worker.start_job()
                pyautogui.hotkey('ctrl', 'f4')
            et = time.time()
            print(f"Time consuming {(et - st) / 60} min")
