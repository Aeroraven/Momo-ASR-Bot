<h2 align = "center"> Assignment 1 for Human Computer Interaction</h2>
<h3 align = "center"> Speech Recognition App</h3>
<p align="center">Aeroraven</p>

### A. Run

Execute the command

```shell
python main.py
```

Here are all parameters supported.

```shell
python main.py [-h] [--msaa MSAA] [--fps FPS]
# --help       Display help
# --msaa MSAA  Antialiasing (Defaults to 16)
# --fps FPS    Limit of FPS (Defaults to 60)
```

NOTE: Deep learning models are not uploaded for they are too large.



### B. Running Prerequisite

#### System Requirement

- Graphics Card
- Microphone
- Python >= 3.7



#### Python Packages

| Package                 | Version | Usage           |
| ----------------------- | ------- | --------------- |
| PyOpenGL (*)            | 3.1.6   | UI              |
| PyOpenGL-accelerate (*) | 3.1.6   | UI Acceleration |
| PyQt5                   | 5.15.4  | MSAA & Context  |
| SpeechRecognition (!)   | 3.8.1   | ASR             |
| NumPy                   | 1.19.3  | Math Operations |

Use `conda` or `pip` to install these packages



---

Following parts are the submitted document.



### 1. Graphic Interface Improvements

#### 1.1 Basic Structure of Modified GUI

##### 1.1.1 Overall Design Goals / Ideas

The aim of this assignment is to design a voice recognition apps. Here are several considerations.

- **Protrait Layout**. This is the default layout of smartphones, which can make user feel the application is more light, compact and familiar.
- **Smooth Transition & Avoid Sharp Elements**. This provides aesthetic beauty. Smooth transition can make the UI more dynamic and the avoidance of sharp elements can make the visual representation easier on eyes.
  - Examples used in this app: Rounded-rectangle, Cubic-bezier transition, Switching animation
- **Placebo Effect & Valid Feedback.** Placebo effect originally refers to a beneficial effect produced by a placebo drug or treatment, which cannot be attributed to the properties of the placebo itself, and must therefore be due to the patient's belief in that treatment. In practice, some placebo-effect designs can usefully reduce user's tense when they use this application.
  - Examples used in this app: Voice power indicator
- **Affinity. ** It's better if the users feel they are contact with an companion instead of a cold machine.
  - Example used in this app: Anthropomorphic expression, Robot icons
- **Performance.** If the recognition model has higher accuracy, users will have better experience.
  - Example used in this app: Denoising, Changing model
- **Guidance.** Users should first know how to use the software first.
  - Example used in this app: Help page. "Wake Up" page (intended to guide users to get familiar with the App)



##### 1.1.2 Integration with OpenGL and Qt5 

The submitted code is modified based on the given code. However, large modifications were done.

The UI framework adopted in this assignment is the integration of `PyQt5` and `PyOpenGL`. `PyOpenGL` serves as the main UI library and `PyQt5` is used to provide the context for OpenGL and listening to events. 

To achieve this, the class `ZwGraphicsContainer` inherits `QGLWidget` and override many virtual functions including `paintGL`, `initializeGL` and `resizeGL`. And two events handlers (`mouseMoveEvent` and `mousePressEvent`) are also overriden to allow the widget to listen to mouse events. And to control the framerate, a `QTimer` is added to limit the max frame rate.

```Python
# graphics_utils.py
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
```

Besides, in Qt5 framework, a main widget should be defined to serve as the main window. Thus, class `InteractionUI` which inherits class `QWidget` to serve as the main window.

```Python
class InteractionUI(QWidget):
    arg_msaa = 16
    max_fps = 60

    def __init__(self, width=590 * 1.5, height=950):
        super().__init__()
        ZwLogger().log(ZwLogger.ROLE_GUIQT, ZwLogger.LV_INFO, "Initializing Window Widget")
        # MSAA Anti-aliasing
        self.msaa = QGLFormat()
        self.msaa.setSamples(InteractionUI.arg_msaa)

        # Init ASR
        SpeechRecognitionUtil().env_noise_record('./noise.wav')

        # QT Configuration
        self.custom_width = int(width)
        self.custom_height = int(height)
        self.ogl_widget = ZwGraphicsContainer(self,
                                              format_s=self.msaa,
                                              frame_rate=InteractionUI.max_fps,
                                              app=ZwUIHCILab01(),
                                              s_width=int(width),
                                              s_height=int(height))
        self.setFixedSize(width, height)
        self.init_ui()

    def init_ui(self):
        ZwLogger().log(ZwLogger.ROLE_GUIQT, ZwLogger.LV_INFO, "Initializing UI")
        self.resize(self.custom_width, self.custom_height)
        self.move(400, 200)
        self.setWindowTitle("Hello")

        # OGL Widget
        self.ogl_widget.move(0, 0)
        self.ogl_widget.resize(self.custom_width, self.custom_height)
        self.show()
```

##### 1.1.3 Encapsulate Shapes 

