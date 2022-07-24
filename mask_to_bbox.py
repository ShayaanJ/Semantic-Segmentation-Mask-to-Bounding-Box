from nis import cat
import os
import shutil
from cv2 import IMREAD_COLOR
import numpy as np
import cv2
from glob import glob
from tqdm import tqdm
from skimage.measure import label, regionprops, find_contours
import rasterio

image_size = (1920//2, 1080//2)

def show_img(img, title="Img"):
    img = cv2.resize(img, image_size)
    cv2.imshow(title, img)
    cv2.waitKey()
    cv2.destroyAllWindows()

def cat_two_img(img1, img2, title="Img"):
    img1 = cv2.resize(img1, image_size)
    img2 = cv2.resize(img2, image_size)
    cat_img = np.concatenate([img1, img2], axis=1)
    show_img(cat_img, title)

def write_img(path, img):
    cv2.imwrite(path, img)

def area(w, h):
    return w * h

def thresh(area, thresh=20):
    return area > thresh

""" Creating a directory """
def create_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

""" Convert a mask to border image """
def mask_to_border(mask):
    h, w = mask.shape
    border = np.zeros((h, w))

    contours = find_contours(mask, 128)
    for contour in contours:
        for c in contour:
            x = int(c[0])
            y = int(c[1])
            border[x][y] = 255

    return border

""" Mask to bounding boxes """
def mask_to_bbox(mask):
    bboxes = []

    mask = mask_to_border(mask)
    lbl = label(mask)
    props = regionprops(lbl)
    for prop in props:
        x1 = prop.bbox[1]
        y1 = prop.bbox[0]

        x2 = prop.bbox[3]
        y2 = prop.bbox[2]

        bboxes.append([x1, y1, x2, y2])

    return bboxes

def parse_mask(mask):
    mask = np.expand_dims(mask, axis=-1)
    mask = np.concatenate([mask, mask, mask], axis=-1)
    return mask

def making_seg_mask(img, id):
    img[img != id] = 0
    img[img == id] = 255
    return img

def read_tif(path):
    img_path = rasterio.open(path)
    img = img_path.read(1)
    return img

def combining_two_masks_or(mask1, mask2):
    mask = np.logical_or(mask1, mask2)
    return mask

def looping_over_bb_boxes(bboxes, x, threshold, color_bbox=(255,0, 0)):
    string = ""
    invalid_bboxes = 0
    for bbox in bboxes:
        class_id = 0
        top_lft_x, top_lft_y, bot_rgt_x, bot_rgt_y = bbox
        width = bot_rgt_x - top_lft_x
        height = bot_rgt_y - top_lft_y
        area_bbox = area(width, height)
        valid = thresh(area_bbox, threshold)
        if valid:
            x = cv2.rectangle(x, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color_bbox, 2)
            ctr_x = (top_lft_x + bot_rgt_x) / 2
            ctr_y = (top_lft_y + bot_rgt_y) / 2
            string += "{} {} {} {} {} \n".format(class_id, ctr_x, ctr_y, width, height)
        else:
            invalid_bboxes += 1

    print("Invalid bboxes: {}".format(invalid_bboxes))
    print("Valid bboxes: {}".format(len(bboxes) - invalid_bboxes))
    return (string, x)

def preparing_data(path):
    create_dir(path+"/RGB")
    create_dir(path+"/GT")
    create_dir(path+"/SHDW")
    create_dir(path+"/BLDG_FTPRINT")
    for file in os.listdir(path):
        try:
            type = file.split("_")[-2]
            if type == "RGB":
                shutil.move(path+"/"+file, path+"/RGB")
            elif type == "CLS":
                shutil.move(path+"/"+file, path+"/GT")
            elif type == "SHDW":
                shutil.move(path+"/"+file, path+"/SHDW")
            elif type == "BLDG_FTPRINT":
                shutil.move(path+"/"+file, path+"/BLDG_FTPRINT")
        except:
            pass

def preparing_results_dir(path):
    create_dir(path+"/txt")
    create_dir(path+"/building+shadow_bbox")
    create_dir(path+"/building_bbox")
    create_dir(path+"/building+shadow_mask")
    create_dir(path+"/building+shadow_bbox_combined")
    create_dir(path+"/building_mask+rgb")

def main(dest_folder, src_folder, threshold):
    """ Load the dataset """
    images = sorted(glob(os.path.join(src_folder, "RGB", "*")))
    masks = sorted(glob(os.path.join(src_folder, "GT", "*")))
    shadows = sorted(glob(os.path.join(src_folder, "SHDW", "*")))
    building_footprints = sorted(glob(os.path.join(src_folder, "BLDG_FTPRINT", "*")))

    """ Create folder to save images """
    preparing_data(src_folder)
    preparing_results_dir(dest_folder)

    """ Loop over the dataset """
    for rgb, gt, shdw, bldg_ftprint in tqdm(zip(images, masks, shadows, building_footprints), total=len(images)):
        """ Extract the name """
        name = rgb.split("/")[-1].split(".")[0]
        
        """ Read image and mask """
        original = cv2.imread(rgb, cv2.IMREAD_COLOR)
        rgb_copy = cv2.imread(rgb, cv2.IMREAD_COLOR)
        rgb = cv2.imread(rgb, cv2.IMREAD_COLOR)
        gt = read_tif(gt)
        shdw = read_tif(shdw)
        bldg_ftprint = read_tif(bldg_ftprint)


        # print(np.unique(shdw), "Shadow unique values")
        # print(np.unique(bldg_ftprint), "Building Footprint unique values")
        # print(np.unique(gt), "Ground Truth unique values")
        
        shdw = making_seg_mask(shdw, 255)
        bldg_ftprint = making_seg_mask(bldg_ftprint, 6)
        gt = making_seg_mask(gt, 6)
        cat_two_img(rgb,cv2.cvtColor(gt, IMREAD_COLOR), "RGB + SHDW")
        
        # bboxes = mask_to_bbox(shdw)
        # (string, new_img) = looping_over_bb_boxes(bboxes, rgb, threshold)
        # cat_two_img(cv2.cvtColor(shdw, IMREAD_COLOR), new_img, "RGB + SHDW")
        # new_mask = combining_two_masks_or(bldg_ftprint, shdw).astype(np.uint8)
        # new_mask = making_seg_mask(new_mask, 1)
        
        str1 = ""
        """ Detecting bounding boxes for footprint """
        bboxes = mask_to_bbox(gt)
        (string, new_img) = looping_over_bb_boxes(bboxes, rgb, threshold)
        str1 += string
        cat_two_img(rgb_copy, new_img, "RGB + GT")

        # """ Detecting bounding boxes for shadow """
        # bboxes = mask_to_bbox(shdw)
        # (string, building_shdw_sep_bbox_img) = looping_over_bb_boxes(bboxes, new_img, threshold, color_bbox=(0,0,255))
        # str1 += string

        # bboxes = mask_to_bbox(new_mask)
        # (string, building_shdw_comb_bbox_img) = looping_over_bb_boxes(bboxes, rgb_copy, threshold, color_bbox=(0,255,0))
        
        # print(len(string.split("\n")))
        # """writing txt file"""
        # file = open("results3/txt/" + name + ".txt", "w")
        # file.write(str1)
        # file.close()
        
        # """ Saving the image """
        # cv2.imwrite("results3/building+shadow_mask/" + name + ".png", np.concatenate([cv2.cvtColor(new_mask, IMREAD_COLOR), original], axis=1))
        # cv2.imwrite("results3/building+shadow_bbox/" + name + ".png", building_shdw_sep_bbox_img) 
        # cv2.imwrite("results3/building+shadow_bbox_combined/" + name + ".png", building_shdw_comb_bbox_img)
        # cv2.imwrite("results3/building_mask+rgb/" + name + ".png", np.concatenate([cv2.cvtColor(bldg_ftprint, IMREAD_COLOR), original], axis=1))
        cv2.imwrite("results3/building_bbox/" + name + ".jpg", new_img)

if __name__ == "__main__":
    """ Constants """
    dest_folder = "results3"
    src_folder = "data3"
    threshold = 500
    main(dest_folder, src_folder, threshold)
    