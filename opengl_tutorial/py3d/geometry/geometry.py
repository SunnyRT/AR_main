from core.attribute import Attribute

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