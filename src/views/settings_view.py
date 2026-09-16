import arcade

from src import constants
from src.camera import WorldCamera
from src.ui.key_names import key_name
from src.ui.menu import MenuButton
from src.ui.scenes import load_scene_texture


KEY_ACTIONS = [
    ("KEY_LEFT", "Aller à gauche"),
    ("KEY_RIGHT", "Aller à droite"),
    ("KEY_INTERACT", "Interagir"),
    ("KEY_CONFIRM", "Valider"),
    ("KEY_SKIP", "Passer le dialogue"),
]


class VolumeSlider:
    def __init__(self, x, y, width, value, label, on_change, scale=1.0):
        self.x = x
        self.y = y
        self.width = width
        self.height = 12 * scale
        self.value = value
        self.label = label
        self.on_change = on_change

        self.label_text = arcade.Text(
            label, x - width / 2, y + 28 * scale, (232, 214, 170),
            int(24 * scale), font_name=constants.FONT_BODY, anchor_x="left", anchor_y="center"
        )

        self.value_text = arcade.Text(
            self._value_text(), x + width / 2 + 20 * scale, y, (190, 178, 158),
            int(20 * scale), font_name=constants.FONT_BODY, anchor_x="left", anchor_y="center"
        )

        self.dragging = False

    def _value_text(self):
        return f"{round(self.value * 100)}%"

    def _update_value(self, mouse_x):
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        self.value = max(0.0, min(1.0, (mouse_x - left) / self.width))
        self.value_text.text = self._value_text()
        self.on_change(self.value)

    def contains(self, x, y):
        left = self.x - self.width / 2
        right = self.x + self.width / 2
        return left <= x <= right and self.y - 25 <= y <= self.y + 25

    def on_mouse_press(self, x, y):
        if self.contains(x, y):
            self.dragging = True
            self._update_value(x)
            return True
        return False

    def on_mouse_release(self):
        self.dragging = False

    def on_mouse_motion(self, x, y):
        if self.dragging:
            self._update_value(x)

    def draw(self):
        left = self.x - self.width / 2

        self.label_text.draw()
        self.value_text.draw()

        arcade.draw_lbwh_rectangle_filled(
            left, self.y - self.height / 2, self.width, self.height, (55, 50, 58)
        )

        arcade.draw_lbwh_rectangle_filled(
            left, self.y - self.height / 2, self.width * self.value, self.height, (180, 165, 130)
        )

        knob_x = left + self.width * self.value

        arcade.draw_circle_filled(knob_x, self.y, 11, (232, 214, 170))
        arcade.draw_circle_outline(knob_x, self.y, 11, arcade.color.WHITE, 2)


