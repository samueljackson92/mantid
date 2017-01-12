from __future__ import (absolute_import, division, print_function)
import numpy as np


def _rotate_image(data, rotation):
    # rot90 rotates counterclockwise; config.pre.rotation rotates clockwise
    data[:, :] = np.rot90(data[:, :], rotation)
    return data


def _rotate_stack(data, rotation):
    """
    NOTE: ONLY WORKS FOR SQUARE IMAGES
    Rotate every image of a stack

    :param data :: image stack as a 3d numpy array
    :param rotation :: rotation for the image

    Returns :: rotated data (stack of images)
    """

    counterclock_rotations = 4 - rotation

    for idx in range(0, data.shape[0]):
        _rotate_image(data[idx], counterclock_rotations)

    return data


def execute(data, config, flat=None, dark=None):
    """
    Rotates a stack (sample, flat and dark images).
    This function is usually used on the whole picture, which is a square.
    If the picture is cropped first, the ROI coordinates
    have to be adjusted separately to be pointing at the NON ROTATED image!

    :param data :: stack of sample images
    :param config :: pre-processing configuration
    :param flat :: stack of flat images
    :param dark :: stack of dark images

    Returns :: rotated images
    """

    from recon.helper import Helper
    h = Helper(config)
    h.check_data_stack(data)

    if not config.pre.rotation or config.pre.rotation < 0:
        h.tomo_print(" * Note: NOT rotating the input images.")
        return data, flat, dark

    rotation = config.pre.rotation
    h.pstart(
        " * Starting rotation step ({0} degrees clockwise), with pixel data type: {1}...".
            format(rotation * 90, data.dtype))

    data = _rotate_stack(data, rotation)
    if flat is not None:
        flat = _rotate_image(flat, rotation)
    if dark is not None:
        dark = _rotate_image(dark, rotation)

    h.pstop(" * Finished rotation step ({0} degrees clockwise), with pixel data type: {1}."
            .format(rotation * 90, data.dtype))

    h.check_data_stack(data)

    return data, flat, dark
