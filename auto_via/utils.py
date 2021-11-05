import ssl

import base64
import datetime
import os
import pickle
import pyotp
import clipboard
import requests
import logging
import pymongo
import pyautogui
import time
import random
import uuid
import re
import pickle

from bs4 import BeautifulSoup
from exchangelib import Credentials, Account
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# create logger with 'spam_application'
logger = logging.getLogger('application')
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('app.log', 'w', 'utf-8')
# fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
# ch.setLevel(logging.ERROR)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)


client = pymongo.MongoClient("mongodb+srv://facebook:auft.baff1vawn*WEC@cluster0.dtlfk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",
                             ssl=True,ssl_cert_reqs=ssl.CERT_NONE)
db = client.test
phone_table = db['phone']
email_table = db['emails']
cookies_table = db['cookies']
via_share_table = db['via_share']


def random_interval():
    return random.uniform(0.1, 0.5)


def click_to(btn, confidence=0.8, region=None, waiting_time=50, interval=None, check_close=True):
    logger.debug(f"Click to {btn}")
    start_count = 0
    if check_close:
        click_many("x_btn.PNG", confidence=0.97, region=(0, 100, 1920, 800), log=False)
    while start_count < waiting_time:
        ret = pyautogui.locateCenterOnScreen(f"btn/{btn}", confidence=confidence, region=region)
        start_count += 1
        if ret:
            btn_x, btn_y = ret
            pyautogui.moveTo(btn_x, btn_y)
            interval = random_interval() if interval is None else interval
            pyautogui.click(btn_x, btn_y, interval=interval)
            break

        if region:
            region_x, region_y, w, h = region
            if w >= 288 and h >= 26 and pyautogui.locateOnScreen(f"btn/input_password_to_continue.PNG",
                                                                 confidence=0.7, region=region):
                click_to("passowrd_input_txt.PNG")
                paste_text("Minh1234@")
                click_to("input_password_next.PNG", confidence=0.7)
        time.sleep(0.3)


def click_many(btn, region=None, confidence=0.8, log=True):
    if log:
        logger.debug(f"Click many {btn}")
    elements = pyautogui.locateAllOnScreen(f"btn/{btn}", confidence=confidence, region=region)
    number_element = len(list(pyautogui.locateAllOnScreen(f"btn/{btn}", confidence=0.85, region=region)))
    for ret in elements:
        pyautogui.click(ret, interval=random_interval())
    return number_element


def check_exist(btn, region=None, confidence=0.8):
    exist = pyautogui.locateOnScreen(f"btn/{btn}", confidence=confidence, region=region)
    logger.debug(f"Check exist {btn} result {exist}")
    return exist


def waiting_for(btn, region=None, confidence=0.8, waiting_time=50):
    logger.debug(f"Waiting for {btn}")
    start_count = 0
    while start_count < waiting_time:
        start_count += 1
        ret = pyautogui.locateCenterOnScreen(f"btn/{btn}", confidence=confidence, region=region)
        if ret:
            x, y = ret
            return x, y

        if region:
            region_x, region_y, w, h = region
            if w >= 288 and h >= 26 and pyautogui.locateOnScreen(f"btn/input_password_to_continue.PNG",
                                                                 confidence=0.7, region=region):
                click_to("passowrd_input_txt.PNG")
                paste_text("Minh1234@")
                click_to("input_password_next.PNG", confidence=0.7)
        time.sleep(0.2)
    return None


def deciscion(btns, region=None, confidence=0.8):
    while True:
        logger.debug(f"Waiting for {btns}")
        for btn_index, btn in enumerate(btns):
            ret = pyautogui.locateCenterOnScreen(f"btn/{btn}", confidence=confidence, region=region)
            if ret:
                x, y = ret
                return x, y, btn_index


def typeing_text(inp_text):
    pyautogui.typewrite(inp_text, interval=0.2)


def paste_text(inp_text):
    clipboard.copy(inp_text)
    pyautogui.hotkey('ctrl', 'v', interval=0.5)


def get_new_phone():
    network = random.randint(1, 6)
#     network = random.choice([1,3,6])
    api_uri = f"https://otpsim.com/api/phones/request?token=8c4be439c12d0e53fd21bfb25cd07b46&service=7"
    while True:
        res = requests.get(api_uri)
        if res.status_code == 200:
            res_json = res.json()
            logger.debug(f"Get new phone {res_json}")
            if res_json['status_code'] == 200:
                res_json['_id'] = str(uuid.uuid4())
                res_json['api_type'] = 'get_new_phone'
                phone_table.insert_one(res_json)
                logger.info(f"Get new phone: {res_json['data']['phone_number']}")
                return res_json['data']['phone_number'], res_json['data']['session']
            time.sleep(5)


