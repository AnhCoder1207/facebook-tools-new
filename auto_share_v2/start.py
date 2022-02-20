import os
import shutil
import threading
import time
import uuid

import PySimpleGUI as sg
import pyautogui

from bson import ObjectId
from datetime import datetime

from get_subtitle import video_comments
from helper import ChromeHelper
from utils import logger, get_scheduler_data, get_via_data, \
    get_group_joining_data, scheduler_table, via_share, joining_group
from controller import thread_join_group, start_login_via, start_share, start_join_group


def make_main_window(table_data):
    menu_def = ['&Menu', ['&Start share', '&Stop share', '---', '&Shutdown Chrome', '&Exit']], \
               ['&Video', ['&Add A New Video', '&Add Multiple Videos', "&Delete Videos"]], \
               ['&Edit', ['&Via Management', '&Edit list group', '&Edit Default Share Descriptions']], \
               ['&Tools', ['&Get Youtube Comments', '&Downloader']]

    headings = ['video_id', 'share group', 'share done', "Gỗ", "Cơ Khí", "Xây Dựng", "Tùy Chọn"]
    layout = [
        [sg.Menu(menu_def, key='menu_bar')],
        [
            # sg.Button('Start share'),
            # sg.Button('Add New Video'),
            # sg.Button('Shutdown Chrome'),
            # sg.Button('Get Youtube Comments'),
            # sg.Button('Via Management'),
            # sg.Button('Edit list group'),
            # sg.Button('Start Join Group', key="start_join_group"),
            # sg.Button('Edit Default Share Descriptions'),
            sg.Text("Number threads"), sg.InputText(key="number_threads", default_text=2, size=(4, 1)),
            sg.Checkbox('Use Proxy', key='proxy_enable', enable_events=False, default=True),
        ],
        [
            sg.Table(values=table_data,
                     headings=headings,
                     display_row_numbers=True,
                     justification='right',
                     enable_events=True,
                     auto_size_columns=False,
                     col_widths=[20, 25, 20, 15, 15, 15, 15],
                     vertical_scroll_only=False,
                     num_rows=24, key='table')
        ]
    ]
    # Create the Window
    return sg.Window('Auto Share V1.2', layout, finalize=True)


def add_vid_window():
    layout_add_video = [
        [
            [sg.Text('Video ID')],
            [sg.InputText(size=(100, 5), key="video_id")],
        ],
        [
            [sg.Text('Custom Share Links')],
            [sg.Multiline(size=(100, 10), key="video_custom_share_links")],
        ],
        [
            [sg.Text('Share Descriptions')],
            [sg.Multiline(size=(100, 10), key="video_custom_share_descriptions")],
        ],
        [
            sg.Checkbox(
                'Gỗ', key='groups.go', enable_events=False, default=False),
            sg.Checkbox(
                'Cơ Khí', key='groups.co_khi', enable_events=False, default=False),
            sg.Checkbox(
                'Xây Dựng', key='groups.xay_dung', enable_events=False, default=False),
            sg.Checkbox(
                'Tùy Chọn', key='groups.options', enable_events=False, default=False),
        ],
        [sg.Button('Them')]
    ]

    return sg.Window('Add Video', layout_add_video, finalize=True)


def add_multiple_vid_window():
    layout_add_video = [
        [
            [sg.Text('Video IDs')],
            [sg.Multiline(size=(100, 5), key="video_ids")],
        ],
        [
            [sg.Text('Share Descriptions')],
            [sg.Multiline(size=(100, 10), key="video_custom_share_descriptions")],
        ],
        [
            sg.Checkbox(
                'Gỗ', key='groups.go', enable_events=False, default=False),
            sg.Checkbox(
                'Cơ Khí', key='groups.co_khi', enable_events=False, default=False),
            sg.Checkbox(
                'Xây Dựng', key='groups.xay_dung', enable_events=False, default=False),
            sg.Checkbox(
                'Tùy Chọn', key='groups.options', enable_events=False, default=False),
        ],
        [sg.Button('Them', key='add_multiple_videos')]
    ]

    return sg.Window('Add Multiple Videos', layout_add_video, finalize=True)


