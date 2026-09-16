import random

import arcade

from src import constants


class DeathEffect:
    """Séquence de mort : flash / glitch → noir → dialogues → retour."""

    def __init__(self):
        self.active = False
        self.phase = None
        self.timer = 0.0
        self.spec = {}
        self.just_void = False
        self.just_returned = False
        self.cover = 0.0
        self.flash = 0.0
        self.glitch = 0.0
        self.extra_hold = 0.0
        self._rects = []

    @property
    def blocking(self):
        return self.active

    @property
    def hiding_world(self):
        return self.active and self.phase in ("void", "return") and self.cover > 0.55

    def start(self, spec, extra_hold=0.0):
        self.spec = spec or {}
        self.active = True
        self.phase = "flash"
        self.timer = 0.0
        self.just_void = False
        self.just_returned = False
        self.cover = 0.0
        self.flash = 1.0
        self.glitch = 1.0 if self.spec.get("effect") == "green_glitch" else 0.0
        self.extra_hold = extra_hold
        self._roll_rects()

    def notify_void_done(self):
        if self.phase == "void":
            self.phase = "return"
            self.timer = 0.0

    def update(self, delta_time):
        self.just_void = False
        self.just_returned = False
        if not self.active:
            return

        self.timer += delta_time
        effect = self.spec.get("effect", "white_flash")

        if self.phase == "flash":
            duration = 0.45
            t = min(1.0, self.timer / duration)
            if effect == "green_glitch":
                self.flash = 0.0
                self.glitch = 1.0
                self.cover = t * 0.35
                if int(self.timer * 18) != int((self.timer - delta_time) * 18):
                    self._roll_rects()
            else:
                self.flash = 1.0 - t * 0.25
                self.cover = t * 0.2
            if self.timer >= duration:
                self.phase = "fade"
                self.timer = 0.0

        elif self.phase == "fade":
            duration = 0.55
            t = min(1.0, self.timer / duration)
            self.flash = max(0.0, 0.75 * (1.0 - t))
            self.glitch = max(0.0, (1.0 - t) * (1.0 if effect == "green_glitch" else 0.0))
            self.cover = 0.2 + 0.8 * t
            if self.timer >= duration:
                self.phase = "void"
                self.timer = 0.0
                self.flash = 0.0
                self.cover = 1.0
                self.just_void = True

        elif self.phase == "void":
            self.cover = 1.0
            self.flash = 0.0
            self.glitch = 0.08 if effect == "green_glitch" else 0.0

        elif self.phase == "return":
            duration = 0.7 + self.extra_hold
            t = min(1.0, self.timer / duration)
            self.cover = 1.0 - t
            residual = 1.0 - min(1.0, self.timer / max(0.35, self.extra_hold + 0.35))
            self.glitch = residual * (0.85 if effect == "green_glitch" else 0.15)
            if int(self.timer * 14) != int((self.timer - delta_time) * 14):
                self._roll_rects()
            if self.timer >= duration:
                self.active = False
                self.phase = None
                self.cover = 0.0
                self.glitch = 0.0
                self.just_returned = True

    def draw(self):
        if not self.active and self.cover <= 0:
            return
        if self.flash > 0.02:
            arcade.draw_lrbt_rectangle_filled(
                0,
                constants.SCREEN_WIDTH,
                0,
                constants.SCREEN_HEIGHT,
                (255, 255, 255, int(255 * min(1.0, self.flash))),
            )
        if self.cover > 0.02:
            arcade.draw_lrbt_rectangle_filled(
                0,
                constants.SCREEN_WIDTH,
                0,
                constants.SCREEN_HEIGHT,
                (6, 4, 8, int(255 * min(1.0, self.cover))),
            )
        if self.glitch > 0.04:
            alpha = int(220 * self.glitch)
            for left, bottom, width, height in self._rects:
                arcade.draw_lbwh_rectangle_filled(
                    left, bottom, width, height, (48, 255, 92, alpha)
                )

    def _roll_rects(self):
        self._rects = []
        for _ in range(28):
            width = random.randint(8, 90)
            height = random.randint(4, 22)
            left = random.randint(0, max(1, constants.SCREEN_WIDTH - width))
            bottom = random.randint(0, max(1, constants.SCREEN_HEIGHT - height))
            self._rects.append((left, bottom, width, height))
