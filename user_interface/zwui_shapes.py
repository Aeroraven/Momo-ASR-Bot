import ctypes
import math

import OpenGL.GL as gl
import OpenGL.GLUT as glut

from user_interface.zwui_helper import ZwUIHelper

PI = 3.1415926


class ZwUIAbstractShape:
    def __init__(self, **kwargs):
        # Primitive Attributes
        self.fill_type = gl.GL_POLYGON
        self.text_mode = False
        self.shape_list = []
        self.color_list = []
        # Text Attributes
        self.caption = ""
        self.location_x = 0
        self.location_y = 0
        self.scale = 5
        self.line_width = 2
        self.font_color = ZwUIHelper.get_opengl_rgba_vector(0, 0, 0)
        self.space_modifier = -10000
        self.letter_modifier = 1900

    def render(self,**kwargs):
        offset_z = 0
        if 'z_index' in kwargs:
            offset_z = kwargs['z_index']

        if not self.text_mode:
            gl.glBegin(self.fill_type)
            for i in range(len(self.shape_list)):
                gl.glColor4f(self.color_list[i][0], self.color_list[i][1], self.color_list[i][2], self.color_list[i][3])
                gl.glVertex3f(self.shape_list[i][0], self.shape_list[i][1], self.shape_list[i][2]+offset_z)
            gl.glEnd()
        else:
            gl.glPushMatrix()
            gl.glTranslatef(self.location_x, self.location_y, offset_z)
            gl.glScalef(self.scale, self.scale, 0)
            gl.glLineWidth(self.line_width)
            for i in range(len(self.caption)):
                gl.glColor4f(self.font_color[0], self.font_color[1], self.font_color[2], self.font_color[3])
                glut.glutStrokeCharacter(ctypes.c_void_p(0), ctypes.c_int(ord(self.caption[i])))
                if self.caption[i] == ' ':
                    gl.glTranslatef(self.space_modifier * self.scale, 0, 0)
                else:
                    gl.glTranslatef(self.letter_modifier * self.scale, 0, 0)
            gl.glLineWidth(1)
            gl.glPopMatrix()

    def reset(self):
        self.shape_list = []
        self.color_list = []

    def insert(self, shape, color):
        if not isinstance(shape, list) or not isinstance(color, list):
            raise Exception("Arguments must be lists")
        if len(shape) != 3 or len(color) != 4:
            raise Exception("Vector dimensions mismatch")
        self.shape_list.append(shape)
        self.color_list.append(color)

    def initialize(self, **kwargs):
        # Custom shapes should re-implement this method
        pass


class ZwUIText(ZwUIAbstractShape):
    def __init__(self, x, y, text, color, size=12, line_width=1):
        super(ZwUIText, self).__init__()
        self.location_y = y
        self.location_x = x
        self.font_color = color
        self.caption = text
        self.scale = size
        self.text_mode = True
        self.line_width = line_width


class ZwUIRectangle(ZwUIAbstractShape):
    def __init__(self, left, bottom, width, height, color):
        super(ZwUIRectangle, self).__init__()
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height
        self.color = color
        self.initialize()

    def initialize(self, **kwargs):
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left, self.bottom), self.color)
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left, self.bottom + self.height), self.color)
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left + self.width, self.bottom + self.height), self.color)
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left + self.width, self.bottom), self.color)


class ZwUITriangle(ZwUIAbstractShape):
    def __init__(self, pa, pb, pc, color):
        super(ZwUITriangle, self).__init__()
        self.pa = pa
        self.pb = pb
        self.pc = pc
        self.color = color
        self.initialize()

    def initialize(self, **kwargs):
        self.insert(self.pa, self.color)
        self.insert(self.pb, self.color)
        self.insert(self.pc, self.color)


class ZwUICircle(ZwUIAbstractShape):
    def __init__(self, center_x, center_y, radius, color, starting_deg=0.0, ending_deg=2 * PI):
        super(ZwUICircle, self).__init__()
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.starting_deg = starting_deg
        self.ending_deg = ending_deg
        self.initialize()

    def initialize(self, **kwargs):
        steps = 360
        for i in range(steps):
            tx = self.center_x + self.radius * math.cos(
                (self.ending_deg - self.starting_deg) * i / steps + self.starting_deg)
            ty = self.center_y + self.radius * math.sin(
                (self.ending_deg - self.starting_deg) * i / steps + self.starting_deg)
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(tx, ty), self.color)