def get_youtube_comment_window():
    layout_youtube_comment_window = [
        [
            [sg.Text('Youtube Video ID')],
            [sg.InputText(key="youtube_video_id")],
        ],
        [
            [sg.Text('Share Descriptions')],
            [sg.Multiline(size=(200, 10), key="youtube_comments_area")],
        ],
        [sg.Button('Process', key="process_youtube_video")]
    ]

    return sg.Window('Get youtube comments', layout_youtube_comment_window, finalize=True)


def show_detail_video_info(video_data):
    number_shared = len(video_data.get('groups_shared', []))
    number_share_description = len(video_data.get('share_descriptions', []))
    number_share_remaining = len(video_data.get('groups_remaining', []))
    number_video_custom_share_links = len(video_data.get('video_custom_share_links', []))
    layout_detail_video_info = [
        [
            [sg.Text('Video ID')],
            [sg.InputText(video_data.get('video_id'), size=(100, 5), readonly=True, key="detail_video_id")]
        ],
        [
            [sg.Text('Share Config')],
            [
                sg.Checkbox(
                    'Gỗ', key='groups.go', enable_events=False, default=video_data.get("go_enable", False)),
                sg.Checkbox(
                    'Cơ Khí', key='groups.co_khi', enable_events=False, default=video_data.get("co_khi_enable", False)),
                sg.Checkbox(
                    'Xây Dựng', key='groups.xay_dung', enable_events=False,
                    default=video_data.get("xay_dung_enable", False)),
                sg.Checkbox(
                    'Tùy Chọn', key='groups.options', enable_events=False,
                    default=video_data.get("options_enable", False)),
                sg.Checkbox(
                    'Share Done', key='video_shared', enable_events=False,
                    default=video_data.get("shared", False)),
            ],
        ],
        [
           [sg.Text(f'Custom Share Links: {number_video_custom_share_links}')],
           [sg.Multiline("\n".join(video_data.get('video_custom_share_links', [])), size=(100, 10),
                         key="detail_video_custom_share_links")],
        ],
        [
            [sg.Text(f'Share Descriptions: {number_share_description}')],
            [sg.Multiline("\n".join(video_data.get('share_descriptions', [])), size=(100, 10), key="detail_share_description")],
        ],
        [
            [sg.Text(f'Shared Groups: {number_shared}')],
            [sg.Multiline("\n".join(video_data.get('groups_shared', [])), size=(100, 10), key="detail_groups_shared")],
        ],
        [
            [sg.Text(f'Remaining: {number_share_remaining}')],
            [sg.Multiline("\n".join(video_data.get('groups_remaining', [])), size=(100, 10), key="detail_groups_remaining")],
        ],
        [sg.Button('Save', key="video_modified"), sg.Button('Delete', key="remove_video")]
    ]

    return sg.Window('Detail Video', layout_detail_video_info, finalize=True)


def export_via_window():
    layout_detail_video_info = [
        [sg.Text('Select type')],
        [
            sg.Radio(
                'Toàn bộ', group_id="gr_start_export_via", default=True, key="all_via"),
            sg.Radio(
                'Via Die', group_id="gr_start_export_via", key="checkpoint_via")
        ],
        [sg.Button('Export', key="start_export_via")]
    ]

    return sg.Window('Export Via', layout_detail_video_info, finalize=True)


def via_manage_window(via_data):
    headings = ['fb_id', 'password', '2fa', "email", "email password", "proxy", "status", "auto share today", "last modified"]
    layout_via_manage_video = [
        [sg.Button('Add new here', key='add_new_via'),
         sg.Button('Open Via in Browser', key='open_via_in_browser'),
         sg.Button('Edit Via', key='edit_via_btn'),
         sg.Button('Export Via Checkpoint', key="export_checkpoint_via_btn"),
         sg.Button('Delete Via', key="delete_via")],
        [
            sg.Table(values=via_data,
                     headings=headings,
                     display_row_numbers=True,
                     justification='right',
                     auto_size_columns=False,
                     col_widths=[15, 15, 15, 15, 15, 20, 15, 15, 20],
                     vertical_scroll_only=False,
                     num_rows=24, key='via_table')
        ]
    ]

    return sg.Window('Via Management', layout_via_manage_video, finalize=True)