def get_exist_phone(phone_number):
    logger.info("Get exist phone")
    api_uri = f"https://otpsim.com/api/phones/request?token=8c4be439c12d0e53fd21bfb25cd07b46&service=7&number={phone_number}"
    res = requests.get(api_uri)
    if res.status_code == 200:
        res_json = res.json()
        logger.debug(f"Get exist phone {res_json}")
        if res_json['status_code'] == 200:
            res_json['_id'] = str(uuid.uuid4())
            res_json['api_type'] = 'get_exist_phone'
            phone_table.insert_one(res_json)
            return res_json['data']['session']
    return "", ""


def get_code(session):
    # code = res['data']['messages']['otp']
    api_uri = f"https://otpsim.com/api/sessions/{session}?token=8c4be439c12d0e53fd21bfb25cd07b46"
    st = time.time()
    while True:
        time.sleep(5)
        try:
            res = requests.get(api_uri)
            if res.status_code == 200:
                res_json = res.json()
                logger.debug(f"Get code otp {res_json}")
                if res_json['status_code'] == 200:
                    data_json = res_json['data']
                    if data_json['status'] == 0:
                        res_json['_id'] = str(uuid.uuid4())
                        res_json['api_type'] = 'get_code'
                        phone_table.insert_one(res_json)
                        return data_json['messages'][0]['otp']
                current_time = time.time()
                if current_time - st > 120:
                    # waiting for 5 min
                    cancel_session(session)
                    return None
        except Exception as ex:
            logger.error(f'Call api get token errors: {ex}')


def cancel_session(session):
    api_uri = f"https://otpsim.com/api/sessions/cancel?session={session}&token=8c4be439c12d0e53fd21bfb25cd07b46"
    res = requests.get(api_uri)
    res_json = res.json()
    res_json['_id'] = str(uuid.uuid4())
    res_json['api_type'] = 'cancel_session'
    phone_table.insert_one(res_json)
    logger.debug(f"cancel session: {session} json {res_json}")
    return True if res.status_code == 200 else False


def get_out_look(email_outlook, email_password, account_outlook):
    while True:
        try:
            for item in account_outlook.inbox.all().order_by('-datetime_received')[:50]:
                if item.sender.email_address == 'security@facebookmail.com':
                    print(item.datetime_received)
                    soup = BeautifulSoup(item.body, 'html.parser')
                    all_tags = soup.find_all('a')
                    href = ""
                    for tag in all_tags:
                        # href="https://www.facebook.com/confirmcontact.php?c=60029&z=0&gfid=AQDLZ-4fI-MohTeh-Ls"
                        href = tag.get('href')
                        if 'confirmcontact' in href and email_outlook in str(item.body):
                            print(href)
                            break

                    otp_code = re.search("\d{5}", item.body)
                    if otp_code:
                        start, end = otp_code.span()
                        otp_code = item.body[start: end]
                    return href, otp_code
        except Exception as ex:
            print(ex)


def get_emails(target):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    gmail_service = build('gmail', 'v1', credentials=creds)

    while True:
        # request a list of all the messages
        result = gmail_service.users().messages().list(userId='me', labelIds=["UNREAD", "INBOX"],
                                                       maxResults=3).execute()

        # We can also pass maxResults to get any number of emails. Like this:
        # result = service.users().messages().list(maxResults=200, userId='me').execute()
        messages = result.get('messages')

        # messages is a list of dictionaries where each dictionary contains a message id.

        # iterate through all the messages
        if messages:
            for msg in messages:
                # Get the message from its id
                txt = gmail_service.users().messages().get(userId='me', id=msg['id']).execute()

                # mark email is read
                gmail_service.users().messages().modify(userId='me', id=msg["id"],
                                                        body={'removeLabelIds': ['UNREAD']}).execute()
                # Use try-except to avoid any Errors
                try:
                    # Get value of 'payload' from dictionary 'txt'
                    payload = txt['payload']
                    headers = payload['headers']
                    subject = sender = None
                    # Look for Subject and Sender Email in the headers
                    for d in headers:
                        if d['name'] == 'Subject':
                            subject = d['value']
                        if d['name'] == 'From':
                            sender = d['value']

                    # The Body of the message is in Encrypted format. So, we have to decode it.
                    # Get the data and decode it with base 64 decoder.
                    parts = payload.get('parts')[0]
                    data = parts['body']['data']
                    data = data.replace("-", "+").replace("_", "/")
                    decoded_data = base64.b64decode(data)
                    #             print(decoded_data)
                    # Now, the data obtained is in lxml. So, we will parse
                    # it with BeautifulSoup library
                    soup = BeautifulSoup(decoded_data, "lxml")
                    body = soup.body()
                    if subject and sender:
                        # Printing the subject, sender's email and message
                        print("Subject: ", subject)
                        print("From: ", sender)
                        if sender == 'Facebook <security@facebookmail.com>' and target in str(body):
                            bodies = str(body).split('\r\n')
                            result = filter(lambda x: 'confirmcontact' in x, bodies)
                            result = next(result)
                            return result[result.index('https'):]

                except Exception as ex:
                    gmail_service.users().messages().modify(userId='me', id=msg["id"],
                                                            body={'addLabelIds': ['UNREAD']}).execute()
                    logger.error(f"get email errors: {ex}")
        time.sleep(5)


