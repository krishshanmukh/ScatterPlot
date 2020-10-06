from skimage.feature import blob_log
from skimage.color import rgb2gray
from skimage.io import imread
import matplotlib.pyplot as plt
import cv2

#https://stackoverflow.com/questions/7227074/horizontal-line-detection-with-opencv
'''
Function takes in parameter as the path of the image and saves the 
subplots in save_path+count.png 
'''
def findSubPlots(img_path, save_path):
    import math
    import matplotlib.lines as mlines

    return_data =  {}

    img = imread(img_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 80, 120)
    lines = cv2.HoughLinesP(edges, 1, math.pi/2, 2, None, 30, 1);
    max_x = max([abs(line[0][2] - line[0][0]) for line in lines])
    max_y = max([abs(line[0][3] - line[0][1]) for line in lines])
    # print(max_x, max_y)
    # fig, ax = plt.subplots(1, 1, figsize=(10,10))
    # ax.imshow(img)

    # print(lines)
    y1 = 0
    x1 = 100000
    for line in lines:
        line = line[0]
        if abs(line[0] - line[2])/max_x > 0.9 and max(line[1], line[3]) > y1:
        # print(line, "b")
            y1 = max(line[1], line[3])
    
    y = [y1]

    for line in lines:
        line = line[0]
        if abs(line[1] - line[3])/max_y > 0.9 and min(line[0], line[2]) < x1:
            # print(line, "b")
            x1 = min(line[0], line[2])

    Flag = True

    # Add the bottom y coordinates for each of the plots
    while Flag:
        Flag = False
        for line in lines:
            diff_y = abs(line[0][3] - line[0][1])
            # Check if the horizontal line is part of next scatter plot bottom axes
            # print(line, max_x, max_y, y)
            if abs(diff_y/max_y) > 0.9 and 1.0 > max(line[0][1], line[0][3])/(y[-1] - max_y) > 0.7:
                # print(y, line[0])
                y.append(max(line[0][3], line[0][1]))
                Flag = True
                break
    
    # make a bounding box on the individual scatter plot
    def draw(x1, y1, max_x, max_y, cnt):
        if y1-max_y < 0:
            return
        crop_img = imread(img_path)[y1-max_y:y1, x1:x1+max_x]
        cv2.line(img, (x1, y1), (x1, y1-max_y), (255, 0, 0), 5)
        cv2.line(img, (x1, y1), (x1+max_x, y1), (255, 0, 0), 5)
        cv2.line(img, (x1+max_x, y1), (x1+max_x, y1-max_y), (255, 0, 0), 5)
        cv2.line(img, (x1, y1-max_y), (x1+max_x, y1-max_y), (255, 0, 0), 5)
        # cv2.imshow("", crop_img)
        cv2.imwrite(save_path[:-4]+ str(cnt) + ".png", crop_img)
        # x, y = [x1, x1], [y1, y1-max_y]
        # plt.plot(x, y, marker = 'o', color="g")
        # x, y = [x1, x1+max_x], [y1, y1]
        # plt.plot(x, y, marker = 'o', color="g")
        # x, y = [x1+max_x, x1+max_x], [y1, y1-max_y]
        # plt.plot(x, y, marker = 'o', color="g")
        # x, y = [x1, x1+max_x], [y1-max_y, y1-max_y]
        # plt.plot(x, y, marker = 'o', color="g")
    
    return_data['images'] = []
    for i, y1 in enumerate(y):
        # print(i, y1)
        draw(x1, y1, max_x, max_y, i)
        return_data['images'].append(save_path[:-4]+ str(i) + ".png")
    cv2.imwrite(save_path, img)
    # plt.savefig("split_" + img_path)

    return return_data
# findSubPlots("test.png", "test_split.png")