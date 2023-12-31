# Back-End Server of the ImageHacker Web Application
from requests import get
from base64 import b64decode, b64encode
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from image_editors.helpers.file_handling import get_new_image_filename
from image_editors.ImageBgRemover import ImageBgRemover
from image_editors.ImageConverter import ImageConverter
from image_editors.ImageCropper import ImageCropper
from image_editors.ImageFilterer import ImageFilterer
from image_editors.ImagePositionModifier import ImagePositionModifier
from image_editors.ImageResizer import ImageResizer
from image_editors.errors.image_errors import UnauthorizedImageFormatError, SameImageFormatError, ImageConversionError, InvalidImageSizeParameterError, InvalidImageSizeParameterTypeError, ImageResizingError, ImageBgRemovalError, InvalidFilterError, InvalidColorParameterError, ImageColorFilteringError, InvalidRotationDegreeError, InvalidRotationOrientationError, InvalidFlippingDirectionError, ImagePositionModifyingError, InvalidCoordinateTypeError, InvalidCoordinateError, ImageCroppingError

from helpers.server_helpers import clear_out_folder, get_unique_identifier, get_valid_action_types, get_valid_actions_by_action_type, get_valid_parameter_names_by_action
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
      "bgRemove": ("bgRemove",),
      "convert": ("convert",), 
      "crop": ("crop",), 
      "filter", ("filter", "transformBlackNWhite", "colorFilter")
      "posModify": ("rotate", "flip"), 
      "resize": ("resize", "resizeKeepRatio", "resizeByPercentage")
    }
    
    The following is the dict of acceptable parameters and data types of parameters for image editting actions:
    {
        "bgRemove": None,
        "transformBlackNWhite": None,
        "convert": {
            outputImageFormat: String
        },
        "crop": {
            x1: Integer,
            y1: Integer,
            x2: Integer,
            y2: Integer
        },
        "filter": {
            filter: String
        },
        "colorFilter": {
            brightness: Float,
            contrast: Float,
            saturation: Float,
            sharpness: Float
        },
        "rotate": {
            degrees: Integer,
            orientation: String
        },
        "flip": {
            direction: String
        },
        "resize": {
            width: Integer,
            height: Integer
        },
        "resizeKeepRatio": {
            dimparam: Integer,
            dimparamType: String
        },
        "resizeByPercentage": {
            percentage: Integer
        }
    }
    
    The following are an example structures of the action JSON field
    
    action: {
        "resize": {
            "resizeByPercentage": {
                percentage: 30
            }
        }
    }
    
    action: {
        "crop": {
            "crop": {
                x1: 90,
                y1: 120,
                x2: 250,
                y2: 200
            }
        }
    }
    
    action: {
        "convert": {
            "convert" : {
                outputImageFormat: "ICO"
            }
        }
    }
    
    action: {
        "bgRemove": {
            "bgRemove": None
        }
    }
    
    action: {
        "filter": {
            "transformBlackNWhite": None
        }
    }
    
    Structure of JSON object to receive from the front-end
    {
        imageBase64URL: URL that represents the binary data of the image encoded in Base 64,
        imageFormat:    File Format of the Received Image (PNG if not specified),
        action:         Image Editting operation to perform along with all associated information
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

"""Error Handlers"""

"""Client-Side Errors"""
@app.errorhandler(400)
def bad_request(e):
    return custom_response({"errorMessage": "A bad request was sent"}, 400)
    
@app.errorhandler(404)
def not_found(e):
    return custom_response({"errorMessage": "The requested resource could not be found"}, 404)

@app.errorhandler(405)
def method_not_allowed(e):
    return custom_response({"errorMessage": "The requested method cannot be used in the requested route"}, 405)

@app.errorhandler(408)
def request_timeout(e):
    return custom_response({"errorMessage": "It took more time than expected to produce a proper response for your request"}, 408)

@app.errorhandler(413)
def payload_too_large(e):
    return custom_response({"errorMessage": "The request contains a payload that is too large for the server to process"}, 413)

@app.errorhandler(414)
def uri_too_long(e):
    return custom_response({"errorMessage": "The request contains a URI that is too long for the server to process"}, 414)

@app.errorhandler(415)
def unsupported_media_type(e):
    return custom_response({"errorMessage": "The request contains media type that is unsupported by the server"}, 415)

"""Server-Side Errors"""
@app.errorhandler(500)
def internal_server_error(e):
    return custom_response({"errorMessage": "The server failed to provide a proper response for your request"},500)

@app.errorhandler(501)
def not_implemented(e):
    return custom_response({"errorMessage": "The requested method is not implemented by the server"}, 501)

@app.errorhandler(503)
def service_unavailable(e):
    return custom_response({"errorMessage": "The server is currently unavailable to process your request"}, 503)

"""HTTP Routes"""
@app.route("/", methods=["GET"])
def home():
    """Prove to the Front-End this web server works."""
    
    message = {"message": "ImageHacker Image Editting Web API server is up and running"}
    return custom_response(message, 200)

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
    image_format = extract_image_format_from_request(image_data)
        
    # Generate a unique file name to save in the temp folder
    complete_input_temp_filename = get_temp_filename(image_format)
    
    try:
        # Get Image Pillow Object from Base 64 Encoded Image URL
        image = get_image_from_base64_url(image_data)
        
        # Save the image in the temp folver
        image.save(complete_input_temp_filename)
        
        # Close the image
        image.close()
        
        # Reopen the image saved in temp to ensure it's the right file format
        image_to_modify = Image.open(complete_input_temp_filename)
        
        # Apply filter to the image
        editted_image = get_editted_image(image_to_modify, image_data)
        
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
        res["errorMessage"] = "The server failed to process your request"
        return custom_response(res, 500)
    
    else:
        return custom_response(res, 200)
    
    finally:
         # Remove the input and output images since they're no longer required
        clear_out_folder("temp")


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

def extract_image_format_from_request(image_data):
    """Return the image format from the JSON image data provided by a HTTP request."""
    
    try:
        image_format = image_data["imageFormat"]
        image_format = "PNG" if image_format == None else image_format
    
    except KeyError:
        raise JsonError("The JSON field: \"imageFormat\" for the Image Format is absent in this request")
    
    else:
        return image_format
     
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
    
    except KeyError:
        raise JsonError("The JSON field: \"imageBase64URL\" for the encoded Base64 Image URL is absent in this request")
    
    except Exception:
        raise JsonError("The encoded Base64 Image URL provided in this request is invalid")
    
    else:
        return image

def get_editted_image(input_image, image_data):
    """Return the editted image according to JSON data that came from an HTTP request."""
    
    try:
        
        # Extract data about the action to perform
        action_dict = image_data["action"]
        
        # If the length of the types of actions is not equal to one raise a JSON Error
        if len(action_dict) != 1:
            raise JsonError("Only one category of image editting operations must be specified for the JSON \"action\" field.")
        
        # Grab the action category
        action_type = tuple(action_dict.keys())[0]
        
        # If the action category is invalid raise a JSON Error
        if not action_type in get_valid_action_types():
            raise JsonError(f"The action category: \"{action_type}\" is invalid.")
        
        # Grab data about the specific action to perform
        specific_action_dict = action_dict[action_type]
        
        # If the length of the actions to perform is not equal to one raise a JSON Error
        if len(specific_action_dict) != 1:
            raise JsonError(f"Only one image editting operation must be specified per request.")
        
        # Grab the specific action to perform
        specific_action = tuple(specific_action_dict.keys())[0]
        
        # If the specific action is invalid raise a JSON Error
        if not specific_action in get_valid_actions_by_action_type(action_type):
            raise JsonError(f"The action: \"{specific_action}\" is invalid.")
        
        # Grab the parameters the specific action needs to edit the image
        specific_action_params_dict = specific_action_dict[specific_action]
        
        # If parameters were provided for an operation that does not require it raise a JsonError
        if specific_action_params_dict and (specific_action == "bgRemove" or specific_action == "transformBlackNWhite"):
            raise JsonError(f"The action: \"{specific_action}\" requires no arguments for it to work.")
        
        # If no parameters have been given for actions that are not "bgRemove" and "transformBlackNWhite" raise a JSON Error
        if not specific_action_params_dict and specific_action != "bgRemove" and specific_action != "transformBlackNWhite":
             raise JsonError(f"The action: \"{specific_action}\" requires arguments for it to work.")
        
        # Grab the arguments for this action if the specific action params dict is not none
        if specific_action_params_dict:
            specific_action_params = tuple(specific_action_params_dict.keys())
            
            # If the given parameters are different from the expected parameters for this specific action raise a JSON Error
            if set(specific_action_params) != set(get_valid_parameter_names_by_action(specific_action)):
                raise JsonError(f"The action : \"{specific_action}\" was provided with the wrong parameters for this request.")
            
            # Convert to integer every parameter that was given as a number
            for specific_action_param in specific_action_params_dict:
                
                if isinstance(specific_action_params_dict[specific_action_param], str):
                
                    if specific_action_params_dict[specific_action_param].isdigit():
                        specific_action_params_dict[specific_action_param] = int(specific_action_params_dict[specific_action_param])
            
        
        # Edit the image and return a new one
        if specific_action == "bgRemove":
            editted_image = ImageBgRemover.remove_bg(input_image)
        
        elif specific_action == "convert":
            editted_image = ImageConverter.convert(input_image, specific_action_params_dict["outputImageFormat"])
        
        elif specific_action == "crop":
            editted_image = ImageCropper.crop_img(input_image, specific_action_params_dict["x1"], specific_action_params_dict["y1"], specific_action_params_dict["x2"], specific_action_params_dict["y2"])
        
        elif specific_action == "filter":
            editted_image = ImageFilterer.apply_filter(input_image, specific_action_params_dict["filter"])
        
        elif specific_action == "colorFilter":
            editted_image = ImageFilterer.apply_color_filter(input_image, specific_action_params_dict["brightness"], specific_action_params_dict["contrast"], specific_action_params_dict["saturation"], specific_action_params_dict["sharpness"])
        
        elif specific_action == "transformBlackNWhite":
            editted_image = ImageFilterer.transform_to_black_n_white(input_image)
        
        elif specific_action == "rotate":
            editted_image = ImagePositionModifier.rotate_img(input_image, specific_action_params_dict["degrees"], specific_action_params_dict["orientation"])
        
        elif specific_action == "flip":
            editted_image = ImagePositionModifier.flip_img(input_image, specific_action_params_dict["direction"])
        
        elif specific_action == "resize":
            editted_image = ImageResizer.resize(input_image, specific_action_params_dict["width"], specific_action_params_dict["height"])
        
        elif specific_action == "resizeKeepRatio":
            editted_image = ImageResizer.resize_keep_ratio(input_image, specific_action_params_dict["dimparam"], specific_action_params_dict["dimparamType"])
        
        elif specific_action == "resizeByPercentage":
            editted_image = ImageResizer.resize_by_percentage(input_image, specific_action_params_dict["percentage"])
        
        else:
            pass
    
    except KeyError:
        raise JsonError("The given JSON payload does not contain proper data to edit the given image.")
    
    except AttributeError as e:
        print(e)
        raise JsonError("The given JSON data could not be parsed.")
    
    except (UnauthorizedImageFormatError, SameImageFormatError, ImageConversionError, InvalidImageSizeParameterError, InvalidImageSizeParameterTypeError, ImageResizingError, ImageBgRemovalError, InvalidFilterError, InvalidColorParameterError, ImageColorFilteringError, InvalidRotationDegreeError, InvalidRotationOrientationError, InvalidFlippingDirectionError, ImagePositionModifyingError, InvalidCoordinateTypeError, InvalidCoordinateError, ImageCroppingError) as e:
        raise JsonError(e.message)
    
    else:
        return editted_image

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
    