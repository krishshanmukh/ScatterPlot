from __future__ import division

from models import *
from utils.utils import *
from utils.datasets import *

import os
import sys
import time
import datetime
import argparse

from PIL import Image

import torch
from torch.utils.data import DataLoader
from torchvision import datasets
from torch.autograd import Variable

import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.ticker import NullLocator

PREDICTED_FOLDER = os.path.join('static', 'predicted')

def detectPoints(folderName, column_values):
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_folder", type=str, default="./static/uploads/"+folderName+'/test', help="path to dataset")
    parser.add_argument("--model_def", type=str, default="./trainedmodel/config/yolov3-custom.cfg", help="path to model definition file")
    parser.add_argument("--weights_path", type=str, default="./trainedmodel/checkpoints/yolov3_ckpt_100.pth", help="path to weights file")
    parser.add_argument("--class_path", type=str, default="./trainedmodel/data/custom/classes.names", help="path to class label file")
    parser.add_argument("--conf_thres", type=float, default=0.8, help="object confidence threshold")
    parser.add_argument("--nms_thres", type=float, default=0, help="iou thresshold for non-maximum suppression")
    parser.add_argument("--batch_size", type=int, default=1, help="size of the batches")
    parser.add_argument("--n_cpu", type=int, default=0, help="number of cpu threads to use during batch generation")
    parser.add_argument("--img_size", type=int, default=416, help="size of each image dimension")
    parser.add_argument("--checkpoint_model", type=str, help="path to checkpoint model")
    opt = parser.parse_args()
    print(opt)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # os.makedirs("output/"+folderName+"/test", exist_ok=True)
    fname = os.path.join(PREDICTED_FOLDER, folderName, 'test')
    os.makedirs(fname, exist_ok=True)
    print(os.path.join(fname, 'test'))

    # Set up model
    model = Darknet(opt.model_def, img_size=opt.img_size).to(device)

    if torch.cuda.is_available():
        map_location=lambda storage, loc: storage.cuda()
    else:
        map_location='cpu'

    if opt.weights_path.endswith(".weights"):
        # Load darknet weights
        model.load_darknet_weights(opt.weights_path)
    else:
        # Load checkpoint weights
        model.load_state_dict(torch.load(opt.weights_path,map_location=map_location))

    model.eval()  # Set in evaluation mode

    dataloader = DataLoader(
        ImageFolder(opt.image_folder, img_size=opt.img_size),
        batch_size=opt.batch_size,
        shuffle=False,
        num_workers=opt.n_cpu,
    )

    classes = load_classes(opt.class_path)  # Extracts class labels from file

    Tensor = torch.cuda.FloatTensor if torch.cuda.is_available() else torch.FloatTensor

    imgs = []  # Stores image paths
    img_detections = []  # Stores detections for each image index

    # print("\nPerforming object detection:")
    prev_time = time.time()
    for batch_i, (img_paths, input_imgs) in enumerate(dataloader):
        # Configure input
        input_imgs = Variable(input_imgs.type(Tensor))

        # Get detections
        with torch.no_grad():
            detections = model(input_imgs)
            detections = non_max_suppression(detections, opt.conf_thres, opt.nms_thres)

        # Log progress
        current_time = time.time()
        inference_time = datetime.timedelta(seconds=current_time - prev_time)
        prev_time = current_time
        # print("\t+ Batch %d, Inference Time: %s" % (batch_i, inference_time))

        # Save image and detections
        imgs.extend(img_paths)
        img_detections.extend(detections)

    # Bounding-box colors
    cmap = plt.get_cmap("tab20b")
    colors = [cmap(i) for i in np.linspace(0, 1, 20)]

    imgPointsDict = {}
    # print(imgs)
    # print("\nSaving images:")
    # Iterate through images and save plot of detections
    for img_i, (path, detections) in enumerate(zip(imgs, img_detections)):

        print("(%d) Image: '%s'" % (img_i, path))

        # Create plot
        img = np.array(Image.open(path))
        plt.figure()
        fig, ax = plt.subplots(1)
        ax.imshow(img)

        imgPointsDict[img_i+1] = []
        
        # Draw bounding boxes and labels of detections
        if detections is not None:
            # Rescale boxes to original image
            detections = rescale_boxes(detections, opt.img_size, img.shape[:2])
            unique_labels = detections[:, -1].cpu().unique()
            n_cls_preds = len(unique_labels)
            bbox_colors = random.sample(colors, n_cls_preds)
            for x1, y1, x2, y2, conf, cls_conf, cls_pred in detections:

                # print("\t+ Label: %s, Conf: %.5f" % (classes[int(cls_pred)], cls_conf.item()))

                box_w = x2 - x1
                box_h = y2 - y1

                # print(img.shape)
                if x1<0 or x2<0 or y1<0 or y2<0 or x1 >img.shape[1] or x2>img.shape[1] or \
                y1 > img.shape[0] or y2 > img.shape[0]:
                    # print(x1, x2, y1, y2, "dsfs")
                    continue
                
                y_scale = (column_values[img_i+1][1] - column_values[img_i+1][0])
                y_limit = column_values[img_i+1][0]
                x_scale = column_values[0][1] - column_values[0][0]
                x_limit = column_values[0][0]
                point_x_cord = (x1 + x2)/2 * (x_scale) / img.shape[1] + x_limit
                point_y_cord = (img.shape[1] - (y1 + y2)/2)*y_scale/img.shape[0] + y_limit
                # print(point_x_cord, point_y_cord, conf, cls_conf, cls_pred)
                imgPointsDict[img_i+1].append((point_x_cord.item(),point_y_cord.item(), box_w, box_h))

                color = bbox_colors[int(np.where(unique_labels == int(cls_pred))[0])]
                #if not classes[int(cls_pred)] == "labels":
                # Create a Rectangle patch
                bbox = patches.Rectangle((x1, y1), box_w, box_h, linewidth=2, edgecolor=color, facecolor="none")
                  # Add the bbox to the plot
                ax.add_patch(bbox)
                # Add label
                # plt.text(
                #     x1,
                #     y1,
                #     s=classes[int(cls_pred)],
                #     color="white",
                #     verticalalignment="top",
                #     bbox={"color": color, "pad": 0},
                #     fontdict = {'size': 5},
                # )

        # Save generated image with detections
        plt.axis("off")
        plt.gca().xaxis.set_major_locator(NullLocator())
        plt.gca().yaxis.set_major_locator(NullLocator())
        print(path)
        filename = path.split("/")[-1].split(".")[0]
        plt.savefig(os.path.join(fname, filename+".jpg"), bbox_inches="tight", pad_inches=0.0)
        print(os.path.join(fname, filename+".jpg"))
        plt.close()

    return imgPointsDict, img.shape


if __name__ == "__main__":
    detectPoints("placeHolder")
