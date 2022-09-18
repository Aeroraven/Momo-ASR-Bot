import cgitb
import sys
import argparse

from PyQt5.QtOpenGL import QGLFormat
from PyQt5.QtWidgets import QApplication, QWidget

from algorithm.algorithm_utils import SpeechRecognitionUtil
from app import ZwUIHCILab01
from logger.zw_logger import ZwLogger
from user_interface.graphics_utils import ZwGraphicsContainer


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


# Arg Parse
parser = argparse.ArgumentParser(description="HCILab01 1950641, Tongji Univ SSE")
parser.add_argument("--msaa", help="Sub-samples for multi-scale anti-aliasing (MSAA). (default=16)", default=16)
parser.add_argument("--fps", help="Max frame rate for animations and transitions. (default=60)", default=60)
parser.add_argument("--debug", help="If the value equals to 1, the app will run in Debug mode (default=0)", default=0)
parser.add_argument("--model", help="Model of speech recognition.['sphinx','deepspeech'] (default=deepspeech)",
                    default='deepspeech')

if __name__ == '__main__':
    ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_INFO, "===================================================")
    ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_INFO, "Tongji SSE Human Computer Interaction Assignment 1")
    ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_INFO, "Speech Rocognition App")
    ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_INFO, "1950641 Huang Zhiwen")
    ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_INFO, "===================================================")
    ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_INFO, "Application is launching, please wait...")
    arg = parser.parse_args()
    InteractionUI.arg_msaa = int(arg.msaa)
    InteractionUI.max_fps = int(arg.fps)
    if int(arg.debug) == 1:
        cgitb.enable(format='text')
    if arg.model == "deepspeech":
        SpeechRecognitionUtil.engine = "ds"
    elif arg.model == "sphinx":
        SpeechRecognitionUtil.engine = "sp"
    else:
        ZwLogger().log(ZwLogger.ROLE_CORE, ZwLogger.LV_ERROR, "Model not supported")
        raise Exception("App error")
    app = QApplication(sys.argv)
    w = InteractionUI(int(490 * 1.0), int(800 * 1.0))
    sys.exit(app.exec_())
