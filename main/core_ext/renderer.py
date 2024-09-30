from OpenGL.GL import *
import wx
from core_ext.mesh import Mesh
from light.light import Light

class Renderer(object):

    def __init__(self, glcanvas=None, clearColor=[0,0,0]):

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE) # anti-aliasing
        glClearColor(clearColor[0], clearColor[1], clearColor[2], 1)

        if glcanvas is not None:
            self.windowSize = glcanvas.GetClientSize() # TODO:

    def render(self, scene, camera, clearColor=True, clearDepth=True, renderTarget=None):

        # activate render target if provided
        if renderTarget is None:
            # set render target to window
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glViewport(0, 0, self.windowSize.width, self.windowSize.height)
        else:
            # set render target properties
            glBindFramebuffer(GL_FRAMEBUFFER, renderTarget.framebufferRef)
            glViewport(0, 0, renderTarget.width, renderTarget.height)


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




        

                

            

            