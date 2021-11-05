import os

from image_similarity_measures.quality_metrics import ssim
from skimage.metrics import structural_similarity
import matplotlib.pyplot as plt
import numpy as np
import cv2


def mse(imageA, imageB):
    # the 'Mean Squared Error' between the two images is the
    # sum of the squared difference between the two images;
    # NOTE: the two images must have the same dimension
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])

    # return the MSE, the lower the error, the more "similar"
    # the two images are
    return err


def compare_images(imageA, imageB, title):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(imageA, imageB)
    s = structural_similarity(imageA, imageB)
    # setup the figure
    # fig = plt.figure(title)
    # plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
    # # show first image
    # ax = fig.add_subplot(1, 2, 1)
    # plt.imshow(imageA, cmap=plt.cm.gray)
    # plt.axis("off")
    # # show the second image
    # ax = fig.add_subplot(1, 2, 2)
    # plt.imshow(imageB, cmap=plt.cm.gray)
    # plt.axis("off")
    # # show the images
    # plt.show()
    return s


if __name__ == '__main__':
    root_dir = "downloaded/Daily Dose of Satisfaction"
    start_index = 0
    for file in os.listdir(root_dir):
        # load the images -- the original, the original + contrast,
        # and the original + photoshop
        # Create a VideoCapture object and read from input file
        # If the input is the camera, pass 0 instead of the video file name
        file_name = "Oddly Satisfying Videos"
        input_file = f'downloaded/Daily Dose of Satisfaction/{file}'
        print(input_file)
        cap = cv2.VideoCapture(input_file)
        fps = cap.get(cv2.CAP_PROP_FPS)

        prev_frame = None
        similar = None
        # Check if camera opened successfully
        if cap.isOpened() == False:
            print("Error opening video stream or file")

        frame_width = int(cap.get(3))
        frame_height = int(cap.get(4))

        # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
        file_out = f'images/{file_name} Episode {start_index + 1}.avi'
        print(f"file out {file_out}")
        out = cv2.VideoWriter(file_out, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps, (frame_width, frame_height))

        scale_percent = 25  # percent of original img size
        width = int(frame_width * scale_percent / 100)
        height = int(frame_height * scale_percent / 100)
        dim = (width, height)
        number_frame = 0
        total_frame = 0
        # Read until video is completed
        while (cap.isOpened()):
            # Capture frame-by-frame
            ret, frame = cap.read()
            # convert the images to grayscale
            if ret == True:

                # Display the resulting frame
                # cv2.imshow('Frame', frame)
                if prev_frame is not None:
                    origin_frame = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
                    prev_img = cv2.resize(prev_frame, dim, interpolation=cv2.INTER_AREA)
                    similar = ssim(origin_frame, prev_img)
                    # prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
                    # original_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # similar = compare_images(frame, prev_frame, 'demo')
                    # print("SSIM: %.2f FILE_OUT: %s Time %.1f" % (similar, file_out, round(total_frame/(fps*60), 1)))

                if similar:
                    if similar < 0.9 and number_frame/(fps*60) > 4:
                        # 3 minutes
                        print('='*50)
                        number_frame = 0
                        start_index += 1
                        file_out = f'images/{file_name} Episode {start_index + 1}.avi'
                        out = cv2.VideoWriter(file_out, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                              fps, (frame_width, frame_height))
                    else:
                        number_frame += 1
                        out.write(frame)

                total_frame += 1
                prev_frame = frame
                # Press Q on keyboard to  exit
                if cv2.waitKey(25) & 0xFF == ord('q'):
                    break

            # Break the loop
            else:
                break

        # When everything done, release the video capture object
        cap.release()

        # Closes all the frames
        cv2.destroyAllWindows()

        os.rename(input_file, f'split/Daily Dose of Satisfaction/{file}')
