
import SimpleITK as sitk
import os
import glob
import numpy as np
from load_tiff import tiffy
import cv2

def crop_center(img,cropx=1000,cropy=1000):
    
    y,x = img.shape
    startx = x//2-(cropx//2)
    starty = y//2-(cropy//2)    
    return img[starty:starty+cropy,startx:startx+cropx]

def blur_back_subtract(tiff_2d, num_tiles):
    blur_kernel  = tuple(np.array(tiff_2d.shape)//num_tiles)
    #print(f'{blur_kernel=}')
    blurry_img = cv2.blur(tiff_2d,blur_kernel)
    tiff_2d = cv2.subtract(tiff_2d, blurry_img)
    
    return tiff_2d

    
def blur_back_subtract_3d(tiff, num_tiles=3):
    
    for i in range(tiff.shape[0]):
        tiff[i,:,:] = blur_back_subtract(tiff[i,:,:], num_tiles)
    return tiff

def denoise(img_2d):

    img_2d = cv2.normalize(img_2d, None, 0, 255, cv2.NORM_MINMAX)
    
    
    img_2d = img_2d.astype(np.uint8)

    return img_2d
    
def preprocess_align(img, three_d=True, crop = None):
    """
    Preprocess image before alignment
    """
#     img = img[:,:crop,:crop]
    
    #img = blur_back_subtract_3d(img, num_tiles = 1000)
    
    tophat = 5
    kernel =cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(tophat,tophat))
        
    
    #print(f'{img.shape=}')
    #img = img*50
    img = cv2.normalize(img, None, 0, 100, cv2.NORM_MINMAX).astype(np.uint8)
    for z in range(img.shape[0]):
        blur = 5

        img[z] = cv2.GaussianBlur(img[z],(blur, blur),0) 
        
       # img[z] = cv2.morphologyEx(img[z], cv2.MORPH_OPEN, kernel)
        #
#     #img = blur_back_subtract_3d(img)
        #img= img*10000
        # clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        # img[z] = clahe.apply(img[z])
        #img[z] = cv2.equalizeHist(img[z])
        img[z] = cv2.morphologyEx(img[z], cv2.MORPH_TOPHAT, kernel)
        
    
        
    return img #     img_2d = cv2.cvtColor(img_2d.astype(np.uint8),cv2.COLOR_GRAY2RGB)
   
    
def mean_squares_blur(fixed_image_src, moving_image_src):
    
    fixed_np = tiffy.load(fixed_image_src)
    moving_np = tiffy.load(moving_image_src)

    crop = 3000

    fixed_dapi_np = preprocess_align(fixed_np[:,3,:,:])
    
    moving_dapi_np = preprocess_align(moving_np[:,3,:,:])
    
    moving_image = sitk.GetImageFromArray(moving_dapi_np)
    fixed_image = sitk.GetImageFromArray(fixed_dapi_np)

    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixed_image,moving_image.GetPixelID()), 
                                                      moving_image, 
                                                      sitk.Euler3DTransform(), 
                                                      sitk.CenteredTransformInitializerFilter.GEOMETRY)

    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    registration_method.SetMetricAsMattesMutualInformation(numberOfHistogramBins = 50)
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.001)

    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    registration_method.SetOptimizerAsGradientDescent(learningRate=1, numberOfIterations=200, convergenceMinimumValue=1e-10000, convergenceWindowSize=2)
    registration_method.SetOptimizerScalesFromPhysicalShift()


    # Don't optimize in-place, we would possibly like to run this cell multiple times.
    registration_method.SetInitialTransform(initial_transform, inPlace=False)


    final_transform = registration_method.Execute(sitk.Cast(fixed_image, sitk.sitkFloat32), 
                                                   sitk.Cast(moving_image, sitk.sitkFloat32))
    
    
    offset_str = str(final_transform).split('Offset: ')[1].split('Center:')[0].split(']')[0] 
    
    offset_list = (offset_str + ']').strip('][').split(', ') 
    offset_list_int = [float(i) for i in offset_list]
    
    offset_flip = np.flip(offset_list_int)
    
    offset_neg = np.negative(offset_flip)


    print(f'{offset_neg=}')
    return offset_neg
    