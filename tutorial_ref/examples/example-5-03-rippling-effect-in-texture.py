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
from tutorial_ref.material.material import Material


class Example(Base):
    """
    Create a rippling effect in a texture, by adding a sine-based displacement
    to the V component of the UV coordinates in the fragment shader.
    """
    def initialize(self):
        print("Initializing program...")
        self.renderer = Renderer()
        self.scene = Scene()
        self.camera = Camera(aspect_ratio=800/600)
        self.camera.set_position([0, 0, 1.5])
        vertex_shader_code = """
            uniform mat4 projectionMatrix;
            uniform mat4 viewMatrix;
            uniform mat4 modelMatrix;
            in vec3 vertexPosition;
            in vec2 vertexUV;
            out vec2 UV;
            
            void main()
            {
                gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPosition, 1.0);
                UV = vertexUV;
            }
        """
        fragment_shader_code = """
            uniform sampler2D textureSampler;
            in vec2 UV;
            uniform float time;
            out vec4 fragColor;
            
            void main()
            {
                vec2 shiftUV = UV + vec2(0, 0.2 * sin(6.0 * UV.x + time));
                fragColor = texture(textureSampler, shiftUV);
            }
        """
        grid_texure = Texture("../images/grid.jpg")
        self.wave_material = Material(vertex_shader_code, fragment_shader_code)
        self.wave_material.add_uniform("sampler2D", "textureSampler", [grid_texure.texture_ref, 1])
        self.wave_material.add_uniform("float", "time", 0.0)
        self.wave_material.locate_uniforms()

        geometry = RectangleGeometry()
        self.mesh = Mesh(geometry, self.wave_material)
        self.scene.add(self.mesh)

    def update(self):
        self.wave_material.uniform_dict["time"].data += self.delta_time
        self.renderer.render(self.scene, self.camera)


# Instantiate this class and run the program
Example(screen_size=[800, 600]).run()
