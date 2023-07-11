# Custom Errors to be thrown when handling image editing operations
class UnauthorizedImageFormatError(Exception):
    """Throw this error when the given image is not allowed by the image converter."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class SameImageFormatError(Exception):
    """Throw this error when trying to convert image files of the same format."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ImageConversionError(Exception):
    """Throw this error while trying to convert an image to another format."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidImageSizeParameterError(Exception):
    """Throw this error when the user provides an invalid size parameter for images."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class InvalidImageSizeParameterTypeError(Exception):
    """Throw this error when ther provider type of image size parameter is neither width nor height."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ImageResizingError(Exception):
    """Throw this error while trying to resize an image."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

class ImageBgRemovalError(Exception):
    """Throw this error while trying to remove the backgrounf of an image."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)