To render stuffs on the screen, drawing calls should be explicitly included in the codes. However, although OpenGL provides more freedom than Qt5 Components, all shapes should be defined by ourself. To perserve the maintainability of the code, the drawing calls are encapsulated in the abstract class which defines the shared behaviours of all shape rendering procedure.

The class `ZwUIAbstractShape` encapsulate all OpenGL rendering calls and provide an methods to create other shapes by inheriting the class itself.

```Python
# zwui_shapes.py
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
```

In most design practices, rounded rectangle enjoys high popularity. Thus, in this assignment, The rounded rectangle is implemented.

```Python
# zwui_shapes.py
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
```

Implemented shapes are listed below: 

| Class Name           | Function         | File:Line            |
| -------------------- | ---------------- | -------------------- |
| ZwUIText             | Plain text       | zwui_shapes.py : 72  |
| ZwUIRectangle        | Rectangle        | zwui_shapes.py : 84  |
| ZwUITriangle         | Triangle         | zwui_shapes.py : 101 |
| ZwUICircle           | Circle           | zwui_shapes.py : 116 |
| ZwUIArc              | Arc              | zwui_shapes.py : 137 |
| ZwUIRoundedRectangle | RoundedRectangle | zwui_shapes.py : 159 |
| ZwUICompoundShape    | Shape container  | zwui_shapes.py : 213 |
| ZwUIFunctionalCurve  | Curve y=f(x)     | zwui_shapes.py : 226 |



##### 1.1.4 Encapsulate Components and Controls

A component or a control is a set of shapes, which are integrated together to function consistently. Buttons and labels are typical components. Besides, in order to display transition or animation, keyframe mechanism is added to the components to improve the visual expression. Like the shape, a vitrual class `ZwUIAbstractControl` is designed for all components to reduce the code redundancy.

Scene is the special component.

```Python
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
```

Implemented components are listed below: 

| Class                     | Function                                                     | File : Line            |
| ------------------------- | ------------------------------------------------------------ | ---------------------- |
| ZwUIScene                 | Scene                                                        | zwui_controls.py : 75  |
| ZwUICustomStaticControl   | Custom shape container                                       | zwui_controls.py : 119 |
| ZwUIButtonControl         | Button <br/>(with rounded rectangle border)<br/>(Available transition: fade_in, fade_out) | zwui_controls.py : 131 |
| ZwUILabelControl          | Label <br/>(Available transition: rising, descending, typing) | zwui_controls.py : 226 |
| ZwUINestedLabelControl    | Label with Rounded Rectangle Background<br/>(Available transition: typing) | zwui_controls.py : 281 |
| ZwUIStripedWaveControl    | Voice power indicator                                        | zwui_controls.py : 359 |
| ZwUISwitchMaskControl     | Mask used for scene switching                                | zwui_controls.py : 413 |
| ZwUIMicrophoneIconControl | Microphone icon                                              | zwui_controls.py : 456 |
| ZwUITimer                 | Timer                                                        | zwui_controls.py : 487 |
| ZwUIMomoBotIconControl    | Robot icon                                                   | zwui_controls.py : 514 |
| ZwUIAniMomoBotIconControl | Robot icon with transition support<br/>(Available transition: fade_in) | zwui_controls.py : 632 |



#### 1.2 Transition and Bezier Curve

A Bézier curve is a parametric curve used in computer graphics and related fields. A set of discrete "control points" defines a smooth, continuous curve by means of a formula. 

A transition with Bezier curve can display the interface with elasticity and dynamic traits.

![image-20220429151128246](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429151128246.png)

A cubic Bezier curve is the Bezier curve that has four control points. For simplicity, point $P_0$ is the origin and $P_3$ is (1,1). It can be described in the following form.
$$
F(x,y): P_0(1-t)^3+3P_1t(1-t)+3P_2t^2(1-t)+P_3t^3=0
$$

```Python
# zwui_animation.py
def standard_cubic_bezier(x1, y1, x2, y2):
    return lambda t: 3 * np.array([x1, y1]) * t * (1 - t) * (1 - t) + 3 * np.array([x2, y2]) * t * t * (
        1 - t) + np.array([1, 1]) * t * t * t
```

To transform the $F(x,y)$ into the form of $y=f(x)$, solving the cubic equation is required.

```Python
# zwui_animation.py
def standard_cubic_bezier_time(x1, y1, x2, y2):
    def cubic_root(x):
        if x >= 0:
            return x ** (1. / 3.)
        else:
            return -(-x) ** (1. / 3.)

        def solver(x):
            a = (1 + 3 * x1 - 3 * x2)
            a2 = a * a
            b = (3 * x2 - 6 * x1)
            b2 = b * b
            c = 3 * x1
            p = (3. * a * c - b2) / (9. * a2)
            q = (-9. * a * b * c - 27. * a2 * x + 2. * b * b2) / (54. * a * a2)
            w = math.sqrt(q * q + p * p * p)
            v = -0.5 + math.sqrt(3) * 0.5j
            v2 = v * v
            f = b / 3. / a
            s = cubic_root(-q + w)
            t = cubic_root(-q - w)
            ex = 1000
            ret = [s + t - f,
                   v * s + v2 * t * 1j - f,
                   v2 * s + v * t * 1j - f]
            for i in ret:
                if (isinstance(i, float) or isinstance(i, int)) and (0.0 <= i <= 1.0):
                    return round(i * ex) / ex
                if isinstance(i, complex):
                    if math.fabs(i.imag) < 1e-5 and (0.0 <= i.real <= 1.0):
                        return round(i.real * ex) / ex
                    raise Exception("No solution", " X=" + str(x), "t=" + str(t), "SimCoef" + str([1, p, q]),
                                    "Coef=" + str([a, b, c, -x]), ret, )

                    def solver_x(x):
                        t = solver(x)
                        eq = ZwUITransition.standard_cubic_bezier(x1, y1, x2, y2)
                        return eq(t)

                    return lambda x: solver_x(x)
```

