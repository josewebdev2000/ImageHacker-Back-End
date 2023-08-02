# Custom Errors to be thrown when handling JSON data from the front-end"""

class JsonError(Exception):
    """Common class for all JSON errors."""
    
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)