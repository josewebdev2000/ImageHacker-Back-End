"""
    This file contains an Image Position Modifier to handle Operations that change the positions in the pixels of an image.
"""
from os import path, getcwd
from PIL import Image

from .helpers.file_handling import get_image_extension_from_img, get_new_image_filename, get_pure_filename_from_img
from .errors.image_errors import InvalidRotationDegreeError, InvalidFlippingDirectionError, InvalidRotationOrientationError, ImagePositionModifyingError

class ImagePositionModifier(object):
    """Handles Image Positioning Operations"""
    
    # Make a tuple of allowed orientations for rotation
    VALID_ORIENTATION_PARAMETERS = ("CLOCKWISE", "ANTI_CLOCKWISE")
    
    # Make a dictionary of valid directions
    VALID_DIRECTIONS = {
        "HORIZONTAL": Image.FLIP_LEFT_RIGHT,
        "VERTICAL": Image.FLIP_TOP_BOTTOM
    }
    
    @staticmethod
    def rotate_img(img, degrees, orientation = "ANTI_CLOCKWISE"):
        """Rotate an image according to the given degree."""
        
        # Positive Degree -> Clockwise
        # Negative Degree -> Anticlockwise
        
        # If the user does not enter a positive integer, throw an error
        if not isinstance(degrees, int):
            raise InvalidRotationDegreeError("The rotation degree must be a positive integer between 0 and 360.")
        
        # If the given rotation degree is negative or its absolute value is greater than 360 throw an error
        if degrees < 0 or abs(degrees) > 360:
            raise InvalidRotationDegreeError("The rotation degree must be a positive integer between 0 and 360.")
        
        # If the given orientation is not in the list of valid orientation parameters throw an error
        if not orientation.upper() in ImagePositionModifier.VALID_ORIENTATION_PARAMETERS:
            raise InvalidRotationOrientationError(f"{orientation} is an invalid rotation orientation.")
        
        # If the orientation is clockwise, multiply the rotation degree by -1 so it becomes negative
        if orientation.upper() == "CLOCKWISE":
            degrees *= -1
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        try:
            new_img = img.rotate(degrees)
            new_img.save(converted_image_name)
            return new_img
        
        except Exception as e:
            print(e)
            raise ImagePositionModifyingError("An unknown error occurred while trying to rotate the image.")
    
    @staticmethod
    def flip_img(img, direction):
        """Flip an image either horizontally or vertically."""
        
        # Throw an error if the given flipping direction is undefined
        if not direction.upper() in ImagePositionModifier.VALID_DIRECTIONS:
            raise InvalidFlippingDirectionError(f"{direction} is an invalid flipping direction.")
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        try:
            new_img = img.transpose(ImagePositionModifier.VALID_DIRECTIONS[direction.upper()])
            new_img.save(converted_image_name)
            return new_img
        
        except Exception as e:
            print(e)
            raise ImagePositionModifyingError("An unknown error occurred while trying to flip the image.")
        