Following items are transitions used in this app

```Python
# app.py
# Transition Schemes
t_bezier = ZwUITransition.standard_cubic_bezier_time(.76, .36, .24, .56)
t_bezier_beta = ZwUITransition.standard_cubic_bezier_time(.78, .17, .22, .85)
t_bezier_alpha = ZwUITransition.standard_cubic_bezier_time(.88, .28, .26, .91)
t_linear = lambda x: (x, x)
```



#### 1.3 Recognition & Multithreading & Instruction Mapping

To render the interface and listen to the recorder in parallel, multithreading is the best solution. When the application starts, a new thread will be created to do recognition works.

```Python
# app.py
class ZwUIHCILab01EventThread(threading.Thread):
    def __init__(self, parent: object = None, event_callback_handler: callable = None):
        super(ZwUIHCILab01EventThread, self).__init__()
        self.callback = event_callback_handler
        self.parent = parent

    def run(self):
        ZwLogger().log(ZwLogger.ROLE_APP, ZwLogger.LV_INFO, "Speech recognition thread starts")
        responder = Responder()
        responder.waiting_and_respond(self.callback, True, self.parent)
```

the class `Responder` is the junction for the ASR kernel and the UI front end. It calls the function provided by the ASR kernel and send the message to the UI module via the call back function provided in the argument.

```Python
class Responder:
    def __init__(self):
        self.text_analyst = TextUtil()
        self.application_map = { ... }

    def waiting_and_respond(self,
                            callback_function: callable = None,
                            is_member_function: bool = False,
                            parent_node: object = None):
        async def callback_wrapper(**kwargs):
            ZwLogger().log(ZwLogger.ROLE_ALRSP, ZwLogger.LV_INFO, "Initiating the callback procedure"
                                                                  " to the event handler")
            await asyncio.sleep(1)
            if callback_function is not None:
                callback_function(**kwargs)

        sr = SpeechRecognitionUtil()
        tx = TextUtil()
        while True:
            rec = sr.interpret_from_microphone(None)
            action = None
            for key in self.application_map.keys():
                if tx.similarity(key, rec) > 0.8:
                    action = self.application_map[key]
                    break
            asyncio.run(callback_wrapper(initiator="responder", action=action, result=rec))
```

The core function mentioned in the code above is `interpret_from_microphone`. It involves following steps

- First, record an audio and save the audio clip (via `record_audio` function)
  - First, a wave stream is opened and basic parameters and thresholds are set
  - Second, FFT is performed to calculate the power of the audio clip. If the power is lager than the threshold, the record procedure will be started.
  - When the power is lower than the threshold for about a second, the record procedure will be terminated. 
  - Last, the stream is closed and denosing processing is performed to the audio file.
- Second, load the saved audio clip and transform it into the spectrogram (for DeepSpeech). After the preprocessing, the data is fed into the model for inference.

```python
    # algorithm_utils.py
    def record_audio(self, wave_out_path, callback_function=None):
        async def callback_wrapper(**kwargs):
            await asyncio.sleep(1)
            if callback_function is not None:
                callback_function(**kwargs)

        chunk = 1024
        audio_format = pyaudio.paInt16
        channels = 1
        rate = 16000
        p = pyaudio.PyAudio()
        stream = p.open(format=audio_format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk)
        wf = wave.open(wave_out_path, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(audio_format))
        wf.setframerate(rate)
        occupied = False
        stopflag = 0
        stopflag2 = 0
        threshold = 7000
        ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Start to listening the Recorder")
        while True:
            data = stream.read(chunk)
            rt_data = np.frombuffer(data, np.dtype('<i2'))
            fft_temp_data = fftpack.fft(rt_data, rt_data.size, overwrite_x=True)
            fft_data = np.abs(fft_temp_data)[0:fft_temp_data.size // 2 + 1]
            SpeechRecognitionUtil.wave_ratio = sum(fft_data) // len(fft_data)
            if sum(fft_data) // len(fft_data) > threshold:
                stopflag += 1
                if not occupied:
                    ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Start recording. Power gained via FFT:" +
                                   str(sum(fft_data) // len(fft_data)))
                    occupied = True
                    stopflag = 0
                    stopflag2 = 0
            else:
                stopflag2 += 1
                if not occupied:
                    continue
            ons = rate / chunk * 2
            if stopflag2 + stopflag > ons:
                if stopflag2 > ons * 0.8:
                    ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, "Record completed")
                    break
                else:
                    stopflag2 = 0
                    stopflag = 0

            wf.writeframes(data)
            # ZwLogger().log(ZwLogger.ROLE_ALRC, ZwLogger.LV_INFO, data)
        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        rate, data = wavfile.read(wave_out_path)
        _, noise_data = wavfile.read("./noise.wav")
        reduced_noise = nr.reduce_noise(y=data, y_noise=noise_data, sr=rate)
        wavfile.write(wave_out_path, rate, reduced_noise)
```

