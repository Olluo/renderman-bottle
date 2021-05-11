import argparse
import prman
import os
import sys
import subprocess


def compile_shader(shader: str):
    """Checks and compiles a shader file (osl) into an object file (oso) to be used by Renderman.

    Args:
        shader (str): The name of the shader
    """
    if not os.path.isfile(shader+'.oso') or os.stat(shader+'.osl').st_mtime - os.stat(shader+'.oso').st_mtime > 0:
        try:
            subprocess.check_call(['oslc', shader + '.osl'])
        except subprocess.CalledProcessError as err:
            sys.exit('Shader compilation failed: {0}'.format(err))


def color(red: int, green: int, blue: int):
    """Create a Renderman color list from values < 255.

    Args:
        red (int): The red value
        green (int): The green value
        blue (int): The blue value

    Returns:
        List of floats of the color values divided by 255.0
    """
    return [red / 255.0, green / 255.0, blue / 255.0]


class BottleMaker:
    def __init__(self, ri: prman.Ri) -> None:
        """Create a bottle maker that is responsible for drawing a bottle.

        Args:
            ri (prman.Ri): A reference to the Renderman interface.
        """
        self.ri = ri

    def draw(self, height: float = 2.5, radius: float = 0.4,
             x: float = 0, y: float = -1.5, z: float = 0,
             rx: float = 0, ry: float = 0, rz: float = 0,
             sx: float = 1, sy: float = 1, sz: float = 1,
             body_color=color(10, 0, 16)):
        """Draw the bottle.
        Order of transformations is translate, scale, then rotate.
        The cap is always 0.4 high with radius of radius - 0.01.

        Args:
            height (float, optional): Height of the main body. Defaults to 2.5.
            radius (float, optional): Radius of the main body. Defaults to 0.4.
            x (float, optional): X position. Defaults to 0.
            y (float, optional): Y position. Defaults to -1.5.
            z (float, optional): Z position. Defaults to 0.
            rx (float, optional): X rotation. Defaults to 0.
            ry (float, optional): Y rotation. Defaults to 0.
            rz (float, optional): Z rotation. Defaults to 0.
            sx (float, optional): X scale. Defaults to 1.
            sy (float, optional): Y scale. Defaults to 1.
            sz (float, optional): Z scale. Defaults to 1.
        """
        self.body_height = height * 0.8
        self.body_color = body_color

        self.ri.ArchiveRecord(self.ri.COMMENT, 'Drawing bottle')
        self.ri.TransformBegin()
        self.ri.Translate(x, y, z)

        self.ri.Scale(sx, sy, sz)

        self.ri.Rotate(rx, 1, 0, 0)
        self.ri.Rotate(ry, 0, 1, 0)
        self.ri.Rotate(rz, 0, 0, 1)

        self.ri.AttributeBegin()
        self.ri.Attribute('identifier', {'name': 'bottle'})

        self._shader()

        self.ri.TransformBegin()

        self.ri.Rotate(-90, 1, 0, 0)

        self.ri.Disk(0, radius, 360)
        self.ri.Cylinder(radius, 0, self.body_height, 360)

        self.ri.TransformEnd()

        self.ri.AttributeEnd()

        self.ri.ArchiveRecord(self.ri.COMMENT, 'End of bottle drawing')
        self.ri.TransformEnd()

    def _shader(self):
        """The shader that is applied to take the bottle from a basic cylinder, to a textured,
        colored, worn plastic bottle.
        """
        self.ri.CoordinateSystem("bodyCoordinates")

        # Apply displacement to round shape and create cap attachment
        compile_shader('bodyShape')
        self.ri.Pattern('bodyShape', 'bodyTx')
        self.ri.Attribute('displacementbound',
                          {
                              'sphere': [0.2],
                              'coordinatesystem': ['object']
                          })
        self.ri.Displace('PxrDisplace', 'bodyDisplace',
                         {
                             'float dispAmount': [0.09],
                             'reference float dispScalar': ['bodyTx:result']
                         })

        # Create base layer
        self.ri.Pattern('PxrLayer', 'bodyColor',
                        {
                            'int enableDiffuse': [1],
                            'int enableDiffuseAlways': [1],
                            'color diffuseColor': self.body_color,
                            'float diffuseGain': [1.0],
                        })

        # Create layer for discoloration
        compile_shader('discolor')
        self.ri.Pattern('discolor', 'discolorLayer',
                        {
                            'color Cin': self.body_color,
                            'float pscale': [2.5],
                            'float discolorValue': [0.8],
                        })

        # Create layer for texture
        self.ri.Pattern('PxrTexture', 'bodyLabelTexture',
                        {
                            'string filename': ['../img/bottle_4k.tx'],
                            'int linearize': [1],
                        })

        # Create layer for small dirt
        compile_shader('dirt')
        self.ri.Pattern('dirt', 'dirtLayer',
                        {
                            'color Cin': self.body_color,
                            'float pscale': [20.0],
                            'float xscale': [0.1],
                            'float yscale': [1],
                            'float zscale': [1],
                            'float dirtValue': [0.75],
                            'float dirtCutoff': [0.5],
                        })

        # Create layer for scuffs
        self.ri.Pattern('dirt', 'prescuffLayer',
                        {
                            'color Cin': self.body_color,
                            'float pscale': [7.0],
                            'float xscale': [1],
                            'float yscale': [1],
                            'float zscale': [1],
                            'float dirtValue': [1.2],
                            'float dirtCutoff': [0.6],
                        })
        self.ri.Pattern('dirt', 'scuffLayer',
                        {
                            'reference color Cin': ['prescuffLayer:resultRGB'],
                            'float pscale': [100.0],
                            'float xscale': [1],
                            'float yscale': [0.1],
                            'float zscale': [1],
                            'float dirtValue': [0.0],
                            'float dirtCutoff': [0.0],
                        })

        # Mix all the layers
        self.ri.Pattern('PxrLayerMixer', 'bodyMix',
                        {
                            'int enableDiffuseAlways': [1],
                            'int baselayer_enableDiffuse': [1],
                            'reference color baselayer_diffuseColor': ['bodyColor:pxrMaterialOut_diffuseColor'],
                            'reference float baselayer_diffuseGain': ["bodyColor:pxrMaterialOut_diffuseGain"],

                            'int layer1Enabled': [1],
                            'int layer1_enableDiffuse': [1],
                            'reference color layer1_diffuseColor': ['discolorLayer:resultRGB'],
                            'reference float layer1Mask': ['discolorLayer:resultA'],
                            'float layer1_diffuseGain':  [0.5],

                            'int layer2Enabled': [1],
                            'int layer2_enableDiffuse': [1],
                            'reference color layer2_diffuseColor': ['bodyLabelTexture:resultRGB'],
                            'reference float layer2Mask': ['bodyLabelTexture:resultA'],
                            'float layer2_diffuseGain':  [0.5],

                            'int layer3Enabled': [1],
                            'int layer3_enableDiffuse': [1],
                            'reference color layer3_diffuseColor': ['dirtLayer:resultRGB'],
                            'reference float layer3Mask': ['dirtLayer:resultA'],
                            'float layer3_diffuseGain':  [0.75],

                            'int layer4Enabled': [1],
                            'int layer4_enableDiffuse': [1],
                            'reference color layer4_diffuseColor': ['scuffLayer:resultRGB'],
                            'reference float layer4Mask': ['prescuffLayer:resultA'],
                            'float layer4_diffuseGain':  [0.2],
                            'float layer4_diffuseRoughness':  [0.5],
                        })

        # Apply BXDF
        self.ri.Bxdf('PxrLayerSurface', 'plastic',
                     {
                         'reference float diffuseGain': ['bodyMix:pxrMaterialOut_diffuseGain'],
                         'reference color diffuseColor': ['bodyMix:pxrMaterialOut_diffuseColor'],
                         'float diffuseRoughness': [0.5],
                         'float diffuseExponent': [1.0],
                         'int specularFresnelMode': [1],
                         'color specularEdgeColor': color(1, 1, 1),
                         'float specularRoughness': [0.6],
                         'float refractionGain': [0.7],
                         'color refractionColor': color(100, 100, 100),
                         'float reflectionGain': [0.01],
                         'float glassRoughness': [0.28],
                     })


