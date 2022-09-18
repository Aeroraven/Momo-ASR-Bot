from logger.zw_logger import ZwLogger
from user_interface.zwui_animation import ZwUIClips, ZwUIKeyFrame, ZwUITransition
from user_interface.zwui_constant import ZwUIConstant
from user_interface.zwui_shapes import *


class ZwUIAbstractControl:
    def __init__(self, **kwargs):
        self.ani_clips = {"default": ZwUIClips()}
        self.current_clips = "default"
        self.z_index = 0
        self.paused = False
        self.play_ended = False
        self.handlers = {}
        self.name = ""
        self.hidden = False
        self.recorded_dict = kwargs

    def reload(self, **kwargs):
        for key in kwargs.keys():
            self.recorded_dict[key] = kwargs[key]
        self.ani_clips = {"default": ZwUIClips()}
        self.initialize(**self.recorded_dict)

    def add_handler(self, event: str, handler: callable):
        self.handlers[event] = handler

    def switch_to_animation_list(self, name):
        self.current_clips = name
        if name not in self.ani_clips:
            self.ani_clips[name] = ZwUIClips()

    def switch_to_keyframe(self, idx):
        self.ani_clips[self.current_clips].selected_clips = idx

    def play_animation(self, **kwargs):
        if self.paused:
            return
        self.ani_clips[self.current_clips].selected_clips += 1
        if self.ani_clips[self.current_clips].selected_clips >= len(self.ani_clips[self.current_clips].clips):
            self.ani_clips[self.current_clips].selected_clips = len(self.ani_clips[self.current_clips].clips) - 1
            if not self.play_ended:
                if ZwUIConstant.EV_PLAY_ENDED in self.handlers:
                    self.handlers[ZwUIConstant.EV_PLAY_ENDED](
                        initiator=ZwUIConstant.ROLE,
                        control_name=self.name,
                        event=ZwUIConstant.EV_PLAY_ENDED
                    )
            self.play_ended = True
        else:
            self.play_ended = False

    def append_keyframe(self, keyframe):
        self.ani_clips[self.current_clips].add_frame(keyframe)

    def pop_keyframe(self):
        self.ani_clips[self.current_clips].pop_frame()

    def render(self):
        if not self.hidden:
            self.ani_clips[self.current_clips].render(z_index=self.z_index)

    def on_mouse_down(self, x, y):
        pass

    def initialize(self, **kwargs):
        ZwLogger().log(ZwLogger.ROLE_GUILA, ZwLogger.LV_WARN, "Abstract initialization function is called")
        keyframe = ZwUIKeyFrame()
        self.append_keyframe(keyframe)

    def frame_update(self, **kwargs):
        pass


class ZwUIScene(ZwUIAbstractControl):
    def __init__(self):
        super(ZwUIScene, self).__init__()
        self.control_list: dict[str, ZwUIAbstractControl] = {}

    def add_control(self, name: str, control: ZwUIAbstractControl):
        control.name = name
        self.control_list[name] = control

    def render(self):
        for i in self.control_list.values():
            i.render()

    def play_animation(self, **kwargs):
        for i in self.control_list.values():
            i.play_animation(**kwargs)

    def frame_update(self, **kwargs):
        for i in self.control_list.values():
            i.frame_update()

    def on_mouse_down(self, x, y):
        for i in self.control_list.values():
            i.on_mouse_down(x, y)

    def get_control(self, name):
        return self.control_list[name]


class ZwUITestControl(ZwUIAbstractControl):
    def __init__(self):
        super(ZwUITestControl, self).__init__()
        self.initialize()

    def initialize(self, **kwargs):
        print("HERE 1")
        rrect = ZwUIRectangle(-1, -1, 2, 2, ZwUIHelper.get_opengl_rgba_vector(1.0, 0.0, 0.0))
        rrect2 = ZwUIRoundedRectangle(-1, -1, 2, 2, 0.5, ZwUIHelper.get_opengl_rgba_vector(1.0, 1.0, 0.0))
        keyframe = ZwUIKeyFrame()
        # keyframe.add_shape(rrect)
        keyframe.add_shape(rrect2)
        self.append_keyframe(keyframe)


