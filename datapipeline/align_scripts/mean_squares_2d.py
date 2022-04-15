import os
import sys

import SimpleITK as sitk
import numpy as np

from datapipeline.align_scripts.align_errors import get_align_errors
from datapipeline.align_scripts.helpers.saving_align_errors import save_align_errors
from datapipeline.align_scripts.helpers.saving_offset import save_offset
from datapipeline.load_tiff import tiffy


def mean_squares_2d(fixed_image_src, moving_image_src, rand_dir, num_wav, start_time):
    print(f'{type(num_wav)=}')
    # Get Images from sources
    # ---------------------------------------------------
    fixed_np = tiffy.load(fixed_image_src, num_wav)
    moving_np = tiffy.load(moving_image_src, num_wav)
    median_z = fixed_np.shape[0] // 2
    fixed_dapi_np = fixed_np[median_z, -1, :, :]
    moving_dapi_np = moving_np[median_z, -1, :, :]
    # ---------------------------------------------------

    # Set image into proper variable
    # ---------------------------------------------------
    moving_image = sitk.GetImageFromArray(moving_dapi_np)
    fixed_image = sitk.GetImageFromArray(fixed_dapi_np)
    # ---------------------------------------------------

    # Run Simpleitk registration
    # ---------------------------------------------------
    print('Running Mean Squares 2D Alignment')
    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixed_image, moving_image.GetPixelID()),
                                                          moving_image,
                                                          sitk.Euler2DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)
    registration_method = sitk.ImageRegistrationMethod()
    registration_method.SetMetricAsMeanSquares()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.1)
    registration_method.SetInterpolator(sitk.sitkLinear)
    registration_method.SetOptimizerAsGradientDescent(learningRate=3, numberOfIterations=20,
                                                      convergenceMinimumValue=1e-100, convergenceWindowSize=200)
    registration_method.SetOptimizerScalesFromPhysicalShift()
    registration_method.SetInitialTransform(initial_transform, inPlace=False)
    # ---------------------------------------------------

    # Result from SimpleITK
    # ---------------------------------------------------
    final_transform = registration_method.Execute(sitk.Cast(fixed_image, sitk.sitkFloat32),
                                                  sitk.Cast(moving_image, sitk.sitkFloat32))
    print(f'{str(final_transform)=}')
    # ---------------------------------------------------

    # Get offset from result
    # ---------------------------------------------------
    offset_str = str(final_transform).split('Offset: ')[1].split('Center:')[0].split(']')[0]
    offset_list = (offset_str + ']').strip('][').split(', ')
    offset_list_int = [float(i) for i in offset_list]
    offset_flip = np.flip(offset_list_int)
    offset_neg = np.negative(offset_flip)
    # ---------------------------------------------------

    # Save the offset
    # ---------------------------------------------------
    save_offset(moving_image_src, offset_neg, rand_dir)
    # ---------------------------------------------------

    print(f'{offset_neg=}')

    # Get the alignment error
    # ---------------------------------------------------
    align_error = get_align_errors(fixed_np, moving_np, offset_neg)
    save_align_errors(moving_image_src, align_error, rand_dir)
    # ---------------------------------------------------


if __name__ == '__main__':

    if 'debug' not in sys.argv[1]:
        import argparse

        parser = argparse.ArgumentParser()
        parser.add_argument("--fixed_src")
        parser.add_argument("--moving_src")
        parser.add_argument("--rand_dir")
        parser.add_argument("--num_wav")
        parser.add_argument("--start_time")

        args, unknown = parser.parse_known_args()

        mean_squares_2d(args.fixed_src, args.moving_src, args.rand_dir, float(args.num_wav), args.start_time)

    elif sys.argv[1] == 'debug_mean_squares_2d':

        fixed_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_3/MMStack_Pos0.ome.tif'
        moving_src = '/groups/CaiLab/personal/alinares/raw/2021_0512_mouse_hydrogel/HybCycle_20/MMStack_Pos0.ome.tif'

        rand_dir = 'foo/mean_squares_2d'
        os.makedirs(rand_dir, exist_ok=True)
        num_wav = 4
        start_time = None

        mean_squares_2d(fixed_src, moving_src, rand_dir, num_wav, start_time)
