import json
import os
import random
import threading
import time
import uuid
from datetime import datetime
import PySimpleGUI as sg
import pyautogui
import sqlalchemy as db

# from models import via_share, scheduler_video, connection, joining_group
from bson import ObjectId

from helper import ChromeHelper
from utils import logger, get_scheduler_data, get_via_data, \
    get_group_joining_data, scheduler_table, via_share, joining_group
from controller import thread_join_group


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
        # query via live
        # results = connection.execute(db.select([via_share]).where(db.and_(
        #     via_share.columns.status == 'live',
        #     via_share.columns.share_number < 4
        # ))).fetchall()
        results = via_share.find({"status": 'live', "share_number": {"$lte": 4}})
        results = list(results)
        if len(results) == 0:
            continue

        via_data = random.choice(results)
        current_date = str(datetime.date(datetime.now()))
        # via_data = dict(zip(result.keys(), result))

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


def make_main_window(table_data):
    headings = ['video_id', 'share group', 'share done', "Gỗ", "Cơ Khí", "Xây Dựng", "Tùy Chọn"]
    layout = [
        [
            sg.Button('Start share'),
            sg.Button('Remove'),
            sg.Button('Add New Video'),
            sg.Button('Kill Chrome'),
            sg.Button('Via Management'),
            sg.Button('Edit list group'),
            sg.Button('Start Join Group'),
            sg.Button('Edit Share Descriptions')
        ],
        [
            sg.Table(values=table_data,
                     headings=headings,
                     display_row_numbers=True,
                     justification='right',
                     auto_size_columns=False,
                     col_widths=[20, 20, 15, 15, 15, 15, 15],
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
         sg.Checkbox('Import existed via', key='login.options', enable_events=False, default=False)],
        [
            sg.Table(values=via_data,
                     headings=headings,
                     display_row_numbers=True,
                     justification='right',
                     auto_size_columns=False,
                     col_widths=[15, 15, 15, 15, 15, 15, 15],
                     vertical_scroll_only=False,
                     num_rows=24, key='via_table')
        ],
        [sg.Button('Open in Browser'),
         sg.Button('Edit', key='edit_via_btn'),
         sg.Button('Export', key="export_checkpoint_via_btn"),
         sg.Button('Delete', key="delete_via")]
    ]

    return sg.Window('Via Management', layout_via_manage_video, finalize=True)


def group_to_join_window(join_group, group_go, group_co_khi, group_xay_dung):
    layout_group_to_join = [
        [
            [
                [sg.Text('Gỗ')],
                [sg.Multiline(size=(100, 10), key="group_go", default_text=group_go)],
                [sg.Text('Cơ khí')],
                [sg.Multiline(size=(100, 10), key="group_co_khi", default_text=group_co_khi)]
             ],
            [
                [sg.Text('Xây Dựng')],
                [sg.Multiline(size=(100, 10), key="group_xay_dung", default_text=group_xay_dung)],
                [sg.Text('Group for joining')],
                [sg.Multiline(size=(100, 10), key="group_join", default_text=join_group)]
            ]
        ],
        [
            sg.Button('Save', key="group_modified")
        ]
    ]
    return sg.Window('Group Join', layout_group_to_join, finalize=True)


def text_seo_window(text_seo_data):
    layout_text_seo_window = [
        [sg.Multiline(size=(200, 20), key="share_description_data", default_text=text_seo_data)],
        [sg.Button('Save', key="text_seo_modified")]
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
        [sg.Listbox(default_values=status, values=['live', 'checkpoint', 'can not login', 'disable', 'join group'], size=(20, 5), enable_events=False, key='_LIST_VIA_STATUS_')],
        [sg.Button('Save', key='edit_via_save')]
    ]
    window = sg.Window('Edit Via Data', layout_edit_via, finalize=True)

    return window


if __name__ == '__main__':
    # time.sleep(2)
    # print(pyautogui.position())

    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    table_data = get_scheduler_data()
    window1, window2, window3, window4, window5, window6 = make_main_window(table_data), None, None, None, None, None
    # chrome_worker = ChromeHelper()
    stop_join_group = False
    sharing = False
    joining = False
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        window, event, values = sg.read_all_windows()
        logger.debug(f'{event} You entered {values}')
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            if window:
                window.close()
            else:
                break
        elif event == 'Kill Chrome':
            browserExe = "chrome.exe"
            os.system("taskkill /f /im " + browserExe)
            browserExe = "chromedriver.exe"
            os.system("taskkill /f /im " + browserExe)
        elif event == 'Start share':
            if not sharing:
                sharing = True
                window1.Element('Start share').Update(text="Stop Share")
                stop_threads = False
                threads = []
                via_share.update({"status": 'sharing'}, {"$set": {"status": "live"}})
                for _ in range(5):
                    thread = threading.Thread(target=start_share,
                                              args=(window1, lambda: stop_threads), daemon=True)
                    threads.append(thread)
                for thread in threads:
                    thread.start()
            else:
                stop_threads = True
                sharing = False
                window1.Element('Start share').Update(text="Start share")
        elif event == 'Remove':
            removed = values['table']
            table_data = window1.Element('table').Get()
            for idx in reversed(removed):
                video_id = table_data[idx][0]
                # print(video_id)
                scheduler_table.delete_one({"video_id": video_id})
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
                    # query = db.delete(scheduler_video).where(scheduler_video.columns.video_id == video_id)
                    # results = connection.execute(query)
                    # query = db.insert(scheduler_video).values(
                    #     video_id=video_id, created_date=int(time.time()),
                    #     go=values.get("groups.go", False), co_khi=values.get("groups.co_khi", False),
                    #     xay_dung=values.get("groups.xay_dung", False), options=values.get("groups.options", False),
                    #     groups_shared=json.dumps([])
                    # )
                    # ResultProxy = connection.execute(query)
                    exist_scheduler = scheduler_table.find_one({"video_id": video_id})
                    if exist_scheduler:
                        scheduler_table.update_one({"_id": exist_scheduler['_id']}, {"$set": {
                            "shared": False,
                            "go_enable": values.get("groups.go", False),
                            "co_khi_enable": values.get("groups.co_khi", False),
                            "xay_dung_enable": values.get("groups.xay_dung", False),
                            "options_enable": values.get("groups.options", False)
                        }})
                        continue

                    new_scheduler = {
                        "_id": str(uuid.uuid4()),
                        "video_id": video_id,
                        "scheduler_time": datetime.now().timestamp(),
                        "create_date": datetime.now().timestamp(),
                        "shared": False,
                        "share_number": 0,
                        "title_shared": [],
                        "groups_shared": [],
                        "go_enable": values.get("groups.go", False),
                        "co_khi_enable": values.get("groups.co_khi", False),
                        "xay_dung_enable": values.get("groups.xay_dung", False),
                        "options_enable": values.get("groups.options", False)
                    }

                    result = scheduler_table.insert_one(new_scheduler)
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
            sg.Popup('Them thanh cong', keep_on_top=True)
            window2.close()
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
            groups = [{"_id": str(ObjectId()), "name": group.strip(), "group_type": "join_group"} for group in group_join if
                      group.strip() != '']

            group_go = values.get("group_go", "").split('\n')
            groups.extend(
                [{"_id": str(ObjectId()), "name": group.strip(), "group_type": "group_go"} for group in group_go if group.strip() != ''])

            group_co_khi = values.get("group_co_khi", "").split('\n')
            groups.extend(
                [{"_id": str(ObjectId()), "name": group.strip(), "group_type": "group_co_khi"} for group in group_co_khi if
                           group.strip() != ''])

            group_xay_dung = values.get("group_xay_dung", "").split('\n')
            groups.extend(
                [{"_id": str(ObjectId()), "name": group.strip(), "group_type": "group_xay_dung"} for group in group_xay_dung if
                           group.strip() != ''])

            # remove all exist
            # query = db.delete(joining_group).where(joining_group.columns.group_type != "share_description_data")
            # results = connection.execute(query)
            joining_group.delete_many({"group_type": "join_group"})
            joining_group.delete_many({"group_type": "group_go"})
            joining_group.delete_many({"group_type": "group_co_khi"})
            joining_group.delete_many({"group_type": "group_xay_dung"})

            # update new
            joining_group.insert_many(groups)
            sg.Popup('Successfully', keep_on_top=True)
            window4.close()
        elif event == "delete_via":
            removed = values['via_table']
            table_data = window3.Element('via_table').Get()
            label = pyautogui.confirm(text='Are you sure?', title='', buttons=["yes", "no"])
            if label == "no":
                continue

            for idx in reversed(removed):
                fb_id = table_data[idx][0]
                # print(video_id)
                via_share.delete_one({"fb_id": fb_id})
                # query = db.delete(via_share).where(via_share.columns.fb_id == fb_id)
                # results = connection.execute(query)
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
                    if status and status.strip() not in ['live', 'sharing', 'join group']:
                        cp_via_files.write(f'{fb_id}|{password}|{mfa}|{email}|{email_password}|{proxy_data}\n')
            cp_via_files.close()
            sg.Popup('Exported, file checkpoint.txt in your code directory.', keep_on_top=True)
        elif event == 'edit_via_btn':
            selected = values['via_table']
            table_data = window3.Element('via_table').Get()
            for idx in selected:
                via_data = table_data[idx]
                window6 = edit_via_window(via_data)
                break
        # elif event == 'login_via_manual':
        #     """Open single via and login manual"""
        #     selected = values['via_table']
        #     table_data = window3.Element('via_table').Get()
        #     for idx in selected:
        #         via_data = table_data[idx]
        #         fb_id, password, mfa, email, email_password, proxy_data, status = via_data
        #         via_status = "not ready"
        #         # force close drive
        #         try:
        #             chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
        #             chrome_worker.login()
        #             # login success
        #             via_status = "live"
        #             # query = db.update(via_share).values(
        #             #     status=via_status
        #             # ).where(via_share.columns.fb_id == fb_id)
        #             # connection.execute(query)
        #             via_share.update_one({"fb_id": fb_id}, {"status": via_status})
        #         except Exception as ex:
        #             via_status = "can not login"
        #             print(ex)
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
                    # query = db.update(via_share).values(
                    #     password=edit_via_password, mfa=edit_via_mfa,
                    #     email=edit_via_email, email_password=edit_via_email_password,
                    #     proxy=edit_via_proxy_data,
                    #     status=status_via
                    # ).where(via_share.columns.fb_id == fb_id)
                    # connection.execute(query)
                    via_share.update_one(
                        {"fb_id": fb_id},
                        {"$set": {
                            "password": edit_via_password,
                            "mfa": edit_via_mfa,
                            "email": edit_via_email,
                            "email_password": edit_via_email_password,
                            "proxy": edit_via_proxy_data,
                            "status": status_via
                        }}
                    )
                    break

            window3.Element('via_table').Update(values=table_data_copy, select_rows=[via_idx])

            if window6:
                window6.close()
        elif event == 'Start login via':
            file_input = values.get('file_via_input')
            if not os.path.isfile(file_input):
                sg.Popup('File not exist', keep_on_top=True)
                continue
            start_login_thread = threading.Thread(target=start_login_via,
                                                  args=(window3, file_input, values.get('login.options', False)), daemon=True)
            start_login_thread.start()
        elif event == "Open in Browser":
            via_selected = values.get('via_table')
            via_table_data = window3.Element('via_table').Get()
            for via_idx in via_selected:
                via_data = via_table_data[via_idx]
                fb_id, password, mfa, email, email_password, proxy_data, status = via_data
                # chrome_worker = get_free_worker()
                try:
                    default_chrome_worker = ChromeHelper()
                    default_chrome_worker.open_chrome(fb_id, password, mfa, proxy_data)
                    break
                except Exception as ex:
                    logger.error(f"Can not open browser {ex}")
        elif event == "Edit Share Descriptions":
            share_descriptions = get_group_joining_data('share_descriptions')
            window5 = text_seo_window(share_descriptions)
        elif event == "text_seo_modified":
            share_description = values.get("share_description_data", "").split('\n')
            groups = [{"_id": str(ObjectId()), "name": name.strip(), "group_type": "share_descriptions"} for name in share_description if
                      name.strip() != '']
            # remove all exist
            joining_group.delete_many({"group_type": "share_descriptions"})
            # query = db.delete(joining_group).where(joining_group.columns.group_type == "share_description_data")
            # results = connection.execute(query)

            # update new
            # query = db.insert(joining_group)
            # ResultProxy = connection.execute(query, groups)
            joining_group.insert_many(groups)
            sg.Popup('Luu Thanh Cong')
            window5.close()
        elif event == 'Start Join Group':
            if not joining:
                stop_join_group = False
                joining_threads = []
                via_share.update_one({"status": "join group"}, {"$set": {"status": 'live'}})
                for _ in range(5):
                    thread_join_gr = threading.Thread(target=thread_join_group,
                                                      args=(lambda: stop_join_group,), daemon=True)
                    joining_threads.append(thread_join_gr)

                for thread_join_gr in joining_threads:
                    thread_join_gr.start()
                window1.Element('Start Join Group').Update(text="Stop Join Group")
            else:
                stop_join_group = True
                window1.Element('Start Join Group').Update(text="Start Join Group")
        elif event == 'new_via_login':
            if window3:
                via_data = get_via_data()
                window3.Element('via_table').Update(values=via_data)

    for window in [window1, window2, window3, window4, window5, window6]:
        if window:
            window.close()