class SettingsView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()

        self.world_camera = WorldCamera(self.window)
        self.previous_view = previous_view
        self.scale = constants.SCREEN_HEIGHT / constants.BASE_HEIGHT
        s = self.scale

        self.background = load_scene_texture(constants.SCENE_MENU)

        self.title = arcade.Text(
            "Paramètres", constants.SCREEN_WIDTH / 2, 940 * s, (232, 214, 170),
            int(60 * s), font_name=constants.FONT_TITLE, bold=True, anchor_x="center"
        )

        self.waiting_action = None
        self.buttons = []
        self.key_labels = []
        self.key_buttons = {}

        # Touche
        row_y = 790

        for action, label in KEY_ACTIONS:
            self.key_labels.append(
                arcade.Text(
                    label, 530 * s, row_y * s, (232, 214, 170), int(26 * s),
                    font_name=constants.FONT_BODY, anchor_y="center"
                )
            )

            button = MenuButton(
                "", 1190 * s, row_y * s, 400 * s, 64 * s,
                lambda a=action: self.start_waiting(a), int(24 * s)
            )

            self.buttons.append(button)
            self.key_buttons[action] = button
            row_y -= 85

        # Volume
        audio = self.window.audio

        self.music_slider = VolumeSlider(
            x=960 * s, y=270 * s, width=500 * s, value=audio.music_volume,
            label="Musique", on_change=audio.set_music_volume, scale=s
        )

        self.sfx_slider = VolumeSlider(
            x=960 * s, y=170 * s, width=500 * s, value=audio.sfx_volume,
            label="Sons", on_change=self._set_sfx_volume, scale=s
        )

        # Message
        self.status = arcade.Text(
            "", constants.SCREEN_WIDTH / 2, 100 * s, (190, 178, 158), int(20 * s),
            font_name=constants.FONT_BODY, anchor_x="center", anchor_y="center"
        )

        # Retour
        self.buttons.append(
            MenuButton(
                "Retour", constants.SCREEN_WIDTH / 2, 55 * s, 320 * s, 64 * s,
                self.on_back, int(26 * s)
            )
        )

        self.refresh_key_buttons()

    # Audio
    def _set_sfx_volume(self, value):
        self.window.audio.sfx_volume = max(0.0, min(1.0, value))


    def on_show_view(self):
        self.world_camera.fit_to_window()

    def on_draw(self):
        self.world_camera.begin_frame()
        s = self.scale

        arcade.draw_texture_rect(
            self.background, arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            pixelated=True
        )

        arcade.draw_lbwh_rectangle_filled(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (8, 6, 10, 170)
        )

        panel_w, panel_h = 1000 * s, 990 * s
        panel_left = (constants.SCREEN_WIDTH - panel_w) / 2
        panel_bottom = 45 * s

        arcade.draw_lbwh_rectangle_filled(
            panel_left, panel_bottom, panel_w, panel_h, (18, 14, 20, 235)
        )

        arcade.draw_lbwh_rectangle_outline(
            panel_left, panel_bottom, panel_w, panel_h, (214, 200, 168), 2
        )

        self.title.draw()

        for label in self.key_labels:
            label.draw()

        self.music_slider.draw()
        self.sfx_slider.draw()
        self.status.draw()

        for button in self.buttons:
            if self.waiting_action and button is self.key_buttons.get(self.waiting_action):
                button.hovered = True
            button.draw()

    def refresh_key_buttons(self):
        for action, button in self.key_buttons.items():
            if action == self.waiting_action:
                button.label.text = "Nouvelle touche…"
            else:
                button.label.text = key_name(getattr(constants, action))

    def start_waiting(self, action):
        self.waiting_action = action
        self.status.text = "Appuyez sur la nouvelle touche (Échap pour annuler)"
        self.refresh_key_buttons()

    def assign_key(self, key):
        action = self.waiting_action

        if key != arcade.key.ESCAPE:
            old_key = getattr(constants, action)

            for other, _ in KEY_ACTIONS:
                if other != action and getattr(constants, other) == key:
                    setattr(constants, other, old_key)

            setattr(constants, action, key)

        self.waiting_action = None
        self.status.text = ""
        self.refresh_key_buttons()

    def on_key_press(self, key, modifiers):
        if self.waiting_action is not None:
            self.assign_key(key)
        elif key == arcade.key.ESCAPE:
            self.on_back()

    def on_mouse_motion(self, x, y, dx, dy):
        x, y = self.world_camera.to_world(x, y)

        self.music_slider.on_mouse_motion(x, y)
        self.sfx_slider.on_mouse_motion(x, y)

        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_mouse_press(self, x, y, button, modifiers):
        x, y = self.world_camera.to_world(x, y)

        if self.music_slider.on_mouse_press(x, y):
            return

        if self.sfx_slider.on_mouse_press(x, y):
            return

        for menu_button in self.buttons:
            if menu_button.contains(x, y):
                menu_button.on_click()
                return

    def on_mouse_release(self, x, y, button, modifiers):
        self.music_slider.on_mouse_release()
        self.sfx_slider.on_mouse_release()

    def on_back(self):
        self.window.show_view(self.previous_view)

    def on_resize(self, width, height):
        self.world_camera.fit_to_window()