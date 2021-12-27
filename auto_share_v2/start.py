import json
import os
import random
import threading
import time
import uuid
import logging
from datetime import datetime
import PySimpleGUI as sg
import sqlalchemy as db
import pandas as pd

from share import auto_share
from models import via_share, scheduler_video, connection, joining_group
from helper import ChromeHelper

# create logger with 'spam_application'
logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


def start_share(main_window, stop_thread):
    # Step 1 query all via live
    while True:
        video_sharing = connection.execute(db.select([scheduler_video]).where(scheduler_video.columns.shared == False)).fetchone()
        if not video_sharing:
            return True
        video_sharing = dict(zip(video_sharing.keys(), video_sharing))
        video_id = video_sharing.get('video_id')
        groups_shared = video_sharing.get('groups_shared', None)
        shared = video_sharing.get('shared', False)
        go_enable = video_sharing.get('go', False)
        co_khi_enable = video_sharing.get('co_khi', False)
        xay_dung_enable = video_sharing.get('xay_dung', False)
        options_enable = video_sharing.get('options', False)

        # query via live
        results = connection.execute(db.select([via_share]).where(db.and_(
            via_share.columns.status == 'live',
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
        # reset via share counting
        if share_date != current_date:
            query = db.update(via_share).values(date=current_date, share_number=0)
            query = query.where(via_share.columns.id == fb_id)
            connection.execute(query)

        # mark via running
        query = db.update(via_share).values(status='sharing')
        query = query.where(via_share.columns.id == fb_id)
        connection.execute(query)
        # start sharing
        chrome_worker = ChromeHelper(fb_id, password, mfa, proxy_data)
        try:

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

            share_status = chrome_worker.sharing(video_id, groups_share, fb_id, via_share_number)
        except Exception as ex:
            print(ex)
        finally:
            chrome_worker.driver.close()

        time.sleep(1)


def mapping_table(item):
    return [
        item.get('video_id', ''),
        item.get('share_number', 0),
        item.get('shared', False),
        item.get('go', False),
        item.get('co_khi', False),
        item.get('xay_dung', False),
        item.get('options', False),
    ]


def mapping_via_table(item):
    # # 'id', 'password', '2fa', "email", "email password", "proxy", "status"
    return [
        item.get('fb_id', ''),
        item.get('password', ''),
        item.get('mfa', ''),
        item.get('email', ''),
        item.get('email_password', ''),
        item.get('proxy', ''),
        item.get('status', ''),
    ]


def get_scheduler_data():
    results = connection.execute(db.select([scheduler_video])).fetchall()
    if len(results) == 0:
        return []
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    table_default = list(map(mapping_table, df.to_dict(orient='records')))
    return table_default


def get_group_joining_data(group_type):
    results = connection.execute(
        db.select([joining_group]).where(joining_group.columns.group_type == group_type)).fetchall()
    groups = [result.name for result in results if result.name.strip() != '']
    data_group_join = "\n".join(groups)
    return data_group_join


def get_via_data():
    # 'id', 'password', '2fa', "email", "email password", "proxy", "status"
    results = connection.execute(db.select([via_share])).fetchall()
    if len(results) == 0:
        return []
    df = pd.DataFrame(results)
    df.columns = results[0].keys()
    table_default = list(map(mapping_via_table, df.to_dict(orient='records')))
    return table_default


def make_main_window(table_data):
    headings = ['video_id', 'share group', 'share done', "Gỗ", "Cơ Khí", "Xây Dựng", "Tùy Chọn"]
    layout = [
        [
            sg.Button('Start share'),
            sg.Button('Remove'),
            sg.Button('Add New Video'),
            sg.Button('Kill Chrome'),
            sg.Button('Via Management'),
            sg.Checkbox('Join group when sharing video', key='join_group', enable_events=False, default=False),
            sg.Button('Edit list group'),
            sg.Button('Edit Share Descriptions')
        ],
        [
            sg.Table(values=table_data,
                     headings=headings,
                     display_row_numbers=True,
                     justification='right',
                     auto_size_columns=False,
                     col_widths=[20, 20, 15],
                     vertical_scroll_only=False,
                     num_rows=24, key='table')
        ]
    ]
    # Create the Window
    return sg.Window('Auto Share', layout, finalize=True)


def add_vid_window():
    layout_add_video = [
        [sg.Text('Video ID'), sg.Multiline(size=(30, 5), key="video_id"), sg.Button('Them')],
        [
            sg.Checkbox(
                'Gỗ', key='groups.go', enable_events=False, default=True),
            sg.Checkbox(
                'Cơ Khí', key='groups.co_khi', enable_events=False, default=True),
            sg.Checkbox(
                'Xây Dựng', key='groups.xay_dung', enable_events=False, default=True),
            sg.Checkbox(
                'Tùy Chọn', key='groups.options', enable_events=False, default=True),
        ]
    ]

    return sg.Window('Add Video', layout_add_video, finalize=True)


def via_manage_window(via_data):
    headings = ['fb_id', 'password', '2fa', "email", "email password", "proxy", "status"]
    layout_via_manage_video = [
        [sg.Text("Browser file: "), sg.FileBrowse(key='file_via_input', enable_events=True),
         sg.Button('Start login via'),
         sg.Checkbox('Login when adding', key='login.options', enable_events=False, default=True)],
        [
            sg.Table(values=via_data,
                     headings=headings,
                     display_row_numbers=True,
                     justification='right',
                     auto_size_columns=False,
                     vertical_scroll_only=False,
                     num_rows=24, key='via_table')
        ],
        [sg.Button('Open in Browser'),
         sg.Button('Edit', key='edit_via_btn'),
         sg.Button('Start Login', key='login_via_manual'),
         sg.Button('Export', key="export_checkpoint_via_btn"),
         sg.Button('Delete', key="delete_via")]

    ]

    return sg.Window('Via Management', layout_via_manage_video, finalize=True)


def group_to_join_window(join_group, group_go, group_co_khi, group_xay_dung):
    layout_group_to_join = [
        [
            [
                sg.Text('Gỗ'),
                sg.Multiline(size=(40, 10), key="group_go", default_text=group_go),
                sg.Text('Cơ khí'),
                sg.Multiline(size=(40, 10), key="group_co_khi", default_text=group_co_khi),
                sg.Text('Xây Dựng'),
                sg.Multiline(size=(40, 10), key="group_xay_dung", default_text=group_xay_dung),
                sg.Text('Join khi share'),
                sg.Multiline(size=(40, 10), key="group_join", default_text=join_group)
            ],
        ],
        [
            sg.Button('Ok', key="group_modified")
        ]
    ]
    return sg.Window('Group Join', layout_group_to_join, finalize=True)


def text_seo_window(text_seo_data):
    layout_text_seo_window = [
        [sg.Multiline(size=(40, 10), key="share_description_data", default_text=text_seo_data)],
        [sg.Button('Ok', key="text_seo_modified")]
    ]
    return sg.Window('Share descriptions', layout_text_seo_window, finalize=True)


def edit_via_window(via_data):
    fb_id, password, mfa, email, email_password, proxy_data, status = via_data
    layout_edit_via = [
        [sg.Text('Via ID')],
        [sg.InputText(fb_id, key="edit_via_id", readonly=True)],
        [sg.Text('password')],
        [sg.InputText(password, key="edit_via_password")],
        [sg.Text('mfa')],
        [sg.InputText(mfa, key="edit_via_mfa")],
        [sg.Text('email')],
        [sg.InputText(email, key="edit_via_email")],
        [sg.Text('email_password')],
        [sg.InputText(email_password, key="edit_via_email_password")],
        [sg.Text('proxy_data')],
        [sg.InputText(proxy_data, key="edit_via_proxy_data")],
        [sg.Text('status')],
        [sg.Listbox(default_values=status, values=['live', 'checkpoint', 'can not login'], size=(20, 4), enable_events=False, key='_LIST_VIA_STATUS_')],
        [sg.Button('Save', key='edit_via_save')]
    ]
    window = sg.Window('Edit Via Data', layout_edit_via, finalize=True)

    return window


def create_browser():
    chrome_worker = ChromeHelper(fb_id, password, mfa, proxy_data)


if __name__ == '__main__':
    # time.sleep(2)
    # print(pyautogui.position())

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    table_data = get_scheduler_data()
    window1, window2, window3, window4, window5, window6 = make_main_window(table_data), None, None, None, None, None

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        window, event, values = sg.read_all_windows()
        print(f'{event} You entered {values}')
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            if window:
                window.close()
            else:
                break
        elif event == 'Kill Chrome':
            #chromedriver.exe
            browserExe = "chrome.exe"
            os.system("taskkill /f /im " + browserExe)
            browserExe = "chromedriver.exe"
            os.system("taskkill /f /im " + browserExe)
        elif event == 'Start share':
            window1.Element('Start share').Update(text="Sharing")
            stop_threads = False
            table_data = window1.Element('table').Get()
            for _ in range(1):
                thread = threading.Thread(
                    target=auto_share,
                    daemon=True
                )
                thread.start()
                time.sleep(5)
        elif event == 'Remove':
            removed = values['table']
            table_data = window1.Element('table').Get()
            for idx in reversed(removed):
                video_id = table_data[idx][0]
                # print(video_id)
                query = db.delete(scheduler_video).where(scheduler_video.columns.video_id == video_id)
                results = connection.execute(query)
                # table_data.pop(item)
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
        elif event == '-THREAD-':
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
        elif event == 'Them':
            # them video
            video_ids = str(values['video_id']).strip().split('\n')
            for video_id in video_ids:
                if video_id != "":
                    query = db.delete(scheduler_video).where(scheduler_video.columns.video_id == video_id)
                    results = connection.execute(query)
                    query = db.insert(scheduler_video).values(
                        video_id=video_id, created_date=int(time.time()),
                        go=values.get("groups.go", False), co_khi=values.get("groups.co_khi", False),
                        xay_dung=values.get("groups.xay_dung", False), options=values.get("groups.options", False),
                        groups_shared=json.dumps([])
                    )
                    ResultProxy = connection.execute(query)
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
            sg.Popup('Them thanh cong', keep_on_top=True)
        elif event == "Add New Video":
            window2 = add_vid_window()
        elif event == "Via Management":
            via_data = get_via_data()
            window3 = via_manage_window(via_data)
        elif event == "Edit list group":
            join_group = get_group_joining_data('join_group')
            group_go = get_group_joining_data('group_go')
            group_co_khi = get_group_joining_data('group_co_khi')
            group_xay_dung = get_group_joining_data('group_xay_dung')
            window4 = group_to_join_window(join_group, group_go, group_co_khi, group_xay_dung)
        elif event == "group_modified":
            group_join = values.get("group_join", "").split('\n')
            groups = [{"name": group.strip(), "group_type": "join_group"} for group in group_join if
                      group.strip() != '']

            group_go = values.get("group_go", "").split('\n')
            groups.extend(
                [{"name": group.strip(), "group_type": "group_go"} for group in group_go if group.strip() != ''])

            group_co_khi = values.get("group_co_khi", "").split('\n')
            groups.extend([{"name": group.strip(), "group_type": "group_co_khi"} for group in group_co_khi if
                           group.strip() != ''])

            group_xay_dung = values.get("group_xay_dung", "").split('\n')
            groups.extend([{"name": group.strip(), "group_type": "group_xay_dung"} for group in group_xay_dung if
                           group.strip() != ''])

            # remove all exist
            query = db.delete(joining_group).where(joining_group.columns.group_type != "share_description_data")
            results = connection.execute(query)

            # update new
            query = db.insert(joining_group)
            if len(groups) > 0:
                ResultProxy = connection.execute(query, groups)
                sg.Popup('Successfully', keep_on_top=True)
                window4.close()

        elif event == "delete_via":
            removed = values['via_table']
            table_data = window3.Element('via_table').Get()
            for idx in reversed(removed):
                fb_id = table_data[idx][0]
                # print(video_id)
                query = db.delete(via_share).where(via_share.columns.fb_id == fb_id)
                results = connection.execute(query)
                # table_data.pop(item)
            table_data = get_via_data()
            window3.Element('via_table').Update(values=table_data)
        elif event == 'export_checkpoint_via_btn':
            via_table_data = window3.Element('via_table').Get()
            if os.path.isfile("checkpoint.txt"):
                os.remove("checkpoint.txt")
            with open("checkpoint.txt", mode='w') as cp_via_files:
                for via_data in via_table_data:
                    fb_id, password, mfa, email, email_password, proxy_data, status = via_data
                    if status and status.strip() == 'checkpoint':
                        cp_via_files.write(f'{fb_id},{password},{mfa},{email},{email_password},{proxy_data}\n')
            cp_via_files.close()
            sg.Popup('Exported, file checkpoint.txt in your code directory.', keep_on_top=True)
        elif event == 'edit_via_btn':
            selected = values['via_table']
            table_data = window3.Element('via_table').Get()
            for idx in selected:
                via_data = table_data[idx]
                window6 = edit_via_window(via_data)
                break
        elif event == 'login_via_manual':
            """Open single via and login manual"""
            selected = values['via_table']
            table_data = window3.Element('via_table').Get()
            for idx in selected:
                via_data = table_data[idx]
                fb_id, password, mfa, email, email_password, proxy_data, status = via_data
                via_status = "not ready"
                # force close drive
                try:
                    chrome_worker.driver.close()
                except:
                    pass

                chrome_worker = ChromeHelper(fb_id, password, mfa, proxy_data)
                try:
                    chrome_worker.login()
                    # login success
                    via_status = "live"
                    query = db.update(via_share).values(
                        status=via_status
                    ).where(via_share.columns.fb_id == fb_id)
                    connection.execute(query)
                except Exception as ex:
                    via_status = "can not login"
                    print(ex)
                chrome_worker.driver.close()

        elif event == 'edit_via_save':
            """
            {'edit_via_id': '100062931873023', 
            'edit_via_password': 'kaxcsvrurs', 
            'edit_via_mfa': 'KXAWBLA5SQAHAOXUQ654F7KOIV2Z5HUM',
            'edit_via_email': 'eileendawnlew@hotmail.com', 
            'edit_via_email_password': 'wAvrbwjwvo7', 
            'edit_via_proxy_data': '107.181.160.6:21516:huyduc399:3b4i7mMN', 
            '_LIST_VIA_STATUS_': ['can not login']}
            """
            if not window3:
                continue

            table_data = window3.Element('via_table').Get()
            table_data_copy = table_data
            edit_via_id = values.get("edit_via_id", "").strip()
            edit_via_password = values.get("edit_via_password", "").strip()
            edit_via_mfa = values.get("edit_via_mfa", "").strip()
            edit_via_email = values.get("edit_via_email", "").strip()
            edit_via_email_password = values.get("edit_via_email_password", "").strip()
            edit_via_proxy_data = values.get("edit_via_proxy_data", "").strip()
            edit_via_status = values.get("_LIST_VIA_STATUS_", [])
            if len(edit_via_status) == 0:
                status_via = 'can not login'
            else:
                status_via = edit_via_status[0].strip()

            via_idx = 0
            for via_idx, via_data in enumerate(table_data):
                fb_id, password, mfa, email, email_password, proxy_data, status = via_data
                if fb_id == edit_via_id:
                    new_via_data = edit_via_id, edit_via_password, edit_via_mfa, edit_via_email, edit_via_email_password, edit_via_proxy_data, status_via
                    table_data_copy[via_idx] = [fb_id, edit_via_password, edit_via_mfa, edit_via_email, edit_via_email_password, edit_via_proxy_data, status_via]
                    query = db.update(via_share).values(
                        password=edit_via_password, mfa=edit_via_mfa,
                        email=edit_via_email, email_password=edit_via_email_password,
                        proxy=edit_via_proxy_data,
                        status=status_via
                    ).where(via_share.columns.fb_id == fb_id)
                    connection.execute(query)
                    break

            window3.Element('via_table').Update(values=table_data_copy, select_rows=[via_idx])

            if window6:
                window6.close()

        elif event == 'Start login via':
            file_input = values.get('file_via_input')
            if not os.path.isfile(file_input):
                sg.Popup('File not exist', keep_on_top=True)
                continue
            with open(file_input) as via_files:
                for via in via_files:
                    user_data = via.strip().split('|')
                    if len(user_data) != 6:
                        sg.Popup(
                            f'Via Format khong dung: fb_id|password|mfa|email|email_password|ProxyIP:ProxyPORT:ProxyUsername:ProxyPassword',
                            keep_on_top=True)
                        break
                    fb_id, password, mfa, email, email_password, proxy_data = user_data
                    proxy_data_split = proxy_data.split(":")
                    if len(proxy_data_split) != 4:
                        sg.Popup(
                            f'Via Format khong dung: fb_id|password|mfa|email|email_password|ProxyIP:ProxyPORT:ProxyUsername:ProxyPassword',
                            keep_on_top=True)
                        break

                    via_exist = connection.execute(db.select([via_share]).where(via_share.columns.fb_id == fb_id.strip())).fetchone()
                    if via_exist:
                        continue

                    via_status = "not ready"
                    if values.get('login.options', False):
                        chrome_worker = ChromeHelper(fb_id, password, mfa, proxy_data)
                        try:
                            chrome_worker.login()
                            # login success
                            via_status = "live"

                        except Exception as ex:
                            via_status = "can not login"
                            print(ex)
                        chrome_worker.driver.close()
                    query = db.insert(via_share).values(
                        fb_id=fb_id, password=password, mfa=mfa,
                        email=email, email_password=email_password,
                        proxy=proxy_data, share_number=0,
                        group_joined=json.dumps([""]), date="",
                        status=via_status
                    )
                    ResultProxy = connection.execute(query)
            via_data = get_via_data()
            window3.Element('via_table').Update(values=via_data)
        elif event == "Open in Browser":
            via_selected = values.get('via_table')
            via_table_data = window3.Element('via_table').Get()
            for via_idx in via_selected:
                via_data = via_table_data[via_idx]
                try:
                    chrome_worker.driver.close()
                except Exception as ex:
                    logger.error(ex)
                    pass

                fb_id, password, mfa, email, email_password, proxy_data, status = via_data
                chrome_worker = ChromeHelper(fb_id, password, mfa, proxy_data)
                #job_thread = threading.Thread(target=create_browser, daemon=True)
                #job_thread.start()
                time.sleep(1)
        elif event == "Edit Share Descriptions":
            share_descriptions = get_group_joining_data('share_descriptions')
            window5 = text_seo_window(share_descriptions)
        elif event == "text_seo_modified":
            share_description = values.get("share_description_data", "").split('\n')
            groups = [{"name": name.strip(), "group_type": "share_descriptions"} for name in share_description if
                      name.strip() != '']
            # remove all exist
            query = db.delete(joining_group).where(joining_group.columns.group_type == "share_description_data")
            results = connection.execute(query)

            # update new
            query = db.insert(joining_group)
            ResultProxy = connection.execute(query, groups)
    for window in [window1, window2, window3, window4, window5, window6]:
        if window:
            window.close()
