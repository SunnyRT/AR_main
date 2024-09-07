from core_ext.object3d import Object3D
from core.matrix import Matrix
from numpy.linalg import inv
from math import tan


class Camera(Object3D):

    def __init__(self, angleOfView=60,
                    aspectRatio=1.0,
                    near=0.1,
                    far=1000):
            super().__init__()

            self.theta = angleOfView
            self.r = aspectRatio
            self.n = near
            self.f = far
            self.zoom = 1.0

            self.perspectiveMatrix = Matrix.makePerspective(self.theta, self.r, self.n, self.f)
            
            # compute orthographic projection matrix to match perspective matrix
            self.orthographicMatrix = Matrix.makeOrthographic(-1, 1, -1, 1, self.n, self.f)
            self.updateOrthographicMatrix()
            
            # default to perspective projection
            self.isPerspective = True
            self.projectionMatrix = self.perspectiveMatrix
            self.viewMatrix = Matrix.makeIdentity()

    def updateViewMatrix(self):
        self.viewMatrix = inv(self.getWorldMatrix())



# FIXME: need to find a better way to define projection?????
    def toggleProjection(self):
        self.isPerspective = not self.isPerspective
        if self.isPerspective:
            self.projectionMatrix = self.perspectiveMatrix
        else:
            self.updateOrthographicMatrix()
            self.projectionMatrix = self.orthographicMatrix
    
    def updateOrthographicMatrix(self):
        d = 5 
        d = d / self.zoom
        # top = d * tan(self.theta/2)
        top = d * 4
        bottom = -top
        right = top * self.r
        left = -right
        self.orthographicMatrix = Matrix.makeOrthographic(left, right, bottom, top,
                                                        self.n, self.f)


    def update(self, inputObject, deltaTime=None):
        if inputObject.isKeyDown('space'):
            self.toggleProjection()
        
        
        if self.isPerspective:
            if inputObject.isKeyPressed('up'):
                self.theta -= 0.1
                self.perspectiveMatrix = Matrix.makePerspective(self.theta, self.r, self.n, self.f)
                self.projectionMatrix = self.perspectiveMatrix
            if inputObject.isKeyPressed('down'):
                self.theta += 0.1
                self.perspectiveMatrix = Matrix.makePerspective(self.theta, self.r, self.n, self.f)
                self.projectionMatrix = self.perspectiveMatrix
        else:
            if inputObject.isKeyPressed('up'):
                self.zoom += 0.001
                self.updateOrthographicMatrix()
                self.projectionMatrix = self.orthographicMatrix
            if inputObject.isKeyPressed('down'):
                self.zoom -= 0.001
                self.updateOrthographicMatrix()
                self.projectionMatrix = self.orthographicMatrix
            mouseScroll = inputObject.getMouseScroll()
            if mouseScroll != 0:
                self.zoom += mouseScroll * 0.01
                self.updateOrthographicMatrix()
                self.projectionMatrix = self.orthographicMatrix