#!/usr/bin/python3
import math
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
from tutorial_ref.material.sprite import SpriteMaterial
from tutorial_ref.material.texture import TextureMaterial
from tutorial_ref.extras.movement_rig import MovementRig
from tutorial_ref.extras.grid import GridHelper


class Example(Base):
    """
    Demonstrate billboarding by the 4-by-3 spritesheet of Sonic.
    A billboard always faces a camera.
    Move the camera: WASDRF(move), QE(turn), TG(look).
    """
    def initialize(self):
        print("Initializing program...")
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.set_position([0, 0.5, 3])
        self.scene.add(self.rig)
        geometry = RectangleGeometry()
        tile_set = Texture("../images/sonic-spritesheet.jpg")
        sprite_material = SpriteMaterial(
            tile_set,
            {
                "billboard": True,
                "tileCount": [4, 3],
                "tileNumber": 0
            }
        )
        self.tiles_per_second = 8
        self.sprite = Mesh(geometry, sprite_material)
        self.scene.add(self.sprite)
        grid = GridHelper(
            size=20,
            grid_color=[1, 1, 1],
            center_color=[1, 1, 0]
        )
        grid.rotate_x(-math.pi / 2)
        self.scene.add(grid)

    def update(self):
        tile_number = math.floor(self.time * self.tiles_per_second)
        self.sprite.material.uniform_dict["tileNumber"].data = tile_number
        self.rig.update(self.input, self.delta_time)
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
