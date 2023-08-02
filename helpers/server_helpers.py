"""
    This file contains code that will execute repetitious and self-contained operations to run the server of Image Hacker
"""

from uuid import uuid4
from os import path, remove

def get_unique_identifier():
    """Return an ID to be associated to an object."""
    
    return str(uuid4())

def remove_temp_file(temp_filename):
    """Remove a temp file."""
    
    if path.exists(temp_filename):
        remove(temp_filename)
    