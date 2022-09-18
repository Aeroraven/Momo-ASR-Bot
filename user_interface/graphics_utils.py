import array

import OpenGL.GL as ogl
import OpenGL.GLUT as glut
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QOpenGLShader, QOpenGLShaderProgram
from PyQt5.QtOpenGL import QGLWidget
from PyQt5.QtQuick import QSGGeometry

from logger.zw_logger import ZwLogger
from app import ZwUIHCILab01


class ZwOpenGLHelper():
    GL_COLOR_BUFFER_BIT = 2

    def get_vertex_shader(self):
        ret = ""
        with open(r"../shader/vertex.shader", "r") as f:
            ret = f.read()
        shader = QOpenGLShader(QOpenGLShader.Vertex)
        print("ZwGC compile vert shader")
        res = shader.compileSourceCode(ret)
        if not res:
            raise Exception("ZwOpenGLHelper: Vertex Shader Error")
        print("ZwGC shader returned")
        return shader

    def get_fragment_shader(self):
        ret = ""
        with open(r"../shader/fragment.shader", "r") as f:
            ret = f.read()
        shader = QOpenGLShader(QOpenGLShader.Fragment)
        res = shader.compileSourceCode(ret)
        if not res:
            raise Exception("ZwOpenGLHelper: Fragment Shader Error")
        return shader

    def get_compiled_shader(self):
        shader_program = QOpenGLShaderProgram()
        print("ZwGC ready to get vert shader")
        shader_program.addShader(self.get_vertex_shader())
        print("ZwGC ready to get frag shader")
        shader_program.addShader(self.get_fragment_shader())
        print("ZwGC ready to link shader")
        res = shader_program.link()
        if not res:
            raise Exception("ZwOpenGLHelper: Cannot Link Shader Program")
        shader_program.bind()
        return shader_program

    def bind_vertices(self, shader_program: QOpenGLShaderProgram, vertices):
        vertices = array.array(vertices)
        shader_program.bindAttributeLocation("vertexv", 0)
        shader_program.enableAttributeArray(0)
        shader_program.setAttributeArray(0, vertices)

    def bind_color(self, shader_program: QOpenGLShaderProgram, colors):
        colors = array.array(colors)
        shader_program.bindAttributeLocation("colorv", 1)
        shader_program.enableAttributeArray(1)
        shader_program.setAttributeArray(1, colors)

    def test_data(self):
        vertex = [
            0.0, 0.0, 0.0,
            1.0, 0.0, 0.0,
            0.0, 1.0, 0.0,
        ]
        color = [
            1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0,
        ]
        return vertex, color

    def draw(self, gl, shader_program: QOpenGLShaderProgram, vertices, colors):
        length = len(vertices)
        shader_program.bind()
        self.bind_vertices(shader_program, vertices)
        self.bind_color(shader_program, colors)
        ogl.glDrawArrays(QSGGeometry.GL_TRIANGLES, 0, length)
        shader_program.release()


class ZwInteractivePageAttrib:
    def __init__(self):
        self.page_width_scale = 5
        self.z_near = -100
        self.z_far = 100


class ZwGraphicsContainer(QGLWidget):
    def __init__(self, parent, format_s, frame_rate=60, app=None, s_width=None, s_height=None):
        super().__init__(format_s, parent)
        self.wparent = parent
        self.gl_assist = ZwOpenGLHelper()
        self.attrib = ZwInteractivePageAttrib()
        self.application = app
        self.updater = QTimer(self)
        self.updater.timeout.connect(self.frame_advance)
        self.interval = 1000 / frame_rate
        self.setMouseTracking(True)
        self.s_width = s_width
        self.s_height = s_height

    def mouseMoveEvent(self, event):
        try:
            x = event.x()
            y = event.y()
            dy = self.attrib.page_width_scale * self.s_height / self.s_width * (y / self.s_height)
            dy = dy * 2 - self.attrib.page_width_scale * self.s_height / self.s_width
            dx = self.attrib.page_width_scale * (x / self.s_width)
            dx = dx * 2 - self.attrib.page_width_scale
            self.application.qt_mouse_move_event(dx, dy)
            event.accept()
        except AttributeError:
            pass

    def mousePressEvent(self, event):
        try:
            x = event.x()
            y = event.y()
            dy = self.attrib.page_width_scale * self.s_height / self.s_width * (y / self.s_height)
            dy = - dy * 2 + self.attrib.page_width_scale * self.s_height / self.s_width
            dx = self.attrib.page_width_scale * (x / self.s_width)
            dx = dx * 2 - self.attrib.page_width_scale
            self.application.qt_mouse_down_event(dx, dy)
            ZwLogger().log(ZwLogger.ROLE_GUIQT, ZwLogger.LV_INFO,
                           "Mouse press event. ax=" + str(dx) + ", ay=" + str(dy))
            event.accept()
        except AttributeError:
            pass

    def frame_advance(self):
        self.application.frame_update()
        self.application.play()
        self.update()

    def paintGL(self) -> None:
        self.makeCurrent()
        self.application.gl_clear_func()
        ogl.glLoadIdentity()
        ogl.glTranslated(0, 0, -10)
        ogl.glClear(ogl.GL_COLOR_BUFFER_BIT | ogl.GL_DEPTH_BUFFER_BIT)
        self.application.render()

    def initializeGL(self) -> None:
        self.updater.start(int(self.interval))
        self.makeCurrent()
        ZwLogger().log(ZwLogger.ROLE_GUI, ZwLogger.LV_INFO, "Initializing OpenGL in Qt5 Framework")
        ogl.glShadeModel(ogl.GL_SMOOTH)
        ogl.glEnable(ogl.GL_DEPTH_TEST)
        # ogl.glEnable(ogl.GL_CULL_FACE)
        ogl.glEnable(ogl.GL_POINT_SMOOTH)
        ogl.glEnable(ogl.GL_LINE_SMOOTH)
        ogl.glEnable(ogl.GL_MULTISAMPLE)
        ogl.glEnable(ogl.GL_POLYGON_SMOOTH)
        ogl.glHint(ogl.GL_POLYGON_SMOOTH_HINT, ogl.GL_NICEST)
        ogl.glHint(ogl.GL_LINE_SMOOTH_HINT, ogl.GL_NICEST)
        ogl.glHint(ogl.GL_POINT_SMOOTH_HINT, ogl.GL_NICEST)
        ZwLogger().log(ZwLogger.ROLE_GUI, ZwLogger.LV_INFO, "Initializing OpenGL Utility Tools in Qt5 Framework")
        self.glut_initialization()
        ZwLogger().log(ZwLogger.ROLE_GUI, ZwLogger.LV_INFO, "Graphic initialization completed.")

    def glut_initialization(self):
        glut.glutInit()
        glut.glutMouseFunc(self.glut_mouse_event)
        glut.glutMotionFunc(self.glut_motion_event)

    def glut_mouse_event(self, button, state, x, y):
        print(button, state, x, y)

    def glut_motion_event(self, x, y):
        print("Motion", x, y)

    def resizeGL(self, w: int, h: int) -> None:
        self.makeCurrent()
        side = min(w, h)
        if side < 0:
            return
        ogl.glViewport(0, 0, w, h)
        ogl.glMatrixMode(ogl.GL_PROJECTION)
        ogl.glLoadIdentity()
        ogl.glOrtho(-self.attrib.page_width_scale, self.attrib.page_width_scale,
                    -self.attrib.page_width_scale * h / w, self.attrib.page_width_scale * h / w,
                    self.attrib.z_near, self.attrib.z_far)
        ogl.glMatrixMode(ogl.GL_MODELVIEW)
