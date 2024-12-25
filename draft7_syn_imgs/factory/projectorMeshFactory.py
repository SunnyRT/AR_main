from factory.meshFactory import MeshFactory
from mesh.mesh import Mesh
from geometry.projectorGeometry import ProjectorGeometry
from geometry.geometry import Geometry
from material.lambertMaterial import LambertMaterial
from material.lineMaterial import LineMaterial

from core.matrix import Matrix
import numpy as np

class ProjectorMeshFactory(MeshFactory):
    def __init__(self, microscope, contourMesh, n, f, delta, color, alpha=0.3, mediator=None):
        super().__init__(mediator)
        
        self.n = n
        self.f = f
        self.delta = delta
        self.color = color
        self.ms = microscope
        self.contour=contourMesh

        self.material = LambertMaterial(properties={"useVertexColors":True, "alpha":alpha})


    def _getContourWorldPos(self, contourMesh): # one-off calling to load information
        contourPos = contourMesh.getWorldPosition()
        contourRot = contourMesh.getWorldRotationMatrix()
        contourVertPos_segments = contourMesh.geometry.positionData_segments

        contourVertWorldPos_segments = []
        # displace each vertex by the contour position & rotate by the contour rotation
        for i, segment in enumerate(contourVertPos_segments): 
            # Apply the transformation to each vertex in the segment
            temp = np.array([contourRot @ vertex + contourPos for vertex in segment])
            contourVertWorldPos_segments.append(temp)
        return contourVertWorldPos_segments       


    def createMesh(self):
        msPos = self.ms.getWorldPosition()
        contourWorldPos_segments = self._getContourWorldPos(self.contour)
        geometry = ProjectorGeometry(msPos=msPos, contourVertWorldPos_segments=contourWorldPos_segments, 
                                     n=self.n, f=self.f, delta=self.delta, color=self.color)
        self.mesh = Mesh(geometry, self.material)

        return self.mesh

    def correctWorldPos(self):
        msRot = self.ms.getWorldRotationMatrix()
        msInv = np.linalg.inv(msRot)
        msPos = self.ms.getWorldPosition()

        meshRot_old = self.mesh.getWorldRotationMatrix()
        meshRot= msInv @ meshRot_old
        self.mesh.setWorldRotation(meshRot)
        self.mesh.translate(-msPos[0], -msPos[1], -msPos[2]) 
        return self.mesh

    
    def update(self, del_n=None, del_f=None, delta=None, n=None, f=None):
        # override parent class method
        if del_n is not None: # update n
            self.n += del_n
        elif n is not None:
            self.n = n
        if del_f is not None:
            self.f += del_f
        elif f is not None:
            self.f = f
        if delta is not None:
            self.delta = delta
        self.mesh = super().update()
        if self.mesh is None:
            raise ValueError("ProjectorMeshFactory.update() error: NEW projectorMesh is None")
        else:
            pass
            self.correctWorldPos() # FIXME: translate back to the microscope position
        return self.mesh
    
















    # For DEBUGGING:
    def _createConeNormalMesh(self, vertex_positions, vertex_normals):
        if vertex_positions.shape[0] != vertex_normals.shape[0]:
            raise ValueError("vertex_positions and vertex_normals must have the same number of vertices")
        vertex_p1 = vertex_positions
        vertex_p2 = vertex_positions + 5*vertex_normals
        # Interleave vertex_p1 and vertex_p2
        positionData = np.empty((2 * len(vertex_p1), 3), dtype=vertex_p1.dtype)
        positionData[0::2] = vertex_p1  # Even indices: start points
        positionData[1::2] = vertex_p2  # Odd indices: end points
        colorData = np.tile([1, 0, 0], (positionData.shape[0], 1)) 
        normalGeometry = Geometry()
        normalGeometry.addAttribute("vec3", "vertexPosition", positionData)
        normalGeometry.addAttribute("vec3", "vertexColor", colorData)
    
        """""""""""""""create projector ray material"""""""""""""""
        normalMaterial = LineMaterial({"useVertexColors":True,
                            "lineWidth":2,
                            "lineType":"segments", 
                            "alpha":1})
                            

        return Mesh(normalGeometry, normalMaterial)