"""
    This file contains an Image Background Remover class to handle image background removing operations.
"""
from os import path, getcwd
from rembg import remove

from .ImageConverter import ImageConverter
from .errors.image_errors import ImageBgRemovalError, UnauthorizedImageFormatError
from .helpers.file_handling import get_pure_filename_from_img, get_new_image_filename, get_image_extension_from_img

class ImageBgRemover(object):
    """Handle Image Background Removing."""
    
    @staticmethod
    def remove_bg(img):
        """Remove the background from the given image."""
        
        # Only PNG images are allowed to have their background removed
        if not ImageConverter.is_img_of_type(img, "png"):
            raise UnauthorizedImageFormatError("Only PNG image files can have their backgrounds removed.")
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        try:
            img_no_bg = remove(img)
            img_no_bg.save(converted_image_name)
            return img_no_bg
        
        except Exception as e:
            print(e)
            raise ImageBgRemovalError("An unknown error occurred while trying to remove the backround from the given image.")      