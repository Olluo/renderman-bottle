import argparse
import prman


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
             sx: float = 1, sy: float = 1, sz: float = 1):
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
        body_height = height * 0.8
        cap_height = 0.2
        cap_radius = radius - 0.01

        self.ri.ArchiveRecord(self.ri.COMMENT, 'Drawing bottle')
        self.ri.TransformBegin()
        self.ri.Translate(x, y, z)

        self.ri.Scale(sx, sy, sz)

        self.ri.Rotate(rx, 1, 0, 0)
        self.ri.Rotate(ry, 0, 1, 0)
        self.ri.Rotate(rz, 0, 0, 1)

        self._draw_cylinder_component('bottleBody', self._body_shader,
                                      radius, body_height)
        self._draw_cylinder_component('bottleCapBottom', self._cap_bottom_shader,
                                      cap_radius, cap_height,
                                      y=body_height)
        self._draw_cylinder_component('bottleCapTop', self._cap_top_shader,
                                      cap_radius, cap_height,
                                      y=body_height + cap_height)
        self._draw_cylinder_component('bottleCapLock', self._cap_lock_shader,
                                      0.25, cap_height,
                                      y=body_height + cap_height, z=-cap_radius * 1.1,
                                      sx=0.4, sy=0.6, rx=0)

        self.ri.ArchiveRecord(self.ri.COMMENT, 'End of bottle drawing')
        self.ri.TransformEnd()

    def _body_shader(self):
        self.ri.CoordinateSystem("bodyCoordinates")

        # Apply displacement to round shape and create cap attachment

        # Apply pattern for texture

        # Apply pattern for scratches

        # Apply pattern for scuffs

        # Apply BXDF
        self.ri.Bxdf('PxrSurface', 'plastic',
                     {'color diffuseColor': [25/255.0, 0/255.0, 51/255.0],
                      'float diffuseRoughness': [0.75], })

    def _cap_bottom_shader(self):
        self.ri.CoordinateSystem("capBottomCoordinates")

        # Apply displacement to round edges

        # Apply displacement to create lock outer

        # Apply pattern for rubber purple band on black

        # Apply pattern for scratches

        # Apply pattern for scuffs

        # Apply BXDF for rubber band
        self.ri.Bxdf('PxrSurface', 'rubber',
                     {'color diffuseColor': [0.0, 1.0, 1.0],
                      'float diffuseRoughness': [0.75], })

        # Apply BXDF for black plastic
        self.ri.Bxdf('PxrSurface', 'blackPlastic',
                     {'color diffuseColor': [0.0, 1.0, 1.0],
                      'float diffuseRoughness': [0.75], })

    def _cap_top_shader(self):
        self.ri.CoordinateSystem("capTopCoordinates")

        # Apply displacement to round top edge

        # Apply displacement to cut out back

        # Apply displacement to create lock outer

        # Apply pattern for top circle colour

        # Apply pattern for scratches

        # Apply pattern for scuffs

        # Apply BXDF
        self.ri.Bxdf('PxrSurface', 'clearPlastic',
                     {'color diffuseColor': [0.0, 1.0, 0.0],
                      'float diffuseRoughness': [0.2], })

    def _cap_lock_shader(self):
        self.ri.CoordinateSystem("capLockCoordinates")

        # Apply displacement to squeeze in sides

        # Apply displacement to add knurling

        # Apply pattern for shiny knurl

        # Apply pattern for scratches

        # Apply pattern for scuffs

        # Apply BXDF
        self.ri.Bxdf('PxrSurface', 'blackPlastic',
                     {'color diffuseColor': [1.0, 1.0, 0.0],
                      'float diffuseRoughness': [0.2], })

    def _draw_cylinder_component(self, name: str, shader,
                                 radius: float, height: float,
                                 x: float = 0, y: float = 0, z: float = 0,
                                 sx: float = 1, sy: float = 1, sz: float = 1,
                                 rx: float = -90, ry: float = 0, rz: float = 0):
        """Draws a cylinder

        Args:
            name (str): The name of the attribute being drawn.
            radius (float): Radius.
            height (float): Height.
            x (float, optional): X position. Defaults to 0.
            y (float, optional): Y position. Defaults to 0.
            z (float, optional): Z position. Defaults to 0.
            sx (float, optional): X rotation. Defaults to 1.
            sy (float, optional): Y rotation. Defaults to 1.
            sz (float, optional): Z rotation. Defaults to 1.
            rx (float, optional): X scale. Defaults to -90.
            ry (float, optional): Y scale. Defaults to 0.
            rz (float, optional): Z scale. Defaults to 0.
        """
        self.ri.ArchiveRecord(self.ri.COMMENT, 'Drawing ' + name)
        self.ri.AttributeBegin()
        self.ri.Attribute('identifier', {'name': name})

        shader()

        self.ri.TransformBegin()
        self.ri.Translate(x, y, z)

        self.ri.Scale(sx, sy, sz)

        self.ri.Rotate(rx, 1, 0, 0)
        self.ri.Rotate(ry, 0, 1, 0)
        self.ri.Rotate(rz, 0, 0, 1)

        self.ri.Disk(0, radius, 360)
        self.ri.Cylinder(radius, 0, height, 360)
        self.ri.Disk(height, radius, 360)

        self.ri.TransformEnd()

        self.ri.AttributeEnd()