class TableMaker:
    def __init__(self, ri: prman.Ri) -> None:
        """Create a table maker that is responsible for drawing a table.

        Args:
            ri (prman.Ri): A reference to the Renderman interface.
        """
        self.ri = ri

    def draw(self,
             width: float = 4, height: float = 0.3, depth: float = 3,
             x: float = 0, y: float = -1.65, z: float = 0,
             rx: float = 0, ry: float = 70, rz: float = 0,
             sx: float = 1, sy: float = 1, sz: float = 1):
        """Draw the table.
        Order of transformations is translate, scale, then rotate.

        Args:
            width (float, optional): Width. Defaults to 3.75.
            height (float, optional): Height. Defaults to 0.3.
            depth (float, optional): Depth. Defaults to 3.
            x (float, optional): X position. Defaults to 0.
            y (float, optional): Y position. Defaults to -1.65.
            z (float, optional): Z position. Defaults to 0.
            rx (float, optional): X rotation. Defaults to 0.
            ry (float, optional): Y rotation. Defaults to 70.
            rz (float, optional): Z rotation. Defaults to 0.
            sx (float, optional): X scale. Defaults to 1.
            sy (float, optional): Y scale. Defaults to 1.
            sz (float, optional): Z scale. Defaults to 1.
        """
        self.ri.ArchiveRecord(self.ri.COMMENT, 'Drawing table')
        self.ri.AttributeBegin()
        self.ri.Attribute('identifier', {'name': 'table'})

        self._shader()

        self.ri.TransformBegin()
        self.ri.Translate(x, y, z)

        self.ri.Scale(sx, sy, sz)

        self.ri.Rotate(rx, 1, 0, 0)
        self.ri.Rotate(ry, 0, 1, 0)
        self.ri.Rotate(rz, 0, 0, 1)

        self._cube(width, height, depth)

        self.ri.ArchiveRecord(self.ri.COMMENT, 'End of table drawing')
        self.ri.TransformEnd()
        self.ri.AttributeEnd()

    def _shader(self):
        """The shader that is applied to the table to make it look like wood with a shiny coat
        """
        self.ri.CoordinateSystem("tableCoordinates")

        # Apply pattern for texture
        compile_shader('wood')
        ri.Pattern('wood', 'woodPattern',
                   {
                       'color Cin': [1, 1, 1],
                       'float scale': [4],
                       'float freq': [2],
                       'float variation': [0.02],
                   })

        # Apply BXDF
        self.ri.Bxdf('PxrSurface', 'woodBxdf',
                     {
                         'reference color diffuseColor': ['woodPattern:Cout'],
                         'float diffuseRoughness': [0.75],
                         'float reflectionGain': [0.2],
                         'color clearcoatFaceColor': color(80, 25, 0),
                         'color clearcoatEdgeColor': color(0, 0, 0),
                         'color clearcoatExtinctionCoeff': [0.0, 0.0, 0.0],
                         'float clearcoatThickness': [1.0],
                         'float clearcoatRoughness': [0.4],
                     })

    def _cube(self, width: float = 1.0, height: float = 1.0, depth: float = 1.0):
        """Generates a cube. Modified from Cube.py by Jon Macey
        (https://github.com/NCCA/Renderman/blob/master/Lecture1Intro/Cube.py).

        Args:
            width (float, optional): Width. Defaults to 1.0.
            height (float, optional): Height. Defaults to 1.0.
            depth (float, optional): Depth. Defaults to 1.0.
        """
        w = width / 2.0
        h = height / 2.0
        d = depth / 2.0

        # rear
        face = [-w, -h, d, -w, h, d, w, -h, d, w, h, d]
        self.ri.Patch("bilinear", {'P': face})
        # front
        face = [-w, -h, -d, -w, h, -d, w, -h, -d, w, h, -d]
        self.ri.Patch("bilinear", {'P': face})
        # left
        face = [-w, -h, -d, -w, h, -d, -w, -h, d, -w, h, d]
        self.ri.Patch("bilinear", {'P': face})
        # right
        face = [w, -h, -d, w, h, -d, w, -h, d, w, h, d]
        self.ri.Patch("bilinear", {'P': face})
        # bottom
        face = [w, -h, d, w, -h, -d, -w, -h, d, -w, -h, -d]
        self.ri.Patch("bilinear", {'P': face})
        # top
        face = [w, h, d, w, h, -d, -w, h, d, -w, h, -d]
        self.ri.Patch("bilinear", {'P': face})


