import numpy as np
import logging
from scipy.optimize import least_squares

from geometry.boxGeometry import BoxGeometry
from material.surfaceMaterial import SurfaceMaterial
from core_ext.mesh import Mesh
from core.matrix import Matrix




class RegistratorICP(object):
    """ Iterative Closest Point (ICP) registration algorithm 
        To align mesh1 to target mesh2.
        By using Levenberg–Marquardt optimization. """
    

    def __init__(self, mesh1, mesh2):
        self.mesh1 = mesh1
        self.mesh2 = mesh2

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
    
    
    def findSameColorPoints(self, mesh2Vertices, rtol=0.01):
        mesh1Colors = self.mesh1.geometry.attributes["vertexColor"].data
        mesh2Colors = self.mesh2.geometry.attributes["vertexColor"].data
        sameColorPoints = []

        # Check if mesh1 only has a single color
        if len(np.unique(mesh1Colors, axis=0)) > 1:
            raise ValueError("Mesh1 must have a single color for ICP registration.")
        
        mesh1Color = mesh1Colors[0]
        for i, color in enumerate(mesh2Colors):
            # if np.array_equal(color, mesh1Color):
            if np.allclose(color, mesh1Color, rtol=rtol): # Allow for small relative errors
                sameColorPoints.append(mesh2Vertices[i])
        
        return np.array(sameColorPoints)

    def findClosestPoints(self, mesh1Vertices, mesh2Vertices, d_max):
        """ for each vertex in source mesh1, find the closest vertex in target mesh2 """
        if mesh1Vertices.shape[1] != 3 or mesh2Vertices.shape[1] != 3:
            raise ValueError("Input vertices must be 3D coordinates.")
        closestPoints = []
        for v1 in mesh1Vertices:
            # Compute the Euclidean distances from vertex v1 to all vertices in mesh2
            distances = np.linalg.norm(mesh2Vertices - v1, axis=1)

            # Find the closest vertex within max distance d_max
            min_dist = np.min(distances)
            if min_dist < d_max:
                closestPoints.append((v1, mesh2Vertices[np.argmin(distances)]))

        return closestPoints

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
    def register(self, d_max, n_iterations=10, tolerance=1e-3):

        # Extract vertexPosition with world matrix applied from both meshes
        mesh1Vertices = self.getMeshVertices(self.mesh1)
        mesh2Vertices = self.getMeshVertices(self.mesh2) 
        print(f"Number of vertices in mesh1: {mesh1Vertices.shape}")
        print(f"Number of vertices in mesh2: {mesh2Vertices.shape}")

        mesh2Vertices = self.findSameColorPoints(mesh2Vertices)
        print(f"Number of vertices in mesh2 with the same color as mesh1: {mesh2Vertices.shape}")
        if len(mesh2Vertices) == 0:
            raise ValueError("No matching color found in target mesh.")
                                
        # Initial transformation parameters (identity transformation)
        params = np.zeros(6)  # [theta_x, theta_y, theta_z, t_x, t_y, t_z]

        for i in range(n_iterations):
            # 1. Find closest points between mesh1 and mesh2
            closestPairs = self.findClosestPoints(mesh1Vertices, mesh2Vertices, d_max)
            if len(closestPairs) == 0:
                print("No matches found within max distance.")
                break

            source_points, target_points = zip(*closestPairs)
            source_points = np.array(source_points)
            target_points = np.array(target_points)


            # 2. Optimize transformation using Levenberg–Marquardt
            result = least_squares(self.objectiveFunction, params, args=(source_points, target_points))
            paramsPrev = params
            params = result.x # Update the transformation parameters


            # 3. Apply the new transformation to mesh1 vertices and update the vertex positions in mesh1
            transformMatrix = self.makeTransformMatrix(*params)
            self.transformMesh(self.mesh1, transformMatrix)
            mesh1Vertices = self.getMeshVertices(self.mesh1)
            
            print(f"Iteration {i + 1}: Optimized parameters {params}")

            # 4. Check for convergence
            if np.linalg.norm(params - paramsPrev) < tolerance:
                break

        return params  # Final transformation parameters