class ZwUICustomStaticControl(ZwUIAbstractControl):
    def __init__(self, **kwargs):
        super(ZwUICustomStaticControl, self).__init__()
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        keyframe = ZwUIKeyFrame()
        for key in kwargs.keys():
            keyframe.add_shape(kwargs[key])
        self.append_keyframe(keyframe)


class ZwUIButtonControl(ZwUIAbstractControl):
    def __init__(self, x, y, width, height, text, fore_color, back_color, size=12, font_weight=1, **kwargs):
        super(ZwUIButtonControl, self).__init__(**kwargs)
        self.location_y = y
        self.location_x = x
        self.width = width
        self.height = height
        self.text = text
        self.font_color = fore_color
        self.back_color = back_color
        self.scale = size
        self.font_weight = font_weight
        self.initialize(**kwargs)

    def on_mouse_down(self, x, y):
        if self.location_x < x < self.location_x + self.width:
            if self.location_y < y < self.location_y + self.height:
                if ZwUIConstant.EV_CLICK in self.handlers:
                    self.handlers[ZwUIConstant.EV_CLICK](
                        initiator=ZwUIConstant.ROLE,
                        control_name=self.name,
                        event=ZwUIConstant.EV_CLICK
                    )

    def initialize(self, **kwargs):
        if 'animated' in kwargs:
            assert 'animation_duration' in kwargs, "Animation duration must be configured"
            tra = lambda x: x
            if 'animation_transition' in kwargs:
                tra = lambda x: kwargs['animation_transition'](x)[1]
            if kwargs['animated'] == 'fade_in':
                for i in range(int(kwargs['animation_duration'])):
                    kf = ZwUIKeyFrame()
                    d = 0.02
                    rect_a = ZwUIRoundedRectangle(self.location_x, self.location_y, self.width, self.height, 0.1,
                                                  ZwUITransition.color_trans(tra, self.back_color, self.font_color,
                                                                             (i + 1) / int(
                                                                                 kwargs['animation_duration'])))
                    rect_b = ZwUIRoundedRectangle(self.location_x + d * 1,
                                                  self.location_y + d * 1,
                                                  self.width - d * 2,
                                                  self.height - d * 2, 0.1, self.back_color)
                    tx = ZwUIText(self.location_x + 0.3,
                                  self.location_y + self.height / 2 - 0.1,
                                  self.text,
                                  ZwUITransition.color_trans(tra, self.back_color, self.font_color,
                                                             (i + 1) / int(kwargs['animation_duration'])),
                                  self.scale, self.scale)
                    kf.add_shape(tx)
                    kf.add_shape(rect_b)
                    kf.add_shape(rect_a)
                    self.append_keyframe(kf)
            if kwargs['animated'] == 'fade_out':
                for i in range(int(kwargs['animation_duration'])):
                    kf = ZwUIKeyFrame()
                    d = 0.02
                    rect_a = ZwUIRoundedRectangle(self.location_x, self.location_y, self.width, self.height, 0.1,
                                                  ZwUITransition.color_trans(tra, self.font_color, self.back_color,
                                                                             (i + 1) / int(
                                                                                 kwargs['animation_duration'])))
                    rect_b = ZwUIRoundedRectangle(self.location_x + d * 1,
                                                  self.location_y + d * 1,
                                                  self.width - d * 2,
                                                  self.height - d * 2, 0.1, self.back_color)
                    tx = ZwUIText(self.location_x + 0.3,
                                  self.location_y + self.height / 2 - 0.1,
                                  self.text,
                                  ZwUITransition.color_trans(tra, self.font_color, self.back_color,
                                                             (i + 1) / int(kwargs['animation_duration'])),
                                  self.scale, self.scale)
                    kf.add_shape(tx)
                    kf.add_shape(rect_b)
                    kf.add_shape(rect_a)
                    self.append_keyframe(kf)

        else:
            kf = ZwUIKeyFrame()
            d = 0.02
            rect_a = ZwUIRoundedRectangle(self.location_x, self.location_y, self.width, self.height, 0.1,
                                          self.font_color)
            rect_b = ZwUIRoundedRectangle(self.location_x + d * 1,
                                          self.location_y + d * 1,
                                          self.width - d * 2,
                                          self.height - d * 2, 0.1, self.back_color)
            tx = ZwUIText(self.location_x + 0.3,
                          self.location_y + self.height / 2 - 0.1,
                          self.text, self.font_color,
                          self.scale, self.scale)
            kf.add_shape(tx)
            kf.add_shape(rect_b)
            kf.add_shape(rect_a)

            self.append_keyframe(kf)


