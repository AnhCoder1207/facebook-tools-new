import os
import subprocess
import re
import time
import requests
import youtube_dl
import json
import threading
import PySimpleGUI as sg
import pyautogui
import logging

from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import os

retry_time = 0
stop_threads = False
pyautogui.FAILSAFE = False
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


options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument('--headless')
driver = webdriver.Chrome('./chromedriver.exe', options=options)


def waiting_for_id(id_here):
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, id_here))
        )
        return element
    except Exception as ex:
        print(ex)
        return False


def waiting_for_class(class_here):
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CLASS_NAME, class_here))
        )
        return element
    except Exception as ex:
        print(ex)
        return False


def waiting_for_xpath(xpath):
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        return element
    except Exception as ex:
        print(ex)
        return False


def waiting_for_selector(selector):
    try:
        element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selector))
        )
        return element
    except Exception as ex:
        print(ex)
        return False


def download_video(table_data, current_index, window, ten_phim, pause_download):
    os.makedirs(f"downloaded/{ten_phim}", exist_ok=True)
    for idx, row in enumerate(table_data):
        if idx >= current_index:
            if pause_download():
                return True

            link, name, views, status = row
            ydl_opts = {}
            if status == "waiting":
                if not os.path.isfile(f'downloaded/{ten_phim}/{views}-{name}.mp4'):
                    window.write_event_value('-THREAD-', [idx, 'Downloading'])
                    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                        try:
                            info_dict = ydl.extract_info(link, download=False)
                            video_title = info_dict.get('title', None)
                            ext = info_dict.get('ext', None)
                            ydl_opts = {'outtmpl': f'downloaded/{ten_phim}/{views}-{name}'}
                            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([link])
                            window.write_event_value('-THREAD-', [idx, 'Downloaded'])  # put a message into queue for GUI
                        except Exception as ex:
                            print(ex)
                            filename = f'downloaded/{ten_phim}/{views}-{name}.mp4'
                            download_chromium(idx, link, filename, window)
                else:
                    window.write_event_value('-THREAD-', [idx, 'Downloaded'])  # put a message into queue for GUI


def download_chromium(idx, link, filename, window):
    try:
        for _ in range(3):
            driver.get("https://snapsave.app/")
            input_url_xpath = """//*[@id="url"]"""
            input_url = waiting_for_xpath(input_url_xpath)
            submit_btn_xpath = """//*[@id="send"]"""
            submit_btn = waiting_for_xpath(submit_btn_xpath)
            if input_url and submit_btn:
                input_url.send_keys(link)
                submit_btn.click()
                waiting_for_class("media-content")
                body_table = """//*[@id="download-section"]/section/div/div[1]/div[2]/div/table/tbody/tr"""
                waiting_for_xpath(body_table)
                # button is-success is-small
                quality = driver.find_elements(By.XPATH, body_table)
                first_link = ""
                for row_idx, row in enumerate(quality):
                    video_quality_el = download_link_el = button_render_el = None
                    try:
                        video_quality_el = row.find_element(By.CSS_SELECTOR, "td.video-quality")
                    except NoSuchElementException:  # spelling error making this code not work as expected
                        pass
                    try:
                        download_link_el = row.find_element(By.TAG_NAME, "a")
                    except NoSuchElementException:  # spelling error making this code not work as expected
                        pass
                    try:
                        button_render_el = row.find_element(By.TAG_NAME, "button")
                    except NoSuchElementException:  # spelling error making this code not work as expected
                        pass

                    if video_quality_el and download_link_el and download_link_el.text == "Download":
                        resolution = video_quality_el.text
                        video_link = download_link_el.get_attribute('href')
                        if '1080p' in resolution or '720p' in resolution:
                            try:
                                logger.info(f"Download file {filename} resolution {resolution}")
                                download_file(video_link, filename)
                                window.write_event_value('-THREAD-', [idx, 'Downloaded'])
                            except Exception as ex:
                                window.write_event_value('-THREAD-', [idx, 'Error'])

                            return True
                        if row_idx == 0:
                            first_link = video_link

                # can not download, try to render
                quality = driver.find_elements(By.XPATH, body_table)
                for row_idx, row in enumerate(quality):
                    video_quality_el = button_render_el = None
                    try:
                        video_quality_el = row.find_element(By.CSS_SELECTOR, "td.video-quality")
                    except NoSuchElementException:  # spelling error making this code not work as expected
                        pass
                    try:
                        button_render_el = row.find_element(By.TAG_NAME, "button")
                    except NoSuchElementException:  # spelling error making this code not work as expected
                        pass

                    if video_quality_el and button_render_el:
                        resolution = video_quality_el.text
                        logger.info(f'render resolution {resolution}')
                        button_render_el.click()

                        waiting = 0
                        while waiting < 6:
                            waiting += 1
                            download_video_btn = waiting_for_selector("#procress-dllink > div > a")
                            download_video_btn_2 = waiting_for_selector("#process-section > section > div > div.columns.btn-convert-dl > div > a")
                            if download_video_btn and "download video" in download_video_btn.text.lower():
                                video_link = download_video_btn.get_attribute('href')
                                logger.info(f"Download render file {filename} resolution {resolution}")
                                download_file(video_link, filename)
                                window.write_event_value('-THREAD-', [idx, 'Downloaded'])
                                return True
                            if download_video_btn_2 and "download video" in download_video_btn_2.text.lower():
                                video_link = download_video_btn_2.get_attribute('href')
                                logger.info(f"Download render file {filename} resolution {resolution}")
                                download_file(video_link, filename)
                                window.write_event_value('-THREAD-', [idx, 'Downloaded'])
                                return True

                # can not download render file, let's download with first link
                if first_link != "":
                    logger.info(f"Download first file {filename}")
                    download_file(first_link, filename)
                    window.write_event_value('-THREAD-', [idx, 'Downloaded'])
                    return True
        window.write_event_value('-THREAD-', [idx, 'Error'])
        return False
    except Exception as ex:
        # driver.close()
        window.write_event_value('-THREAD-', [idx, 'Error'])
        print(ex)


