"""
    This file contains an Image Resizer Class to handle resizing of image files
"""
from os import getcwd, path

from .errors.image_errors import InvalidImageSizeParameterError, InvalidImageSizeParameterTypeError, ImageResizingError
from .helpers.file_handling import get_pure_filename_from_img, get_new_image_filename, get_image_extension_from_img

class ImageResizer(object):
    """Handles Image Resizing."""
    
    @staticmethod
    def resize(img, width, height):
        
        try:
            # Grab the pure filename of this image
            pure_filename = get_pure_filename_from_img(img)
            
            # Grab the complete file path of this image
            converted_image_name = get_new_image_filename(
                path.join(getcwd(), "temp"),
                pure_filename,
                get_image_extension_from_img(img)
            )
            
            resized_img = img.resize((width, height))
            resized_img.save(converted_image_name)
            resized_img.format = get_image_extension_from_img(img).upper()[1:]
            resized_img.format = "JPEG" if resized_img.format == "JPG" else resized_img.format
            
            return resized_img
        
        except (ValueError, TypeError):
            raise InvalidImageSizeParameterError("Width and height parameters must be positive integers.")
        
        except Exception as e:
            print(e)
            raise ImageResizingError("An unknown error occurred while trying to resize the image.")
    
    @staticmethod
    def resize_keep_ratio(img, dimparam, dimparam_type = "w"):
        
        # Grab the original width and height of the image
        ori_width, ori_height = img.size
        
        if not isinstance(dimparam, int):
            raise InvalidImageSizeParameterError("Image size parameter must be an integer.")
        
        if dimparam <= 0:
            raise InvalidImageSizeParameterError("Image size parameter must be an integer.")
        
        # Grab the pure filename of this image
        pure_filename = get_pure_filename_from_img(img)
        
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
            )
        
        if dimparam_type == "w":
            new_height = int(ori_height * (dimparam / ori_width))
            
            try:
                resized_img = img.resize((dimparam, new_height))
                resized_img.save(converted_image_name)
                resized_img.format = get_image_extension_from_img(img).upper()[1:]
                resized_img.format = "JPEG" if resized_img.format == "JPG" else resized_img.format
                return resized_img
            
            except Exception as e:
                print(e)
                raise ImageResizingError("An unknown error occurred while trying to resize the image.")
        
        elif dimparam_type == "h":
            new_width = int(ori_width * (dimparam / ori_height))
            
            try:
                resized_img = img.resize((new_width, dimparam))
                resized_img.save(converted_image_name)
                resized_img.format = get_image_extension_from_img(img).upper()[1:]
                resized_img.format = "JPEG" if resized_img.format == "JPG" else resized_img.format
                return resized_img
            
            except Exception as e:
                print(e)
                raise ImageResizingError("An unknown error occurred while trying to resize the image.")
        
        else:
            raise InvalidImageSizeParameterTypeError(f"The given image size parameter {dimparam_type} is invalid.")
    
    @staticmethod
    def resize_by_percentage(img, percentage):
        """Resize an image according to a given percentage ratio."""
        
        # Define errors to throw according to percentage parameter
        if not isinstance(percentage, int):
            raise InvalidImageSizeParameterError("Image size parameter must be an integer.")
        
        if percentage <= 0:
            raise InvalidImageSizeParameterError("Image size parameter must be an integer.")
        
        # Grab the pure filename of this image
        pure_filename = get_pure_filename_from_img(img)
        
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
            )
        
        # Grab original width and height of this image
        ori_width, ori_height = img.size
        
        # Calculate new width and height according to given percentage
        new_width = int(ori_width * percentage / 100)
        new_height = int(ori_height * percentage / 100)
        
        try:
            resized_img = img.resize((new_width, new_height))
            resized_img.save(converted_image_name)
            resized_img.format = get_image_extension_from_img(img).upper()[1:]
            resized_img.format = "JPEG" if resized_img.format == "JPG" else resized_img.format
            return resized_img
            
        except Exception as e:
            print(e)
            raise ImageResizingError("An unknown error occurred while trying to resize the image.")