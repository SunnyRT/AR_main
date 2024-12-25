from PIL import Image
import wx
from OpenGL.GL import *


class Texture(object):

    def __init__(self, fileName=None, properties={}):
        # # wx.Bitmap object for storing pixel data (converted from Pillow)
        # self.surface = None
        self.image_data = None

        # Reference of available texture from GPU
        self.textureRef = glGenTextures(1)

        # Default property values for texture
        self.properties = {
            "magFilter": GL_LINEAR,
            "minFilter": GL_LINEAR_MIPMAP_LINEAR,
            "wrap": GL_REPEAT,
        }

        # Overwrite default properties with user-defined ones
        self.setProperties(properties)

        if fileName is not None:
            self.loadImage(fileName)
            self.uploadData()

    # Load image from file using Pillow and convert to wx.Bitmap
    def loadImage(self, fileName):
        # Load the image using Pillow (PIL)
        image = Image.open(fileName)

        # Convert the image to RGBA format (to include alpha channel)
        image = image.convert("RGBA")

        # Get the raw image data as bytes (for OpenGL or other purposes)
        self.image_data = image.tobytes()

        # Get image width and height
        self.width, self.height = image.size

        print("Loaded image: %s (%d x %d)" % (fileName, self.width, self.height))

        # Convert to wx.Image for display in wxPython
        wx_image = wx.Image(image.size[0], image.size[1])
        wx_image.SetData(image.convert("RGB").tobytes())  # Set the RGB data
        wx_image.SetAlpha(image.getchannel("A").tobytes())  # Set the Alpha channel (transparency)

        # # Convert the wx.Image to wx.Bitmap for display in wx widgets
        # self.surface = wx.Bitmap(wx_image)

    # Set properties for texture
    def setProperties(self, properties):
        for name, data in properties.items():
            if name in self.properties.keys():
                self.properties[name] = data
            else:  # Unknown property type
                raise Exception("Unknown texture property: %s" % name)

    # Upload pixel data to GPU
    def uploadData(self):


        # Bind the texture, and upload the pixel data from Pillow
        glBindTexture(GL_TEXTURE_2D, self.textureRef)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, self.image_data)

        # Generate mipmaps from the uploaded pixel data
        glGenerateMipmap(GL_TEXTURE_2D)

        # Set texture properties
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.properties["magFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.properties["minFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.properties["wrap"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.properties["wrap"])

        # Set default border color to white (important for rendering shadows)
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])
