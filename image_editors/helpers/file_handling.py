"""
    This file contains code that will be repeated multiple times throughout the application.
    
    This code has nothing to do with Web Servers.
    
"""
import os

def get_pure_filename_from_img(img):
    """Get the file name from a Pillow Image Object without the folder path nor the file extension."""
    return os.path.splitext(os.path.basename(img.filename))[0]

def get_image_extension_from_img(img):
    """Get the image extension from a Pillow Image Object."""
    
    return os.path.splitext(os.path.basename(img.filename))[1]

def get_new_image_filename(folder_path, filename, extension):
    """Return the name of a new image file name"""
    
    filename_with_ext = f"{filename}{extension.lower()}" if extension.startswith(".") else f"{filename}.{extension.lower()}"
    return os.path.join(folder_path, filename_with_ext)