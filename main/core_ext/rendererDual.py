from OpenGL.GL import *
import wx
from mesh.mesh import Mesh
from light.light import Light

class RendererDual(object):

    def __init__(self, glcanvas, clearColor=[0,0,0]):

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE) # anti-aliasing
        glClearColor(clearColor[0], clearColor[1], clearColor[2], 1)

        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) 

        self.glcanvas = glcanvas
        self.vpL = None # viewport Left
        self.vpR = None # viewport Right


    def render(self, scene, camera, clearColor=True, clearDepth=True, viewportSplit=None):

        # glBindFramebuffer(GL_FRAMEBUFFER, 0) # set render target to window
        
        if viewportSplit is not None: # TODO: 
            height= self.glcanvas.GetClientSize().height
            width = int(self.glcanvas.aspectRatio * height)
            self.vp = (0, 0, width, height)

            if viewportSplit == "left":

                self.vpL = (0, 0, width // 2, height)
                glViewport(self.vpL[0], self.vpL[1], self.vpL[2], self.vpL[3])

            elif viewportSplit == "right":
                aspectRatio = camera.r
                right_height = int(width // 2 / aspectRatio)
                # center viewport vertically
                self.vpR = (width // 2+10, (height - right_height) // 2, width // 2, right_height)
                glViewport(self.vpR[0], self.vpR[1], self.vpR[2], self.vpR[3])
                
            else:
                raise ValueError("viewportSplit must be 'left' or 'right'")
        

        # clear color and depth buffer
        if clearColor:
            glClear(GL_COLOR_BUFFER_BIT)
        if clearDepth:
            glClear(GL_DEPTH_BUFFER_BIT)
            

        # update camera view (calculate inverse)
        camera.updateViewMatrix()

        # extract list of all Mesh objects in scene
        descendantList = scene.getDescendantList()
        meshFilter = lambda obj: isinstance(obj, Mesh) # anonymous function which returns True if obj is of type Mesh
        meshList = list(filter(meshFilter, descendantList)) # filter() returns an iterator, which contains only objects of type Mesh

        # extract list of all Light objects in scene
        lightFilter = lambda obj: isinstance(obj, Light) # anonymous function which returns True if obj is of type Light
        lightList = list(filter(lightFilter, descendantList)) # filter() returns an iterator, which contains only objects of type Light
        # scenes support 4 lights; precisely 4 must be present in the scene
        while len(lightList) < 4:
            lightList.append(Light())
        

        for mesh in meshList:

            # if this object is not visible, skip it
            if not mesh.visible:
                # print("skipping invisible object")
                continue
            
            # FIXME: handle transparency!!!
            if mesh.material.uniforms["alpha"].data != 1.0:
                glEnable(GL_BLEND)
                glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
                glDepthMask(GL_FALSE)
            else:
                glDisable(GL_BLEND)
                glDepthMask(GL_TRUE)

            glUseProgram(mesh.material.programRef)

            # bind (activate) VAO for rendering
            glBindVertexArray(mesh.vaoRef)

            # update uniform values stored outside of material
            mesh.material.uniforms["modelMatrix"].data = mesh.getWorldMatrix()
            mesh.material.uniforms["viewMatrix"].data = camera.viewMatrix
            mesh.material.uniforms["projectionMatrix"].data = camera.projectionMatrix
            # render lights
            # if material uses light data, add lights from list
            if "light0" in mesh.material.uniforms.keys():
                for lightNumber in range(4):
                    lightName = "light" + str(lightNumber)
                    lightObject = lightList[lightNumber]
                    mesh.material.uniforms[lightName].data = lightObject
                    # print(f"light {lightNumber} type: {lightObject}; color: {lightObject.color}")
                    # if lightObject.lightType == Light.DIRECTIONAL:
                    #     print(f"directional light direction: {lightObject.getDirection()}")
                    # elif lightObject.lightType == Light.POINT:
                    #     print(f"point light position: {lightObject.getPosition()}")
                    #     print(f"point light attenuation: {lightObject.attenuation}")
            # add camera position if needed (for specular highlights)
            if "viewPosition" in mesh.material.uniforms.keys():
                mesh.material.uniforms["viewPosition"].data = camera.getWorldPosition()

            # update uniforms stored in material
            for uniformObject in mesh.material.uniforms.values():
                uniformObject.uploadData()

            # update render settings
            mesh.material.updateRenderSettings()
            
            glDrawArrays(mesh.material.settings["drawStyle"], 0, mesh.geometry.vertexCount)



    def capture_vp(self, viewportSplit=None):
        """ Capture a screenshot of the chosen viewport, return wx.Image object """
        glFlush()

        if viewportSplit is None:
            viewport = self.vp
        elif viewportSplit == "left":
            viewport = self.vpL
        elif viewportSplit == "right":
            viewport = self.vpR
        else:
            raise ValueError("viewportSplit must be 'left' or 'right'")
        
        x,y,w,h = viewport

        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        data = glReadPixels(x,y,w,h, GL_RGB, GL_UNSIGNED_BYTE)
        image = wx.Image(w,h, data)
        image_flip = image.Mirror(False)
        return image_flip



        

                

            

            