def get_email():
    # check email is access able
    while True:
        email = email_table.find_one({"used": False, "failed": False})
        if email:
            email_outlook = email['email']
            email_password = email['password']
            exist_via = via_share_table.find_one({"email": email_outlook})
            if not exist_via:
                try:
                    credentials = Credentials(email_outlook, email_password)
                    account = Account(email_outlook, credentials=credentials, autodiscover=True)
                    email_ok = True
                    for item in account.inbox.all().order_by('-datetime_received')[:50]:
                        if item.sender.email_address == 'security@facebookmail.com':
                            myquery = {"_id": email['_id']}
                            newvalues = {"$set": {"failed": False, "used": True}}
                            email_table.update_one(myquery, newvalues)
                            logger.error(f"email is not accessible: {email_outlook}")
                            email_ok = False
                            break

                    if email_ok:
                        myquery = {"_id": email['_id']}
                        newvalues = {"$set": {"used": True}}
                        email_table.update_one(myquery, newvalues)
                        logger.debug(f"email is ready: {email_outlook}")
                        return email_outlook, email_password, account
                except Exception as ex:
                    myquery = {"_id": email['_id']}
                    newvalues = {"$set": {"failed": True, "used": False}}
                    email_table.update_one(myquery, newvalues)
                    # hma_x, hma_y = waiting_for("hma_app.PNG")
                    # pyautogui.moveTo(hma_x, hma_y)
                    # pyautogui.click(hma_x, hma_y, button='right', interval=3)
                    # click_to("change_ip_address.png", interval=3)
                    # waiting_for("change_ip_success.PNG")
                    logger.error(f"email is not accessible: {email_outlook}")


def get_email_cenationtshirt():
    # check email is access able
    while True:
        with open("old_email/T3LwDx0wBn-1.txt") as file:
            line = random.choice(file.readlines())
            line = line.split('@')[0] + str(random.randint(0, 10000))
            random_name = f"{line}@cenationtshirt.club"
            email = email_table.find_one({"used": False, "email": random_name})
            if email is None:
                new_email = {
                    "_id": str(uuid.uuid1()),
                    "email": random_name,
                    "password": "",
                    "used": False,
                    "failed": False,
                    "created_date": datetime.datetime.now()
                }
                email_table.insert_one(new_email)
                logger.debug(f"email is ready: {random_name}")
                return random_name, ""


def get_fb_id(cookie_id):
    pyautogui.click(x=1709, y=587)
    pyautogui.hotkey('ctrl', 't')
    click_to("home_page.PNG", confidence=0.9)
    pyautogui.click(x=264, y=50, interval=2)
    pyautogui.hotkey('ctrl', 'c')
    fb_link = clipboard.paste()
    if 'checkpoint' in fb_link:
        # clear cookies
        myquery = {"_id": cookie_id}
        newvalues = {"$set": {"used": True, "failed": True}}
        cookies_table.update_one(myquery, newvalues)
        return None

    click_to("fb_cookies.PNG")
    click_to("get_fb_uid.PNG")
    pyautogui.hotkey('ctrl', 'v')
    click_to("get_id.PNG")
    if not waiting_for("facebookid_dialog.PNG", waiting_time=20):
        return None
    pyautogui.hotkey('ctrl', 'c')
    pyautogui.press('esc')
    fb_id = clipboard.paste()

    try:
        check = int(fb_id)
    except Exception as ex:
        logger.error(f"facebook id is not integer {fb_id}")
        return None
    pyautogui.hotkey('ctrl', 'w')
    time.sleep(1)
    if not check_exist("cookies_alive_1.PNG"):
        pyautogui.hotkey('ctrl', 'w')
    return fb_id