class ZwUILabelControl(ZwUIAbstractControl):
    def __init__(self, x, y, text, color, size=12, font_weight=1, **kwargs):
        super(ZwUILabelControl, self).__init__(**kwargs)
        self.location_y = y
        self.location_x = x
        self.font_color = color
        self.caption = text
        self.scale = size
        self.text_mode = True
        self.weight = font_weight
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        if 'overridden_text' in kwargs:
            self.caption = kwargs['overridden_text']
        if 'animated' in kwargs:
            assert 'animation_duration' in kwargs, "Animation duration must be configured"
            tra = lambda x: x
            if 'animation_transition' in kwargs:
                tra = lambda x: kwargs['animation_transition'](x)[1]
            if kwargs['animated'] == 'typing':
                for i in range(int(kwargs['animation_duration'])):
                    st = self.caption[:int((i + 1) / kwargs['animation_duration'] * len(self.caption))]
                    tx = ZwUIText(self.location_x, self.location_y, st, self.font_color, self.scale, self.weight)
                    kf = ZwUIKeyFrame()
                    kf.add_shape(tx)
                    self.append_keyframe(kf)
            if kwargs['animated'] == 'rising':
                assert 'rising_dy' in kwargs, "Rising offset must be configured"
                for i in range(int(kwargs['animation_duration'])):
                    tx = ZwUIText(self.location_x,
                                  self.location_y + tra((i + 1) / kwargs['animation_duration']) * kwargs['rising_dy'],
                                  self.caption, self.font_color,
                                  self.scale, self.weight)
                    kf = ZwUIKeyFrame()
                    kf.add_shape(tx)
                    self.append_keyframe(kf)

            if kwargs['animated'] == 'descending':
                assert 'desc_dy' in kwargs, "Falling offset must be configured"
                for i in range(int(kwargs['animation_duration'])):
                    tx = ZwUIText(self.location_x,
                                  self.location_y + (tra((i + 1) / kwargs['animation_duration'])) * -kwargs['desc_dy'],
                                  self.caption, self.font_color,
                                  self.scale, self.weight)
                    kf = ZwUIKeyFrame()
                    kf.add_shape(tx)
                    self.append_keyframe(kf)
        else:
            tx = ZwUIText(self.location_x, self.location_y, self.caption, self.font_color, self.scale, self.weight)
            kf = ZwUIKeyFrame()
            kf.add_shape(tx)
            self.append_keyframe(kf)