class ZwUIArc(ZwUIAbstractShape):
    def __init__(self, center_x, center_y, radius, color, starting_deg=0.0, ending_deg=2 * PI):
        super(ZwUIArc, self).__init__()
        self.fill_type = gl.GL_LINE_STRIP
        self.center_x = center_x
        self.center_y = center_y
        self.radius = radius
        self.color = color
        self.starting_deg = starting_deg
        self.ending_deg = ending_deg
        self.initialize()

    def initialize(self, **kwargs):
        steps = 360
        for i in range(steps):
            tx = self.center_x + self.radius * math.cos(
                (self.ending_deg - self.starting_deg) * i / steps + self.starting_deg)
            ty = self.center_y + self.radius * math.sin(
                (self.ending_deg - self.starting_deg) * i / steps + self.starting_deg)
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(tx, ty), self.color)


class ZwUIRoundedRectangle(ZwUIAbstractShape):
    def __init__(self, left, bottom, width, height, radius, color):
        super(ZwUIRoundedRectangle, self).__init__()
        self.left = left
        self.bottom = bottom
        self.width = width
        self.height = height
        self.color = color
        self.radius = radius
        self.initialize()

    def initialize(self, **kwargs):
        step = 90
        # Left bottom end
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left + self.radius, self.bottom), self.color)
        # Right bottom start
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left + self.width - self.radius, self.bottom), self.color)
        # Right bottom arc
        for i in range(1, step + 1):
            tx = self.left + self.width - self.radius
            ty = self.bottom + self.radius
            tx += self.radius * math.cos(i / step * PI / 2 - PI / 2)
            ty += self.radius * math.sin(i / step * PI / 2 - PI / 2)
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(tx, ty), self.color)
        # Right Top start:
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left + self.width, self.bottom + self.height - self.radius),
                    self.color)
        # Right top arc
        for i in range(1, step + 1):
            tx = self.left + self.width - self.radius
            ty = self.bottom + self.height - self.radius
            tx += self.radius * math.cos(i / step * PI / 2)
            ty += self.radius * math.sin(i / step * PI / 2)
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(tx, ty), self.color)
        # Left top start:
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left + self.radius, self.bottom + self.height), self.color)
        # Left top arc:
        for i in range(1, step + 1):
            tx = self.left + self.radius
            ty = self.bottom + self.height - self.radius
            tx += self.radius * math.cos(i / step * PI / 2 + PI / 2)
            ty += self.radius * math.sin(i / step * PI / 2 + PI / 2)
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(tx, ty), self.color)
        # Left bottom start
        self.insert(ZwUIHelper.get_opengl_pos3d_vector(self.left, self.bottom + self.radius), self.color)
        # Left bottom arc
        for i in range(1, step + 1):
            tx = self.left + self.radius
            ty = self.bottom + self.radius
            tx += self.radius * math.cos(i / step * PI / 2 + PI)
            ty += self.radius * math.sin(i / step * PI / 2 + PI)
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(tx, ty), self.color)


class ZwUICompoundShape(ZwUIAbstractShape):
    def __init__(self):
        super(ZwUICompoundShape, self).__init__()
        self.children = []

    def add_shape(self, shape: ZwUIAbstractShape):
        self.children.append(shape)

    def render(self):
        for i in range(len(self.children)):
            self.children[i].render()


class ZwUIFunctionalCurve(ZwUIAbstractShape):
    def __init__(self, offset_x, offset_y, func_x, color, scale_x=1.0, scale_y=1.0, x_left=0.0, x_right=1.0):
        super(ZwUIFunctionalCurve, self).__init__()
        self.ox = offset_x
        self.color = color
        self.sx = scale_x
        self.sy = scale_y
        self.oy = offset_y
        self.fun = func_x
        self.fill_type = gl.GL_LINE_STRIP
        self.xl = x_left
        self.xr = x_right
        self.initialize()

    def initialize(self, **kwargs):
        for i in range(360 + 1):
            ry = self.oy + (self.fun(i / 360 * (self.xr - self.xl) + self.xl)) * self.sy
            rx = self.ox + (i / 360 * (self.xr - self.xl) + self.xl) * self.sx
            self.insert(ZwUIHelper.get_opengl_pos3d_vector(rx, ry), self.color)


class ZwUIParameterizedCurve(ZwUIAbstractShape):
    def __init__(self):
        super(ZwUIParameterizedCurve, self).__init__()

    def initialize(self, **kwargs):
        pass
