import SimpleITK as sitk
import cv2
import numpy as np

from datapipeline.load_tiff import tiffy


def preprocess_align(img, three_d=True):
    """
    Preprocess image before alignment
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

    for z in range(img.shape[0]):
        img[z] = cv2.GaussianBlur(img[z], (3, 3), 0)
        img[z] = cv2.morphologyEx(img[z], cv2.MORPH_TOPHAT, kernel)

    img = cv2.normalize(img, None, 0, 300, cv2.NORM_MINMAX)

    return img


def phase_correlation_blur(fixed_image_src, moving_image_src, return_dict):
    fixed_np = tiffy.load(fixed_image_src)
    moving_np = tiffy.load(moving_image_src)

    fixed_dapi_np = preprocess_align(fixed_np[:, 3, :, :])
    moving_dapi_np = preprocess_align(moving_np[:, 3, :, :])

    moving_image = sitk.GetImageFromArray(moving_dapi_np)
    fixed_image = sitk.GetImageFromArray(fixed_dapi_np)

    initial_transform = sitk.CenteredTransformInitializer(sitk.Cast(fixed_image, moving_image.GetPixelID()),
                                                          moving_image,
                                                          sitk.Euler3DTransform(),
                                                          sitk.CenteredTransformInitializerFilter.GEOMETRY)

    registration_method = sitk.ImageRegistrationMethod()

    # Similarity metric settings.
    registration_method.SetMetricAsCorrelation()
    registration_method.SetMetricSamplingStrategy(registration_method.RANDOM)
    registration_method.SetMetricSamplingPercentage(0.1)

    registration_method.SetInterpolator(sitk.sitkLinear)

    # Optimizer settings.
    registration_method.SetOptimizerAsGradientDescent(learningRate=3, numberOfIterations=20,
                                                      convergenceMinimumValue=1e-100, convergenceWindowSize=200)
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

    return_dict[moving_image_src] = list(offset_neg)
