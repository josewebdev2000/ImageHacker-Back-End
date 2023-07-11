"""
    This file contains an Image Filterer to handle image filtering operations
"""

from os import path, getcwd
from PIL import ImageFilter, ImageEnhance

from .helpers.file_handling import get_pure_filename_from_img, get_new_image_filename, get_image_extension_from_img
from .errors.image_errors import InvalidFilterError, InvalidColorParameterError, ImageColorFilteringError

class ImageFilterer(object):
    """Handles Image Filtering Operations."""
    
    # Define a dictionary of filters
    VALID_FILTERS = {
        "BLUR": ImageFilter.BLUR,
        "CONTOUR": ImageFilter.CONTOUR,
        "DETAIL": ImageFilter.DETAIL,
        "EDGE_ENHANCE": ImageFilter.EDGE_ENHANCE,
        "EDGE_ENHANCE_MORE": ImageFilter.EDGE_ENHANCE_MORE,
        "EMBOSS": ImageFilter.EMBOSS,
        "FIND_EDGES": ImageFilter.FIND_EDGES,
        "SHARPEN": ImageFilter.SHARPEN,
        "SMOOTH": ImageFilter.SMOOTH,
        "SMOOTH_MORE": ImageFilter.SMOOTH_MORE
    }
    
    
    @staticmethod
    def apply_filter(img, filter):
        
        # Throw an error if the given filter is not defined
        if filter.upper() not in ImageFilterer.VALID_FILTERS:
            raise InvalidFilterError(f"{filter} is an invalid filter.")
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        try:
            new_img = img.filter(ImageFilterer.VALID_FILTERS[filter.upper()])
            new_img.save(converted_image_name)
            return new_img
        
        except Exception as e:
            print(e)
            raise ImageColorFilteringError("An unknown error occured while applying color filters to the image.")
        
    
    @staticmethod
    def transform_to_black_n_white(img):
        """Convert an image to black and white."""
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        try:
            new_img = img.convert("L")
            new_img.save(converted_image_name)
            return new_img
        
        except Exception as e:
            print(e)
            raise ImageColorFilteringError("An unknown error occured while applying color filters to the image.")
            
    
    @staticmethod
    def apply_color_filter(img, brightness=1.0, contrast=1.0, saturation=1.0, sharpness=1.0):
        """Apply color filter to an image."""
        
        # Check that all given color paremeters are numbers
        is_brightness_num = isinstance(brightness, float) or isinstance(brightness, int)
        is_constrast_num = isinstance(contrast, float) or isinstance(contrast, int)
        is_saturation_num = isinstance(saturation, float) or isinstance(saturation, int)
        is_sharpness_num = isinstance(sharpness, float) or isinstance(sharpness, int)
        
        # If any of the given checks fail, throw an invalid color parameter error
        if not all((is_brightness_num, is_constrast_num, is_saturation_num, is_sharpness_num)):
            raise InvalidColorParameterError("Color parameters must be numbers.")
        
        pure_filename = get_pure_filename_from_img(img)
            
        # Grab the complete file path of this image
        converted_image_name = get_new_image_filename(
            path.join(getcwd(), "temp"),
            pure_filename,
            get_image_extension_from_img(img)
        )
        
        # Adjust color parameters
        try:
            
            brightness_enhancer = ImageEnhance.Brightness(img) # Brightness
            new_img = brightness_enhancer.enhance(brightness)
            
            contrast_enhancer = ImageEnhance.Contrast(new_img) # Constrast
            new_img = contrast_enhancer.enhance(contrast)
            
            color_enhancer = ImageEnhance.Color(new_img) # Saturation
            new_img = color_enhancer.enhance(saturation)
            
            sharpness_enhancer = ImageEnhance.Sharpness(new_img) # Sharpness
            new_img = sharpness_enhancer.enhance(sharpness)
            
            new_img.save(converted_image_name)
            return new_img
        
        except Exception as e:
            print(e)
            raise ImageColorFilteringError("An unknown error occured while applying color filters to the image.")