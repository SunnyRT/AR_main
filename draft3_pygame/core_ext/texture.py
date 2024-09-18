import pygame
from OpenGL.GL import *

class Texture(object):

    def __init__(self, fileName=None, properties={}):

        # pygame object for storing pixel data;
        # can load from image or manipulate directly
        self.surface=None

        # reference of available texture from GPU
        self.textureRef = glGenTextures(1)

        # default property values for texture
        self.properties = {
            "magFilter": GL_LINEAR,
            "minFilter": GL_LINEAR_MIPMAP_LINEAR,
            "wrap": GL_REPEAT,
        }

        # overwrite default properties with user defined
        self.setProperties(properties)

        if fileName is not None:
            self.loadImage(fileName)
            self.uploadData()

    # load image from file
    def loadImage(self, fileName):
        self.surface = pygame.image.load(fileName)

    # set properties for texture
    def setProperties(self, properties):
        for name, data in properties.items():
            if name in self.properties.keys():
                self.properties[name] = data
            else: # unknown property type
                raise Exception("Unkown texture property: %s" % name)
            
    # upload pixel data to GPU
    def uploadData(self):

        # store image dimensions
        width = self.surface.get_width()
        height = self.surface.get_height()

        # convert image to string buffer format
        pixelData = pygame.image.tostring(self.surface, "RGBA", 1)

        # specify texture used by the following functions
        glBindTexture(GL_TEXTURE_2D, self.textureRef)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, 
                     width, height, 0, GL_RGBA, 
                     GL_UNSIGNED_BYTE, pixelData
                     )
        
        # generate mipmaps from uploaded pixel data
        glGenerateMipmap(GL_TEXTURE_2D) 

        # set texture properties
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, self.properties["magFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, self.properties["minFilter"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, self.properties["wrap"])
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, self.properties["wrap"])

        # set default border color to white;
        # important for rendering shadows
        glTexParameterfv(GL_TEXTURE_2D, GL_TEXTURE_BORDER_COLOR, [1.0, 1.0, 1.0, 1.0])