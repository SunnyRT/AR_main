import numpy as np
import logging
from scipy.optimize import least_squares
from scipy.spatial import KDTree

from geometry.boxGeometry import BoxGeometry
from geometry.matchGeometry import MatchGeometry
from material.surfaceMaterial import SurfaceMaterial
from material.lineMaterial import LineMaterial
from mesh.mesh import Mesh
from core.matrix import Matrix




class RegistratorICP(object):
    """ Iterative Closest Point (ICP) registration algorithm 
        To align mesh1 to target mesh2.
        By using Levenberg–Marquardt optimization. """
    

    def __init__(self, mesh1_ls, mesh2, microscopeRig, d_max=10.0, matchMeshFactory=None):
        
        
        self.mesh1_ls = mesh1_ls # a list of multiple projector meshes
        self.mesh2 = mesh2
        self.msRig = microscopeRig
        self.d_max = d_max
        self.closestPairsPerRay = None
        self.matchMeshFactory = matchMeshFactory

        # Debugging output
        self.matchCount = 0
        self.meanError = float('inf')
        self.meanNormMeasure = 0

        print("Initializing ICP registrator...")
        # 0. Extract vertexPosition with world matrix applied from both meshes

        
        mesh1Vertices_ls, mesh1VertNorm_ls, mesh1VertRay_ls = [], [], []
        mesh2Vertices_all, mesh2VertNorm_all, mesh2VertColor_all = self.getMeshVertData(self.mesh2)
        mesh2Vertices_ls, mesh2VertNorm_ls = [], []

        for i, mesh1 in enumerate(mesh1_ls):
            mesh1Vertices, mesh1VertNorm, mesh1VertColor = self.getMeshVertData(mesh1)
            mesh1Vertices_ls.append(mesh1Vertices)
            mesh1VertNorm_ls.append(mesh1VertNorm)
            mesh1VertRay_ls.append(mesh1.geometry.attributes["uniqueVertexRay"].data) # Record which ray each vertex in mesh1 lies on
            print(f"Number of rays in mesh1: {len(np.unique(mesh1VertRay_ls[i]))}")
            
            # 1. Filter out each set of corresponding vertices in mesh2 with the same color as each mesh1
            mesh2Vertices, mesh2VertNom = self.findSameColorPoints(mesh1VertColor, mesh2VertColor_all, mesh2Vertices_all, mesh2VertNorm_all)
            mesh2Vertices_ls.append(mesh2Vertices)
            mesh2VertNorm_ls.append(mesh2VertNom)
            print(f"Number of vertices in mesh2 with the same color as mesh1: {mesh2Vertices.shape}")
            if len(mesh2Vertices) == 0:
                raise ValueError(f"No matching color found in target projector{i} (mesh1).")

        self.mesh1Vertices_ls = mesh1Vertices_ls
        self.mesh1VertNorm_ls = mesh1VertNorm_ls
        self.mesh1VertRay_ls = mesh1VertRay_ls

        self.mesh2Vertices_ls = mesh2Vertices_ls
        self.mesh2VertNorm_ls = mesh2VertNorm_ls
        
         
              
        # 2. Find closest points between mesh1 and mesh2, and visualize mathcing pairs
        self.updateMatch()
        self.matchMeshFactory.update(self.closestPairsPerRay) # call matchMeshFactory to create new match pair mesh for visualization





    # need to reinitialize the registrator with new mesh1
    def updateMesh1(self, mesh1=None, idx=-1):
        print("Updating ICP registrator with new mesh1...")
        if mesh1 is not None and idx >= 0:
            self.mesh1_ls[idx] = mesh1
        self.updateMatch(updateMesh1idx=idx)


    def updateMatch(self, updateMesh1idx=-1):
        # print("Updating ICP registrator...")
        if updateMesh1idx >= 0:
            idx = updateMesh1idx
            mesh1 = self.mesh1_ls[idx]
            self.mesh1Vertices_ls[idx], self.mesh1VertNorm_ls[idx], _ = self.getMeshVertData(mesh1)
            self.mesh1VertRay_ls[idx] = mesh1.geometry.attributes["uniqueVertexRay"].data # Record which ray each vertex in mesh1 lies on
        
        # iterate through each mesh1 and mesh2 pair
        closestPairsPerRay_ls, closestPairsNormDistPerRay_ls = [], []
        for i in range(len(self.mesh1_ls)):
            if updateMesh1idx==-1:
                self.mesh1Vertices_ls[i], self.mesh1VertNorm_ls[i], _ = self.getMeshVertData(self.mesh1_ls[i])
            closestPoints, closestPairsRay, closestPairsNormDist = self.findClosestPoints(self.mesh1Vertices_ls[i], 
                                                                                          self.mesh1VertNorm_ls[i], 
                                                                                          self.mesh1VertRay_ls[i], 
                                                                                          self.mesh2Vertices_ls[i], 
                                                                                          self.mesh2VertNorm_ls[i])
            closestPairsPerRay, closestPairsNormDistPerRay = self.findClosestPointsPerRay(closestPoints, closestPairsRay, closestPairsNormDist)
            closestPairsPerRay_ls.append(closestPairsPerRay)
            closestPairsNormDistPerRay_ls.append(closestPairsNormDistPerRay)

        # flatten the list of closest pairs
        self.closestPairsPerRay = [pair for pairs in closestPairsPerRay_ls for pair in pairs]
        self.closestPairsNormDistPerRay = [dist for dists in closestPairsNormDistPerRay_ls for dist in dists]
        
        self.calcMatchInfo(self.closestPairsPerRay, self.closestPairsNormDistPerRay) # calc and display match information for debugging!!!
        
 





    def getMeshVertData(self, mesh):
        meshTransform = mesh.getWorldMatrix()
        if meshTransform.shape != (4, 4):
            raise ValueError(f"Invalid world matrix shape{meshTransform.shape}. Expected (4, 4).")
        meshRotation = meshTransform[:3, :3]
        vertexPos = np.array(mesh.geometry.attributes["uniqueVertexPosition"].data) # vertexPosition have no duplicated vertices
        vertexNorm = np.array(mesh.geometry.attributes["uniqueVertexNormal"].data)
        vertexColor = np.array(mesh.geometry.attributes["uniqueVertexColor"].data)
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
        
        return worldVertexPos, worldVertexNorm, vertexColor
    
    
    def findSameColorPoints(self, mesh1Colors, mesh2Colors, mesh2Vertices, mesh2VertNorm, rtol=0.1):
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


    def findClosestPoints(self, mesh1Vertices, mesh1VertNorm, mesh1VertRay, mesh2Vertices, mesh2VertNorm): 
        """ for each vertex in source mesh1, find the closest vertex in target mesh2 """
        if mesh1Vertices.shape[1] != 3 or mesh2Vertices.shape[1] != 3:
            raise ValueError("Input vertices must be 3D coordinates.")
        
        # Construct a KDTree for mesh2 vertices
        kdTree= KDTree(mesh2Vertices)
        closestPoints = []
        closestPointsNorm = []
        closestPointsRay = []


        for i, v1 in enumerate(mesh1Vertices):

            dist, idx = kdTree.query(v1, distance_upper_bound=self.d_max)
            if dist < self.d_max: # FIXME: self.d_max
                closestPoints.append((v1, mesh2Vertices[idx]))
                closestPointsNorm.append((mesh1VertNorm[i], mesh2VertNorm[idx]))
                closestPointsRay.append(mesh1VertRay[i]) 
                
                
        
        print(f"Number of closest pairs found: {len(closestPoints)}")
        if len(closestPoints) == 0:
            # raise ValueError("No matching points found within max distance.")
            print("No matching points found within max distance.")
            return [], [], []

        closestPairsNormDist = [np.dot(norm1, norm2) for norm1, norm2 in closestPointsNorm] # assume normal data is normalized to unit length
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
            return [], []
            

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

        
        return closestPairsPerRay, closestPairsNormDistPerRay
    
        
        
    def calcMatchInfo(self, closestPairsPerRay, closestPairsNormDist):
        self.matchCount = len(closestPairsPerRay)
        # print(f"Number of closest pairs (1 per ray) within dmax: {len(self.closestPairsPerRay)}")
        
        # compute mean absolute distance between matching points
        try:
            sourcePoints, targetPoints = zip(*closestPairsPerRay)
        except:
            print("No matching points found within max distance.")
            return
        sourcePoints = np.array(sourcePoints)
        targetPoints = np.array(targetPoints)
        self.meanError = np.mean(np.linalg.norm(sourcePoints - targetPoints, axis=1))
        # print(f"Mean distance between matching points: {meanError}")

        # compute mean normal similarity between matching points
        self.meanNormMeasure = np.mean(closestPairsNormDist)
        # print(f"Mean normal similarity between matching points: {meanNormMeasure}")


    # # replaced by matchMeshFactory
    # def createMatchMesh(self):
    #     if self.closestPairsPerRay is None or len(self.closestPairsPerRay) == 0:
    #         # raise ValueError("No matching points found within max distance.")
    #         # print("No matching points found within max distance.")
    #         return
    #     matchGeo = MatchGeometry(self.closestPairsPerRay)
    #     matchMat = LineMaterial({"lineType": "segments", "lineWidth": 1})
    #     matchMesh = Mesh(matchGeo, matchMat)
    #     if self.matchMesh in self.sceneObject.children:
    #         self.sceneObject.remove(self.matchMesh)
    #         del self.matchMesh
    #     self.matchMesh = matchMesh
    #     self.sceneObject.add(self.matchMesh)        

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
        mesh.applyMatrix(transformMatrix, localCoord=False) 

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


            # put this in as global variable to track all transformations
            # Initial transformation parameters (identity transformation)
            params = np.zeros(6)  # [theta_x, theta_y, theta_z, t_x, t_y, t_z]

            # 3. Optimize transformation using Levenberg–Marquardt
            result = least_squares(self.objectiveFunction, params, args=(source_points, target_points))
            paramsPrev = params
            params = result.x # Update the transformation parameters


            # 4. Apply the new transformation to mesh1 vertices and update the vertex positions in mesh1
            transformMatrix = self.makeTransformMatrix(*params)

            self.transformMesh(self.msRig, transformMatrix) # updated the microscope rig

            for j, mesh1 in enumerate(self.mesh1_ls):
                self.mesh1Vertices_ls[j], self.mesh1VertNorm_ls[j], _ = self.getMeshVertData(mesh1)
            
            print(f"Iteration {i + 1}: Optimized parameters {params}")



            """ prepare for next iteration """
            # 2. Find closest points between mesh1 and mesh2
            self.updateMatch()
            self.matchMeshFactory.update(self.closestPairsPerRay)
            
            if len(self.closestPairsPerRay) == 0:
                print("No matches found within max distance.")
                break
            """ end of iteration """


            # 5. Check for convergence
            if np.linalg.norm(params - paramsPrev) < tolerance:
                break

        return params  # Final transformation parameters




    

        