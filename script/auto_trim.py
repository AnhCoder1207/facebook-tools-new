import os
import random

import cv2
import datetime
import subprocess
import numpy as np
from image_similarity_measures.quality_metrics import ssim


if __name__ == '__main__':
    root_folder = """downloaded"""
    for file in os.listdir(root_folder):
        file_ext = os.path.splitext(file)[1]
        if file_ext != '.mp4':
            continue
        filename = f"{root_folder}/{file}"
        print(f"process file {filename}")
        cap = cv2.VideoCapture(filename)
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"fps: {fps}")
        time_per_frame = 1/fps
        start_time = 0
        counting = True
        prev_frame = None
        similar = None
        # Check if camera opened successfully
        if cap.isOpened() == False:
            print("Error opening video stream or file")

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))
        print(frame_width, frame_height)
        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        start_index = 0
        os.makedirs(f'{root_folder}/done', exist_ok=True)
        file_out = f"{root_folder}/done/{os.path.splitext(file)[0]}.mp4"
        file_out_tmp = f"{root_folder}/done/{os.path.splitext(file)[0]}_raw.mp4"
        # out = cv2.VideoWriter(file_out, cv2.VideoWriter_fourcc('M','J','P','G'), fps, (frame_width, frame_height))

        scale_percent = 10  # percent of original img size
        width = int(frame_width * scale_percent / 100)
        height = int(frame_height * scale_percent / 100)
        dim = (width, height)
        start_frame = 0
        is_full_sense = False
        keep_ratio = 0.85
        total_frame = 0
        times = []
        # Read until video is completed
        while cap.isOpened():
            # Capture frame-by-frame
            ret, frame = cap.read()
            # convert the images to grayscale
            if ret:
                # Display the resulting frame

                frame_resize = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
                # print(frame.shape)
                # prev_img = cv2.resize(prev_frame, dim, interpolation=cv2.INTER_AREA)
                if type(prev_frame) == np.ndarray:
                    similar = ssim(frame_resize, prev_frame)
                    # prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    # original_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # similar = compare_images(frame, prev_frame, 'demo')
                    # print("SSIM: %.2f FILE_OUT: %s Time %.1f" % (similar, file_out, round(total_frame/(fps*60), 1)))
                prev_frame = frame_resize

                if similar:
                    current_time_format = datetime.datetime.utcfromtimestamp(total_frame / fps).strftime("%H:%M:%S")
                    # print(current_time_format, similar)
                    if similar < 0.9 and (total_frame - start_frame) > 5 * fps and counting:

                        # if total_frame - start_frame < 5 * fps:
                        #     continue

                        print(current_time_format, similar)

                        # if (total_frame - start_frame) > 5 * fps and counting:
                        #     counting = False

                        if random.choice([1, 2]) == 1:  # keep 50%
                            remove_frame = (start_frame + (keep_ratio * (total_frame - start_frame))) / fps
                            current_time_remove = datetime.datetime.utcfromtimestamp(remove_frame).strftime("%H:%M:%S")
                            start_time_format = datetime.datetime.utcfromtimestamp(start_frame / fps).strftime(
                                "%H:%M:%S")
                            times.append([start_time_format, current_time_format])
                            print(f"New Scene: {start_time_format}, {current_time_remove}, {current_time_format}")
                        start_frame = total_frame

                    # elif similar < 0.85 and not counting:
                    #     counting = True
                    #     start_frame = total_frame

                total_frame += 1
                # Press Q on keyboard to  exit
                # cv2.waitKey(1)
            else:
                break

        # times = [["00:00:00", get_duration(name)]]
        if os.path.isfile('concatenate.txt'):
            os.remove('concatenate.txt')

        open('concatenate.txt', 'w').close()
        for idx, time in enumerate(times):
            os.makedirs('tmp', exist_ok=True)
            output_filename = f"tmp/output{idx}.mp4"
            cmd = ["ffmpeg", "-i", filename, "-ss", time[0], "-to", time[1], "-f", "mp4", output_filename, "-y"]
            subprocess.check_output(cmd)

            with open("concatenate.txt", "a") as myfile:
                myfile.write(f"file {output_filename}\n")

        cmd = ["ffmpeg", "-f", "concat", "-i", "concatenate.txt", "-c", "copy", file_out_tmp, "-y"]
        try:
            subprocess.check_output(cmd).decode("utf-8").strip()
        except Exception as ex:
            pass

        cmd = [
            "ffmpeg",
            "-i", file_out_tmp,
            "-vf", "setpts=PTS/1.2,crop=in_w*0.9:in_h*0.9,scale=1080:1080,setdar=1",
            "-af", "atempo=1.2",
            "-vcodec", "libx264",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-g", "60",
            "-b:v", "3000k",
            "-acodec", "libmp3lame",
            "-ar", "44100",
            "-crf", "20",
            "-preset", "ultrafast",
            file_out,
            "-y"]
        try:
            subprocess.check_output(cmd).decode("utf-8").strip()
        except:
            pass

        for file_tmp in os.listdir('tmp'):
            os.remove(f"tmp/{file_tmp}")
        if os.path.isfile('concatenate.txt'):
            os.remove('concatenate.txt')
        # When everything done, release the video capture object
        cap.release()
        # out.release()

        # Closes all the frames
        cv2.destroyAllWindows()
