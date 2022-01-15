from googleapiclient.discovery import build
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def validate_string(input_txt):
    if type(input_txt) is str:
        return ''.join(e for e in input_txt if (e.isalnum() or e == " " or e == '.'))
    return input_txt


def video_comments(video_id):
    api_key = 'AIzaSyCwCavl6taBxti5xF4it6xdlq2se2JEV5g'
    analyzer = SentimentIntensityAnalyzer()
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


if __name__ == '__main__':
    # Enter video id
    video_id = input

    # Call function
    comments = video_comments(video_id)
    for comment in comments:
        print(comment)