from OpenGL.GL import *
import wx
from core_ext.texture import Texture

class RenderTarget(object):

    def __init__(self, resolution=[512,512],
                 texture=None, properties={}):
        
        # values should equal texture dimensions
        self.width, self.height = resolution

        if texture is not None:
            self.texture = texture
        else:
            self.texture = Texture(None, {
                "magFilter": GL_LINEAR,
                "minFilter": GL_LINEAR,
                "wrapS": GL_CLAMP_TO_EDGE,
            })
            self.texture.setProperties(properties)
            self.texture.surface = wx.Bitmap(wx.Image(self.width, self.height)) # FIXME: not sure if this is correct
            self.texture.uploadData()

        
        # create framebuffer object
        self.framebufferRef = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebufferRef)

        # configure color buffer to use this texture 
        glFramebufferTexture2D(GL_FRAMEBUFFER, 
                               GL_COLOR_ATTACHMENT0, 
                               GL_TEXTURE_2D, 
                               self.texture.textureRef, 0)
        
        # generate a buffer to store depth information
        depthBufferRef = glGenRenderbuffers(1)
        glBindRenderbuffer(GL_RENDERBUFFER, depthBufferRef)
        glRenderbufferStorage(GL_RENDERBUFFER, 
                              GL_DEPTH_COMPONENT, 
                              self.width, self.height)
        glFramebufferRenderbuffer(GL_FRAMEBUFFER,
                                  GL_DEPTH_ATTACHMENT,
                                  GL_RENDERBUFFER,
                                  depthBufferRef);

        # check framebuffer status
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise Exception("Framebuffer status error!")



