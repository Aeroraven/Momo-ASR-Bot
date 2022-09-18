import datetime
import random
import random as rd
import threading
import webbrowser

from algorithm.algorithm_utils import *
from user_interface.zwui_application import *


class ZwUIHCILab01EventThread(threading.Thread):
    def __init__(self, parent: object = None, event_callback_handler: callable = None):
        super(ZwUIHCILab01EventThread, self).__init__()
        self.callback = event_callback_handler
        self.parent = parent

    def run(self):
        ZwLogger().log(ZwLogger.ROLE_APP, ZwLogger.LV_INFO, "Speech recognition thread starts")
        responder = Responder()
        responder.waiting_and_respond(self.callback, True, self.parent)


class ZwUIHCILab01(ZwUIApplication):
    def __init__(self):
        self.example_cnt = 3
        self.mode = "starting"
        self.example_list = [
            "Open the calculator",
            "Play music",
            "Watch a movie",
            "Open the notepad",
            "Throw a dice"
        ]
        self.apologize_unclear = [
            "I didn't hear clearly.",
            "Can you repeat again?",
            "I was just absent-minded.",
            "I was just daydreaming.",
            "I didn't understand well.",
        ]
        self.action_list = {
            "movie": {
                "Bilibili": r"https://www.bilibili.com/movie/",
                "IMDB": r"https://www.imdb.com/",
                "iQIYI": r"https://www.iqiyi.com/lib/",
                "Tencent Video": r"https://v.qq.com/",
                "NetFlex": r"https://www.netflix.com/",
                "MTime": r"http://www.mtime.com/",
            },
            "applications": {
                "Calculator": "calc.exe",
                "Notepad": "notepad.exe",
                "Painter": "mspaint.exe",
                "Music Player": "music.mp3",
            }
        }
        self.event_thread = ZwUIHCILab01EventThread(self, self.event_handle)
        self.recorder_stop = False
        self.mutex = threading.Lock()
        super(ZwUIHCILab01, self).__init__()

    def gl_clear_func(self, **kwargs):
        gl.glClearColor(0, 0, 0, 1)

    def action_execution(self, action):
        if action[0] == "web_browse" and action[1] == "movie":
            self.get_scene("response_scene").get_control("tip_2").reload(
                overridden_text="I'll open a movie website!")

            key_chosen = random.choice(list(self.action_list["movie"].keys()))
            webbrowser.open(self.action_list["movie"][key_chosen], new=0, autoraise=True)
            self.get_scene("response_scene").get_control("rec_2a").reload(
                overridden_text=key_chosen)
            self.get_scene("response_scene").get_control("rec_2b").reload(
                overridden_text=self.action_list["movie"][key_chosen])
        elif action[0] == "shell":
            self.get_scene("response_scene").get_control("tip_2").reload(
                overridden_text="I've found the application!")
            self.get_scene("response_scene").get_control("rec_2a").reload(
                overridden_text=action[1])
            self.get_scene("response_scene").get_control("rec_2b").reload(
                overridden_text="Execute " + self.action_list["applications"][action[1]])
            ShellUtil.execute(self.action_list["applications"][action[1]])
        elif action[0] == "event":
            if action[1] == "dice":
                self.get_scene("response_scene").get_control("tip_2").reload(
                    overridden_text="Is that you want?")
                self.get_scene("response_scene").get_control("rec_2a").reload(
                    overridden_text="Dice Rolling")
                self.get_scene("response_scene").get_control("rec_2b").reload(
                    overridden_text="Result is " + str(random.randint(1, 6)))
        pass

    def on_frame_update(self, **kwargs):
        hw = (min(0.05 * max(math.log(SpeechRecognitionUtil.wave_ratio + 1) - 0.2, 0), 0.5) + 0.05)
        self.get_scene("main_scene") \
            .get_control("wave") \
            .set_height(hw)

        self.get_scene("welcome_scene") \
            .get_control("start_guide_mcb") \
            .set_height(hw)

    def event_handle(self, **kwargs):
        ZwLogger().log(ZwLogger.ROLE_APP, ZwLogger.LV_INFO, "Event handler is triggered. KwArgs=" + str(kwargs))

        # Speech Recognition Events
        if "initiator" in kwargs and kwargs['initiator'] == "responder":
            # Receive responses from ASR util.
            if self.mode != "starting":
                self.mutex.acquire()
                if self.recorder_stop:
                    self.mutex.release()
                    return
                self.recorder_stop = True
                self.mutex.release()
                self.get_scene("main_scene").get_control("switch_hover").paused = False
                if kwargs['action'] is not None:
                    self.get_scene("response_scene").get_control("tip_2a").reload(
                        overridden_text="Sure")
                    self.action_execution(kwargs['action'])
                    self.get_scene("response_scene").get_control("rec_2a").hidden = False
                    self.get_scene("response_scene").get_control("rec_2b").hidden = False
                else:
                    self.get_scene("response_scene").get_control("tip_2a").reload(
                        overridden_text="Sorry")
                    self.get_scene("response_scene").get_control("tip_2").reload(
                        overridden_text=random.choice(self.apologize_unclear))
                    self.get_scene("response_scene").get_control("rec_2a").hidden = True
                    self.get_scene("response_scene").get_control("rec_2b").hidden = True
                self.get_scene("response_scene").get_control("tip_2").switch_to_keyframe(0)
                self.get_scene("response_scene").get_control("tip_2").paused = True
                self.get_scene("response_scene").get_control("rec_2a").switch_to_keyframe(0)
                self.get_scene("response_scene").get_control("rec_2a").paused = True
                self.get_scene("response_scene").get_control("rec_2b").switch_to_keyframe(0)
                self.get_scene("response_scene").get_control("rec_2b").paused = True
            else:
                self.mutex.acquire()
                if self.recorder_stop:
                    self.mutex.release()
                    return
                self.recorder_stop = True
                self.mutex.release()
                if kwargs['result'] is not None and \
                        (kwargs['result'].find('hello') != -1 or
                         kwargs['result'].find('elo') != -1 or
                         kwargs['result'].find('loh') != -1):
                    self.get_scene("welcome_scene").get_control("help_btn").hidden = True
                    self.get_scene("welcome_scene").get_control("problem_label").hidden = True
                    self.get_scene("welcome_scene").get_control("start_guide").hidden = True
                    self.get_scene("welcome_scene").get_control("out_ani_1").hidden = False
                    self.get_scene("welcome_scene").get_control("out_ani_1").paused = False
                    self.get_scene("welcome_scene").get_control("out_ani_2").hidden = False
                    self.get_scene("welcome_scene").get_control("out_ani_2").paused = False
                    self.get_scene("welcome_scene").get_control("out_ani_3").hidden = False
                    self.get_scene("welcome_scene").get_control("out_ani_3").paused = False
                else:
                    self.mutex.acquire()
                    self.recorder_stop = False
                    self.mutex.release()

        # UI Events
        if "initiator" in kwargs and kwargs['initiator'] == "zw_gui":
            if kwargs['control_name'] == "switch_hover" and kwargs['event'] == ZwUIConstant.EV_PLAY_ENDED:
                self.set_active_scene("response_scene")
                self.get_scene("response_scene").get_control("switch_hover_2").hidden = False
                self.get_scene("response_scene").get_control("switch_hover_2").paused = False
                self.get_scene("response_scene").get_control("switch_hover_2").switch_to_keyframe(0)
                self.get_scene("response_scene").get_control("tip_2").paused = False
                self.get_scene("response_scene").get_control("rec_2a").paused = False
                self.get_scene("response_scene").get_control("rec_2b").paused = False
                self.get_scene("main_scene").get_control("switch_hover").paused = True
                self.get_scene("main_scene").get_control("switch_hover").switch_to_keyframe(0)
                self.get_scene("response_scene").get_control("timer_2a").activated = True

            if kwargs['control_name'] == "switch_hover_v_2" and kwargs['event'] == ZwUIConstant.EV_PLAY_ENDED:
                self.mutex.acquire()
                self.recorder_stop = False
                self.mutex.release()
                self.set_active_scene("main_scene")
                self.get_scene("main_scene").get_control("switch_hover_v").hidden = False
                self.get_scene("main_scene").get_control("switch_hover_v").paused = False
                self.get_scene("main_scene").get_control("switch_hover_v").switch_to_keyframe(0)
                self.get_scene("response_scene").get_control("switch_hover_v_2").paused = True
                self.get_scene("response_scene").get_control("switch_hover_v_2").switch_to_keyframe(0)

            if kwargs['control_name'] == "timer_2a" and kwargs['event'] == ZwUIConstant.EV_TIMER_TIMEOUT:
                self.get_scene("response_scene").get_control("switch_hover_v_2").paused = False
                self.get_scene("response_scene").get_control("switch_hover_v_2").switch_to_keyframe(0)

            if kwargs['control_name'] == 'st_greet_label' and kwargs['event'] == ZwUIConstant.EV_PLAY_ENDED:
                self.get_scene("welcome_scene").get_control("st_greet_label_timer").activated = True

            if kwargs['control_name'] == 'st_greet_label_timer' and kwargs['event'] == ZwUIConstant.EV_TIMER_TIMEOUT:
                self.get_scene("welcome_scene").get_control("st_greet_label").hidden = True
                self.get_scene("welcome_scene").get_control("st_greet_label_after").hidden = False
                self.get_scene("welcome_scene").get_control("st_greet_label_after").paused = False

            if kwargs['control_name'] == 'st_greet_label_after' and kwargs['event'] == ZwUIConstant.EV_PLAY_ENDED:
                self.get_scene("welcome_scene").get_control("start_guide").hidden = False
                self.get_scene("welcome_scene").get_control("start_guide").paused = False

            if kwargs['control_name'] == 'start_guide' and kwargs['event'] == ZwUIConstant.EV_PLAY_ENDED:
                self.get_scene("welcome_scene").get_control("start_guide_mc").hidden = False
                self.get_scene("welcome_scene").get_control("start_guide_mcb").hidden = False
                self.get_scene("welcome_scene").get_control("problem_label").hidden = False
                self.get_scene("welcome_scene").get_control("problem_label").paused = False
                self.get_scene("welcome_scene").get_control("help_btn").hidden = False
                self.get_scene("welcome_scene").get_control("help_btn").paused = False
                # Debug
                # self.get_scene("welcome_scene").get_control("out_ani_timer").activated = True

            if kwargs['control_name'] == 'help_return' and kwargs['event'] == ZwUIConstant.EV_CLICK:
                self.set_active_scene("welcome_scene")

            if kwargs['control_name'] == 'help_btn' and kwargs['event'] == ZwUIConstant.EV_CLICK:
                self.set_active_scene("help_scene")

            if kwargs['control_name'] == 'out_ani_timer' and kwargs['event'] == ZwUIConstant.EV_TIMER_TIMEOUT:
                self.get_scene("welcome_scene").get_control("help_btn").hidden = True
                self.get_scene("welcome_scene").get_control("problem_label").hidden = True
                self.get_scene("welcome_scene").get_control("start_guide").hidden = True
                self.get_scene("welcome_scene").get_control("out_ani_1").hidden = False
                self.get_scene("welcome_scene").get_control("out_ani_1").paused = False
                self.get_scene("welcome_scene").get_control("out_ani_2").hidden = False
                self.get_scene("welcome_scene").get_control("out_ani_2").paused = False
                self.get_scene("welcome_scene").get_control("out_ani_3").hidden = False
                self.get_scene("welcome_scene").get_control("out_ani_3").paused = False

            if kwargs['control_name'] == 'out_ani_3' and kwargs['event'] == ZwUIConstant.EV_PLAY_ENDED:
                self.set_active_scene("main_scene")
                self.mode = "main"
                self.mutex.acquire()
                self.recorder_stop = False
                self.mutex.release()

    def initialize(self, **kwargs):
        # Application UI Starts Here

        # Initiate Event Handler
        self.event_thread.start()

        # Color Schemes
        c_black = ZwUIHelper.get_opengl_rgba_vector(0, 0, 0)
        c_white = ZwUIHelper.get_opengl_rgba_vector(1, 1, 1)
        c_debug = ZwUIHelper.get_opengl_rgba_vector(1, 0, 0)

        # Animation Speed
        base_animate_rate = 60

        # Transition Schemes
        t_bezier = ZwUITransition.standard_cubic_bezier_time(.76, .36, .24, .56)
        t_bezier_beta = ZwUITransition.standard_cubic_bezier_time(.78, .17, .22, .85)
        t_bezier_alpha = ZwUITransition.standard_cubic_bezier_time(.88, .28, .26, .91)
        t_linear = lambda x: (x, x)

        # ==== Scene 1 - Main Scene ====
        scene1 = ZwUIScene()
        control1 = ZwUIAniMomoBotIconControl(-2, 2, fore=c_black, back=c_white, animation_duration=base_animate_rate,
                                             animation_transition=t_linear)
        control2 = ZwUILabelControl(-3.6, -0, "What can I do for you?",
                                    c_white, 0.004, 2, animated='typing', animation_duration=base_animate_rate)
        control3 = ZwUINestedLabelControl(-4.5, -0.5, "Hello! What can I do for you?",
                                          c_white, c_black, 1.25, 9, 0.004, 2, animated='typing',
                                          animation_duration=base_animate_rate * 1.5, animation_transition=t_bezier)
        control5 = ZwUIMicrophoneIconControl(-4, -7, c_white, c_black, 0.8)
        control6 = ZwUIStripedWaveControl(-2.8, -6.5, 12, 0.4, 0.2, c_white)
        control7 = ZwUISwitchMaskControl(c_white, animated="default", animation_duration=base_animate_rate,
                                         animation_transition=t_bezier, delayed_frames=0,
                                         ignore_out=True)
        control8 = ZwUISwitchMaskControl(c_white, animated="default", animation_duration=base_animate_rate,
                                         animation_transition=t_bezier, delayed_frames=0,
                                         ignore_in=True, vertical=True)
        control8.hidden = True
        control1.paused = False

        # Attach Event Handler
        control7.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)
        control8.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)

        # Examples
        kw_list = rd.sample(self.example_list, self.example_cnt)
        for i in range(len(kw_list)):
            control_w = ZwUINestedLabelControl(-4, -0.5 - (i + 1) * 1.5, kw_list[i],
                                               c_black, c_white, 1.0, 8, 0.003, 1,
                                               animated='typing', animation_duration=base_animate_rate,
                                               animation_transition=t_bezier,
                                               delayed_frames=base_animate_rate * (i + 1), text_offset_y=0.08,
                                               text_offset_x=0.25)
            scene1.add_control("example_" + str(i), control_w)
        scene1.add_control("name", control1)
        scene1.add_control("greeting", control2)
        scene1.add_control("micro", control5)
        scene1.add_control("wave", control6)
        scene1.add_control("switch_hover", control7)
        scene1.add_control("switch_hover_v", control8)
        self.add_scene("main_scene", scene1)

        # ==== Scene 2 - Unknown Command ====
        scene2 = ZwUIScene()
        control2_1 = ZwUISwitchMaskControl(c_white, animated="default", animation_duration=base_animate_rate,
                                           animation_transition=t_bezier, delayed_frames=0,
                                           ignore_in=True)
        control2_2 = ZwUIMomoBotIconControl(-2, 2, fore=c_black, back=c_white)
        control2_2.switch_to_animation_list("normal")
        control2_3 = ZwUILabelControl(-4, -1, "Can you repeat again?",
                                      c_white, 0.004, 1, animated='typing', animation_duration=base_animate_rate * 1.5)

        control2_4 = ZwUISwitchMaskControl(c_white, animated="default", animation_duration=base_animate_rate,
                                           animation_transition=t_bezier, delayed_frames=0,
                                           ignore_out=True, vertical=True)
        control2_5 = ZwUITimer(600)
        control2_6 = ZwUILabelControl(-4, -0, "Sorry",
                                      c_white, 0.004, 2, animated='typing', animation_duration=base_animate_rate * 0.5)

        control2_7 = ZwUINestedLabelControl(-4, -0.5 - 2 * 1.5, "None",
                                            c_black, c_white, 1.0, 8, 0.003, 2,
                                            animated='typing', animation_duration=base_animate_rate,
                                            animation_transition=t_bezier,
                                            delayed_frames=base_animate_rate * (0 + 1), text_offset_y=0.08,
                                            text_offset_x=0.25)
        control2_8 = ZwUINestedLabelControl(-4, -0.5 - 3 * 1.5, "None",
                                            c_black, c_white, 1.0, 8, 0.003, 1,
                                            animated='typing', animation_duration=base_animate_rate,
                                            animation_transition=t_bezier,
                                            delayed_frames=base_animate_rate * (0 + 1), text_offset_y=0.08,
                                            text_offset_x=0.25)

        # Attach Event Handler
        control2_4.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)
        control2_5.add_handler(ZwUIConstant.EV_TIMER_TIMEOUT, self.event_handle)

        scene2.add_control("switch_hover_2", control2_1)
        scene2.add_control("bot_2", control2_2)
        scene2.add_control("tip_2", control2_3)
        scene2.add_control("switch_hover_v_2", control2_4)
        scene2.add_control("timer_2a", control2_5)
        scene2.add_control("tip_2a", control2_6)
        scene2.add_control("rec_2a", control2_7)
        scene2.add_control("rec_2b", control2_8)
        self.add_scene("response_scene", scene2)

        # ==== Scene 3 - Shell Exec ====
        scene3 = ZwUIScene()
        control3_1 = ZwUISwitchMaskControl(c_white, animated="default", animation_duration=base_animate_rate,
                                           animation_transition=t_bezier, delayed_frames=0,
                                           ignore_in=True)
        control3_2 = ZwUIMomoBotIconControl(-2, 2, fore=c_black, back=c_white)
        scene3.add_control("swtich_hover_3", control3_1)
        scene3.add_control("bot_3", control3_2)
        self.add_scene("shell_open_scene", scene3)

        # === Scene 4 - Startup ====
        scene4 = ZwUIScene()
        hour = int(datetime.datetime.now().strftime("%H"))
        if 6 <= hour < 12:
            control4_1 = ZwUILabelControl(-2, 0, "Good Morning!", c_white, 0.004,
                                          animated="rising", rising_dy=1, animation_duration=base_animate_rate,
                                          animation_transition=t_bezier_beta)
        elif 12 <= hour <= 18:
            control4_1 = ZwUILabelControl(-2, 0, "Good Afternoon!", c_white, 0.004,
                                          animated="rising", rising_dy=1, animation_duration=base_animate_rate,
                                          animation_transition=t_bezier_beta)
        else:
            control4_1 = ZwUILabelControl(-2, 0, "Good Evening!", c_white, 0.004,
                                          animated="rising", rising_dy=1, animation_duration=base_animate_rate,
                                          animation_transition=t_bezier_beta)
        shape4_2_1 = ZwUIRectangle(-5, -0.3, 10, 1, c_black)
        control4_2 = ZwUICustomStaticControl(shape1=shape4_2_1)
        if 6 <= hour < 12:
            control4_3 = ZwUILabelControl(-2, 1, "Good Morning!", c_white, 0.004,
                                          animated="descending", desc_dy=1, animation_duration=base_animate_rate,
                                          animation_transition=t_bezier_alpha
                                          )
        elif 12 <= hour <= 18:
            control4_3 = ZwUILabelControl(-2, 1, "Good Afternoon!", c_white, 0.004,
                                          animated="descending", desc_dy=1, animation_duration=base_animate_rate,
                                          animation_transition=t_bezier_alpha
                                          )
        else:
            control4_3 = ZwUILabelControl(-2, 1, "Good Evening!", c_white, 0.004,
                                          animated="descending", desc_dy=1, animation_duration=base_animate_rate,
                                          animation_transition=t_bezier_alpha
                                          )
        control4_5 = ZwUILabelControl(-3.4, 0, "Say Hello to wake me up!", c_white, 0.004,
                                      animated="rising", rising_dy=1, animation_duration=base_animate_rate,
                                      animation_transition=t_bezier_beta)
        control4_6 = ZwUIMicrophoneIconControl(-4, -7, c_white, c_black, 0.8)
        control4_7 = ZwUIStripedWaveControl(-2.8, -6.5, 12, 0.4, 0.2, c_white)
        control4_8 = ZwUILabelControl(-2.6, 9, "Having problems? Click the button below.", c_white, 0.002,
                                      animated="descending", desc_dy=1.2, animation_duration=base_animate_rate,
                                      animation_transition=t_bezier_alpha
                                      )
        control4_9 = ZwUIButtonControl(-1.4, 6.8, 2.6, 0.7, "Help & Support", c_white, c_black,
                                       0.002, animated="fade_in", animation_duration=base_animate_rate,
                                       animation_transition=t_linear)

        control4_10 = ZwUIButtonControl(-1.4, 6.8, 2.6, 0.7, "Help & Support", c_white, c_black,
                                        0.002, animated="fade_out", animation_duration=base_animate_rate,
                                        animation_transition=t_linear)
        control4_11 = ZwUILabelControl(-2.6, 9 - 1.2, "Having problems? Click the button below.", c_white, 0.002,
                                       animated="rising", rising_dy=1.2, animation_duration=base_animate_rate,
                                       animation_transition=t_bezier_alpha
                                       )
        control4_12 = ZwUILabelControl(-3.4, 1, "Say Hello to wake me up!", c_white, 0.004,
                                       animated="descending", desc_dy=1, animation_duration=base_animate_rate,
                                       animation_transition=t_bezier_beta)

        control4_13 = ZwUITimer(100)

        control4_3.hidden = True
        control4_3.paused = True
        control4_4 = ZwUITimer(base_animate_rate)
        control4_4.activated = False
        control4_5.hidden = True
        control4_5.paused = True
        control4_6.hidden = True
        control4_7.hidden = True
        control4_8.hidden = True
        control4_8.paused = True
        control4_9.hidden = True
        control4_9.paused = True

        control4_10.hidden = True
        control4_10.paused = True
        control4_11.hidden = True
        control4_11.paused = True
        control4_12.hidden = True
        control4_12.paused = True
        control4_13.activated = False

        # Attach Event Handler
        control4_1.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)
        control4_3.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)
        control4_4.add_handler(ZwUIConstant.EV_TIMER_TIMEOUT, self.event_handle)
        control4_5.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)
        control4_9.add_handler(ZwUIConstant.EV_CLICK, self.event_handle)
        control4_12.add_handler(ZwUIConstant.EV_PLAY_ENDED, self.event_handle)

        # Debug Timer
        control4_13.add_handler(ZwUIConstant.EV_TIMER_TIMEOUT, self.event_handle)

        # Register Controls
        scene4.add_control("st_greet_label_ani_mask", control4_2)
        scene4.add_control("st_greet_label", control4_1)
        scene4.add_control("start_guide", control4_5)
        scene4.add_control("start_guide_mc", control4_6)
        scene4.add_control("start_guide_mcb", control4_7)
        scene4.add_control("problem_label", control4_8)
        scene4.add_control("st_greet_label_after", control4_3)
        scene4.add_control("st_greet_label_timer", control4_4)
        scene4.add_control("help_btn", control4_9)

        scene4.add_control("out_ani_1", control4_10)
        scene4.add_control("out_ani_2", control4_11)
        scene4.add_control("out_ani_3", control4_12)
        scene4.add_control("out_ani_timer", control4_13)

        self.add_scene("welcome_scene", scene4)

        # === Scene 5 - Help ====
        scene5 = ZwUIScene()
        control5_1 = ZwUILabelControl(-4, 7, "Help", c_white, 0.004, 3)
        control5_2 = ZwUILabelControl(-4, 6, "Hi! You can give me some VOICE instructions ", c_white, 0.0023, 1)
        control5_3 = ZwUILabelControl(-4, 5.5, "to let me do what you want.", c_white, 0.0023, 1)
        control5_4 = ZwUILabelControl(-4, 5, "Therefore, please make sure that your microphone", c_white, 0.0023, 1)
        control5_5 = ZwUILabelControl(-4, 4.5, "works normally.", c_white, 0.0023, 1)
        control5_6 = ZwUILabelControl(-4, 4.0, "Clear pronunciation and a noiseless place can", c_white, 0.0023, 1)
        control5_7 = ZwUILabelControl(-4, 3.5, "help me understand your words easier!", c_white, 0.0023, 1)

        control5_8 = ZwUILabelControl(-4, 2, "Some Instruction Examples", c_white, 0.003, 2)
        control5_9 = ZwUILabelControl(-4, 1, "Open Notepad or default text editor", c_white, 0.0023, 1)
        control5_10 = ZwUINestedLabelControl(-4, -0.1, "Open notepad", c_black, c_white, 0.8, 8, 0.0023, 1)
        control5_11 = ZwUILabelControl(-4, -1, "Play a random music via default player ", c_white, 0.0023, 1)
        control5_12 = ZwUINestedLabelControl(-4, -2.1, "Play music", c_black, c_white, 0.8, 8, 0.0023, 1)

        control5_13 = ZwUILabelControl(-4, -3, "Open a random online video / streaming website", c_white, 0.0023, 1)
        control5_14 = ZwUINestedLabelControl(-4, -4.1, "Watch a movie", c_black, c_white, 0.8, 8, 0.0023, 1)
        control5_15 = ZwUILabelControl(-4, -5, "There are more functions like opening the calculator", c_white,
                                       0.0023, 1)
        control5_16 = ZwUILabelControl(-4, -5.5, "CHECK THE DOCUMENT to view ALL FUNCTIONS", c_white, 0.0023, 1)
        control5_17 = ZwUIButtonControl(-1.4, -7.2, 2.6, 0.7, "<< Go Back", c_white, c_black,
                                        0.002, animated="fade_in", animation_duration=base_animate_rate,
                                        animation_transition=t_linear)
        # Event Handler
        control5_17.add_handler(ZwUIConstant.EV_CLICK, self.event_handle)

        # Register Control/Components
        scene5.add_control("help_title", control5_1)
        scene5.add_control("help_ins1", control5_2)
        scene5.add_control("help_ins2", control5_3)
        scene5.add_control("help_ins3", control5_4)
        scene5.add_control("help_ins4", control5_5)
        scene5.add_control("help_ins5", control5_6)
        scene5.add_control("help_ins6", control5_7)
        scene5.add_control("help_ins7", control5_8)

        scene5.add_control("help_inst_1", control5_9)
        scene5.add_control("help_inst_1a", control5_10)

        scene5.add_control("help_inst_2", control5_11)
        scene5.add_control("help_inst_2a", control5_12)

        scene5.add_control("help_inst_3", control5_13)
        scene5.add_control("help_inst_3a", control5_14)

        scene5.add_control("help_ins8", control5_15)
        scene5.add_control("help_ins9", control5_16)

        scene5.add_control("help_return", control5_17)

        self.add_scene("help_scene", scene5)

        # Set the Default Scene
        # self.mode = "main"
        self.set_active_scene("welcome_scene")
