import PySimpleGUI as sg
from get_subtitle import video_comments
from utils import logger


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
        logger.debug(f'{event} You entered {values}')
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
                logger.error(f"get youtube comments errors: {ex}")
                comments = []
            comments = "\n".join(comments)
            window.Element('youtube_comments_area').update(comments)
