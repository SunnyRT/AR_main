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
from tutorial_ref.core_ext.renderer import Renderer
from tutorial_ref.core_ext.scene import Scene
from tutorial_ref.core_ext.camera import Camera
from tutorial_ref.core_ext.mesh import Mesh
from tutorial_ref.core_ext.texture import Texture
from tutorial_ref.light.ambient import AmbientLight
from tutorial_ref.light.directional import DirectionalLight
from tutorial_ref.material.phong import PhongMaterial
from tutorial_ref.material.texture import TextureMaterial
from tutorial_ref.geometry.rectangle import RectangleGeometry
from tutorial_ref.geometry.sphere import SphereGeometry
from tutorial_ref.extras.movement_rig import MovementRig
from tutorial_ref.extras.directional_light import DirectionalLightHelper


class Example(Base):
    """
    Render shadows using shadow pass by depth buffers for the directional light.
    """
    def initialize(self):
        self.renderer = Renderer([0.2, 0.2, 0.2])
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.rig = MovementRig()
        self.rig.add(self.camera)
        self.rig.set_position([0, 2, 5])

        ambient_light = AmbientLight(color=[0.2, 0.2, 0.2])
        self.scene.add(ambient_light)
        self.directional_light = DirectionalLight(color=[0.5, 0.5, 0.5], direction=[-1, -1, 0])
        # The directional light can take any position because it covers all the space.
        # The directional light helper is a child of the directional light.
        # So changing the global matrix of the parent leads to changing
        # the global matrix of its child.
        self.directional_light.set_position([2, 4, 0])
        self.scene.add(self.directional_light)
        direct_helper = DirectionalLightHelper(self.directional_light)
        self.directional_light.add(direct_helper)

        sphere_geometry = SphereGeometry()
        phong_material = PhongMaterial(
            texture=Texture("../images/grid.jpg"),
            number_of_light_sources=2,
            use_shadow=True
        )

        sphere1 = Mesh(sphere_geometry, phong_material)
        sphere1.set_position([-2, 1, 0])
        self.scene.add(sphere1)

        sphere2 = Mesh(sphere_geometry, phong_material)
        sphere2.set_position([1, 2.2, -0.5])
        self.scene.add(sphere2)

        self.renderer.enable_shadows(self.directional_light)

        """
        # optional: render depth texture to mesh in scene
        depth_texture = self.renderer.shadow_object.render_target.texture
        shadow_display = Mesh(RectangleGeometry(), TextureMaterial(depth_texture))
        shadow_display.set_position([-1, 3, 0])
        self.scene.add(shadow_display)
        """

        floor = Mesh(RectangleGeometry(width=20, height=20), phong_material)
        floor.rotate_x(-math.pi / 2)
        self.scene.add(floor)

    def update(self):
        #"""
        # view dynamic shadows -- need to increase shadow camera range
        self.directional_light.rotate_y(0.01337, False)
        #"""
        self.rig.update( self.input, self.delta_time)
        self.renderer.render(self.scene, self.camera)
        """
        # render scene from shadow camera
        shadow_camera = self.renderer.shadow_object.camera
        self.renderer.render(self.scene, shadow_camera)
        """


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
