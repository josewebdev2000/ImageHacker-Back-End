"""
    This file contains code that will execute repetitious and self-contained operations to run the server of Image Hacker
"""

from uuid import uuid4
from os import listdir, path, remove

def get_valid_action_types():
    """Return a tuple of valid image editting operation categories."""
    
    return ("bgRemove", "convert", "crop", "filter", "posModify", "resize")

def get_valid_actions_by_action_type(action_type):
    """Return a tuple of valid image editting operations a category may perform."""
    
    if action_type == "bgRemove":
        return ("bgRemove",)
    
    elif action_type == "convert":
        return ("convert",)
    
    elif action_type == "crop":
        return ("crop",)
    
    elif action_type == "filter":
        return ("filter", "transformBlackNWhite", "colorFilter")
    
    elif action_type == "posModify":
        return ("rotate", "flip")
    
    elif action_type == "resize":
        return ("resize", "resizeKeepRatio", "resizeByPercentage")
    
    else:
        return ("Invalid Action Type",)

def get_valid_parameter_names_by_action(action):
    """Return a tuple of valid parameter according to the given action."""
    
    if action == "bgRemove" or action == "transformBlackNWhite":
        return None
    
    elif action == "convert":
        return ("outputImageFormat",)
    
    elif action == "crop":
        return ("x1", "y1", "x2", "y2")
    
    elif action == "filter":
        return ("filter",)
    
    elif action == "colorFilter":
        return ("brightness", "contrast", "saturation", "sharpness")
    
    elif action == "rotate":
        return ("degrees", "orientation")
    
    elif action == "flip":
        return ("direction",)
    
    elif action == "resize":
        return ("width", "height")
    
    elif action == "resizeKeepRatio":
        return ("dimparam", "dimparamType")
    
    elif action == "resizeByPercentage":
        return ("percentage",)
    
    else:
        return ("Invalid Action",)

def get_unique_identifier():
    """Return an ID to be associated to an object."""
    
    return str(uuid4())

def clear_out_folder(folder_path):
    """Delete all files of a folder."""
    
    # List all files in the folder
    files = listdir(folder_path)
    
    for file in files:
        
        file_path = path.join(folder_path, file)
        remove(file_path)