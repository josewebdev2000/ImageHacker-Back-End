# Back-End Server of the ImageHacker Web Application
from requests import get
from base64 import b64decode, b64encode
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from image_editors.helpers.file_handling import get_new_image_filename
from image_editors.ImageFilterer import ImageFilterer

from helpers.server_helpers import get_unique_identifier, remove_temp_file
from errors.json_errors import JsonError
"""
    Note:
    
    This server works as an API.
    Be sure that it ALWAYS RECEIVES JSON AS INPUT and that
    IT ALWAYS RETURNS JSON AS OUTPUT.
    
    NEVER RETURN HTML OR ANYTHING ELSE.
    ONLY JSON
    
    LONG LIVE JSON!!!!!!!!!!!!!!!!!!!!!!
    LONG LIVE JSON!!!!!!!!!!!!!!!!!!!!!!
    LONG LIVE JSON!!!!!!!!!!!!!!!!!!!!!!

    The following is the dict of acceptable action types with the actions they may perform:
    {
      "bg-remove": ("bg-remove",),
      "convert": ("convert",), 
      "crop": ("crop",), 
      "filter", ("filter", "transform-black-n-white", "color-filter")
      "pos-modify": ("rotate", "flip"), 
      "resize": ("resize", "resize-keep-ratio", "resize-keep-percentage")
    }
    
    Structure of JSON object to receive from the front-end
    {
        imageBase64URL: URL that represents the binary data of the image encoded in Base 64,
        imageFormat:    File Format of the Received Image (PNG if not specified),
        actionType:     Type of editting operation to be performed,
        action:         Specifies the action to be performed by the server,
        args:           Arguments to be provided to the specific image editting operation besides the image
    }
    
    Structure of JSON object to return from a successful 200 OK HTTP Response
    {
        imageBase64URL: URL that represents the binary data of the editted image encoded in Base 64,
        imageFormat: File Format of the editted image
    }
    
    Structure of JSON object to return from an unsuccessful 400 Client Error Response
    {
        errorMessage: An error message that specifies what the user did wrong
    }
    
    Structure of JSON object to return from an unsuccessful 500 Server Error Response
    {
        errorMessage: Tell there was a server-side error that interrupted the code
    }
    
    Custom Python Exception Classes to build related to HTTP:
    
    HttpBadRequestError: Throw this exception when the user performs a bad request
    HttpMethodNotAllowedError: Throw this exception when the user tries to access a route with a method that is not allowed
    HttpNotFoundError: Throw this exception when the user tries to access a route that does not exist
    HttpRequestTimeoutError: Throw this exception when the server wishes to cut off connection with the client immediately.
    HttpInternalServerError: Throw this exception when the server is unable to produce a proper response
    HttpServiceUnavailableError: Throw this exception when the server is down or overloaded
    
"""

app = Flask(__name__)
CORS(app)


"""HTTP Routes"""

@app.route("/", methods=["GET"])
def home():
    """Prove to the Front-End this web server works."""
    
    message = {"message": "ImageHacker Image Editting Web API server is up and running"}
    return jsonify(message)

@app.route("/img-proxy", methods=["GET"])
def image_proxy():
    """Proxy an Image URL to avoid CORS Error in the Front-End."""
    
    # Get Image Url
    image_url = request.args.get("url")
    
    if image_url:
        try:
            # Receive Image from Image URL
            response = get(image_url)
            if response.status_code == 200:
                
                # Prepare headers to send to the front-end
                headers = {"Content-Type": response.headers.get("Content-Type")}
                
                # Return a response that contains image data to the front-end
                return Response(response.content, headers=headers)
        
        # If something went wrong print it
        except Exception as e:
            print(e)
    
    # Return a Not Found response in case something went wrong
    return Response(status=404)

@app.route("/edit-img", methods=["POST"])
def edit_img():
    """Get an image to apply a color filter to it."""
    
    # Read the JSON data using the request Object from Flask
    image_data = request.json
    
    # Build response message
    res = {}
    
    # Get the file format from the request
    # Assign PNG if no image format was provided
    image_format = image_data.get("imageFormat", "PNG")
        
    # Generate a unique file name to save in the temp folder
    complete_temp_filename = get_temp_filename(image_format)
    
    try:
        # Get Image Pillow Object from Base 64 Encoded Image URL
        image = get_image_from_base64_url(image_data)
        
        # Save the image in the temp folver
        image.save(complete_temp_filename)
        
        # Close the image
        image.close()
        
        # Reopen the image saved in temp to ensure it's the right file format
        image_to_modify = Image.open(complete_temp_filename)
        
        # Apply filter to the image
        editted_image = ImageFilterer.transform_to_black_n_white(image_to_modify)
        
        # Extract Image Base64 URL from the editted image
        encoded_image_data = get_image_base64_url_from_image(editted_image)
        
        # Add the image data to the response along with its format
        res.update({"imageBase64URL": encoded_image_data, "imageFormat": editted_image.format.lower()})
        
        # Close the editted image object
        editted_image.close()
    
    except JsonError as e:
        print(e)
        res["errorMessage"] = e.message
        return custom_response(res, 400)
    
    except Exception as e:
        print(e)
        res["errorMessage"] = "The server failed to process your image"
        return custom_response(res, 500)
    
    else:
        return custom_response(res, 200)
    
    finally:
         # Remove the image since it's no longer required
        remove_temp_file(complete_temp_filename)


"""General functions"""
def custom_response(res_data, http_code):
    """Produce your own JSON response by providing JSON data along with an associated HTTP code"""
    
    res = jsonify(res_data)
    res.status_code = http_code
    return res

def get_temp_filename(image_format):
    """Get a temporary filename for an image based on its format."""
    
    # Produce a unique filename for this image
    unique_filename = get_unique_identifier()
    
    # Produce the temp filename
    temp_filename = get_new_image_filename(
        "temp",
        unique_filename,
        image_format
    )
    
    return temp_filename

def get_image_from_base64_url(image_data):
    """Return a Pillow Image Object from a Base 64"""
    
    try:
         # Get the Base64 Encoded Image data from the request
        image_base64 = image_data["imageBase64URL"]
        
        # Decode the Base64 Image data
        decoded_image_data = b64decode(image_base64)
        
        # Generate a fill-like object using the decoded image data
        image_pseudo_file = BytesIO(decoded_image_data)
    
        # Generate an image object from the received image data
        image = Image.open(image_pseudo_file)
    
    except KeyError as e:
        raise JsonError("The JSON field: \"imageBase64URL\" for the encoded Base64 Image URL is absent in this request.")
    
    except Exception as e:
        raise JsonError("The encoded Base64 Image URL provided in this request is invalid.")
    
    else:
        return image

def get_image_base64_url_from_image(image_obj):
    """Return an Image Base64 URL from a Python Pillow Object"""
    
    # Create a stream to get image binary data
    stream_for_editted_image = BytesIO()
    
    # Save the editted image to the temp folder with the format of the editted image
    image_obj.save(stream_for_editted_image, format=image_obj.format)
    
    # Seek back the beginning of the stream
    stream_for_editted_image.seek(0)
    
    # Read the stream to get the image data as bytes
    image_bytes = stream_for_editted_image.read()
    
    # Encode the bytes in base64
    encoded_image_data = b64encode(image_bytes).decode("utf-8")
    
    return encoded_image_data
    