class ZwUINestedLabelControl(ZwUIAbstractControl):
    def __init__(self, x, y, text, fore_color, back_color, box_height, box_width, size=12, font_weight=1, **kwargs):
        super(ZwUINestedLabelControl, self).__init__(**kwargs)
        self.location_y = y
        self.location_x = x
        self.boxh = box_height
        self.boxw = box_width
        self.font_color = fore_color
        self.back_color = back_color
        self.caption = text
        self.scale = size
        self.text_mode = True
        self.weight = font_weight
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        if 'overridden_text' in kwargs:
            self.caption = kwargs['overridden_text']
        tx_ox = 0
        tx_oy = 0
        if 'text_offset_y' in kwargs:
            tx_oy = kwargs['text_offset_y']
        if 'text_offset_x' in kwargs:
            tx_ox = kwargs['text_offset_x']

        if 'animated' in kwargs:
            assert 'animation_duration' in kwargs, "Animation duration must be configured"
            if kwargs['animated'] == 'typing':
                transition_activation = lambda x: x
                if 'animation_transition' in kwargs:
                    transition_activation = lambda x: kwargs['animation_transition'](x)[1]
                if 'delayed_frames' in kwargs:
                    for i in range(kwargs['delayed_frames']):
                        self.append_keyframe(ZwUIKeyFrame())
                for i in range(-1, int(kwargs['animation_duration'])):
                    st = self.caption[
                         :int(transition_activation((i + 1.) / kwargs['animation_duration']) * len(self.caption))]
                    tx = ZwUIText(self.location_x + 0.2 + tx_ox, self.location_y + 0.3 + tx_oy, st, self.font_color,
                                  self.scale,
                                  self.weight)
                    bg = ZwUIRoundedRectangle(self.location_x, self.location_y,
                                              self.boxw * transition_activation((i + 1) / kwargs['animation_duration']),
                                              self.boxh, 0.3,
                                              self.back_color)
                    kf = ZwUIKeyFrame()
                    kf.add_shape(tx)
                    kf.add_shape(bg)
                    self.append_keyframe(kf)
        else:
            tx = ZwUIText(self.location_x + 0.2 + tx_ox, self.location_y + 0.3 + tx_oy, self.caption, self.font_color,
                          self.scale, self.weight)
            bg = ZwUIRoundedRectangle(self.location_x, self.location_y, self.boxw, self.boxh, 0.3, self.back_color)
            kf = ZwUIKeyFrame()
            kf.add_shape(tx)
            kf.add_shape(bg)
            self.append_keyframe(kf)


class ZwUIFuncCurveDispControl(ZwUIAbstractControl):
    def __init__(self, offset_x, offset_y, func_x, color, scale_x=1.0, scale_y=1.0, x_left=0.0, x_right=1.0):
        super(ZwUIFuncCurveDispControl, self).__init__()
        self.ox = offset_x
        self.color = color
        self.sx = scale_x
        self.sy = scale_y
        self.oy = offset_y
        self.fun = func_x
        self.xl = x_left
        self.xr = x_right
        self.initialize()

    def initialize(self, **kwargs):
        cr = ZwUIFunctionalCurve(self.ox, self.oy, self.fun, self.color, self.sx, self.sy, self.xl, self.xr)
        kf = ZwUIKeyFrame()
        kf.add_shape(cr)
        self.append_keyframe(kf)


class ZwUIStripedWaveControl(ZwUIAbstractControl):
    def __init__(self, x, center_y, strips, strip_width, strip_gap, color):
        super(ZwUIStripedWaveControl, self).__init__()
        self.x = x
        self.y = center_y
        self.st = strips
        self.wid = strip_width
        self.gap = strip_gap
        self.color = color
        self.initialize()
        self.floating = 0
        self.floating_lim = 45
        self.hv = 0.05
        self.emp_list = [0.05 for _ in range(100)]

    def initialize(self, **kwargs):
        kf = ZwUIKeyFrame()
        for i in range(self.st):
            t = ZwUIRectangle(self.x + (self.wid + self.gap) * i, -0.1 + self.y, self.wid, 0.2, self.color)
            kf.add_shape(t)
        self.append_keyframe(kf)

    def set_height(self, height=0.1):
        self.hv = height

    def frame_update(self, **kwargs):
        self.floating = self.floating + 1

        kf = ZwUIKeyFrame()
        for i in range(self.st - 1):
            t = ZwUIRectangle(self.x + (self.wid + self.gap) * i +
                              (self.floating / self.floating_lim) * (self.wid + self.gap),
                              -self.emp_list[i + 1] + self.y, self.wid, self.emp_list[i + 1] * 2, self.color)
            kf.add_shape(t)
        dr = self.floating / self.floating_lim
        dl = self.gap / (self.wid + self.gap)
        if dr >= dl:
            t = ZwUIRectangle(self.x, self.y - self.emp_list[0],
                              self.wid * (dr - dl) / (1 - dl), self.emp_list[0] * 2, self.color)
            kf.add_shape(t)
        else:
            t = ZwUIRectangle(self.x + (self.wid + self.gap) * (self.st - 1) +
                              (self.floating / self.floating_lim) * (self.wid + self.gap),
                              -self.emp_list[self.st] + self.y, self.wid * (1 - dr / dl),
                              self.emp_list[self.st] * 2, self.color)
            kf.add_shape(t)
        if self.floating == self.floating_lim:
            self.emp_list.pop()
            self.emp_list.insert(0, self.hv)
            self.floating = 0
        self.pop_keyframe()
        self.append_keyframe(kf)


