import SimpleITK as sitk
import os
import glob
import numpy as np
import sys
import pickle

sys.path.append(os.getcwd())

from load_tiff import tiffy
from align_scripts.helpers.saving_offset import save_offset

def mean_squares_2d(fixed_image_src, moving_image_src, rand_dir, num_wav):
    fixed_np = tiffy.load(fixed_image_src, num_wav)
    moving_np = tiffy.load(moving_image_src, num_wav)
    
    median_z = fixed_np.shape[0]//2

    fixed_dapi_np = fixed_np[median_z, -1,:,:]
    moving_dapi_np = moving_np[median_z, -1,:,:]

    moving_image = sitk.GetImageFromArray(moving_dapi_np)
    fixed_image = sitk.GetImageFromArray(fixed_dapi_np)

    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixed_image,moving_image.GetPixelID()), 
                                                      moving_image, 
                                                      sitk.Euler2DTransform(), 
                                                      sitk.CenteredTransformInitializerFilter.GEOMETRY)

    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    registration_method.SetMetricAsMeanSquares()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.1)

    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    registration_method.SetOptimizerAsGradientDescent(learningRate=3, numberOfIterations=20, convergenceMinimumValue=1e-100, convergenceWindowSize=200)
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
    
    #offset_neg = np.insert(offset_neg, 0, 0, axis=0)
    
    save_offset(moving_image_src, offset_neg, rand_dir)

import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--fixed_src")
parser.add_argument("--moving_src")
parser.add_argument("--rand_dir")
parser.add_argument("--num_wav")

args, unknown = parser.parse_known_args()

mean_squares_2d(args.fixed_src, args.moving_src, args.rand_dir, float(args.num_wav))
