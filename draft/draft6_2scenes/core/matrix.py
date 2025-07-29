import numpy
from math import sin, cos, tan, pi
from numpy import subtract, divide, cross
from numpy.linalg import norm

class Matrix(object):

    @staticmethod
    def makeIdentity():
        return numpy.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makeTranslation(x,y,z):
        return numpy.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makeRotationX(angle):
        c = cos(angle)
        s = sin(angle)
        return numpy.array([
            [1, 0, 0, 0],
            [0, c,-s, 0],
            [0, s, c, 0],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makeRotationY(angle):
        c = cos(angle)
        s = sin(angle)
        return numpy.array([
            [c, 0, s, 0],
            [0, 1, 0, 0],
            [-s, 0, c, 0],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makeRotationZ(angle):
        c = cos(angle)
        s = sin(angle)
        return numpy.array([
            [c,-s, 0, 0],
            [s, c, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makeScale(s):
        return numpy.array([
            [s, 0, 0, 0],
            [0, s, 0, 0],
            [0, 0, s, 0],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makePerspective(angleOfView=60, aspectRatio=1, near=0.1, far=1000):
        a = angleOfView * pi / 180
        d = 1 / tan(a / 2)
        r = aspectRatio
        b = (near + far) / (near - far)
        c = 2 * near * far / (near - far)
        return numpy.array([
            [d/r, 0, 0, 0],
            [0, d, 0, 0],
            [0, 0, b, c],
            [0, 0, -1, 0]
        ]).astype(float)
    
    @staticmethod
    def makeOrthographic(left=-1, right=1, bottom=-1, top=1, near=0.1, far=1000):
        return numpy.array([
            [2/(right-left), 0, 0, -(right+left)/(right-left)],
            [0, 2/(top-bottom), 0, -(top+bottom)/(top-bottom)],
            [0, 0, -2/(far-near), -(far+near)/(far-near)],
            [0, 0, 0, 1]
        ]).astype(float)
    
    @staticmethod
    def makeLookAt(position, target):
        worldUp = numpy.array([0, 1, 0])
        forward = subtract(target, position)
        right = cross(worldUp, forward)

        # if forward and worldUp are parallel, 
        # right cross product is zero;
        # fix by perturbing worldUp vector slightly
        if norm(right) < 0.001:
            offset = numpy.array([0.001, 0.0, 0.0])
            right = cross(worldUp, forward + offset)

        up = cross(forward, right)

        # normalize all vectors to have length 1
        forward = divide(forward, norm(forward))
        right = divide(right, norm(right))
        up = divide(up, norm(up))

        return numpy.array([
            [right[0], up[0], -forward[0], position[0]],
            [right[1], up[1], -forward[1], position[1]],
            [right[2], up[2], -forward[2], position[2]],
            [0, 0, 0, 1]
        ]).astype(float)


    @staticmethod
    def toHomogeneous(matrix):
        """ Convert 3x3 matrix to 4x4 homogeneous matrix """
        if matrix.shape==(3,3):
            homogeneous = Matrix.makeIdentity()
            homogeneous[0:3, 0:3] = matrix
            homogeneous[3, 3] = 1
            return homogeneous
        elif matrix.shape==(4,4):
            return matrix
        else:
            raise ValueError("matrix must be 3x3 or 4x4")