class ZwUISwitchMaskControl(ZwUIAbstractControl):
    def __init__(self, color, **kwargs):
        super(ZwUISwitchMaskControl, self).__init__()
        self.color = color
        self.z_index = 20
        self.initialize(**kwargs)
        self.paused = True

    def initialize(self, **kwargs):
        if 'animated' in kwargs:
            assert 'animation_duration' in kwargs, "Animation duration must be configured"
            vertical = False
            if 'vertical' in kwargs and kwargs['vertical']:
                vertical = True
            if kwargs['animated'] == 'default':
                transition_activation = lambda x: x
                if 'animation_transition' in kwargs:
                    transition_activation = lambda x: kwargs['animation_transition'](x)[1]
                if 'delayed_frames' in kwargs:
                    for i in range(kwargs['delayed_frames']):
                        self.append_keyframe(ZwUIKeyFrame())
                if 'ignore_in' not in kwargs or not kwargs['ignore_in']:
                    for i in range(-1, int(kwargs['animation_duration'])):
                        kf = ZwUIKeyFrame()
                        ratio = transition_activation((i + 1) / kwargs['animation_duration'])
                        if not vertical:
                            bg = ZwUIRectangle(-10, -90, 20 * ratio, 180, self.color)
                        else:
                            bg = ZwUIRectangle(-90, -20, 180, 40 * ratio, self.color)
                        kf.add_shape(bg)
                        self.append_keyframe(kf)
                if 'ignore_out' not in kwargs or not kwargs['ignore_out']:
                    for i in range(-1, int(kwargs['animation_duration'])):
                        kf = ZwUIKeyFrame()
                        ratio = transition_activation((i + 1) / kwargs['animation_duration'])
                        if not vertical:
                            bg = ZwUIRectangle(-10 + 20 * ratio, -90, 20 * (1 - ratio), 180, self.color)
                        else:
                            bg = ZwUIRectangle(-90, -20 + 40 * ratio, 180, 40 * (1 - ratio), self.color)
                        kf.add_shape(bg)
                        self.append_keyframe(kf)


class ZwUIMicrophoneIconControl(ZwUIAbstractControl):
    def __init__(self, x, y, fore_color, back_color, size=2):
        super(ZwUIMicrophoneIconControl, self).__init__()
        self.x = x
        self.y = y
        self.s = size
        self.fc = fore_color
        self.bc = back_color
        self.initialize()

    def initialize(self, **kwargs):
        x = self.x
        y = self.y
        s = self.s
        fx = -0.1
        keyframe1 = ZwUIKeyFrame()
        base = ZwUIRectangle(x, y, s, s / 5, self.fc)
        rod = ZwUIRectangle(x + s / 2 - s / 8, y + s / 5, s / 8 * 2, s / 3, self.fc)
        plate = ZwUICircle(x + s / 2, y + s / 5 + s / 3 + s / 2 + fx, s / 2, self.fc, PI, 2 * PI)
        plate_in = ZwUICircle(x + s / 2, y + s / 5 + s / 3 + s / 2 + fx, s / 3, self.bc, PI, 2 * PI)
        phone = ZwUIRoundedRectangle(x + s / 2 - s / 4,
                                     y + s / 5 + s / 3 + s / 2 + fx - s / 4, s / 2,
                                     s / 1.2, s / 4, self.fc)
        keyframe1.add_shape(base)
        keyframe1.add_shape(rod)
        keyframe1.add_shape(phone)
        keyframe1.add_shape(plate_in)
        keyframe1.add_shape(plate)
        self.append_keyframe(keyframe1)


