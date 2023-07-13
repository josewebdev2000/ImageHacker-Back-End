"""
    This file contains an Image Converter Class to handle image conversion to other file formats
"""
from PIL import Image

from os import getcwd, path

from .helpers.file_handling import get_pure_filename_from_img, get_new_image_filename
from .errors.image_errors import UnauthorizedImageFormatError, ImageConversionError, SameImageFormatError

class ImageConverter(object):
    """Handles Image File Format Conversion."""
    
    # Define allowed image file formats
    FILE_FORMATS = {
        "BMP": (".bmp",),
        "ICO": (".ico",),
        "JPG": (".jpg", ".jpeg"),
        "PNG": (".png",)
    }
    
    @staticmethod
    def is_img_of_type(img, type):
        """Return True if image extension indicates it belongs to the given type."""
        
        img_format = img.format.lower()
        
        # In case any error happens just return False
        try:
            return f".{img_format}" in ImageConverter.FILE_FORMATS[type.upper()]
        except:
            return False
    
    @staticmethod
    def is_img_allowed(img):
        """Return True if image extension belongs to the file formats"""
        
        # Produce list of possibilities for the file format of the given image
        possibilities = []
        
        for file_format in ImageConverter.FILE_FORMATS:
            
            possibilities.append(ImageConverter.is_img_of_type(img, file_format))
        
        return any(possibilities)
    
    @staticmethod
    def convert(img, output_file_format):
        """Convert an image to another file format."""
        
        # First check the given image is allowed
        if not ImageConverter.is_img_allowed(img):
            raise UnauthorizedImageFormatError(f"Image of type {img.format.lower()} is unauthorized.")
        
        if output_file_format.upper() not in ImageConverter.FILE_FORMATS:
            raise UnauthorizedImageFormatError(f"Cannot convert to {output_file_format} because it is unauthorized.")
        
        # If the output file format is the same as the input image, throw an error
        if output_file_format.lower() == img.format.lower():
            raise SameImageFormatError(f"Cannot convert to {output_file_format} because input and output image formats are the same.")
        
        # If everything works fine, do the following
        try:
            # Save the converted image in the temp folder
            pure_filename = get_pure_filename_from_img(img)
            
            converted_image_name = get_new_image_filename(
                path.join(getcwd(), "temp"),
                pure_filename,
                output_file_format
            )
            
            img.save(converted_image_name)
            converted_img = Image.open(converted_image_name)
            converted_img.format = output_file_format
            return converted_img
        
        # Otherwise raise an ImageConversionError
        except Exception as e:
            print(e)
            raise ImageConversionError(f"An unknown error occurred while trying to convert image to the {output_file_format.upper()} format.")