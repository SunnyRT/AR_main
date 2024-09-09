from OpenGL.GL import *
from core_ext.mesh import Mesh

class Renderer(object):

    def __init__(self, clearColor=[0,0,0]):

        glEnable(GL_DEPTH_TEST)
        glEnable(GL_MULTISAMPLE) # anti-aliasing
        glClearColor(clearColor[0], clearColor[1], clearColor[2], 1)

    def render(self, scene, camera, clearColor=True, clearDepth=True):

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

            # update uniforms stored in material
            for variableName, uniformObject in mesh.material.uniforms.items():
                uniformObject.uploadData()

            # update render settings
            mesh.material.updateRenderSettings()
            
            glDrawArrays(mesh.material.settings["drawStyle"], 0, mesh.geometry.vertexCount)

            

            