from logger.zw_logger import ZwLogger
from user_interface.zwui_controls import *


class ZwUIApplication:
    def __init__(self):
        self.scenes: dict[str, ZwUIScene] = {}
        self.current_scene = ""
        ZwLogger().log(ZwLogger.ROLE_GUILA, ZwLogger.LV_INFO, "Initializing Controls")
        self.initialize()
        ZwLogger().log(ZwLogger.ROLE_GUILA, ZwLogger.LV_INFO, "Controls are successfully initialized")

    def on_frame_update(self, **kwargs):
        pass

    def add_scene(self, name: str, scene: ZwUIScene):
        self.scenes[name] = scene

    def set_active_scene(self, name: str):
        self.current_scene = name

    def render(self):
        self.scenes[self.current_scene].render()

    def play(self):
        self.scenes[self.current_scene].play_animation()

    def initialize(self, **kwargs):
        pass

    def frame_update(self, **kwargs):
        self.on_frame_update(**kwargs)
        self.scenes[self.current_scene].frame_update()

    def gl_clear_func(self, **kwargs):
        pass

    def get_scene(self, name):
        return self.scenes[name]

    def qt_mouse_move_event(self, x, y):
        # print("QTME", x, y)
        pass

    def qt_mouse_down_event(self, x, y):
        self.scenes[self.current_scene].on_mouse_down(x, y)
        pass
