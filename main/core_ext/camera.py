from core_ext.object3d import Object3D
from core.matrix import Matrix
from numpy.linalg import inv
from geometry.boxGeometry import BoxGeometry
from material.lambertMaterial import LambertMaterial
from core_ext.mesh import Mesh


class Camera(Object3D):

    def __init__(self, isPerspective=False, angleOfView=60,
                    aspectRatio=1.0, 
                    distance=20, # FIXME: to find a better way to match perspective and orthographic projection????
                    near=0.1,
                    far=1000,
                    renderBox=False, boxDimensions=[5, 5, 10], boxColor=[0.5, 0.5, 0.5]):
        super().__init__()

        self.isPerspective = isPerspective
        self.theta = angleOfView
        self.r = aspectRatio
        self.d = distance
        self.n = near
        self.f = far

        self.zoom = 1.0


        if self.isPerspective:
            self.setPerspective()
        else:
            self.setOrthographic()

        self.viewMatrix = Matrix.makeIdentity()

        if renderBox:
            cameraGeometry = BoxGeometry(boxDimensions[0], boxDimensions[1], boxDimensions[2])
            cameraMaterial = LambertMaterial(properties={"baseColor": boxColor})
            cameraBox = Mesh(cameraGeometry, cameraMaterial)
            self.add(cameraBox)
            cameraBox.translate(0, 0, boxDimensions[2] / 2)

    def updateViewMatrix(self):
        self.viewMatrix = inv(self.getWorldMatrix())

    
    def setPerspective(self):
        self.projectionMatrix = Matrix.makePerspective(self.theta, self.r, self.n, self.f)


    def setOrthographic(self, left=None, right=None, bottom=None, top=None):
        if left is None:
            top = self.d / self.zoom
            bottom = -top
            right = top * self.r
            left = -right
        self.projectionMatrix = Matrix.makeOrthographic(left, right, bottom, top, self.n, self.f)




    # def toggleProjection(self):
    #     self.isPerspective = not self.isPerspective
    #     if self.isPerspective:
    #         self.setPerspective()
    #     else:
    #         self.setOrthographic()


    def update(self, inputObject, deltaTime=None):
        # if inputObject.isKeyDown('space'):
        #     self.toggleProjection()
        
        
        if self.isPerspective:
            if inputObject.isKeyPressed('up'):
                self.theta -= 0.1
                self.setPerspective()
            if inputObject.isKeyPressed('down'):
                self.theta += 0.1
                self.setPerspective()
        else:
            if inputObject.isKeyPressed('w'):
                self.zoom += 0.01
                self.setOrthographic()
            if inputObject.isKeyPressed('s'):
                self.zoom -= 0.01
                self.setOrthographic()
            mouseScroll = inputObject.getMouseScroll()
            if mouseScroll != 0:
                self.zoom += mouseScroll * 0.01
                self.setOrthographic()