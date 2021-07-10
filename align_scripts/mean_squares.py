import SimpleITK as sitk
import os
import glob
import numpy as np
import sys
import pickle

sys.path.append(os.getcwd())

from load_tiff import tiffy
from align_scripts.align_errors import get_align_errors
from align_scripts.helpers.saving_offset import save_offset
from align_scripts.helpers.saving_align_errors import save_align_errors

def mean_squares(fixed_image_src, moving_image_src, rand_dir, num_wav):
    fixed_np = tiffy.load(fixed_image_src, num_wav)
    moving_np = tiffy.load(moving_image_src, num_wav)

    crop = None

    fixed_dapi_np = fixed_np[:,-1,:crop,:crop]
    moving_dapi_np = moving_np[:,-1,:crop,:crop]
    
    moving_image = sitk.GetImageFromArray(moving_dapi_np)
    fixed_image = sitk.GetImageFromArray(fixed_dapi_np)

    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixed_image,moving_image.GetPixelID()), 
                                                      moving_image, 
                                                      sitk.Euler3DTransform(), 
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
    
    save_offset(moving_image_src, offset_neg, rand_dir)
    
    align_error = get_align_errors(fixed_np, moving_np, offset_neg)
    
    save_align_errors(moving_image_src, align_error, rand_dir)
    
    
  
if sys.argv[1] != 'debug_mean_align':
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed_src")
    parser.add_argument("--moving_src")
    parser.add_argument("--rand_dir")
    parser.add_argument("--num_wav")
    
    args, unknown = parser.parse_known_args()
    
    mean_squares(args.fixed_src, args.moving_src, args.rand_dir, float(args.num_wav))
    
else:
    fixed_src = '/groups/CaiLab/personal/nrezaee/raw/test1/HybCycle_1/MMStack_Pos0.ome.tif'
    moving_src = '/groups/CaiLab/personal/nrezaee/raw/test1/HybCycle_2/MMStack_Pos0.ome.tif'
    rand_dir = '/home/nrezaee/temp'
    num_wav =4 
    mean_squares(fixed_src, moving_src, rand_dir, num_wav)