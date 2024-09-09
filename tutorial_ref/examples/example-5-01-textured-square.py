#!/usr/bin/python3
import pathlib
import sys

# Get the package directory
package_dir = str(pathlib.Path(__file__).resolve().parents[2])
# Add the package directory into sys.path if necessary
if package_dir not in sys.path:
    sys.path.insert(0, package_dir)

from tutorial_ref.core.base import Base
from tutorial_ref.core_ext.camera import Camera
from tutorial_ref.core_ext.mesh import Mesh
from tutorial_ref.core_ext.renderer import Renderer
from tutorial_ref.core_ext.scene import Scene
from tutorial_ref.core_ext.texture import Texture
from tutorial_ref.geometry.rectangle import RectangleGeometry
from tutorial_ref.material.texture import TextureMaterial


class Example(Base):
    """ Render a textured square """
    def initialize(self):
        print("Initializing program...")
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 2])
        geometry = RectangleGeometry()
        grid_texture = Texture(file_name="../images/grid.jpg")
        material = TextureMaterial(texture=grid_texture)
        self.mesh = Mesh(
            geometry=geometry,
            material=material
        )
        self.scene.add(self.mesh)

    def update(self):
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
