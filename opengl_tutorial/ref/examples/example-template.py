#!/usr/bin/python3
import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[2])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from ref.core.base import Base
from ref.core_ext.camera import Camera
from ref.core_ext.mesh import Mesh
from ref.core_ext.renderer import Renderer
from ref.core_ext.scene import Scene
from ref.core_ext.texture import Texture
from ref.geometry.box import BoxGeometry
# from py3d.geometry.geometry import Geometry
from ref.material.surface import SurfaceMaterial
from ref.material.texture import TextureMaterial
from ref.geometry.sphere import SphereGeometry
from ref.light.ambient import AmbientLight
from ref.light.directional import DirectionalLight
from ref.light.point import PointLight
from ref.material.flat import FlatMaterial
from ref.material.lambert import LambertMaterial
from ref.material.phong import PhongMaterial


class Example(Base):
    """ Example template """
    def initialize(self):
        print("Initializing program...")
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 4])
        geometry = BoxGeometry()
        # material = SurfaceMaterial(property_dict={"useVertexColors": True})
        material = SurfaceMaterial(
            property_dict={
                "useVertexColors": True,
                "wireframe": True,
                "lineWidth": 8
            }
        )
        self.mesh = Mesh(geometry, material)
        self.scene.add(self.mesh)

    def update(self):
        self.mesh.rotate_y(0.0514)
        self.mesh.rotate_x(0.0337)
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
