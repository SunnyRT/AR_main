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
    

    def __init__(self, mesh1, mesh2, sceneObject, mesh1Parent=None, d_max=10.0):
        self.mesh1 = mesh1 # projector coneMesh
        self.mesh2 = mesh2
        self.sceneObject = sceneObject
        self.mesh1Parent = mesh1Parent
        self.d_max = d_max
        self.closestPairsPerRay = None
        self.matchMesh = None

        # Debugging output
        self.matchCount = 0
        self.meanError = float('inf')
        self.meanNormMeasure = 0

        print("Initializing ICP registrator...")
        # 0. Extract vertexPosition with world matrix applied from both meshes
        mesh1Vertices, mesh1VertNorm = self.getMeshVertData(self.mesh1)
        mesh2Vertices, mesh2VertNorm = self.getMeshVertData(self.mesh2) 
        # print(f"Number of vertices in mesh1: {mesh1Vertices.shape}")
        # print(f"Number of vertices in mesh2: {mesh2Vertices.shape}")
        # print(f"shape of mesh1VertNorm: {mesh1VertNorm.shape}")
        # print(f"shape of mesh2VertNorm: {mesh2VertNorm.shape}")
        self.mesh1VertRay = self.mesh1.geometry.attributes["uniqueVertexRay"].data # Record which ray each vertex in mesh1 lies on

        print(f"Number of rays in mesh1: {len(np.unique(self.mesh1VertRay))}")
        # print(f"rayData shape in mesh1: {self.mesh1VertRay.shape}")

        # 1. Filter out vertices in mesh2 with the same color as mesh1
        self.mesh1Vertices = mesh1Vertices
        self.mesh1VertNorm = mesh1VertNorm
        self.mesh2Vertices, self.mesh2VertNorm = self.findSameColorPoints(mesh2Vertices, mesh2VertNorm)
        print(f"Number of vertices in mesh2 with the same color as mesh1: {self.mesh2Vertices.shape}")
        if len(mesh2Vertices) == 0:
            raise ValueError("No matching color found in target mesh.")
                                
        # 2. Find closest points between mesh1 and mesh2, and visualize mathcing pairs
        self.updateMatch()  

    # need to reinitialize the registrator with new mesh1
    def updateMesh1(self, mesh1=None):
        print("Updating ICP registrator with new mesh1...")
        if mesh1 is not None:
            self.mesh1 = mesh1
        self.updateMatch(updateMesh1Vertices=True)


    def updateMatch(self, updateMesh1Vertices=False):
        # print("Updating ICP registrator...")
        if updateMesh1Vertices:
            self.mesh1Vertices, self.mesh1VertNorm = self.getMeshVertData(self.mesh1)
            self.mesh1VertRay = self.mesh1.geometry.attributes["uniqueVertexRay"].data # Record which ray each vertex in mesh1 lies on
        closestPoints, closestPairsRay, closestPairsNormDist = self.findClosestPoints()
        self.findClosestPointsPerRay(closestPoints, closestPairsRay, closestPairsNormDist)
        self.createMatchMesh()            





    def getMeshVertData(self, mesh, removeDuplicate=True):
        meshTransform = mesh.getWorldMatrix()
        if meshTransform.shape != (4, 4):
            raise ValueError(f"Invalid world matrix shape{meshTransform.shape}. Expected (4, 4).")
        meshRotation = meshTransform[:3, :3]
        vertexPos = np.array(mesh.geometry.attributes["uniqueVertexPosition"].data) # FIXME: vertexPosition have duplicated vertices with triangulated arrangements
        vertexNorm = np.array(mesh.geometry.attributes["uniqueVertexNormal"].data)
        # print(f"vertexPos: {vertexPos.shape}")
        # Apply world matrix to vertex positions
        worldVertexPos4D = np.hstack((vertexPos, np.ones((len(vertexPos), 1)))) @ meshTransform.T
        # print(f"worldVertexPos4D: {worldVertexPos4D.shape}")
        # Convert homogeneous coordinates to 3D coordinates
        worldVertexPos = worldVertexPos4D[:, :3] / worldVertexPos4D[:, 3][:, np.newaxis]
        
        # Normalize normals
        worldVertexNorm = vertexNorm @ meshRotation.T
        epsilon = 1e-6
        norms = np.linalg.norm(worldVertexNorm, axis=1, keepdims=True)
        norms[norms < epsilon] = 1.0
        worldVertexNorm /= norms
        # print(f"worldVertexPos: {worldVertexPos.shape}")
        return worldVertexPos, worldVertexNorm
    
    
    def findSameColorPoints(self, mesh2Vertices, mesh2VertNorm, rtol=0.1):
        mesh1Colors = self.mesh1.geometry.attributes["uniqueVertexColor"].data
        mesh2Colors = self.mesh2.geometry.attributes["uniqueVertexColor"].data
        sameColorPoints = []
        sameColorPointsNorm = []

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
                sameColorPointsNorm.append(mesh2VertNorm[i])
        
        return np.array(sameColorPoints), np.array(sameColorPointsNorm)

    def findClosestPoints(self):
        """ for each vertex in source mesh1, find the closest vertex in target mesh2 """
        if self.mesh1Vertices.shape[1] != 3 or self.mesh2Vertices.shape[1] != 3:
            raise ValueError("Input vertices must be 3D coordinates.")
        
        # mesh1Vertices = self.removeDuiplicateVertices(self.mesh1Vertices)
        # mesh2Vertices = self.removeDuiplicateVertices(self.mesh2Vertices)

        # Construct a KDTree for mesh2 vertices
        kdTree= KDTree(self.mesh2Vertices)
        closestPoints = []
        closestPointsNorm = []
        closestPointsRay = []

        # # if no vertices in mesh2 can be used twice
        # availableMesh2Vertices = self.mesh2Vertices.copy()
        # usedIdx = set()


        for i, v1 in enumerate(self.mesh1Vertices):

            dist, idx = kdTree.query(v1, distance_upper_bound=self.d_max)
            if dist < self.d_max:
                closestPoints.append((v1, self.mesh2Vertices[idx]))
                closestPointsNorm.append((self.mesh1VertNorm[i], self.mesh2VertNorm[idx]))
                closestPointsRay.append(self.mesh1VertRay[i]) # FIXME: error!!!!!!!!! IndexError: index 8609 is out of bounds for axis 0 with size 8496
                
                
        
        print(f"Number of closest pairs found: {len(closestPoints)}")
        if len(closestPoints) == 0:
            # raise ValueError("No matching points found within max distance.")
            print("No matching points found within max distance.")
            return [], [], []

        closestPairsNormDist = [np.dot(norm1, norm2) for norm1, norm2 in closestPointsNorm] # FIXME: assume normal data is normalized to unit length
        closestPairsRay = closestPointsRay

        return closestPoints, closestPairsRay, closestPairsNormDist


    # # TODO: duplicate vertices removal to make program faster
    # def filterUniqueVertices(self, vertices, rtol=1e-5):
    #     """ Remove duplicate vertices in the list of vertices:
    #         return filtered vertices and indices of unique vertices """
    #     uniqueVertices, uniqueIdx = np.unique(vertices, axis=0, return_index=True)

    #     if len(vertices) != len(uniqueVertices):
    #         logging.warning(f"Removed {len(vertices) - len(uniqueVertices)} duplicate vertices.")
    #     return uniqueVertices, uniqueIdx


    
    def findClosestPointsPerRay(self, closestPairs, closestPairsRay, closestPairsNormDist):
        """ sort the closest points by ray
            within each ray, identify the match pair with max normal similarlity """
        
        if closestPairs is None or len(closestPairs) == 0:
            # raise ValueError("No matching points found within max distance.")
            # print("No matching points found within max distance.")
            return
            

        if len(closestPairs) != len(closestPairsRay) or len(closestPairs) != len(closestPairsNormDist):
            raise ValueError("Input closestpPoints arrays must have the same length.")
        
        # closestPairs = self.closestPairs
        # closestPairsRay = self.closestPairsRay
        # closestPairsNormDist = self.closestPairsNormDist

        # arrange the closest pairs into dictionary by ray
        closestPairsByRay = {}
        closestPairsNormDistByRay = {}
        for i, ray in enumerate(closestPairsRay):
            ray = int(ray)
            if ray not in closestPairsByRay:
                closestPairsByRay[ray] = []
                closestPairsNormDistByRay[ray] = []
            closestPairsByRay[ray].append(closestPairs[i])
            closestPairsNormDistByRay[ray].append(closestPairsNormDist[i])
            
        
        # print(f"Number of rays: {len(closestPairsByRay)}")
        # print(f"Number of closest pairs per ray: {[len(pairs) for pairs in closestPairsByRay.values()]}")

        # for each ray, find the pair with max normal similarity
        closestPairsPerRay = []
        closestPairsNormDistPerRay = []
        for ray, pairs in closestPairsByRay.items():
            maxIdx = np.argmax(closestPairsNormDistByRay[ray])
            closestPairsPerRay.append(pairs[maxIdx])
            closestPairsNormDistPerRay.append(closestPairsNormDistByRay[ray][maxIdx]) # record the max normal similarity of each closest pair selected

        self.closestPairsPerRay = closestPairsPerRay 
        self.closestPairsNormDist = closestPairsNormDistPerRay

        self.calcMatchInfo() # calc and display match information for debugging!!!
        
    def calcMatchInfo(self):
        self.matchCount = len(self.closestPairsPerRay)
        # print(f"Number of closest pairs (1 per ray) within dmax: {len(self.closestPairsPerRay)}")
        
        # compute mean absolute distance between matching points
        sourcePoints, targetPoints = zip(*self.closestPairsPerRay)
        sourcePoints = np.array(sourcePoints)
        targetPoints = np.array(targetPoints)
        self.meanError = np.mean(np.linalg.norm(sourcePoints - targetPoints, axis=1))
        # print(f"Mean distance between matching points: {meanError}")

        # compute mean normal similarity between matching points
        self.meanNormMeasure = np.mean(self.closestPairsNormDist)
        # print(f"Mean normal similarity between matching points: {meanNormMeasure}")


    def createMatchMesh(self):
        if self.closestPairsPerRay is None or len(self.closestPairsPerRay) == 0:
            # raise ValueError("No matching points found within max distance.")
            # print("No matching points found within max distance.")
            return
        matchGeo = MatchGeometry(self.closestPairsPerRay)
        matchMat = LineMaterial({"lineType": "segments", "lineWidth": 1})
        matchMesh = Mesh(matchGeo, matchMat)
        if self.matchMesh in self.sceneObject.children:
            self.sceneObject.remove(self.matchMesh)
            del self.matchMesh
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

            source_points, target_points = zip(*self.closestPairsPerRay)
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
            if self.mesh1Parent is not None:
                self.transformMesh(self.mesh1Parent, transformMatrix) # FIXME: updated
            else:
                self.transformMesh(self.mesh1, transformMatrix)
            self.mesh1Vertices, self.mesh1VertNorm = self.getMeshVertData(self.mesh1)
            
            print(f"Iteration {i + 1}: Optimized parameters {params}")



            """ prepare for next iteration """
            # 2. Find closest points between mesh1 and mesh2
            self.updateMatch()
            
            if len(self.closestPairsPerRay) == 0:
                print("No matches found within max distance.")
                break
            """ end of iteration """


            # 5. Check for convergence
            if np.linalg.norm(params - paramsPrev) < tolerance:
                break

        return params  # Final transformation parameters




    

        