from mask_to_bbox import read_tif, making_seg_mask, its_morphin_time
import cv2
import numpy as np

IMAGE_PATH = ""
ANN_PATH = ""

rgb = cv2.imread(IMAGE_PATH, cv2.IMREAD_COLOR)
gt = read_tif(ANN_PATH)
gt = making_seg_mask(gt, 6)
kernel = np.ones((5, 5), np.uint8)
(string, eroded_bbox_img) = its_morphin_time(rgb.copy(), gt, kernel,500)