class TableMaker:
    def __init__(self, ri: prman.Ri) -> None:
        """Create a table maker that is responsible for drawing a table.

        Args:
            ri (prman.Ri): A reference to the Renderman interface.
        """
        self.ri = ri

    def draw(self,
             width: float = 3.75, height: float = 0.3, depth: float = 3,
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
        self.ri.CoordinateSystem("tableCoordinates")

        # Apply displacement to round corners

        # Apply pattern for texture

        # Apply pattern for scratches

        # Apply pattern for scuffs

        # Apply BXDF
        self.ri.Bxdf('PxrSurface', 'wood',
                     {'color diffuseColor': [1, 0.6, 0.5],
                      'float diffuseRoughness': [0.75], })

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
                 {"float exposure": [0],
                  "string lightColorMap": ["..\img\lookout_4k.tex"]})

        ri.TransformEnd()
        ri.AttributeEnd()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='''Draw a scene with 2 MAIGG water bottles using Renderman.
        Example usage: "py -3.5 ./bottle.py -s 16 -rw 640 -rh 480"''')
    parser.add_argument('height', nargs='?', type=float, default=2.5,
                        help='The height of the larger bottle')
    parser.add_argument('radius', nargs='?', type=float, default=0.4,
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
    args = parser.parse_args()

    ri = prman.Ri()

    # ---------- Configure Renderman ----------

    ri.Option("rib", {"string asciistyle": "indented"})

    if args.rib:
        ri.Begin('Bottle.rib')
    else:
        ri.Begin('__render')

    # Export the render to .exr or display it based on args
    ri.Display("Bottle.exr", "openexr" if args.export else "it", "rgba")

    # Specify PAL resolution 1:1 pixel Aspect ratio
    ri.Format(args.resolution_width, args.resolution_height, 1)
    ri.Projection(ri.PERSPECTIVE, {ri.FOV: 90})

    # set depth of field
    # ri.DepthOfField(1,1,1)

    # Set render type
    ri.Hider('raytrace',
             {'int incremental': [1],
              'int maxsamples': [args.samples]})
    # find out what this does
    ri.PixelVariance(0.01)
    ri.Integrator('PxrPathTracer', 'integrator')

    # Create our model helpers
    bottle_maker = BottleMaker(ri)
    table_maker = TableMaker(ri)

    # Compile shaders

    # Finally translate world
    ri.ArchiveRecord(ri.COMMENT, 'Translate world in Z so we can see it')
    ri.Translate(0, 0, 3)

    # ---------- Draw our world ----------

    ri.WorldBegin()
    ri.TransformBegin()

    # Let there be light... add the HDRLight to the scene
    HdrLight(ri)

    # Draw our models
    bottle_maker.draw(args.height * 0.8, args.radius, ry=30, x=-0.5)
    bottle_maker.draw(args.height, args.radius, ry=-5, x=0.4)
    table_maker.draw()

    ri.TransformEnd()
    ri.WorldEnd()

    ri.End()
