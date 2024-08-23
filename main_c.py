import os
import shutil
import cv2
import First
import Second
import image_enhancement.run
from face_swap import face_swap
import argparse 
import time

parser = argparse.ArgumentParser(description='Options')

parser.add_argument('--src_path', dest='src_path', default='./images_test/src.jpg', help='Source image path')
parser.add_argument('--dst_path', dest='dst_path', default='./images_test/dst.jpg', help='Target image path')
parser.add_argument('--part', dest='part', default='face', help='Part to be swapped')
parser.add_argument('--debug', dest='debug', default=True, help='save debug')
parser.add_argument('--cropImg', dest='cropImg', default=False, help='Crop face')

args = parser.parse_args()

device = "cpu"

img_path = args.src_path
img2_path = args.dst_path

part_to_swap = args.part

result_path = './results/'

swapped_img, noClone = face_swap(img_path, img2_path, result_path, part_to_swap, visDebug=args.debug, cropImg=args.cropImg)
cv2.imwrite(result_path + 'swapped.jpg', swapped_img)
cv2.imwrite("static/Swapped.jpg", swapped_img)
cv2.imwrite(result_path + 'swapped_raw.jpg', noClone)

with open("output.txt", "a") as output_file:
    message = "Enhancing Image...\n"
    output_file.write(message)

shutil.copy("./images_test/src.jpg", "./static/src2.jpg")
shutil.copy("./images_test/dst.jpg", "./static/dst2.jpg")

First.startProcess(result_path + 'swapped.jpg')
Second.main()
image_enhancement.run.main()

os.remove('./results/swapped.jpg')
os.remove('FirstEnhanced.jpg')
os.remove('FinalEnhanced.jpg')
os.remove('SecondEnhanced.jpg')

