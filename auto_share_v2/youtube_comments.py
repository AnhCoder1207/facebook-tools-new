import PySimpleGUI as sg
from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def validate_string(input_txt):
    if type(input_txt) is str:
        return ''.join(e for e in input_txt if (e.isalnum() or e == " " or e == '.'))
    return input_txt


def video_comments(video_id):
    api_key = 'AIzaSyCwCavl6taBxti5xF4it6xdlq2se2JEV5g'
    analyzer = SentimentIntensityAnalyzer(lexicon_file="./vader_lexicon.txt", emoji_lexicon="./emoji_utf8_lexicon.txt")
    # empty list for storing reply
    replies = []
    comments = []
    # creating youtube resource object
    youtube = build('youtube', 'v3',
                    developerKey=api_key)

    # retrieve youtube video results
    video_response = youtube.commentThreads().list(
        part='snippet,replies',
        videoId=video_id
    ).execute()

    # iterate video response
    while video_response:

        # extracting required info
        # from each result object
        for item in video_response['items']:

            # Extracting comments
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']

            # counting number of reply of comment
            replycount = item['snippet']['totalReplyCount']

            # if reply is there
            if replycount > 0:

                # iterate through all reply
                for reply in item['replies']['comments']:
                    # Extract reply
                    reply = reply['snippet']['textDisplay']

                    # Store reply is list
                    replies.append(reply)

            # print comment with list of reply
            comment = validate_string(comment)
            comment = comment.replace("39", "'")
            # print(comment, replies, end = '\n\n')
            vs = analyzer.polarity_scores(comment)
            if vs['compound'] > 0.5 and comment not in comments:
                # print(comment + '\n')
                comments.append(comment)
            # empty reply list
            replies = []
        if len(comments) > 100:
            return comments

        # Again repeat
        if 'nextPageToken' in video_response:
            video_response = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                pageToken=video_response['nextPageToken']
            ).execute()
        else:
            return comments


def get_youtube_comment_window():
    layout_youtube_comment_window = [
        [
            [sg.Text('Youtube Video ID')],
            [sg.InputText(key="youtube_video_id")],
        ],
        [
            [sg.Text('Share Descriptions')],
            [sg.Multiline(size=(200, 30), key="youtube_comments_area")],
        ],
        [sg.Button('Process', key="process_youtube_video")]
    ]

    return sg.Window('Get youtube comments', layout_youtube_comment_window, finalize=True)


if __name__ == '__main__':
    # time.sleep(2)
    # print(pyautogui.position())
    # sg.theme_previewer()
    sg.theme('BlueMono')  # Add a touch of color
    # All the stuff inside your window.
    window = get_youtube_comment_window()
    # chrome_worker = ChromeHelper()
    stop_join_group = False
    sharing = False
    joining = False
    # clear via status
    while True:
        window, event, values = sg.read_all_windows()
        if event == sg.WIN_CLOSED:  # if user closes window or clicks cancel
            if window:
                window.close()
            else:
                break
        elif event == "process_youtube_video":
            # windows 8
            # youtube_video_id
            # youtube_comments_area
            youtube_video_id = values.get("youtube_video_id", "").strip()
            try:
                comments = video_comments(youtube_video_id)
            except Exception as ex:
                comments = []
            comments = "\n".join(comments)
            window.Element('youtube_comments_area').update(comments)
