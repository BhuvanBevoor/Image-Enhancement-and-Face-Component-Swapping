import numpy as np
import cv2
import math
import argparse


def pixelMapping(img, scale,height,width):
    pixelX = 0
    pixelY = 0
    resizedHeight = height * scale
    resizedWidth = width * scale
    resized = np.zeros((resizedHeight, resizedWidth, 3), np.uint8)

    for x in range(resizedWidth):
        for y in range(resizedHeight):
            if pixelX * scale == x and pixelY * scale == y:
                resized[y, x] = img[pixelY, pixelX]
                pixelY += 1
                black = False
            else:
                if y == 0:
                    black = True
                    break
                resized[y, x] = [0, 0, 0]
        if not black:
            pixelX += 1
        pixelY = 0
    return resized


def bilinearInterpolation(img, step,height,width):
    x1 = 0
    x2 = step
    left = img[0, 0]
    lb, lg, lr = left

    right = img[0, x2]
    rb, rg, rr = right

    height, width, _ = img.shape

    # Interpolate rows
    for y in range(height):
        if y % step == 0:
            for x in range(1, width):
                if x % step != 0:
                    b = ((x2 - x) / (x2 - x1)) * lb
                    g = ((x2 - x) / (x2 - x1)) * lg
                    r = ((x2 - x) / (x2 - x1)) * lr

                    b += ((x - x1) / (x2 - x1)) * rb
                    g += ((x - x1) / (x2 - x1)) * rg
                    r += ((x - x1) / (x2 - x1)) * rr

                    img[y, x] = [b, g, r]
                else:
                    x1 = x2
                    x2 += step
                    if x2 == width:
                        break

                    left = img[y, x]
                    lb, lg, lr = left

                    right = img[y, x2]
                    rb, rg, rr = right
        x1 = 0
        x2 = step

    left = img[0, 0]
    lb, lg, lr = left

    right = img[x2, 0]
    rb, rg, rr = right

    #Interpolate columns
    for x in range(width):
        for y in range(1, height):
            if y % step != 0:
                b = ((x2 - y) / (x2 - x1)) * lb
                g = ((x2 - y) / (x2 - x1)) * lg
                r = ((x2 - y) / (x2 - x1)) * lr

                b += ((y - x1) / (x2 - x1)) * rb
                g += ((y - x1) / (x2 - x1)) * rg
                r += ((y - x1) / (x2 - x1)) * rr

                img[y, x] = [b, g, r]
            else:
                x1 = x2
                x2 += step
                if x2 == height:
                    break

                left = img[y, x]
                lb, lg, lr = left

                right = img[x2, x]
                rb, rg, rr = right
        x1 = 0
        x2 = step

    return img





def main():
    name = "FirstEnhanced.jpg"
    img = cv2.imread(name)
    height, width, _ = img.shape
    scale = 2
    resized = pixelMapping(img, scale,height, width)
    resized = bilinearInterpolation(resized, scale,height,width)
    cv2.imwrite("SecondEnhanced.jpg", resized)
    cv2.imwrite("image_enhancement/example/original/SecondEnhanced.jpg", resized)
    cv2.imwrite("static/SecondEnhanced.jpg", resized)


if __name__ == "__main__":
    main()
