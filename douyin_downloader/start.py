import os
import subprocess
import re
import json
import threading
import PySimpleGUI as sg
import pyautogui

from downloader import run
from bs4 import BeautifulSoup
import os
from utils import logger

retry_time = 0
stop_threads = False
pyautogui.FAILSAFE = False

def crawl_movie(page_name, filter_number):

    try:
        filter_number = int(filter_number)
    except Exception as ex:
        logger.error(ex)
        filter_number = 0

    if not os.path.isfile(page_name):
        return []

    html_doc = open(page_name, encoding="utf-8")
    soup = BeautifulSoup(html_doc, 'html.parser')
    table_data = []

    for parent in soup.find_all("li"):
        video_href = None
        video_like = None
        for link in parent.find_all('a'):
            href = link.get('href')
            if "https://www.douyin.com/video" in href:
                # print(href)
                video_href = href
        for span in parent.find_all('span', class_="_4c7753003fcad283963e6dd5d4aa5f1e-scss"):
            # print(span.text)
            video_like = span.text

        # convert to int
        try:
            factor = 1
            if 'w' in video_like:
                video_like = video_like.replace('w', '')
                factor = 1000
            video_like = int(video_like) * factor
        except Exception as ex:
            logger.error(ex)
            video_like = 0

        if video_href and video_like >= filter_number:
            logger.info(f"{video_href}-{video_like} Likes")
            table_data.append([
                video_href,
                video_like,
                "waiting"
            ])

    return table_data


if __name__ == '__main__':
    # browserExe = "movies.exe"
    # os.system("taskkill /f /im " + browserExe)
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    headings = ['links', 'likes', 'status']  # the text of the headings

    layout = [[sg.Text('Likes must greater than'), sg.InputText("0", key="input_number")],
              [sg.Table(values=[],
                        headings=headings,
                        display_row_numbers=True,
                        justification='right',
                        auto_size_columns=False,
                        col_widths=[50, 15, 15],
                        vertical_scroll_only=False,
                        num_rows=24, key='table')],
              [sg.Button('Start download'),
               sg.Button('Pause'),
               sg.Button('Remove link'),
               sg.Input(key='file_browser', enable_events=True, visible=False), sg.FileBrowse(button_text="Load HTML file", enable_events=True),
               sg.Button('Remove All Links'),
               sg.Button('Cancel')]]

    # Create the Window
    window = sg.Window('Douyin Downloader', layout)

    # Event Loop to process "events" and get the "values" of the inputs
    while True:
        event, values = window.read()
        print(f'{event} You entered {values}')
        print('event', event)
        if event == sg.WIN_CLOSED or event == 'Cancel':  # if user closes window or clicks cancel
            # browserExe = "movies.exe"
            # os.system("taskkill /f /im " + browserExe)
            break
        elif event == 'Get Links Online':
            sg.Popup('Bat dau lay links videos. Vui long khong dong cua so!', keep_on_top=True, title="Chu y!")
            x = threading.Thread(target=crawl_movie, args=(values[0], window, ))
            x.start()
        elif event == 'Start download':
            window.Element('Start download').Update(text="Downloading")
            stop_threads = False
            current_index = 0
            if len(values['table']) > 0:
                current_index = values['table'][0]
            table_data = window.Element('table').Get()
            thread = threading.Thread(target=run, args=(table_data, current_index, window, lambda: stop_threads,), daemon=True)
            thread.start()
        elif event == 'Remove All Links':
            window.Element('table').Update(values=[])
        elif event == 'Pause':
            window.Element('Start download').Update(text="Resume")
            stop_threads = True
        elif event == 'file_browser':
            if os.path.isfile(values['file_browser']):
                table_data = window.Element('table').Get()
                table_data += crawl_movie(values['file_browser'], values['input_number'])
                window.Element('table').Update(values=table_data)
                window.Element('table').Update(select_rows=[0])
        elif event == 'Remove link':
            removed = values['table']
            table_data = window.Element('table').Get()
            for item in reversed(removed):
                table_data.pop(item)
            window.Element('table').Update(values=table_data)
        elif event == '-THREAD-':
            idx, download_status = values['-THREAD-']
            logger.debug(f"download status: {idx} {download_status} {len(table_data)}")
            table_data = window.Element('table').Get()
            if download_status:
                table_data[idx][-1] = 'Downloaded'
            else:
                table_data[idx][-1] = 'Error'
            window.Element('table').Update(values=table_data, select_rows=[idx])
            window.Refresh()
            if idx == len(table_data) - 1:
                window.Element('Start download').Update(text="Start download")
                pyautogui.alert("Download complete")
        elif event == 'GetLinksSuccessfully':
            with open("movies.json") as json_file:
                data = json.load(json_file)
                table_data = []
                for item in data:
                    link_season = item['link_season']
                    for ep in item['episodes']:
                        table_data.append([
                            link_season,
                            ep['episode_name'],
                            ep['link_episode'],
                            "waiting"
                        ])

                window.Element('table').Update(values=table_data, select_rows=[0])
    window.close()