And

```Python
# algorithm_utils.py
def interpret_from_file(self, path):
    if SpeechRecognitionUtil.engine == "ds":
        fin = wave.open(path, 'rb')
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        return SpeechRecognitionUtil.model.stt(audio)
    else:
        file = sr.AudioFile(path)
        with file as f:
            audio = self.recognizer.record(f)
        return self.recognizer.recognize_sphinx(audio)
```

After receiving the result from the function  `interpret_from_microphone`, the Responder will compare the result with keys in the instruction mapping dictionary `self.application_map` （Appendix 3.3). If the similarity is higher than 80%, the message will return to the UI module.



#### 1.4 Voice Indicator

This design is the placebo-effect design, which is intended to notice user that their voice can be sensed by the software. And this will reduce the tense for users.

![image-20220429143705262](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429143705262.png)

The indicator will display the realtime voice power using FFT algorithm.

```Python
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
```

The power will be updated every frame update

```Python
# app.py 
def on_frame_update(self, **kwargs):
    hw = (min(0.05 * max(math.log(SpeechRecognitionUtil.wave_ratio + 1) - 0.2, 0), 0.5) + 0.05)
    self.get_scene("main_scene") \
    .get_control("wave") \
    .set_height(hw)

    self.get_scene("welcome_scene") \
    .get_control("start_guide_mcb") \
    .set_height(hw)
```



#### 1.5 Functions Implemented

In this assignment, following functions are implemented. 

##### 1.5.1 Open Notepad

The first one is open the notepad. Users can say `open notepad` to let the application launch the notepad (`notepad.exe`)

To ensure the generalizability. There are other alternatives including `notepad`, `write notes`, `write something`, `take notes`. 

The launch procedure is based on the library `win32api`(or `pywin32`). The code below shows the launch procedure.

```Python
# algorithm_utils.py
class ShellUtil:
    @staticmethod
    def execute(path: str):
        ZwLogger().log(ZwLogger.ROLE_ALWIN, ZwLogger.LV_INFO, "Executing "+str(path))
        win32api.ShellExecute(0, 'open', path, '', '', 1)
```

When the instruction is recognized, a tuple `(shell, notepad.exe)` will be passed to the handler. And UI module modifies the elements to be rendered and executes the given application.

```python
# app.py
elif action[0] == "shell":
    self.get_scene("response_scene").get_control("tip_2").reload(
        overridden_text="I've found the application!")
    self.get_scene("response_scene").get_control("rec_2a").reload(
        overridden_text=action[1])
    self.get_scene("response_scene").get_control("rec_2b").reload(
        overridden_text="Execute " + self.action_list["applications"][action[1]])
    ShellUtil.execute(self.action_list["applications"][action[1]])
```

![image-20220429150607981](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429150607981.png)

##### 1.5.2 Play Music

When you say `play music`, the application will launch the default music player and play the music `music.mp3`.

Equivalent instructions include `music`, `play songs`, `listen to music`

The procedure resembles what has already been mentioned in the `open notepad` section

![image-20220429151006502](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429151006502.png)

##### 1.5.3 Open the Calculator

When you say `open calculator`, the application will launch the default calculator.

The procedure resembles what has already been mentioned in the `open notepad` section

![image-20220429150436072](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429150436072.png)

##### 1.5.4 Open Movie Websites

By saying `watch a movie`, you can  command the application to open a movie website for you. This step is done by `webbrowser` in-built package.

```Python
# app.py
if action[0] == "web_browse" and action[1] == "movie":
    self.get_scene("response_scene").get_control("tip_2").reload(
        overridden_text="I'll open a movie website!")

    key_chosen = random.choice(list(self.action_list["movie"].keys()))
    webbrowser.open(self.action_list["movie"][key_chosen], new=0, autoraise=True)
    self.get_scene("response_scene").get_control("rec_2a").reload(
        overridden_text=key_chosen)
    self.get_scene("response_scene").get_control("rec_2b").reload(
        overridden_text=self.action_list["movie"][key_chosen])
```

![image-20220429150128084](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429150128084.png)

Alternative websites (All items are arranged in random order)

| Name          | Website                         |
| ------------- | ------------------------------- |
| IMDB          | https://www.imdb.com/           |
| iQIYI         | https://www.iqiyi.com/lib/      |
| Tencent Video | https://v.qq.com/               |
| MTime         | http://www.mtime.com/           |
| Bilibili      | https://www.bilibili.com/movie/ |
| NetFlex       | https://www.netflix.com/        |



##### 1.5.5 Throw a dice

