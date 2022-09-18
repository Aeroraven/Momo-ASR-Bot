import datetime as date
import threading


class ZwLogger(object):
    _instance = None
    ROLE_GUI = "ZwGUI/OpenGL"
    ROLE_GUILA = "ZwGUI/Layout"
    ROLE_GUIEV = "ZwGUI/Event"
    ROLE_GUIQT = "ZwGUI/PyQt5"
    ROLE_ALSR = "ZwAlgo/ASR_Sphinx"
    ROLE_ALRC = "ZwAlgo/Recorder"
    ROLE_ALPT = "ZwAlgo/Torch"
    ROLE_ALOR = "ZwAlgo/ORT"
    ROLE_ALWIN = "ZwAlgo/WinAPI"
    ROLE_ALTX = "ZwAlgo/TextUtil"
    ROLE_ALRSP = "ZwAlgo/Responder"
    ROLE_APP = "HCILab01"
    ROLE_CORE = "Core"
    LV_INFO = "Info"
    LV_WARN = "Warn"
    LV_ERROR = "Error"
    mutex = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = object.__new__(cls)
        return cls._instance

    def __init__(self):
        pass

    def log(self, initiator, level, info):
        ZwLogger.mutex.acquire()
        print(date.datetime.now().strftime('%F %T'), "[", initiator, "]", "[", level, "]:", info)
        ZwLogger.mutex.release()
