from OpenGL.GL import *
import numpy as np

class Attribute(object):

    def __init__(self, dataType, data):

        # type of elements in data array:
        # int | float | vec2 | vec3 | vec4
        self.dataType = dataType

        # array of data to be sstored in buffer (i.e. sent to GPU)
        self.data = data

        # reference of available buffer from GPU
        # arg = 1: number of buffers to generate
        # 1 buffer is created for each attribute
        self.bufferRef = glGenBuffers(1) 

        # upload data immediately
        self.uploadData()

    def uploadData(self):
        """ Upload data to GPU buffer: VBO """
        
        # convert data to numpy array; 32-bit float
        data = np.array(self.data, dtype=np.float32)

        # bind buffer to target (i.e. select buffer to use)
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)

        # store data in currently bound (i.e. active) buffer
        glBufferData(GL_ARRAY_BUFFER, data.ravel(), GL_STATIC_DRAW)

    
    def associateVariable(self, programRef, variableName):
        """ Associate variable in program with this buffer """

        # get reference for program variable with given name
        variableRef = glGetAttribLocation(programRef, variableName)

        # if the program does not reference the variable, exit
        if variableRef == -1:
            return
        
        # bind buffer to target (i.e. select buffer to use)
        glBindBuffer(GL_ARRAY_BUFFER, self.bufferRef)

        # specify how data will be read from currently bound buffer into specified variable
        # tell OpenGL how to interpret the data in the buffer and how to pass it to GPU for use in the shader program
        if self.dataType == 'int':
            glVertexAttribPointer(variableRef, 1, GL_INT, GL_FALSE, 0, None)
        elif self.dataType == 'float':
            glVertexAttribPointer(variableRef, 1, GL_FLOAT, GL_FALSE, 0, None)
        elif self.dataType == 'vec2':
            glVertexAttribPointer(variableRef, 2, GL_FLOAT, GL_FALSE, 0, None)
        elif self.dataType == 'vec3':
            glVertexAttribPointer(variableRef, 3, GL_FLOAT, GL_FALSE, 0, None)
        elif self.dataType == 'vec4':
            glVertexAttribPointer(variableRef, 4, GL_FLOAT, GL_FALSE, 0, None)
        else:
            raise Exception("Attribute " + variableName + " has invalid data type: " + self.dataType)
        
        # indicate that data will be streamed into the variable
        glEnableVertexAttribArray(variableRef)