If you say `roll a dice`, `throw the dice` or `play dice`, the application will generate a random integer larger than zero and smaller than 7.

```Python
elif action[0] == "event":
    if action[1] == "dice":
        self.get_scene("response_scene").get_control("tip_2").reload(
            overridden_text="Is that you want?")
        self.get_scene("response_scene").get_control("rec_2a").reload(
            overridden_text="Dice Rolling")
        self.get_scene("response_scene").get_control("rec_2b").reload(
            overridden_text="Result is " + str(random.randint(1, 6)))
```

![image-20220429150707246](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429150707246.png)

#### 1.6 Miscellaneous Improvements

##### 1.6.1 Multiscale Anti-Aliasing & Primitive Smoothing

Anti-aliasing is a process of removing the aliasing effect from computer objects. It reduces jagged edges that occur on different edges graphical objects or curved objects. This often improves user's visual feeling by removing "sharp" elements on the user interface.

In the assignment multi-scale anti-aliasing(MSAA) is adopted as the anti-aliasing technique. It's done via `PyQt5` framework

```Python
# main.py
def __init__(self, width=590 * 1.5, height=950):
    super().__init__()
    ZwLogger().log(ZwLogger.ROLE_GUIQT, ZwLogger.LV_INFO, "Initializing Window Widget")
    # MSAA Anti-aliasing
    self.msaa = QGLFormat()
    self.msaa.setSamples(InteractionUI.arg_msaa)
     self.ogl_widget = ZwGraphicsContainer(self,
                                              format_s=self.msaa,...)
    
# graphics_utils.py
class ZwGraphicsContainer(QGLWidget):
    def __init__(self, parent, format_s, frame_rate=60, app=None, s_width=None, s_height=None):
        super().__init__(format_s, parent)
```

Other smoothing options are also configured.

```Python
# graphics_utils.py
ogl.glEnable(ogl.GL_POINT_SMOOTH)
ogl.glEnable(ogl.GL_LINE_SMOOTH)
ogl.glEnable(ogl.GL_MULTISAMPLE)
ogl.glEnable(ogl.GL_POLYGON_SMOOTH)
ogl.glHint(ogl.GL_POLYGON_SMOOTH_HINT, ogl.GL_NICEST)
ogl.glHint(ogl.GL_LINE_SMOOTH_HINT, ogl.GL_NICEST)
ogl.glHint(ogl.GL_POINT_SMOOTH_HINT, ogl.GL_NICEST)
```

Here's the effect of MSAA

| No Anti-aliasing (1x)                                        | 8x MSAA                                                      |
| ------------------------------------------------------------ | ------------------------------------------------------------ |
| ![image-20220429143426005](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429143426005.png) | ![image-20220429143531101](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429143531101.png) |

#### 1.7 Screenshots & Visual Effects

##### 1.7.1 Start Page

Start page shows welcome information and guide user to use the App by saying "Hello". This helps them know how the App works.

![image-20220429144051126](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429144051126.png)

![image-20220429144247566](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429144247566.png)

##### 1.7.2 Help Page

This page shows help information.

![image-20220429144334624](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429144334624.png)

##### 1.7.3 Main Page

This is the main page of the App. There will be three random tips.

![image-20220429144746452](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429144746452.png)

##### 1.7.4 Success Page

If a command is successfully recognized by the App, this page will show.

![image-20220429144926551](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429144926551.png)

##### 1.7.5 Failure Page

If a command cannot be recognized by the App, this page will show.

![image-20220429145150958](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220429145150958.png)

### 2. Recognition Performance Improvements

This part includes the model selection and noise reduction, which contributes to the improvement of recognition accuracy.

#### 2.1 Model Selection

In this assignment, two models are surveyed. The first is the baseline model Sphinx, which is mentioned in the assignment instruction. The second one is DeepSpeech, which is based on neural network.

To determine wheter the deep learning model outperforms the traditional ones, an experiment is carried to investigate the Word Error Rates(WER) of two models under two different situations.

The first situation is the common situation. In this situation, voices of random sentences are given for two models. In the second situationk, voices of short instructions (like `open the notepad`) are given for two models. And to ensure the experiment exhibits the generalizability, four differents text-to-speech(TTS) methods are adopted. These methods include `Google Translate`, `Baidu Translate`, `Bing Translate` and `pyttsx3`.

The result shows DeepSpeech outperforms Sphinx in both situations.

![image-20220428233341918](C:\Users\huang\AppData\Roaming\Typora\typora-user-images\image-20220428233341918.png)

Thus, DeepSpeech is adopted as the default recognition engine. However, user can still use Sphinx via command arguments.

```python
def interpret_from_file(self, path):
    # DeepSpeech
    if SpeechRecognitionUtil.engine == "ds":
        fin = wave.open(path, 'rb')
        audio = np.frombuffer(fin.readframes(fin.getnframes()), np.int16)
        return SpeechRecognitionUtil.model.stt(audio)
    # Sphinx
    else:
        file = sr.AudioFile(path)
        with file as f:
            audio = self.recognizer.record(f)
            return self.recognizer.recognize_sphinx(audio)
```

