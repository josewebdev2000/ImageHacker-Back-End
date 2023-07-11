"""
    Test how the classes that edit images work
"""

from PIL import Image
from image_editors.ImageCropper import ImageCropper

def main():
    
    ori_img = Image.open("test_pics/pikachu.jpg")
    #new_img = ImageCropper.crop_img(ori_img, 50, 60, 100, 120)
    #new_img.show()

if __name__ == "__main__":
    main()