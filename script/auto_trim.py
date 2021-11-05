import os
import cv2
import datetime
import subprocess
import numpy as np
from image_similarity_measures.quality_metrics import ssim


if __name__ == '__main__':
    # load the images -- the original, the original + contrast,
    # and the original + photoshop
    # Create a VideoCapture object and read from input file
    # If the input is the camera, pass 0 instead of the video file name
    root_folder = """downloaded/FamiliadeCalibre"""
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
        counting = False
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
                    # if similar >= 0.85:
                    #     # if number_frame/fps < 5:
                    #     number_frame += 1
                    #     # print(number_frame)
                    #     if number_frame == 1 and not counting:
                    #         # print(f"start counting {current_time}")
                    #         counting = True
                    #         # out.write(frame)
                    #         # cv2.imshow('Frame', frame_resize)
                    #     elif number_frame == 10*int(fps) and counting:
                    #         counting = False
                    #         times.append([start_time, current_time])
                    #         print(f"{start_time}, {current_time}")
                    if similar < 0.85 and ((total_frame - start_frame) > 5 * fps):
                        if counting:
                            counting = False
                        current_time_format = datetime.datetime.utcfromtimestamp(total_frame / fps).strftime("%H:%M:%S")
                        remove_frame = (start_frame + (keep_ratio * (total_frame - start_frame))) / fps
                        current_time_remove = datetime.datetime.utcfromtimestamp(remove_frame).strftime("%H:%M:%S")
                        start_time_format = datetime.datetime.utcfromtimestamp(start_frame / fps).strftime("%H:%M:%S")
                        times.append([start_time_format, current_time_remove])
                        print(f"{start_time_format}, {current_time_remove}, {current_time_format}")
                        start_frame = total_frame

                total_frame += 1
                # Press Q on keyboard to  exit
                # cv2.waitKey(1)
            else:
                break

        # times = [["00:00:00", get_duration(name)]]
        open('concatenate.txt', 'w').close()
        for idx, time in enumerate(times):
            os.makedirs('tmp', exist_ok=True)
            output_filename = f"tmp/output{idx}.mp4"
            cmd = ["ffmpeg", "-i", filename, "-ss", time[0], "-to", time[1], "-f", "mp4", output_filename, "-y"]
            subprocess.check_output(cmd)

            with open("concatenate.txt", "a") as myfile:
                myfile.write(f"file {output_filename}\n")

        cmd = ["ffmpeg", "-f", "concat", "-i", "concatenate.txt", "-c", "copy", file_out, "-y"]
        try:
            output = subprocess.check_output(cmd).decode("utf-8").strip()
        except:
            pass

        for file_tmp in os.listdir('tmp'):
            os.remove(f"tmp/{file_tmp}")
        os.remove('concatenate.txt')
        # When everything done, release the video capture object
        cap.release()
        # out.release()

        # Closes all the frames
        cv2.destroyAllWindows()