class ZwUITimer(ZwUIAbstractControl):
    def __init__(self, timeout, **kwargs):
        super(ZwUITimer, self).__init__()
        self.activated = True
        self.timeout = timeout
        self.cnt = 0
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        keyframe = ZwUIKeyFrame()
        self.append_keyframe(keyframe)

    def play_animation(self, **kwargs):
        if self.activated:
            # print("TIMER", self.cnt, self.timeout)
            self.cnt += 1
            if self.cnt >= self.timeout:
                self.cnt = 0
                self.activated = False
                if ZwUIConstant.EV_TIMER_TIMEOUT in self.handlers:
                    self.handlers[ZwUIConstant.EV_TIMER_TIMEOUT](
                        initiator=ZwUIConstant.ROLE,
                        control_name=self.name,
                        event=ZwUIConstant.EV_TIMER_TIMEOUT
                    )


class ZwUIMomoBotIconControl(ZwUIAbstractControl):
    def __init__(self, x, y, radius=2, fore=ZwUIHelper.get_opengl_rgba_vector(1, 1, 1),
                 back=ZwUIHelper.get_opengl_rgba_vector(0, 0, 0)):
        super(ZwUIMomoBotIconControl, self).__init__()
        self.x = x
        self.y = y
        self.r = radius
        self.fore = fore
        self.back = back
        self.paused = True
        self.initialize()

    def initialize(self, **kwargs):
        # Primary Params
        x = self.x
        y = self.y
        r = self.r
        r2 = self.r * 0.718
        # Face Params
        fr = 0.5
        fr2 = 0.3
        dh = r / 1.618
        fs = r / 3
        delta = 0.01
        # Antenna Params
        anw = r / 5
        anh = r / 3
        anhd = 0.1
        anhr = r / 5
        # Eye Params
        eyecl = r / 2.8
        eyelh = r / 3.8
        eyenr = r / 8
        eyesp = r / 9

        eyecl2 = r / 3
        eyelh2 = r / 3.5
        eyenr2 = r / 5

        eyecl2i = r / 2
        eyelh2i = r / 4.5
        eyenr2i = r / 9

        # Ear Params
        earw = r / 5
        earh = r / 2
        earb = r / 3
        ear_adjust = 0.1

        face1 = ZwUICircle(x + r, y + dh, r, self.back, 0, PI + 1.0 / 360 * PI * 2)
        face2 = ZwUIRoundedRectangle(x, y, 2 * r, dh, fr, self.back)
        face3 = ZwUIRectangle(x, y + fr, 2 * r, dh - fr + delta, self.back)
        face_in1 = ZwUICircle(x + r, y + dh, r2, self.fore, 0, PI + 1.0 / 360 * PI * 2)
        face_in2 = ZwUIRoundedRectangle(x + (r - r2), y + dh - fs + fr2, r2 * 2, fs, fr2, self.fore)
        antenna1 = ZwUIRectangle(x + r - anw / 2, y + dh + r - anhd, anw, anh, self.back)
        antenna2 = ZwUICircle(x + r, y + dh + r - anhd + anh, anhr, self.back)
        eye_normal1 = ZwUICircle(x + r - eyecl, y + dh - fs + fr2 + eyelh, eyenr, self.back)
        eye_normal2 = ZwUICircle(x + r + eyecl, y + dh - fs + fr2 + eyelh, eyenr, self.back)
        eye_exciting1 = ZwUITriangle(
            ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2 + eyenr2, y + dh - fs + fr2 + eyelh2),
            ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2 - eyenr2, y + dh - fs + fr2 + eyelh2 + eyenr2),
            ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2 - eyenr2, y + dh - fs + fr2 + eyelh2 - eyenr2),
            self.back
        )
        eye_exciting2 = ZwUITriangle(
            ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2 - eyenr2, y + dh - fs + fr2 + eyelh2),
            ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2 + eyenr2, y + dh - fs + fr2 + eyelh2 + eyenr2),
            ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2 + eyenr2, y + dh - fs + fr2 + eyelh2 - eyenr2),
            self.back
        )
        eye_exciting_in1 = ZwUITriangle(
            ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2i + eyenr2i, y + dh - fs + fr2 + eyelh2),
            ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2i - eyenr2i, y + dh - fs + fr2 + eyelh2 + eyenr2i),
            ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2i - eyenr2i, y + dh - fs + fr2 + eyelh2 - eyenr2i),
            self.fore
        )
        eye_exciting_in2 = ZwUITriangle(
            ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2i - eyenr2i, y + dh - fs + fr2 + eyelh2),
            ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2i + eyenr2i, y + dh - fs + fr2 + eyelh2 + eyenr2i),
            ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2i + eyenr2i, y + dh - fs + fr2 + eyelh2 - eyenr2i),
            self.fore
        )
        ear1 = ZwUIRectangle(x - earw + ear_adjust, y + earb, earw, earh, self.back)
        ear2 = ZwUIRectangle(x + 2 * r - ear_adjust, y + earb, earw, earh, self.back)

        keyframe1 = ZwUIKeyFrame()
        keyframe1.add_shape(eye_exciting_in1)
        keyframe1.add_shape(eye_exciting_in2)
        keyframe1.add_shape(eye_exciting1)
        keyframe1.add_shape(eye_exciting2)
        keyframe1.add_shape(face_in1)
        keyframe1.add_shape(face_in2)
        keyframe1.add_shape(face1)
        keyframe1.add_shape(face2)
        keyframe1.add_shape(face3)
        keyframe1.add_shape(antenna1)
        keyframe1.add_shape(antenna2)
        keyframe1.add_shape(ear1)
        keyframe1.add_shape(ear2)

        keyframe2 = ZwUIKeyFrame()
        keyframe2.add_shape(eye_normal1)
        keyframe2.add_shape(eye_normal2)
        keyframe2.add_shape(face_in1)
        keyframe2.add_shape(face_in2)
        keyframe2.add_shape(face1)
        keyframe2.add_shape(face2)
        keyframe2.add_shape(face3)
        keyframe2.add_shape(antenna1)
        keyframe2.add_shape(antenna2)
        keyframe2.add_shape(ear1)
        keyframe2.add_shape(ear2)

        self.append_keyframe(keyframe1)
        self.ani_clips["normal"] = ZwUIClips()
        self.ani_clips["normal"].add_frame(keyframe2)


