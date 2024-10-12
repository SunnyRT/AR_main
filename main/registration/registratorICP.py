import numpy as np
from scipy.optimize import least_squares

from geometry.boxGeometry import BoxGeometry
from material.surfaceMaterial import SurfaceMaterial
from core_ext.mesh import Mesh


class RegistratorICP(object):
    def __init__(self, mesh1, mesh2, d_max, max_iterations=10):
        self.mesh1 = mesh1
        self.mesh2 = mesh2
        self.d_max = d_max
        self.max_iterations = max_iterations

    def find_closest_points(self, mesh1_vertices, mesh2_vertices, d_max):
        closest_points = []
        for v1 in mesh1_vertices:
            # Compute the Euclidean distances from vertex v1 to all vertices in mesh2
            distances = np.linalg.norm(mesh2_vertices - v1, axis=1)

            # Find the closest vertex within max distance d_max
            min_dist = np.min(distances)
            if min_dist < d_max:
                closest_points.append((v1, mesh2_vertices[np.argmin(distances)]))

        return closest_points

    def transform_points(self, points, theta_x, theta_y, theta_z, t_x, t_y, t_z):
        # Rotation matrices around each axis
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(theta_x), -np.sin(theta_x)],
                       [0, np.sin(theta_x), np.cos(theta_x)]])
        Ry = np.array([[np.cos(theta_y), 0, np.sin(theta_y)],
                       [0, 1, 0],
                       [-np.sin(theta_y), 0, np.cos(theta_y)]])
        Rz = np.array([[np.cos(theta_z), -np.sin(theta_z), 0],
                       [np.sin(theta_z), np.cos(theta_z), 0],
                       [0, 0, 1]])

        # Combined rotation matrix
        R = Rx @ Ry @ Rz

        # Apply rotation and translation
        return np.dot(points, R.T) + np.array([t_x, t_y, t_z])

    def objective_function(self, params, source_points, target_points):
        theta_x, theta_y, theta_z, t_x, t_y, t_z = params
        transformed_points = self.transform_points(source_points, theta_x, theta_y, theta_z, t_x, t_y, t_z)

        # Calculate residuals (differences between transformed source and target)
        residuals = transformed_points - target_points
        return residuals.flatten()

# ICP Algorithm
def icp(self, d_max, max_iterations=10):
    mesh1_vertices = np.array(self.mesh1.geometry.attributes["vertexPosition"].data)
    mesh2_vertices = np.array(self.mesh2.geometry.attributes["vertexPosition"].data)

    # Initial transformation parameters (identity transformation)
    params = np.zeros(6)  # [theta_x, theta_y, theta_z, t_x, t_y, t_z]

    for i in range(max_iterations):
        # 1. Find closest points between mesh1 and mesh2
        closest_pairs = self.find_closest_points(mesh1_vertices, mesh2_vertices, d_max)
        if len(closest_pairs) == 0:
            print("No matches found within max distance.")
            break

        source_points, target_points = zip(*closest_pairs)
        source_points = np.array(source_points)
        target_points = np.array(target_points)

        # 2. Optimize transformation using Levenberg–Marquardt
        result = least_squares(self.objective_function, params, args=(source_points, target_points))

        # Update the transformation parameters
        params = result.x

        # 3. Apply the new transformation to mesh1 vertices
        mesh1_vertices = self.transform_points(mesh1_vertices, *params)

        # 4. Update the vertex positions in mesh1
        self.mesh1.geometry.attributes["vertexPosition"].data = mesh1_vertices.tolist()
        print(f"Iteration {i + 1}: Optimized parameters {params}")

    return params  # Final transformation parameters
