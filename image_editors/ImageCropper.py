"""
    This file contains an Image Cropper Class to handle image cropping operations
"""
from os import path, getcwd

from .helpers.file_handling import get_image_extension_from_img, get_new_image_filename, get_pure_filename_from_img
from .errors.image_errors import InvalidCoordinateTypeError, InvalidCoordinateError, ImageCroppingError

class ImageCropper(object):
    """Handles Image Cropping Operations."""
    
    @staticmethod
    def get_bottom_right_coors(img):
        """Get back the bottom right coordinates of an image."""
        
        width, height = img.size
        right_coor, bottom_coor = (width - 1, height - 1)
        return right_coor, bottom_coor   
    
    @staticmethod
    def crop_img(img, x1, y1, x2, y2):
        """Crop an image according to given coordinates."""
        
        # Coordinates must be integers
        coors_are_ints = (isinstance(x1, int),isinstance(y1, int),isinstance(x2, int),isinstance(y2, int))
        
        if not all(coors_are_ints):
            raise InvalidCoordinateTypeError("Coordinates must be integers.")
        
        # Coordinates cannot be negative numbers
        coors_are_not_negative = (x1 >= 0, y1 >= 0, x2 >= 0, y2 >= 0)
        
        if not all(coors_are_not_negative):
            raise InvalidCoordinateError("Coordinates must be positive integers.")
        
        # x2 coordinate must be greater than x1 coordinate
        right_greater_than_left = x2 > x1
        
        if not right_greater_than_left:
            raise InvalidCoordinateError("Right coordinate must be greater than left coordinate.")
        
        # y2 coordinate must be greater than y2 coordinate
        bottom_greater_than_top = y2 > y1
        
        if not bottom_greater_than_top:
            raise InvalidCoordinateError("Bottom coordinate must be greater than top coordinate.")
        
        # Ensure right-bottom coordinate is not off-limits
        right_coor, bottom_coor = ImageCropper.get_bottom_right_coors(img)
        bottom_right_coors_within_bounds = x2 <= right_coor and y2 <= bottom_coor
        
        if not bottom_right_coors_within_bounds:
            raise InvalidCoordinateError("The coordinates of the bottom-right point are out of bounds.")
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        try:
            new_img = img.crop([x1, y1, x2, y2])
            new_img.save(converted_image_name)
            new_img.format = get_image_extension_from_img(img).upper()[1:]
            new_img.format = "JPEG" if new_img.format == "JPG" else new_img.format
            return new_img
        
        except Exception as e:
            print(e)
            raise ImageCroppingError("An unknown error occurred while trying to crop the image.")