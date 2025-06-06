from core.matrix import Matrix
import numpy


class Object3D(object):

    def __init__(self):
        self.transform = Matrix.makeIdentity()
        self.parent = None
        self.children = []

    def add(self, child):
        self.children.append(child)
        child.parent = self

    def remove(self, child):
        self.children.remove(child)
        child.parent = None

    # calculate transformation of this Object3D relative 
    # to the root Object3D of the scene graph
    def getWorldMatrix(self):
        if self.parent is None:
            return self.transform
        else:
            return self.parent.getWorldMatrix() @ self.transform
        
    # return a single list containing all descendents
    def getDescendantList(self):
        # master list of all descendant nodes
        descendants = []
        # node to be added to descendants list,
        # and whose children will be added to descendants list
        nodesToProcess = [self]
        # continue processing nodes while any are left
        while len(nodesToProcess) > 0:
            # get next node to process
            node = nodesToProcess.pop()
            # add node to descendants list
            descendants.append(node)
            # add children of node to nodesToProcess list
            nodesToProcess.extend(node.children)
        return descendants
    


    # apply geometric transformation to model matrix of this Object3D
    def applyMatrix(self, matrix, localCoord=True):
        if localCoord:
            self.transform = self.transform @ matrix # local transformation
        else:
            self.transform = matrix @ self.transform # global transformation

    def translate(self, x, y, z, localCoord=True):
        m = Matrix.makeTranslation(x, y, z)
        self.applyMatrix(m, localCoord)

    def rotateX(self, angle, localCoord=True):
        m = Matrix.makeRotationX(angle)
        self.applyMatrix(m, localCoord)

    def rotateY(self, angle, localCoord=True):
        m = Matrix.makeRotationY(angle)
        self.applyMatrix(m, localCoord)

    def rotateZ(self, angle, localCoord=True):
        m = Matrix.makeRotationZ(angle)
        self.applyMatrix(m, localCoord)

    def scale(self, s, localCoord=True):
        m = Matrix.makeScale(s)
        self.applyMatrix(m, localCoord)


    # TODO: (New method) Rotate around the X-axis but relative to the global origin
    def rotateXorigin(self, angle):
        # Step 1: Translate to global origin
        position = self.getPosition()
        self.translate(-position[0], -position[1], -position[2], localCoord=False)

        # Step 2: Rotate around the X-axis in local coordinates
        self.rotateX(angle, localCoord=True)

        # Step 3: Translate back to original position
        self.translate(position[0], position[1], position[2], localCoord=False)

    # TODO: (New method) Rotate around the Y-axis but relative to the global origin
    def rotateYorigin(self, angle):
        # Step 1: Translate to global origin
        position = self.getPosition()
        self.translate(-position[0], -position[1], -position[2], localCoord=False)

        # Step 2: Rotate around the Y-axis in local coordinates
        self.rotateY(angle, localCoord=True)

        # Step 3: Translate back to original position
        self.translate(position[0], position[1], position[2], localCoord=False)


    
    # get/set position components of transform
    def getPosition(self):
        return [self.transform.item((0, 3)), self.transform.item((1, 3)), self.transform.item((2, 3))]
    
    def getWorldPosition(self):
        worldTransform = self.getWorldMatrix()
        return [worldTransform.item((0, 3)), worldTransform.item((1, 3)), worldTransform.item((2, 3))]
    
    def setPosition(self, position):
        self.transform.itemset((0, 3), position[0])
        self.transform.itemset((1, 3), position[1])
        self.transform.itemset((2, 3), position[2])


    def lookAt(self, targetPosition):
        self.transform = Matrix.makeLookAt(self.getWorldPosition(), targetPosition)

    # returns 3x3 submatrix with rotation data
    def getRotationMatrix(self):
        return numpy.array([self.transform[0][0:3],
                            self.transform[1][0:3],
                            self.transform[2][0:3]])
    
    def getDirection(self):
        forward = numpy.array([0, 0, -1])
        return list(self.getRotationMatrix() @ forward)
    
    def setDirection(self, direction):
        position = self.getPosition()
        targetPosition = [position[0] + direction[0],
                          position[1] + direction[1],
                          position[2] + direction[2]]
        self.lookAt(targetPosition)

        

    