def add_new_via_windows():
    add_new_via_layouts = [
        [
            sg.Text("Browser file: "), sg.FileBrowse(key='file_via_input', enable_events=True),
            sg.Checkbox('Import existed via', key='login.options', enable_events=False, default=False),
        ],
        [
            sg.Button('Start login via')
        ]
    ]
    return sg.Window('Via Management', add_new_via_layouts, finalize=True)


def group_to_join_window(group_options, group_go, group_co_khi, group_xay_dung, group_join_auto):
    layout_group_to_join = [
        [
            [
                sg.Column([[sg.Text('Gỗ')], [sg.Multiline(size=(100, 10), key="group_go", default_text=group_go)]]),
                sg.Column([[sg.Text('Cơ khí')], [sg.Multiline(size=(100, 10), key="group_co_khi", default_text=group_co_khi)]])
            ],
            [
                sg.Column([[sg.Text('Xây Dựng')], [sg.Multiline(size=(100, 10), key="group_xay_dung", default_text=group_xay_dung)]]),
                sg.Column([[sg.Text('Tùy Chọn')], [sg.Multiline(size=(100, 10), key="group_options", default_text=group_options)]])
            ],
            [
                sg.Column([[sg.Text('Group Join Auto')],
                           [sg.Multiline(size=(100, 10), key="group_join_auto", default_text=group_join_auto)]])
            ]
        ],
        [
            sg.Button('Save', key="group_modified")
        ]
    ]
    return sg.Window('Group View', layout_group_to_join, finalize=True)


def text_seo_window(text_seo_data):
    layout_text_seo_window = [
        [sg.Multiline(size=(200, 20), key="share_description_data", default_text=text_seo_data)],
        [sg.Button('Save', key="text_seo_modified")]
    ]
    return sg.Window('Default Share descriptions', layout_text_seo_window, finalize=True)


def edit_via_window(via_data):
    fb_id, password, mfa, email, email_password, proxy_data, status, share_number, create_date = via_data
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
        [sg.Listbox(default_values=status, values=['live', 'checkpoint', 'can not login', 'disable', 'join group', 'die proxy', 'can not join group'], size=(42, 6), enable_events=False, key='_LIST_VIA_STATUS_')],
        [sg.Button('Save', key='edit_via_save')]
    ]
    window = sg.Window('Edit Via Data', layout_edit_via, finalize=True)

    return window