#### 2.2 Noise Reducing

When application starts, a short video clip will be recorded. The clip contains the environment noise. And every time a new clip is recorded, this noise clip will be used to noise reducing using spectral gating algorithm

### 3. Appendix

#### 3.1 Accuracy of ASR Models (Random Sentences)

WER is the abbreviation of `Word Error Rate`. This means the lower WER it is, the better the model it should be.

| Ground  Truth                                                | TTS Engine       | Sphinx                                                       | DeepSpeech                                                   | Sphinx WER | DeepSpeech WER |
| ------------------------------------------------------------ | ---------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------- | -------------- |
| parsley sage rosemary and time                               | pyttsx3          | parsley sage rosemary and time                               | parsley say rose marianne time                               | 0.00%      | 23.33%         |
| should old acquaintance be forgot                            | pyttsx3          | should auld acquaintance be forgot                           | soot old the quaintance pefore got                           | 6.06%      | 36.36%         |
| The quick brown fox jumps over a lazy  dog                   | pyttsx3          | the quake brown fox down solvay lazy dog                     | the quick bron fox jumps over ar lazy dog                    | 36.59%     | 7.32%          |
| We have provided a pretrained model                          | pyttsx3          | we have provided a crackling model                           | we have provided a redoring model                            | 20.00%     | 17.14%         |
| it aims  at developing Practical Algorithms for General Image Restoration. | pyttsx3          | it aims at developing practical  algorithms      for generally made to estimation | hey mstap developing practical  algarithms      for a general image resteration | 13.70%     | 16.44%         |
| I want a bottle of water                                     | pyttsx3          | i want a bottle of water                                     | i wan tay bodle of water                                     | 0.00%      | 20.83%         |
| Vulkan  is constantly evolving to bring new      capabilities and improvements to the  API. | pyttsx3          | full kenny's constantly evolving  to bring your      capabilities and improvements to the  a. p. i | fookcal is constantly volving to  bring new     capabilities and improvements to the api | 18.07%     | 8.43%          |
| Ambient  light is light that is diffused equally      throughout an environment. | pyttsx3          | ambient light is like that is  the fewest equally      throughout an environment | anbiant light his like that  instifused equally      through out ind environment | 15.07%     | 17.81%         |
| In  computer graphics, ray tracing is a      rendering technique for generating  an      image by tracing the path of light  as pixels      in an image plane and simulating  the      effects of its encounters with  virtual objects. | pyttsx3          | a computer graphics retracing is  a man during      technique for generating an image by  tracing      the path of light as pixel seen any  makes plain      and simulating the effect some  facing      converse with virtual objects | in conputer graphics ratwacing  is a rendering tachnique for a generating and image by twicing the path of  light aspicks olds in the limit playing an simbiulating the effects of its in  counters with virtual objects | 16.50%     | 16.50%         |
| Logistic  regression is basically a supervised classification algorithm. | pyttsx3          | logistically question is  basically a supervised classification algorithm | lotistic regression the ins  basically a      supervised classification algarithem | 12.68%     | 12.68%         |
| A Lie  group is a smooth manifold obeying the group properties and that satisfies  the additional condition that the group operations are differentiable. | pyttsx3          | they like what they say smallest  manifold the pain the cruel properties and that satisfies that additional  condition that the growth operations are different answerable | a ligrol bis as moovh manifold  abeying the groel properties and their satisfies the additional condition  that the creup operations are differentiable | 30.26%     | 11.84%         |
| The game  features an open-world environment and an action-based battle system using  elemental magic and character-switching. | pyttsx3          | the game features an open world  environment and an action based that old system using elemental magic and  character sweetie | the game features and open  whereold environment and an action baced bat o system using elemental magic  and character switching | 12.10%     | 10.48%         |
| Pudding  is a type of food that can be either a dessert or a savoury dish that is part  of the main meal. | pyttsx3          | pudding is a type of flood that  can be either a dessert or a savory days that is part of the main meal | putting his eight hype food that  can be either aiddesern or a sabory adish that is part of the main meal | 5.83%      | 19.42%         |
| Greenland  is an island nation located between the Arctic and Atlantic oceans | pyttsx3          | we monday said island nation  located between the arctic and atlantic oceans | green lyndisan island nation  located between the arctic andad lantic oceans | 15.79%     | 9.21%          |
| Generative  Adversarial Networks are a powerful class of neural networks that are used  for unsupervised learning | pyttsx3          | the animated adversarial  networks are a powerful class of neural networks that are used for  unsupervised learning | generated adversary ol networks  are a powerful class of nero networks that are used for unsupervised to  learning | 8.11%      | 10.81%         |
| Attention  is a powerful mechanism developed to enhance the performance of the  Encoder-Decoder architecture on neural network-based machine translation  tasks | pyttsx3          | attention is a powerful  mechanism developed to enhanced the performance of the hinkle dirty claudette  architecture on the road network based machine translation tasks | attention they ay powerful  mechanism developed to inhance the performance of the impoder decolder  architecture arm neuro network based machine twenslation tasks | 15.29%     | 12.10%         |
| A  radical Infected organization, Reunion rallies around the cause of Infected  nationalism, rejecting racial and national identities. | pyttsx3          | a medical infected organization  the union bally's about the cause of the infected nationalism rejecting  racial and national identities | a radical infected organization  reunion rallies around the coust of infected nationalism rhich acting racial  end national identities | 14.29%     | 9.77%          |
| The  Panda bear is a large mammal native to central China. These bears are also  known as giant pandas, or simply pandas. | pyttsx3          | the p. and that there is a large  mammal native to central china these days are also milne s. giant pandas are  simply pandas | the pande perious tay large memo  native to central china these pairs are also known nas giant pandes or simply  pandes | 21.01%     | 17.65%         |
| The  Trump administration has accused TikTok of transferring user data to servers  in China and has banned the app. | pyttsx3          | the twelve administration has  accused take till got transforming user david was ever seen china and has  banned the gap | the twele pud ministration has a  cused tictoke of twensfurin user data to server s in china and has band the  ap | 25.66%     | 17.70%         |
| Back  face culling determines whether a polygon of a graphical object is visible. | pyttsx3          | that face colleen determines  whether a colleague on ave graphical object is visible | back face colling determincs  weather a polygon of a graphical objectives visible | 22.50%     | 10.00%         |
| Geometric  camera calibration, also referred to as camera resectioning, estimates the  parameters of a lens and image sensor of an image or video camera. | pyttsx3          | geometric camera calibration  also referred to as camera reception the estimates that the managers of  aliens and he makes sense or an image or video camera | teo metric camera calibration  also referred to ask hamme rebi sectiony astimates the prrameters of alence  and iage sensor of animite or video camera | 18.54%     | 16.56%         |
| Food  security is the measure of the availability of food and individuals ability  to access it. | pyttsx3          | full of securities that measure  of the availability of food and individuals ability to access | ford security is the measure of  the availability of food ale indhividuals ability to access it | 12.63%     | 6.32%          |
| Pineapple  is a large tropical fruit with a spiky, tough skin and sweet insides. | google_translate | find out or so large tropical  fruit with the spiky tasking in sweet insights | pinapple is a large tropical  fruit with a spikin tuff skin an sweden sides | 33.33%     | 14.10%         |
| Rosemary  is one of those wonderful herbs that makes a beautiful ornamental plant as  well as a versatile culinary seasoning. | google_translate | rosemary is one of those  wonderful words that makes the unocal ornamental claim as well as and pursued  alcala neary seasoning | rosmarry is one of those  wonderful erbs that makes op beautiful ornomental plan as well as a vers ital  colinary seasoning | 22.95%     | 9.84%          |
| Lily of  the valley has slender rootstock and two large oblong leaves with prominent  veins. | google_translate | lily of the valley has slender  root stock into large oblong agrees with common in chains | lil of the valley has slender  rootes stock and two large oblong leaves with prominent veins | 22.22%     | 5.56%          |
| Sodium  chloride is an essential nutrient and is used in healthcare to help prevent  patients from becoming dehydrated | google_translate | sodium chloride is an essential  nutrient didn't use to tell her to help her that he since from becoming  dehydrated | sodium cloride is in essential  nutrient ind is used in health care to help prevent patience from becoming  dehydrated | 23.28%     | 5.17%          |
| Rasterization  can be generally defined as a process of converting or mapping fragments into  the projection plane | google_translate | roster as a stinking be  generally teeth are hindus are processor chamber engler mapping fragments  into the rejection plane | reste ization cin be generally  defined as a process of converting or mapping fragments into the projection | 34.82%     | 4.46%          |
| In  information theory, the entropy of a random variable is the average level of  information, surprise, or uncertainty inherent to the variable's possible  outcomes. | google_translate | in information here eat the  entropy upper random variable the average landlord increasing surprise or  uncertainty in hearing did variables possible outcomes | information theory the entripe  of a random variable is the aperage level of information surprise or  uncertainty inherent to the variables possible outcomes | 23.16%     | 5.59%          |
| Red  foxes have long snouts and red fur across the face, back, sides, and tail. | google_translate | ready boxes have long's now  regret for cross nice back sites in taro | boxes have long snouts and red  fur across the face back sides and tail | 38.46%     | 11.54%         |
| A shader  is a computer program that calculates the appropriate levels of light,  darkness, and color during the rendering of a scene, a process known as  shading | baidu_translate  | washington aren't you forgot my  only the all early there are these are monitoring and seen on guard are  changing | shager insicomputer program that  calcinly the appropriate levels of life darkness and colore during the  rentering of the see at process non or shiting | 69.81%     | 20.75%         |
| Structure  from motion is a photogrammetric range imaging technique for estimating  three-dimensional structures from two-dimensional image sequences that may be  coupled with local motion signals. | baidu_translate  | start your commercial need a  doctor not real and lamenting me for me and treatment shirts shoes aren't you  do not sure he makes the greek it got me all the akbar burglar komercni ya | struct ure from toshin if of the  tolk remetric range inegingtectne for at meting treat imentional structures  from sudamantional imex sequenie that may be happled with local motion  ficnals | 71.50%     | 25.39%         |
| A  B-spline or basis spline is a spline function that has minimal support with  respect to a given degree, smoothness, and domain partition | baidu_translate  | at least aren't working on who's  on car should not listening in worker and the stunt men and our main parting  shot | pind or bathis pinis is blin  calsian that has minimal support wat especti icas in degree moveness and o  main qartition | 68.61%     | 32.12%         |
| Level  of detail refers to the complexity of a model representation. It can be  decreased as the model moves away from the viewer or according to other  metrics such as object importance, viewpoint-relative speed or position. | baidu_translate  | let her on let her know grace to  eat 'em are and he shot the king and alm her week on you weren't work lincoln  got an auction got stuck on the importance you want ardently or cutting shot | elevtle of detail referse to the  comprexity he model or presotation egh  can be decreaced to se model move herway from the viewer or ccording to other  metric suc as object importance point relative feed or posention | 69.37%     | 18.02%         |
| A  deputy-involved shooting at a Target store in Kissimmee, Florida, Wednesday  evening left at least one person dead and three others injured, according to  reports. | baidu_translate  | and what we got she on the ring  any law bring you blame not workers and get on yet there's inching poured  into the loot | theputy involved shooting attit  harket stor if theny florida when the evening left at least one person dead  entreer gers indurn thaccording to repours | 67.48%     | 26.99%         |
| The  Belt and Road Initiative, formerly known as One Belt One Road or OBOR for  short, is a global infrastructure development strategy adopted by the Chinese  government in 2013 to invest in nearly 70 countries and international  organizations. | bing_translate   | the dow inroad in a mid dial in  earnest in learning our one bell one good r. o. b. or curse words in the  global interest or you did not answer and c. got it i it's tiny peppermint  indeed that they're hoops and that in your eat and eat and the engine asked  organizations | the belt and rod in it the belt  and rod inationtive por mali nel as one belt one road or obio or fo shore is  a global infrastructure development strategy adopted by the chinese  government intwo thousand thirteen to invest i nearly seventy countries and international  organizations | 67.08%     | 29.17%         |
| Some  results are removed in response to a notice of local law requirement. For  more information, please see here. | bing_translate   | some results are not in response  to an arrogant and local law requirements are laurin mace and meet each year | some results are removed in  response to a notice of local law requirements for more information please  see here | 40.71%     | 2.65%          |
| The 996  working hour system is a work schedule practiced by some companies in the  Peoples Republic of China. | bing_translate   | the nine hundred ninety six  working artist and igor it all is that some companies in it he calls  republican synar | the nisi working hour system is  a work skhedule practiced by some companies in the peoples republic of  china | 60.19%     | 5.56%          |

