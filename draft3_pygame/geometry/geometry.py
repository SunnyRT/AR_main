from core.attribute import Attribute
import numpy as np

class Geometry(object):
    
    def __init__(self): 

        # store Attribute objects in a dictionary,
        # indexed by name of associated variable in shader program.
        # shader variable associations set up later
        # and stored in VAO in Mesh object.
        self.attributes = {}

        # number of vertices in geometry
        self.vertexCount = None

    def addAttribute(self, dataType, variableName, data):
        self.attributes[variableName] = Attribute(dataType, data)
        if self.vertexCount is None:
            self.countVertices()
        
    def countVertices(self):
        # number of vertices can be calculated from length of any Attribute object's array of data
        attrib = list(self.attributes.values())[0]
        self.vertexCount = len(attrib.data)

    # transform the data in an attribute using a matrix
    def applyMatrix(self, matrix, variableName="vertexPosition"):
        
        oldPositionData = self.attributes[variableName].data
        newPositionData = []

        for oldPos in oldPositionData:
            # avoid changing list references
            newPos = oldPos.copy()
            # add homogeneous fourth coordinate
            newPos.append(1)
            # multiply by matrix
            newPos = matrix @ newPos
            # remove homogeneous fourth coordinate
            newPos = list(newPos[:3])
            # add to new data list
            newPositionData.append(newPos)

        self.attributes[variableName].data = newPositionData
        # new data must be uploaded
        self.attributes[variableName].uploadData()


        # extract the rotation submatrix
        rotationMatrix = np.array([matrix[0][0:3],
                                   matrix[1][0:3],
                                   matrix[2][0:3]])
        
        oldVertexNormalData = self.attributes["vertexNormal"].data
        newVertexNormalData = []
        for oldNormal in oldVertexNormalData:
            newNormal = oldNormal.copy()
            newNormal = rotationMatrix @ newNormal
            newVertexNormalData.append(newNormal)
        self.attributes["vertexNormal"].data = newVertexNormalData

        oldFaceNormalData = self.attributes["faceNormal"].data
        newFaceNormalData = []
        for oldNormal in oldFaceNormalData:
            newNormal = oldNormal.copy()
            newNormal = rotationMatrix @ newNormal
            newFaceNormalData.append(newNormal)
        self.attributes["faceNormal"].data = newFaceNormalData


    # merge data from attributes of other geometry into this object;
    # requires both geometris to have attributes with the same names
    def merge(self, otherGeometry):
        for variableName, attributeObject in self.attributes.items():
            otherAttributeObject = otherGeometry.attributes[variableName]
            attributeObject.data += otherAttributeObject.data
            # new data must be uploaded
            attributeObject.uploadData()

        # update vertex count
        self.countVertices()
