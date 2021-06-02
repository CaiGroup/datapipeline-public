import os
import glob
import cv2

def blur_back_subtract(tiff_2d, num_tiles):
    blur_kernel  = tuple(np.array(tiff_2d.shape)//num_tiles)
    blurry_img = cv2.blur(tiff_2d,blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)
    
    return tiff_2d

def blur_back_subtract_3d(img_3d, num_tiles=10):
    
    for i in range(img_3d.shape[0]):
        img_3d[i,:,:] = blur_back_subtract(img_3d[i,:,:], num_tiles)
    return img_3d

def normalize(img, max_norm=1000):
    norm_image = cv2.normalize(img, None, alpha=0, beta=max_norm, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    return norm_image

def tophat_2d(img_2d):
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))*4
    tophat_img = cv2.morphologyEx(img_2d, cv2.MORPH_TOPHAT, kernel)
    return tophat_img

def tophat_3d(img_3d):
    print(f'{img_3d.shape=}')
    for i in range(len(img_3d)):
        print(f'{i=}')
        img_3d[i] = tophat_2d(img_3d[i])
    return img_3d

def preprocess_img(img_3d):
    #norm_img_3d = normalize(img_3d)
    blur_img_3d = blur_back_subtract_3d(img_3d)
    print(f'{blur_img_3d.shape=}')
    #tophat_img_3d = tophat_3d(blur_img_3d)
    nonzero_img_3d = np.where(blur_img_3d < 0, 0, blur_img_3d)
    return nonzero_img_3d