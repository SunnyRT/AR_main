import numpy as np
import logging
from scipy.optimize import least_squares
from scipy.spatial import KDTree

from geometry.boxGeometry import BoxGeometry
from geometry.matchGeometry import MatchGeometry
from material.surfaceMaterial import SurfaceMaterial
from material.lineMaterial import LineMaterial
from core_ext.mesh import Mesh
from core.matrix import Matrix




class RegistratorICP(object):
    """ Iterative Closest Point (ICP) registration algorithm 
        To align mesh1 to target mesh2.
        By using Levenberg–Marquardt optimization. """
    

    def __init__(self, mesh1, mesh2, sceneObject, d_max=10.0):
        # self.mesh1 = mesh1
        self.mesh2 = mesh2
        self.sceneObject = sceneObject
        self.d_max = d_max
        self.closestPairs = None
        self.matchMesh = None
        # self.initialized = False
        self.initialize(mesh1)

    # FIXME:!!!!! need to reinitialize the registrator with new mesh1!!!!!!
    def initialize(self, mesh1=None):
        if mesh1 is not None:
            self.mesh1 = mesh1

        print("Initializing ICP registrator...")
        # 0. Extract vertexPosition with world matrix applied from both meshes
        mesh1Vertices = self.getMeshVertices(self.mesh1)
        mesh2Vertices = self.getMeshVertices(self.mesh2) 
        print(f"Number of vertices in mesh1: {mesh1Vertices.shape}")
        print(f"Number of vertices in mesh2: {mesh2Vertices.shape}")

        # 1. Filter out vertices in mesh2 with the same color as mesh1
        self.mesh1Vertices = mesh1Vertices
        self.mesh2Vertices = self.findSameColorPoints(mesh2Vertices)
        print(f"Number of vertices in mesh2 with the same color as mesh1: {self.mesh2Vertices.shape}")
        if len(mesh2Vertices) == 0:
            raise ValueError("No matching color found in target mesh.")
                                

        # 2. Find closest points between mesh1 and mesh2, and visualize mathcing pairs
        self.updateMatch()  

    def updateMatch(self, updateMesh1Vertices=False):
        # print("Updating ICP registrator...")
        if updateMesh1Vertices:
            self.mesh1Vertices = self.getMeshVertices(self.mesh1)
        self.findClosestPoints()
        self.createMatchMesh()            





    def getMeshVertices(self, mesh):
        meshTransform = mesh.getWorldMatrix()
        if meshTransform.shape != (4, 4):
            raise ValueError(f"Invalid world matrix shape{meshTransform.shape}. Expected (4, 4).")
        vertexPos = np.array(mesh.geometry.attributes["vertexPosition"].data)
        # print(f"vertexPos: {vertexPos.shape}")
        # Apply world matrix to vertex positions
        worldVertexPos4D = np.hstack((vertexPos, np.ones((len(vertexPos), 1)))) @ meshTransform.T
        # print(f"worldVertexPos4D: {worldVertexPos4D.shape}")
        # Convert homogeneous coordinates to 3D coordinates
        worldVertexPos = worldVertexPos4D[:, :3] / worldVertexPos4D[:, 3][:, np.newaxis]
        # print(f"worldVertexPos: {worldVertexPos.shape}")
        return worldVertexPos 
    
    
    def findSameColorPoints(self, mesh2Vertices, rtol=0.1):
        mesh1Colors = self.mesh1.geometry.attributes["vertexColor"].data
        mesh2Colors = self.mesh2.geometry.attributes["vertexColor"].data
        sameColorPoints = []

        # Check if mesh1 only has a single color
        if len(np.unique(mesh1Colors, axis=0)) > 1:
            raise ValueError("Mesh1 must have a single color for ICP registration.")
        
        mesh1Color = mesh1Colors[0]
        # print(f"mesh1Color: {mesh1Color}")
        # ##################################
        # # debugging: print all unique colors in mesh2
        # mesh2uniqueColors = np.unique(mesh2Colors, axis=0)
        # for i, color in enumerate(mesh2uniqueColors):
        #     print(f"mesh2Color #{i}: {color}")
        # ##################################

        for i, color in enumerate(mesh2Colors):
            # if np.array_equal(color, mesh1Color):
            if np.allclose(color, mesh1Color, rtol=rtol): # Allow for small relative errors
                sameColorPoints.append(mesh2Vertices[i])
        
        return np.array(sameColorPoints)

    def findClosestPoints(self):
        """ for each vertex in source mesh1, find the closest vertex in target mesh2 """
        if self.mesh1Vertices.shape[1] != 3 or self.mesh2Vertices.shape[1] != 3:
            raise ValueError("Input vertices must be 3D coordinates.")
        
        # mesh1Vertices = self.removeDuiplicateVertices(self.mesh1Vertices)
        # mesh2Vertices = self.removeDuiplicateVertices(self.mesh2Vertices)

        # Construct a KDTree for mesh2 vertices
        kdTree= KDTree(self.mesh2Vertices)
        closestPoints = []

        # # if no vertices in mesh2 can be used twice
        # availableMesh2Vertices = self.mesh2Vertices.copy()
        # usedIdx = set()


        for v1 in self.mesh1Vertices:

            dist, idx = kdTree.query(v1, distance_upper_bound=self.d_max)
            if dist < self.d_max:
                closestPoints.append((v1, self.mesh2Vertices[idx]))
                
        self.closestPairs = closestPoints
        # print(f"Number of closest pairs found: {len(self.closestPairs)}")
        if len(self.closestPairs) == 0:
            raise ValueError("No matching points found within max distance.")


    # FIXME: is duplicate vertices removal necessary?
    # def removeDuiplicateVertices(self, vertices, rtol=1e-5):
    #     """ Remove duplicate vertices in the list of vertices """
    #     uniqueVertices = np.unique(vertices, axis=0)
    #     if len(vertices) != len(uniqueVertices):
    #         logging.warning(f"Removed {len(vertices) - len(uniqueVertices)} duplicate vertices.")
    #     return uniqueVertices

    def createMatchMesh(self):
        if self.closestPairs is None or len(self.closestPairs) == 0:
            raise ValueError("No matching points found within max distance.")
        matchGeo = MatchGeometry(self.closestPairs)
        matchMat = LineMaterial({"lineType": "segments", "lineWidth": 1})
        matchMesh = Mesh(matchGeo, matchMat)
        if self.matchMesh in self.sceneObject.children:
            self.sceneObject.remove(self.matchMesh)
            del self.matchMesh # TODO: is this necessary????
        self.matchMesh = matchMesh
        self.sceneObject.add(self.matchMesh)        

    def makeTransformMatrix(self, theta_x, theta_y, theta_z, t_x, t_y, t_z):
        # Rotation matrices around each axis
        Rx = Matrix.makeRotationX(theta_x)
        Ry = Matrix.makeRotationY(theta_y)
        Rz = Matrix.makeRotationZ(theta_z)
        Txyz = Matrix.makeTranslation(t_x, t_y, t_z)

        # Combined rotation matrix
        TransformMatrix = Rx @ Ry @ Rz @ Txyz
        # print(f"TransformMatrix: {TransformMatrix}")
        return TransformMatrix
    
    def transformMesh(self, mesh, transformMatrix):
        # Apply rotation and translation
        mesh.applyMatrix(transformMatrix, localCoord=False) # FIXME: global transformation???

    def transformPoints(self, points, transformMatrix):
        # convert into 4D homogeneous coordinates
        # apply transformation
        # and convert back to 3D coordinates
        transformedPoints = (np.hstack((points, np.ones((len(points), 1)))) @ transformMatrix.T)[:, :3]
        # print(f"points before transform: {points.shape}, after transform: {transformedPoints.shape}")
        return transformedPoints 



    def objectiveFunction(self, params, sourcePoints, targetPoints):
        theta_x, theta_y, theta_z, t_x, t_y, t_z = params
        transformMatrix = self.makeTransformMatrix(theta_x, theta_y, theta_z, t_x, t_y, t_z)
        transformedPoints = self.transformPoints(sourcePoints, transformMatrix)

        # Calculate residuals (differences between transformed source and target)
        residuals = transformedPoints - targetPoints
        return residuals.flatten()





    # ICP Algorithm
    def register(self, n_iterations=1, tolerance=1e-3):


        for i in range(n_iterations):

            source_points, target_points = zip(*self.closestPairs)
            source_points = np.array(source_points)
            target_points = np.array(target_points)


            # FIXME: put this in as global variable to track all transformations
            # Initial transformation parameters (identity transformation)
            params = np.zeros(6)  # [theta_x, theta_y, theta_z, t_x, t_y, t_z]

            # 3. Optimize transformation using Levenberg–Marquardt
            result = least_squares(self.objectiveFunction, params, args=(source_points, target_points))
            paramsPrev = params
            params = result.x # Update the transformation parameters


            # 4. Apply the new transformation to mesh1 vertices and update the vertex positions in mesh1
            transformMatrix = self.makeTransformMatrix(*params)
            self.transformMesh(self.mesh1, transformMatrix)
            self.mesh1Vertices = self.getMeshVertices(self.mesh1)
            
            print(f"Iteration {i + 1}: Optimized parameters {params}")



            """ prepare for next iteration """
            # 2. Find closest points between mesh1 and mesh2
            self.updateMatch()
            
            if len(self.closestPairs) == 0:
                print("No matches found within max distance.")
                break
            """ end of iteration """


            # 5. Check for convergence
            if np.linalg.norm(params - paramsPrev) < tolerance:
                break

        return params  # Final transformation parameters




    

        