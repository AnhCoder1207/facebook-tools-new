import time
import uuid

import clipboard
import pyautogui
import pyotp

from utils import cookies_table, waiting_for, get_fb_id, \
    click_to, check_exist, deciscion, via_share_table, \
    logger, paste_text, get_code, get_exist_phone, get_new_phone, get_out_look, get_email, click_many, cancel_session, \
    get_email_cenationtshirt, get_emails


class AutoVia:
    def __init__(self):
        self.fb_id = ''
        self.phone_number = ''
        self.session = ''
        self.email_outlook = ''
        self.email_password = ''
        self.secret_key = ''
        self.cookie = None

    def clear_metadata(self):
        self.fb_id = ''
        self.phone_number = ''
        self.session = ''
        self.email_outlook = ''
        self.email_password = ''
        self.secret_key = ''
        self.cookie = None

    def show_meta_data(self):
        print(f"{self.fb_id}|Minh1234@|{self.secret_key}|{self.email_outlook}|{self.email_password}|{self.phone_number}\n")
        if self.cookie is not None:
            print(self.cookie['cookie'])

    @staticmethod
    def change_ip():
        hma_x, hma_y = waiting_for("hma_app.PNG")
        pyautogui.moveTo(hma_x, hma_y)
        pyautogui.click(hma_x, hma_y, button='right', interval=3)
        click_to("change_ip_address.png", interval=3)
        waiting_for("change_ip_success.PNG")
        click_to("google.PNG")

    def import_cookies(self):
        # while True:
        time.sleep(1)
        self.cookie = cookies_table.find_one({"used": False, "failed": False})
        # self.cookie = cookies_table.find_one({"_id": "ff979902-f2b5-4416-8f85-1ed2f3d19501"})
        if self.cookie:
            if 'cookie' in self.cookie:
                logger.info(f"cookies: {self.cookie['_id']}")
                myquery = {"_id": self.cookie['_id']}
                newvalues = {"$set": {"used": True}}
                cookies_table.update_one(myquery, newvalues)

                if not check_exist("import_cookies.PNG"):
                    click_to("fb_cookies.PNG")
                import_x, import_y = waiting_for("import_cookies.PNG")
                pyautogui.click(import_x, import_y - 50)
                clipboard.copy(self.cookie['cookie'])
                logger.debug(f"cookies id: {self.cookie['_id']}")
                pyautogui.hotkey('ctrl', 'v')
                click_to("import_cookies.PNG")
                # click_many("x_btn.PNG")
                #         pyautogui.click(x=462, y=640, interval=2)
                click_to("check_page.PNG", confidence=0.92)
                click_to("next_long.PNG", waiting_time=5, confidence=0.7)
                click_to("next_long_1.PNG", waiting_time=5, confidence=0.7)

                # check point detect
                pyautogui.click(x=264, y=50, interval=2)
                pyautogui.hotkey('ctrl', 'c')
                fb_link = clipboard.paste()
                if 'checkpoint' not in fb_link:
                    buttons = ['locked.PNG', "cookies_failed.PNG", 'cookies_failed_1.PNG', "dark_logo.PNG", "cookies_alive_1.PNG"]
                    _, _, index_btn = deciscion(buttons, confidence=0.95)
                    if index_btn == 3 or \
                            index_btn == 4:
                        click_to(buttons[index_btn], interval=1)
                        self.fb_id = self.cookie['cookie'].split('|')[0]
                        logger.debug(f"facebook id: {self.fb_id}")
                        if self.fb_id is None:
                            pyautogui.hotkey('ctrl', 'w')
                            return False

                        # check fb_id is not exist on database
                        exist_fb_id = via_share_table.find_one({"fb_id": self.fb_id})
                        if not exist_fb_id:
                            click_to(buttons[index_btn])
                            return True
                        else:
                            # clear cookies
                            myquery = {"_id": self.cookie['_id']}
                            newvalues = {"$set": {"used": True, "failed": False}}
                            cookies_table.update_one(myquery, newvalues)
                    else:
                        cookies_table.update_one({"_id": self.cookie['_id']}, {"$set": {"failed": True, "used": True}})
                else:
                    cookies_table.update_one({"_id": self.cookie['_id']}, {"$set": {"failed": True, "used": True}})
            else:
                cookies_table.delete_one({"_id": self.cookie['_id']})
        return False

    @staticmethod
    def check_dark_light_theme():
        if waiting_for("dark_logo.PNG", waiting_time=2, confidence=0.95):
            click_to("dark_drop_down.PNG", confidence=0.95)
            click_to("dark_theme.PNG")
            click_to("off_dark_theme.PNG")

    @staticmethod
    def change_language():
        # click_to("cookies_alive_1.PNG", confidence=0.95)
        # if check_exist("not_in_fun_screen_light.PNG", confidence=0.85):
        #     click_to("not_in_fun_screen_light.PNG")
        if not check_exist("is_vietnam.PNG"):
            # click_to("setting_dropdown.PNG", interval=2, confidence=0.85)
            # click_to("setting_icon.PNG", confidence=0.85)
            # click_to("change_language.PNG", confidence=0.85)
            click_to("change_language_1.PNG", confidence=0.8)
            waiting_for("cookies_alive_1.PNG")
            pyautogui.scroll(-2000)
            deciscion(["vietnam.PNG", "plus_language.PNG"], confidence=0.7, region=(0, 500, 1920, 500))
            if check_exist("vietnam.PNG", region=(0, 500, 1920, 500), confidence=0.7):
                click_to("vietnam.PNG", region=(0, 500, 1920, 500), confidence=0.7)
                pyautogui.press('f5')
                time.sleep(1)
                pyautogui.click(x=1744, y=403)
            elif check_exist("plus_language.PNG", region=(0, 500, 1920, 500), confidence=0.7):
                click_to("plus_language.PNG", region=(0, 500, 1920, 500), confidence=0.7, interval=5)
                click_to("tieng_viet.PNG", confidence=0.5)
                pyautogui.press('f5')
                time.sleep(1)
                pyautogui.click(x=1744, y=403)
        waiting_for("cookies_alive_1.PNG")

    def change_phone(self):
        # click_to("cookies_alive_1.PNG")
        # click_to("setting_dropdown.PNG", interval=2, confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        click_to("settings_page.PNG", confidence=0.8)
        x, y, btn_idx = deciscion(["cai_dat_tai_khoan.PNG", 'cai_dat_chung.PNG', "cai_dat_chung_1.PNG"], confidence=0.7)
        pyautogui.click(x, y)
        contact = waiting_for("contact.PNG")
        if contact is None:
            return False

        (contact_x, contact_y) = contact
        time.sleep(2)
        click_to("modify_phone.PNG", region=(contact_x + 780, contact_y - 20, 200, 40), confidence=0.8, check_close=False)
        click_to("add_phone_btn.PNG", confidence=0.7)
        click_to("add_your_phone.PNG", confidence=0.7)
        self.phone_number, self.session = get_new_phone()
        #     time.sleep(10)
        click_to("input_phone_inp.PNG", confidence=0.7)
        paste_text(self.phone_number)
        click_to("tiep_tuc.PNG")

        otp_code = get_code(self.session)
        if otp_code is not None:
            if check_exist("input_otp_box.PNG"):
                click_to("input_otp_box.PNG")
            pyautogui.typewrite(otp_code, interval=0.2)
            click_to("confirm_otp.PNG")
            waiting_for("input_otp_success.PNG")
            click_to("ok_btn.PNG")

            # forgot password
            session = get_exist_phone(self.phone_number)
            pyautogui.click(x=1767, y=520)  # click to space
            pyautogui.hotkey('ctrl', 'shift', 'n')
            if check_exist("fun_screen_not_able.PNG"):
                click_to("fun_screen_not_able.PNG")

            click_to("forgot_password.PNG", interval=5)
            btns = ["find_your_account.PNG", "input_phone_fogot_password.PNG"]
            x, y, btn_index = deciscion(btns)
            if btn_index == 0:
                click_to("input_phone_box.PNG")
                paste_text(self.phone_number)
                click_to("tim_kiem_phone.PNG")
                click_to("tim_kiem_phone_2.PNG")
                if waiting_for("no_result.PNG", waiting_time=10):
                    cancel_session(session)
                    return False

                otp_code = get_code(session)
                if otp_code is not None:
                    pyautogui.click(x=1767, y=520, interval=1)  # click to space
                    click_to("nhap_ma_otp.PNG")
                    paste_text(otp_code)
                    click_to("tiep_tuc.PNG")
                    click_to("new_password_box.PNG")
                    paste_text("Minh1234@")
                    click_to("tiep_tuc.PNG", interval=5)
                    pyautogui.click(x=1454, y=610, interval=0.5)
                    time.sleep(15)
                    pyautogui.hotkey("alt", "f4")
                    return True
                else:
                    pyautogui.hotkey('ctrl', 'f4')

            if btn_index == 1:
                click_to("input_phone_fogot_password.PNG")
                paste_text(self.phone_number)
                click_to("forgot_password_search.PNG")
                if waiting_for("no_result.PNG", waiting_time=10):
                    cancel_session(session)
                    return False
                click_to("forgot_password_next.PNG")

                otp_code = get_code(session)
                if otp_code is not None:
                    pyautogui.click(x=1767, y=520, interval=1)  # click to space
                    buttons = ['forgot_password_input_otp.PNG', 'forgot_password_input_otp_1.PNG']
                    _, _, btn_index = deciscion(buttons, confidence=0.8)
                    click_to(buttons[btn_index])
                    paste_text(otp_code)
                    buttons = ["forgot_password_next.PNG", 'forgot_password_next_1.PNG']
                    _, _, btn_index = deciscion(buttons, confidence=0.8)
                    click_to(buttons[btn_index])

                    click_to("new_password_inp.PNG")
                    paste_text("Minh1234@")
                    click_to("forgot_password_next.PNG", interval=5)
                    pyautogui.click(x=1454, y=610, interval=0.5)
                    time.sleep(15)
                    pyautogui.hotkey("alt", "f4")
                    return True
                else:
                    pyautogui.hotkey('ctrl', 'f4')
        return False

    def change_email(self):
        # click_to("cookies_alive_1.PNG")
        # click_to("setting_dropdown.PNG", interval=2, confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        click_to("settings_page.PNG", confidence=0.8)
        x, y, btn_idx = deciscion(["cai_dat_tai_khoan.PNG", 'cai_dat_chung.PNG', "cai_dat_chung_1.PNG"], confidence=0.7)
        pyautogui.click(x, y)
        self.email_outlook, self.email_password = get_email()
        print(self.email_outlook, self.email_password)
        contact_x, contact_y = waiting_for("contact.PNG")
        time.sleep(2)
        click_to("modify_phone.PNG", region=(contact_x + 780, contact_y - 20, 200, 40), confidence=0.7, check_close=False)
        click_to("add_phone_btn.PNG", confidence=0.7)
        click_to("new_email_inp.PNG")
        paste_text(self.email_outlook)
        click_to("add_new_email.PNG")

        waiting_for("nhap lai mat khau.PNG", waiting_time=30)
        if check_exist("nhap lai mat khau.PNG"):
            paste_text("Minh1234@")
            click_to("send_password.PNG")

        if not check_exist("email_already_used.PNG"):
            waiting_for("add_new_email_success.PNG")
            # click_to("close_dialog.PNG")
            href, otp = get_out_look(self.email_outlook, self.email_password)
            pyautogui.click(x=1738, y=517)
            pyautogui.hotkey('ctrl', 't', interval=1)
            clipboard.copy(href)
            pyautogui.hotkey('ctrl', 'v', interval=1)
            pyautogui.press('enter')
            waiting_for("cookies_alive_1.PNG")
            return True
        else:
            click_to("close_dialog.PNG")

        return False

    @staticmethod
    def remove_old_contact():
        # click_to("cookies_alive_1.PNG")
        # click_to("setting_dropdown.PNG", interval=2, confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        click_to("settings_page.PNG", confidence=0.8)
        x, y, btn_idx = deciscion(["cai_dat_tai_khoan.PNG", 'cai_dat_chung.PNG', "cai_dat_chung_1.PNG"], confidence=0.7)
        pyautogui.click(x, y)
        contact = waiting_for("contact.PNG")
        if contact:
            contact_x, contact_y = contact
            time.sleep(1)
            click_to("modify_phone.PNG", region=(contact_x + 780, contact_y - 20, 200, 40), confidence=0.7, check_close=False)
            click_many("remove_old_email.PNG", confidence=0.8)
            pyautogui.press('f5')

    def change_2fa_code(self):
        # click_to("setting_dropdown.PNG", interval=2, confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        # click_to("setting_icon.PNG", confidence=0.85)
        click_to("settings_page.PNG", confidence=0.8)
        # x, y, btn_idx = deciscion(['account_proteted.PNG'], confidence=0.7)
        # pyautogui.click(x, y, interval=1)
        click_to('account_proteted.PNG', confidence=0.9)
        waiting_for("account_proteted_title.PNG", confidence=0.7)
        use_2fa_x, use_2fa_y = waiting_for("use_2fa.PNG")
        click_to("modify_2fa.PNG", region=(use_2fa_x + 500, use_2fa_y - 20, 400, 100))
        time.sleep(5)
        region_x, region_y, btn_index = deciscion(["use_application_authenticator.PNG", "ung_dung_xac_thuc.PNG"])
        if btn_index == 0 or check_exist("use_application_authenticator.PNG", confidence=0.75):
            click_to("use_application_authenticator.PNG", confidence=0.75)
        else:
            # Xác thực 2 yếu tố đang bật
            btns = ["thiet_lap.PNG", "quan_ly_2fa.PNG"]
            x, y, btn_index = deciscion(btns, region=(region_x, region_y - 50, 1000, 70))
            click_to(btns[btn_index], region=(region_x, region_y - 50, 1000, 70))
            if btn_index == 1:
                click_to("add_new_2fa.PNG", region=(region_x, region_y - 50, 1000, 150))

        waiting_for("next_btn_otp.PNG")
        pyautogui.moveTo(989, 540)
        pyautogui.dragTo(1183, 610, 1, button='left')
        pyautogui.hotkey('ctrl', 'c')
        self.secret_key = clipboard.paste().strip().replace(' ', '')
        totp = pyotp.TOTP(self.secret_key)
        print("Current OTP:", totp.now())
        click_to("next_btn_otp.PNG", interval=5, check_close=False)
        clipboard.copy(totp.now())
        pyautogui.hotkey('ctrl', 'v')
        x, y, _ = deciscion(["2fa_enabled.PNG", "otp_done.PNG", 'input_otp_success_1.PNG'])
        pyautogui.click(x, y, interval=1)

    def sign_out_sessions(self):
        click_to("settings_page.PNG", confidence=0.8)
        click_to('account_proteted.PNG', confidence=0.9)
        if waiting_for("xem_them.PNG", waiting_time=20):
            click_to("xem_them.PNG", confidence=0.8)
            while True:
                if check_exist("logout_all_devices.PNG", confidence=0.8):
                    click_to("logout_all_devices.PNG", confidence=0.8)
                    break
                pyautogui.scroll(-300)
                time.sleep(0.5)
            click_to("sign_out.PNG")

    def set_mail_contact(self):
        click_to("settings_page.PNG", confidence=0.8)
        x, y, btn_idx = deciscion(["cai_dat_tai_khoan.PNG", 'cai_dat_chung.PNG', "cai_dat_chung_1.PNG"], confidence=0.7)
        pyautogui.click(x, y)
        contact = waiting_for("contact.PNG")
        if contact:
            contact_x, contact_y = contact
            time.sleep(1)
            click_to("modify_phone.PNG", region=(contact_x + 780, contact_y - 20, 200, 40), confidence=0.7,
                     check_close=False)
            click_to("chon_lam_email_chinh.PNG")

    def reset_cookies(self):
        # clear cookies
        if self.cookie is not None:
            logger.debug(f"reset cookies: {self.cookie['_id']}")
            myquery = {"_id": self.cookie['_id']}
            newvalues = {"$set": {"used": False}}
            cookies_table.update_one(myquery, newvalues)

    def save_results(self):
        pyautogui.hotkey('ctrl', 'w')
        with open("old_via/via-4-7.txt", 'a', encoding='utf-8') as output_file:
            output_file.write(f"{self.fb_id}|Minh1234@|{self.secret_key}|{self.email_outlook}|{self.email_password}|{self.phone_number}\n")
            output_file.close()

        # clear cookies
        myquery = {"_id": self.cookie['_id']}
        newvalues = {"$set": {"used": True}}
        cookies_table.update_one(myquery, newvalues)

        insert_dict = {
            "_id": str(uuid.uuid4()),
            "fb_id": self.fb_id,
            "password": "Minh1234@",
            "secret_key": self.secret_key,
            "email": self.email_outlook,
            "email_password": self.email_password,
            "phone_number": self.phone_number,
            "cookies": self.cookie['cookie']
        }
        via_share_table.insert_one(insert_dict)

    def start_job(self):
        try:
            worker.change_ip()
            worker.show_meta_data()
            time.sleep(10)

            # get cookies
            status = worker.import_cookies()
            worker.show_meta_data()
            if not status:
                self.reset_cookies()
                return False

            worker.check_dark_light_theme()
            worker.show_meta_data()
            worker.change_language()
            worker.show_meta_data()

            # remove old contact

            # change phone and forgot password
            status = worker.change_phone()
            worker.show_meta_data()
            if not status:
                self.reset_cookies()
                return False

            # update current email
            status = worker.change_email()
            worker.show_meta_data()
            if not status:
                self.reset_cookies()
                return False

            worker.show_meta_data()
            worker.change_2fa_code()
            worker.show_meta_data()
            worker.save_results()
            worker.clear_metadata()
            worker.sign_out_sessions()
            worker.remove_old_contact()

            # set mail email
            # worker.set_mail_contact()
            return True
        except Exception as ex:
            print(ex)
            worker.reset_cookies()


if __name__ == '__main__':
    while True:
        st = time.time()
        worker = AutoVia()
        worker.start_job()
        et = time.time()
        print(f"Time consuming {(et - st)/60} min")
