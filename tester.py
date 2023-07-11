"""
    Test how the classes that edit images work
"""

from PIL import Image
from image_editors.ImagePositionModifier import ImagePositionModifier

def main():
    
    ori_img = Image.open("test_pics/pikachu.jpg")
    #new_img = ImagePositionModifier.flip_img(ori_img, "vertical")
    #new_img.show()

if __name__ == "__main__":
    main()