if __name__ == '__main__':
    # time.sleep(2)
    # print(pyautogui.position())
    # sg.theme_previewer()
    sg.theme('BlueMono')  # Add a touch of color
    # All the stuff inside your window.
    table_data = get_scheduler_data()
    window1, window2, window3, window4, window5, window6, windows7, windows8, windows9 = make_main_window(table_data), None, None, None, None, None, None, None, None
    # chrome_worker = ChromeHelper()
    stop_join_group = False
    sharing = False
    joining = False
    # clear via status
    via_share.update_many({"status": 'join group'}, {"$set": {"status": "live"}})
    via_share.update_many({"status": 'sharing'}, {"$set": {"status": "live"}})
    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        window, event, values = sg.read_all_windows()
        logger.debug(f'{event} You entered {values}')
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            if window:
                window.close()
            else:
                break
        elif event == 'Shutdown Chrome':
            browserExe = "chrome.exe"
            os.system("taskkill /f /im " + browserExe)
            browserExe = "chromedriver.exe"
            os.system("taskkill /f /im " + browserExe)
        elif event == 'Start share':
            # get number theads
            number_threads = values.get("number_threads", 1)
            proxy_enable = window1.Element('proxy_enable').Get()
            try:
                number_threads = int(number_threads)
            except Exception as ex:
                sg.Popup("Number threads must be integer")
                continue

            if not sharing:
                sharing = True
                # window1.Element('Start share').Update(text="Stop Share")
                stop_threads = False
                threads = []
                via_share.update_many({"status": 'sharing'}, {"$set": {"status": "live"}})
                for _ in range(number_threads):
                    thread = threading.Thread(target=start_share,
                                              args=(window1, lambda: stop_threads, proxy_enable), daemon=True)
                    threads.append(thread)
                for thread in threads:
                    thread.start()
                    time.sleep(5)
                # browserExe = "chrome.exe"
                # os.system("taskkill /f /im " + browserExe)
                # browserExe = "chromedriver.exe"
                # os.system("taskkill /f /im " + browserExe)
                # window1.Element('Start share').Update(text="Start share")
        elif event == "Stop share":
            stop_threads = True
            sharing = False
            browserExe = "chromedriver.exe"
            os.system("taskkill /f /im " + browserExe)
        elif event == 'remove_video':
            label = pyautogui.confirm(text='Are you sure?', title='Confirm delete', buttons=["yes", "no"])
            if label == "yes":
                video_id = values.get("detail_video_id")
                # removed = values['table']
                # table_data = window1.Element('table').Get()
                # for idx in reversed(removed):
                #     video_id = table_data[idx][0]
                    # scheduler_table.update_one({"video_id": video_id}, {"$set": {"shared": True}})
                scheduler_table.delete_one({"video_id": video_id})
                if windows7:
                    windows7.close()

                table_data = get_scheduler_data()
                window1.Element('table').Update(values=table_data)
        elif event == '-THREAD-':
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
        elif event == 'Them':
            # them video
            video_id = values.get("video_id", "").strip()

            video_custom_share_links = values.get("video_custom_share_links", "").strip()
            if video_custom_share_links != "":
                video_custom_share_links = video_custom_share_links.split('\n')
            else:
                video_custom_share_links = []

            if video_id == "":
                sg.Popup('Video ID is require', keep_on_top=True)
                continue

            exist_scheduler = scheduler_table.find_one({"video_id": video_id})
            share_descriptions = values.get("video_custom_share_descriptions", "").strip()
            if share_descriptions != "":
                share_descriptions = share_descriptions.split('\n')
            else:
                share_descriptions = []

            # video_custom_share_links

            # get list group share
            go_enable = values.get("groups.go", False)
            co_khi_enable = values.get("groups.co_khi", False)
            xay_dung_enable = values.get("groups.xay_dung", False)
            options_enable = values.get("groups.options", False)
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

            if exist_scheduler:
                number_shared = len(exist_scheduler.get("groups_shared"))
                scheduler_table.update_one({"_id": exist_scheduler['_id']}, {"$set": {
                    "share_number": number_shared,
                    "shared": False,
                    "go_enable": go_enable,
                    "co_khi_enable": co_khi_enable,
                    "xay_dung_enable": xay_dung_enable,
                    "options_enable": options_enable,
                    "share_descriptions": share_descriptions,
                    "groups_remaining": groups_share,
                    "video_custom_share_links": video_custom_share_links,
                    "create_date": datetime.now().timestamp()
                }})
            else:
                new_scheduler = {
                    "_id": str(uuid.uuid4()),
                    "video_id": video_id,
                    "scheduler_time": datetime.now().timestamp(),
                    "create_date": datetime.now().timestamp(),
                    "shared": False,
                    "share_number": 0,
                    "title_shared": [],
                    "groups_shared": [],
                    "go_enable": go_enable,
                    "co_khi_enable": co_khi_enable,
                    "xay_dung_enable": xay_dung_enable,
                    "options_enable": options_enable,
                    "share_descriptions": share_descriptions,
                    "groups_remaining": groups_share,
                    "video_custom_share_links": video_custom_share_links
                }
                result = scheduler_table.insert_one(new_scheduler)
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
            sg.Popup('Them thanh cong', keep_on_top=True)
            window2.close()
        elif event == 'Add Multiple Videos':
            add_multiple_vid_window()
        elif event == 'add_multiple_videos':
            # them video
            video_ids = values.get("video_ids", "").strip().split('\n')
            video_custom_share_links = []
            if len(video_ids) == 0:
                sg.Popup('Video ID is require', keep_on_top=True)
                continue
            share_descriptions = values.get("video_custom_share_descriptions", "").strip()
            if share_descriptions != "":
                share_descriptions = share_descriptions.split('\n')
            else:
                share_descriptions = []

            # get list group share
            go_enable = values.get("groups.go", False)
            co_khi_enable = values.get("groups.co_khi", False)
            xay_dung_enable = values.get("groups.xay_dung", False)
            options_enable = values.get("groups.options", False)
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

            for video_id in video_ids:
                video_id = video_id.strip()
                if video_id == "":
                    continue

                exist_scheduler = scheduler_table.find_one({"video_id": video_id})

                if exist_scheduler:
                    number_shared = len(exist_scheduler.get("groups_shared"))
                    scheduler_table.update_one(
                        {"_id": exist_scheduler['_id']},
                        {
                            "$set": {
                                "share_number": number_shared,
                                "shared": False,
                                "go_enable": go_enable,
                                "co_khi_enable": co_khi_enable,
                                "xay_dung_enable": xay_dung_enable,
                                "options_enable": options_enable,
                                "share_descriptions": share_descriptions,
                                "groups_remaining": groups_share,
                                "video_custom_share_links": video_custom_share_links,
                                "create_date": datetime.now().timestamp()
                            }
                        }
                    )
                else:
                    new_scheduler = {
                        "_id": str(uuid.uuid4()),
                        "video_id": video_id,
                        "scheduler_time": datetime.now().timestamp(),
                        "create_date": datetime.now().timestamp(),
                        "shared": False,
                        "share_number": 0,
                        "title_shared": [],
                        "groups_shared": [],
                        "go_enable": go_enable,
                        "co_khi_enable": co_khi_enable,
                        "xay_dung_enable": xay_dung_enable,
                        "options_enable": options_enable,
                        "share_descriptions": share_descriptions,
                        "groups_remaining": groups_share,
                        "video_custom_share_links": video_custom_share_links
                    }
                    result = scheduler_table.insert_one(new_scheduler)
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
            sg.Popup('Them thanh cong', keep_on_top=True)
        elif event == "Add A New Video":
            window2 = add_vid_window()
        elif event == "Via Management":
            via_data = get_via_data()
            window3 = via_manage_window(via_data)
        elif event == "Edit list group":
            group_options = get_group_joining_data('group_options')
            group_go = get_group_joining_data('group_go')
            group_co_khi = get_group_joining_data('group_co_khi')
            group_xay_dung = get_group_joining_data('group_xay_dung')
            group_join_auto = get_group_joining_data('group_join_auto')
            window4 = group_to_join_window(group_options, group_go, group_co_khi, group_xay_dung, group_join_auto)
        elif event == "group_modified":
            group_options = values.get("group_options", "").split('\n')
            groups = [{"_id": str(ObjectId()), "name": group.strip(), "group_type": "group_options"} for group in group_options if
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

            group_join_auto = values.get("group_join_auto", "").split('\n')
            groups.extend(
                [{"_id": str(ObjectId()), "name": group.strip(), "group_type": "group_join_auto"} for group in group_join_auto if
                           group.strip() != ''])

            #group_join_auto

            # remove all exist
            # query = db.delete(joining_group).where(joining_group.columns.group_type != "share_description_data")
            # results = connection.execute(query)
            joining_group.delete_many({"group_type": "group_options"})
            joining_group.delete_many({"group_type": "group_go"})
            joining_group.delete_many({"group_type": "group_co_khi"})
            joining_group.delete_many({"group_type": "group_xay_dung"})
            joining_group.delete_many({"group_type": "group_join_auto"})

            # update new
            joining_group.insert_many(groups)
            sg.Popup('Successfully', keep_on_top=True)
            window4.close()
        elif event == "delete_via":
            removed = values['via_table']
            table_data = window3.Element('via_table').Get()
            label = pyautogui.confirm(text='Are you sure?', title='', buttons=["yes", "no"])

            if label == "yes":
                user_data_dir = "User Data"
                if os.path.isfile("config.txt"):
                    with open("config.txt") as config_file:
                        for line in config_file.readlines():
                            user_data_dir = line.strip()
                            break

                for idx in reversed(removed):
                    fb_id = table_data[idx][0]
                    # print(video_id)

                    try:
                        shutil.rmtree(f"{user_data_dir}/{fb_id}", ignore_errors=True)
                        via_share.delete_one({"fb_id": fb_id})
                    except:
                        sg.Popup(f"Can not remove {fb_id} please close chrome before delete via")
                        break

                    # query = db.delete(via_share).where(via_share.columns.fb_id == fb_id)
                    # results = connection.execute(query)
                    # table_data.pop(item)
                table_data = get_via_data()
                window3.Element('via_table').Update(values=table_data)
        elif event == 'export_checkpoint_via_btn':
            if windows9:
                windows9.close()

            windows9 = export_via_window()
        elif event == "start_export_via":
            config_all_via = values.get("all_via", True)
            config_checkpoint_via = values.get("checkpoint_via", False)
            via_table_data = window3.Element('via_table').Get()
            if os.path.isfile("checkpoint.txt"):
                os.remove("checkpoint.txt")
            with open("checkpoint.txt", mode='w') as cp_via_files:
                for via_data in via_table_data:
                    fb_id, password, mfa, email, email_password, proxy_data, status, share_number, create_date = via_data
                    if config_all_via:
                        if proxy_data != "":
                            cp_via_files.write(f'{fb_id}|{password}|{mfa}|{email}|{email_password}|{proxy_data}\n')
                        else:
                            cp_via_files.write(f'{fb_id}|{password}|{mfa}|{email}|{email_password}\n')
                    else:
                        if status and status.strip() not in ['live', 'sharing', 'join group']:
                            if proxy_data != "":
                                cp_via_files.write(f'{fb_id}|{password}|{mfa}|{email}|{email_password}|{proxy_data}\n')
                            else:
                                cp_via_files.write(f'{fb_id}|{password}|{mfa}|{email}|{email_password}\n')
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
        #         fb_id, password, mfa, email, email_password, proxy_data, status, share_number = via_data
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
            via_share.update_many(
                {"fb_id": edit_via_id},
                {"$set": {
                    "password": edit_via_password,
                    "mfa": edit_via_mfa,
                    "email": edit_via_email,
                    "email_password": edit_via_email_password,
                    "proxy": edit_via_proxy_data,
                    "status": status_via
                }}
            )
            via_data = get_via_data()
            window3.Element('via_table').Update(values=via_data)
            if window6:
                window6.close()
        elif event == 'Start login via':
            file_input = values.get('file_via_input')
            if not os.path.isfile(file_input):
                sg.Popup('File not exist', keep_on_top=True)
                continue
            proxy_enable = window1.Element('proxy_enable').Get()
            number_threads = window1.Element('number_threads').Get()
            try:
                number_threads = int(number_threads)
            except Exception as ex:
                sg.Popup("Number threads must be integer")
                continue

            start_login_via(window3, file_input, values.get('login.options', False), number_threads, proxy_enable)
            # start_login_thread = threading.Thread(target=start_login_via,
            #                                       args=(), daemon=True)
            # start_login_thread.start()
        elif event == "open_via_in_browser":
            via_selected = values.get('via_table')
            proxy_enable = window1.Element('proxy_enable').Get()
            via_table_data = window3.Element('via_table').Get()
            for via_idx in via_selected:
                via_data = via_table_data[via_idx]
                fb_id, password, mfa, email, email_password, proxy_data, status, share_number, create_date = via_data
                # chrome_worker = get_free_worker()
                try:
                    default_chrome_worker = ChromeHelper()
                    default_chrome_worker.open_chrome(fb_id, password, mfa, proxy_data, proxy_enable)
                    break
                except Exception as ex:
                    logger.error(f"Can not open browser {ex}")
        elif event == "Edit Default Share Descriptions":
            share_descriptions = get_group_joining_data('share_descriptions')
            window5 = text_seo_window(share_descriptions)
        elif event == "text_seo_modified":
            share_description = values.get("share_description_data", "").split('\n')
            groups = [{"_id": str(ObjectId()), "name": name.strip(), "group_type": "share_descriptions"} for name in share_description if
                      name.strip() != '']
            # remove all exist
            joining_group.delete_many({"group_type": "share_descriptions"})
            if len(groups) != 0:
                joining_group.insert_many(groups)
            sg.Popup('Luu Thanh Cong')
            window5.close()
        elif event == 'start_join_group':
            # get number theads
            number_threads = values.get("number_threads", 1)

            try:
                number_threads = int(number_threads)
            except Exception as ex:
                sg.Popup("Number threads must be integer")
                continue

            if not joining:
                stop_join_group = False
                joining = True
                joining_threads = []
                via_share.update_one({"status": "join group"}, {"$set": {"status": 'live'}})

                for _ in range(number_threads):
                    thread_join_gr = threading.Thread(target=start_join_group,
                                                      args=(lambda: stop_join_group,), daemon=True)
                    joining_threads.append(thread_join_gr)

                for thread_join_gr in joining_threads:
                    thread_join_gr.start()
                window1.Element('start_join_group').Update(text="Stop Join Group")
            else:
                stop_join_group = True
                joining = False
                window1.Element('start_join_group').Update(text="Start Join Group")
        elif event == 'new_via_login':
            if window3:
                via_data = get_via_data()
                window3.Element('via_table').Update(values=via_data)
        elif event == 'table':
            videos_table_data = window1.Element('table').Get()
            data_selected = [videos_table_data[row] for row in values[event]]
            for data in data_selected:
                video_id = data[0]
                video_metadata = scheduler_table.find_one({"video_id": video_id})
                if video_metadata:
                    windows7 = show_detail_video_info(video_metadata)
        elif event == 'video_modified':
            video_id = values.get("detail_video_id")
            go_enable = values.get("groups.go")
            co_khi_enable = values.get("groups.co_khi")
            xay_dung_enable = values.get("groups.xay_dung")
            options_enable = values.get("groups.options")
            video_shared = values.get("video_shared")
            detail_share_description = [x.strip() for x in values.get("detail_share_description").split("\n") if x.strip() != ""]
            detail_groups_shared = [x.strip() for x in values.get("detail_groups_shared").split("\n") if x.strip() != ""]
            video_custom_share_links = [x.strip() for x in values.get("detail_video_custom_share_links").split("\n") if x.strip() != ""]

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

            groups_share_fixed = list(set(total_groups) - set(detail_groups_shared))

            scheduler_table.update_one({"video_id": video_id}, {"$set": {
                "go_enable": go_enable,
                "co_khi_enable": co_khi_enable,
                "xay_dung_enable": xay_dung_enable,
                "options_enable": options_enable,
                "share_descriptions": detail_share_description,
                "groups_remaining": groups_share_fixed,
                "shared": video_shared,
                "video_custom_share_links": video_custom_share_links
            }})
            sg.Popup("Save success!")
            table_data = get_scheduler_data()
            window1.Element('table').Update(values=table_data)
            if windows7:
                windows7.close()
        elif event == "Get Youtube Comments":
            windows8 = get_youtube_comment_window()
        elif event == "process_youtube_video":
            # windows 8
            # youtube_video_id
            # youtube_comments_area
            if windows8:
                youtube_video_id = values.get("youtube_video_id", "").strip()
                logger.info(f"process video {youtube_video_id}")
                try:
                    comments = video_comments(youtube_video_id)
                except Exception as ex:
                    logger.error(f"get youtube comments errors: {ex}")
                    comments = []
                comments = "\n".join(comments)
                windows8.Element('youtube_comments_area').update(comments)
        elif event == 'Delete Videos':
            label = pyautogui.confirm(text='Are you sure?', title='Confirm delete all videos', buttons=["yes", "no"])
            if label == "yes":
                scheduler_table.drop()
                table_data = get_scheduler_data()
                window1.Element('table').Update(values=table_data)
        elif event == 'add_new_via':
            add_new_via_windows()
    for window in [window1, window2, window3, window4, window5, window6, windows7, windows8, windows9]:
        if window:
            window.close()