#### 3.2 Accuracy of ASR Models (Instructions Used in App)

| Ground  Truth    | TTS Engine       | Sphinx          | DeepSpeech        | Sphinx WER | DeepSpeech WER |
| ---------------- | ---------------- | --------------- | ----------------- | ---------- | -------------- |
| Open the notepad | baidu_translate  | and a           | from the not dad  | 81.25%     | 37.50%         |
| Open the notepad | bing_translate   | logan a note pa | open the note pad | 43.75%     | 6.25%          |
| Open the notepad | google_translate | opening up pat  | pen the note padh | 56.25%     | 18.75%         |
| Hello            | baidu_translate  | hello           | elo               | 0%         | 60%            |
| Hello            | bing_translate   | and leno        | hello             | 100%       | 0%             |
| Hello            | google_translate | hello           | hello             | 0%         | 0%             |
| Play music       | baidu_translate  | protein called  | p mefil           | 100%       | 60%            |
| Play music       | bing_translate   | claim he's dead | play music        | 100%       | 0%             |
| Play music       | google_translate | Play music      | Play music        | 0%         | 0%             |
| Watch a movie    | baidu_translate  | or to me        | in mincy          | 76.92%     | 84.62%         |
| Watch a movie    | bing_translate   | why sanity      | watch a movie     | 76.92%     | 0%             |
| Watch a movie    | google_translate | watch a movie   | watch a movie     | 0%         | 0%             |

#### 3.3 Mapping Dictionary

```Python
self.application_map = {
    "open notepad": ["shell", "Notepad"],
    "notepad": ["shell", "Notepad"],
    "write notes": ["shell", "Notepad"],
    "write something": ["shell", "Notepad"],
    "take notes": ["shell", "Notepad"],
    "play music": ["shell", "Music Player"],
    "music": ["shell", "Music Player"],
    "play songs": ["shell", "Music Player"],
    "listen to music": ["shell", "Music Player"],
    "open calculator": ["shell", "Calculator"],
    "watch a movie": ["web_browse", "movie"],
    "movie": ["web_browse", "movie"],
    "watch movies": ["web_browse", "movie"],
    "a movie": ["web_browse", "movie"],
    "roll a dice": ["event", "dice"],
    "play dice": ["event", "dice"],
    "roll the dice": ["event", "dice"],
    "throw the dice": ["event", "dice"],
    "roll dice": ["event", "dice"]
}
```

#### 3.4 Icon Drawing

```Python
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

```

