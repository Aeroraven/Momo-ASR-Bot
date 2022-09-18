import OpenGL.GL as gl
import numpy as np


class ZwUIHelper():
    @staticmethod
    def get_opengl_rgba_vector(r, g, b, a=1.0, maxlimit=1.0):
        return [r / maxlimit, g / maxlimit, b / maxlimit, a / maxlimit]

    @staticmethod
    def get_opengl_pos3d_vector(x, y, z=0.0):
        return [x, y, z]

    @staticmethod
    def get_preset_color(color_name):
        return ZwUIHelper.get_opengl_rgba_vector(0, 0, 0)