class HdrLight():
    def __init__(self, ri: prman.Ri) -> None:
        """Add an HDR Light to the scene

        Args:
            ri (prman.Ri): A reference to the Renderman interface.
        """
        ri.ArchiveRecord(ri.COMMENT, 'Adding HDR Light')
        ri.AttributeBegin()
        ri.TransformBegin()

        # Rotate the scene in Y so we have the part of the HDR we want
        ri.Rotate(50, 0, 1, 0)
        # Rotate -90 in X so the HDR is the right way up
        ri.Rotate(-90, 1, 0, 0)
        # Scale -ve in Y so the HDR isn't back-to-front
        ri.Scale(1, -1, 1)

        ri.Light("PxrDomeLight", "hdrLight",
                 {
                     "float exposure": [0],
                     "string lightColorMap": ["..\img\lookout_4k.tx"],
                 })

        ri.TransformEnd()
        ri.AttributeEnd()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Draw a scene with 2 MAIGG water bottles using Renderman.
        Example usage: "py -3.5 ./bottle.py -s 16 -rw 640 -rh 480"''')
    parser.add_argument('height', nargs='?', type=float, default=2.75,
                        help='The height of the bottles')
    parser.add_argument('radius', nargs='?', type=float, default=0.3,
                        help='The radius of the bottles')
    parser.add_argument('-r', '--rib', action='store_true',
                        help='Output the code to a rib file instead of rendering')
    parser.add_argument('-e', '--export', action='store_true',
                        help='Export the render as an .exr')
    parser.add_argument('-s', '--samples', type=int, default=512,
                        help='The number of samples to use when rendering')
    parser.add_argument('-rw', '--resolution_width', type=int, default=1920,
                        help='The width of the rendered image')
    parser.add_argument('-rh', '--resolution_height', type=int, default=1080,
                        help='The width of the rendered image')
    parser.add_argument('-a', '--alternate', action='store_true',
                        help='Render the alternate scene')
    args = parser.parse_args()

    ri = prman.Ri()

    # ---------- Configure Renderman ----------

    ri.Option("rib", {"string asciistyle": "indented"})

    if args.rib:
        ri.Begin('bottle{}.rib'.format('_alternate' if args.alternate else ''))
    else:
        ri.Begin('__render')

    # Export the render to .exr or display it based on args
    ri.Display('bottle{}.exr'.format('_alternate' if args.alternate else ''),
               "openexr" if args.export else "it", "rgba")

    # Specify PAL resolution 1:1 pixel Aspect ratio
    ri.Format(args.resolution_width, args.resolution_height, 1)
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: 45})

    # Set depth of field
    if args.alternate:
        ri.DepthOfField(1, 0.1, 3)
    else:
        ri.DepthOfField(1, 0.1, 4.5)

    # Set render type
    ri.Hider('raytrace',
             {'int incremental': [1],
              'int maxsamples': [args.samples]})
    ri.PixelVariance(0.001)
    ri.Integrator('PxrPathTracer', 'integrator')

    # Create our model helpers
    bottle_maker = BottleMaker(ri)
    table_maker = TableMaker(ri)

    # Finally translate world
    ri.ArchiveRecord(ri.COMMENT, 'Translate world in Z so we can see it')
    if args.alternate:
        ri.Translate(-1, 0.4, 3)
        ri.Rotate(-20, 0, 1, 0)
    else:
        ri.Translate(0, 0, 4.5)

    # ---------- Draw our world ----------

    ri.WorldBegin()
    ri.TransformBegin()

    # Let there be light... add the HDRLight to the scene
    HdrLight(ri)

    # Draw our models
    if args.alternate:
        # Purple bottle
        bottle_maker.draw(args.height, args.radius,
                          ry=-15, x=0, z=0.3)
    else:
        # Red bottle
        bottle_maker.draw(args.height, args.radius,
                          ry=-50, x=-0.8, body_color=color(40, 0, 0))
        # Purple bottle
        bottle_maker.draw(args.height, args.radius,
                          ry=-15, x=0, z=0.3)
        # Blue bottle
        bottle_maker.draw(args.height, args.radius,
                          ry=5, x=0.8, z=-0.1, body_color=color(0, 0, 40))

    table_maker.draw()

    ri.TransformEnd()
    ri.WorldEnd()

    ri.End()
