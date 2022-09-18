import math

import numpy as np


class ZwUIKeyFrame:
    def __init__(self):
        self.shape = []
        self.command = []

    def add_shape(self, x):
        self.shape.append(x)

    def add_command(self, x):
        self.command.append(x)

    def render(self, **kwargs):
        for i in range(len(self.shape)):
            self.shape[i].render(**kwargs)


class ZwUIClips:
    def __init__(self):
        self.clips = []
        self.selected_clips = 0

    def add_frame(self, keyframe):
        self.clips.append(keyframe)

    def pop_frame(self):
        self.clips.pop()

    def switch_to_frame(self, idx):
        self.selected_clips = idx

    def render(self, **kwargs):
        self.clips[self.selected_clips].render(**kwargs)


class ZwUITransition:
    @staticmethod
    def color_trans(transition_func, color_src, color_dst, t):
        def mix(src, dst, p):
            return (dst - src) * p + src

        share = transition_func(t)
        return [mix(color_src[i], color_dst[i], share) for i in range(4)]

    @staticmethod
    def standard_cubic_bezier(x1, y1, x2, y2):
        return lambda t: 3 * np.array([x1, y1]) * t * (1 - t) * (1 - t) + 3 * np.array([x2, y2]) * t * t * (
                1 - t) + np.array([1, 1]) * t * t * t

    @staticmethod
    def standard_cubic_bezier_sing_coord(x1, x2):
        return lambda t: 3 * x1 * t * (1 - t) * (1 - t) + 3 * x2 * t * t * (1 - t) + t * t * t

    @staticmethod
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
