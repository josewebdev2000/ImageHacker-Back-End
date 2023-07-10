"""
    Test how the classes that edit images work
"""

from image_editors.ImageResizer import ImageResizer
from PIL import Image

def main():
    
    ori_img = Image.open("test_pics/charmander.png")
    resized_img = ImageResizer.resize_by_percentage(ori_img, 250)
    resized_img.show()

if __name__ == "__main__":
    main()