class ZwUIAniMomoBotIconControl(ZwUIAbstractControl):
    def __init__(self, x, y, radius=2, fore=ZwUIHelper.get_opengl_rgba_vector(1, 1, 1),
                 back=ZwUIHelper.get_opengl_rgba_vector(0, 0, 0), **kwargs):
        super(ZwUIAniMomoBotIconControl, self).__init__()
        self.x = x
        self.y = y
        self.r = radius
        self.fore = fore
        self.back = back
        self.paused = True
        self.initialize(**kwargs)

    def initialize(self, **kwargs):
        # Primary Params
        x = self.x
        y = self.y
        r = self.r
        r2 = self.r * 0.718
        # Face Params
        fr = 0.5
        fr2 = 0.3
        dh = r / 1.618
        fs = r / 3
        delta = 0.01
        # Antenna Params
        anw = r / 5
        anh = r / 3
        anhd = 0.1
        anhr = r / 5
        # Eye Params
        eyecl = r / 2.8
        eyelh = r / 3.8
        eyenr = r / 8
        eyesp = r / 9

        eyecl2 = r / 3
        eyelh2 = r / 3.5
        eyenr2 = r / 5

        eyecl2i = r / 2
        eyelh2i = r / 4.5
        eyenr2i = r / 9

        # Ear Params
        earw = r / 5
        earh = r / 2
        earb = r / 3
        ear_adjust = 0.1

        assert 'animation_duration' in kwargs, "Animation duration must be configured"
        tra = lambda x: x
        if 'animation_transition' in kwargs:
            tra = lambda x: kwargs['animation_transition'](x)[1]
        for i in range(-1, int(kwargs['animation_duration'])):
            fgc = self.fore
            bgc = ZwUITransition.color_trans(tra, self.fore, self.back, (i + 1) / int(kwargs['animation_duration']))
            face1 = ZwUICircle(x + r, y + dh, r, bgc, 0, PI + 1.0 / 360 * PI * 2)
            face2 = ZwUIRoundedRectangle(x, y, 2 * r, dh, fr, bgc)
            face3 = ZwUIRectangle(x, y + fr, 2 * r, dh - fr + delta, bgc)
            face_in1 = ZwUICircle(x + r, y + dh, r2, fgc, 0, PI + 1.0 / 360 * PI * 2)
            face_in2 = ZwUIRoundedRectangle(x + (r - r2), y + dh - fs + fr2, r2 * 2, fs, fr2, fgc)
            antenna1 = ZwUIRectangle(x + r - anw / 2, y + dh + r - anhd, anw, anh, bgc)
            antenna2 = ZwUICircle(x + r, y + dh + r - anhd + anh, anhr, bgc)
            eye_normal1 = ZwUICircle(x + r - eyecl, y + dh - fs + fr2 + eyelh, eyenr, bgc)
            eye_normal2 = ZwUICircle(x + r + eyecl, y + dh - fs + fr2 + eyelh, eyenr, bgc)
            eye_exciting1 = ZwUITriangle(
                ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2 + eyenr2, y + dh - fs + fr2 + eyelh2),
                ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2 - eyenr2, y + dh - fs + fr2 + eyelh2 + eyenr2),
                ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2 - eyenr2, y + dh - fs + fr2 + eyelh2 - eyenr2),
                bgc
            )
            eye_exciting2 = ZwUITriangle(
                ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2 - eyenr2, y + dh - fs + fr2 + eyelh2),
                ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2 + eyenr2, y + dh - fs + fr2 + eyelh2 + eyenr2),
                ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2 + eyenr2, y + dh - fs + fr2 + eyelh2 - eyenr2),
                bgc
            )
            eye_exciting_in1 = ZwUITriangle(
                ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2i + eyenr2i, y + dh - fs + fr2 + eyelh2),
                ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2i - eyenr2i, y + dh - fs + fr2 + eyelh2 + eyenr2i),
                ZwUIHelper.get_opengl_pos3d_vector(x + r - eyecl2i - eyenr2i, y + dh - fs + fr2 + eyelh2 - eyenr2i),
                fgc
            )
            eye_exciting_in2 = ZwUITriangle(
                ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2i - eyenr2i, y + dh - fs + fr2 + eyelh2),
                ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2i + eyenr2i, y + dh - fs + fr2 + eyelh2 + eyenr2i),
                ZwUIHelper.get_opengl_pos3d_vector(x + r + eyecl2i + eyenr2i, y + dh - fs + fr2 + eyelh2 - eyenr2i),
                fgc
            )
            ear1 = ZwUIRectangle(x - earw + ear_adjust, y + earb, earw, earh, bgc)
            ear2 = ZwUIRectangle(x + 2 * r - ear_adjust, y + earb, earw, earh, bgc)

            keyframe1 = ZwUIKeyFrame()
            keyframe1.add_shape(eye_exciting_in1)
            keyframe1.add_shape(eye_exciting_in2)
            keyframe1.add_shape(eye_exciting1)
            keyframe1.add_shape(eye_exciting2)
            keyframe1.add_shape(face_in1)
            keyframe1.add_shape(face_in2)
            keyframe1.add_shape(face1)
            keyframe1.add_shape(face2)
            keyframe1.add_shape(face3)
            keyframe1.add_shape(antenna1)
            keyframe1.add_shape(antenna2)
            keyframe1.add_shape(ear1)
            keyframe1.add_shape(ear2)

            keyframe2 = ZwUIKeyFrame()
            keyframe2.add_shape(eye_normal1)
            keyframe2.add_shape(eye_normal2)
            keyframe2.add_shape(face_in1)
            keyframe2.add_shape(face_in2)
            keyframe2.add_shape(face1)
            keyframe2.add_shape(face2)
            keyframe2.add_shape(face3)
            keyframe2.add_shape(antenna1)
            keyframe2.add_shape(antenna2)
            keyframe2.add_shape(ear1)
            keyframe2.add_shape(ear2)

            self.append_keyframe(keyframe1)
            self.ani_clips["normal"] = ZwUIClips()
            self.ani_clips["normal"].add_frame(keyframe2)