def download_file(url, local_filename):
    # NOTE the stream=True parameter below
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            with tqdm(desc='Download Progress') as pbar:
                print(f"Downloading {local_filename}")
                filesize = 0
                for chunk in r.iter_content(chunk_size=8192):
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk:
                    #
                    f.write(chunk)
                    filesize += 8192
                    pbar.set_description(f"Downloaded: {round(filesize/1024/1024, 1)} Mb")
                print(f"Done {local_filename}")


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
    tables_data = []
    parents = soup.select('div.rq0escxv.rj1gh0hx.buofh1pr.ni8dbmo4.stjgntxs.l9j0dhe7')
    print(f"Number parents {len(parents)}")
    for parent in parents:
        href_el = parent.select_one("div.i1fnvgqd.btwxx1t3.j83agx80.bp9cbjyn > span:nth-child(1) > div:nth-child(2) > a")
        text_video = parent.select_one('div.i1fnvgqd.btwxx1t3.j83agx80.bp9cbjyn > span:nth-child(1) > div:nth-child(2) > a > span > span')
        views = parent.select_one("div.i1fnvgqd.btwxx1t3.j83agx80.bp9cbjyn > span:nth-child(1) > div:nth-child(3) > div > div:nth-child(2) > div > div > span > div")
        if href_el and text_video and views:
            # if "Views" in views.text:
            #     view_count = views.text
            # else:
            #     continue
            view_count = views.text
            href = href_el.get('href')
            if "M" in view_count:
                view_count_float = view_count.replace("M", "").replace("Views", "").replace("views", "")
                view_count = float(view_count_float)*1000000
            elif "K" in view_count:
                view_count = view_count.replace("K", "").replace("Views", "").replace("views", "")
                view_count = float(view_count)*1000
            else:
                view_count = view_count.replace("Views", "").replace("views", "")
                view_count = float(view_count)

            if view_count > filter_number or filter_number == 0:
                if view_count >= 1000000:
                    view_count = f"{view_count/1000000}M"
                elif 1000000 > view_count > 1000:
                    view_count = f"{view_count/1000}K"
                tables_data.append([
                    href,
                    text_video.text,
                    view_count,
                    "waiting"
                ])
    return tables_data


if __name__ == '__main__':
    # browserExe = "movies.exe"
    # os.system("taskkill /f /im " + browserExe)
    sg.theme('DarkAmber')  # Add a touch of color
    # All the stuff inside your window.
    headings = ['links', 'name', 'likes', 'status']  # the text of the headings

    layout = [[sg.Text('views filter'), sg.InputText("0", key="input_number")],
              [sg.Text('Ten Phim'), sg.InputText(key="ten_phim")],
              [sg.Table(values=[],
                        headings=headings,
                        display_row_numbers=True,
                        justification='right',
                        auto_size_columns=False,
                        col_widths=[50, 15, 15, 15],
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
            thread = threading.Thread(target=download_video, args=(table_data, current_index,
                                                                   window, values.get("ten_phim", "").strip(),
                                                                   lambda: stop_threads,), daemon=True)
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
            table_data[idx][-1] = download_status
            # table_data[idx][-1] = download_status
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
