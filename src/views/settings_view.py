import arcade

from src import constants
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


class SettingsView(arcade.View):
    def __init__(self, previous_view):
        super().__init__()
        self.previous_view = previous_view
        self.scale = constants.SCREEN_HEIGHT / constants.BASE_HEIGHT
        s = self.scale

        self.background = load_scene_texture(constants.SCENE_MENU)

        self.title = arcade.Text(
            "Paramètres",
            constants.SCREEN_WIDTH / 2, 940 * s,
            (232, 214, 170),
            int(60 * s),
            font_name=constants.FONT_TITLE,
            bold=True,
            anchor_x="center",
        )

        self.waiting_action = None
        self.buttons = []
        self.key_labels = []
        self.key_buttons = {}

        row_y = 790
        for action, label in KEY_ACTIONS:
            self.key_labels.append(arcade.Text(
                label,
                530 * s, row_y * s,
                (232, 214, 170),
                int(26 * s),
                font_name=constants.FONT_BODY,
                anchor_y="center",
            ))
            button = MenuButton("", 1190 * s, row_y * s, 400 * s, 64 * s,
                                lambda a=action: self.start_waiting(a), int(24 * s))
            self.buttons.append(button)
            self.key_buttons[action] = button
            row_y -= 85

        self.language_button = MenuButton("Français", 1190 * s, 320 * s, 400 * s, 64 * s,
                                          self.on_language, int(24 * s))
        self.buttons.append(self.language_button)
        self.language_label = arcade.Text(
            "Langue", 530 * s, 320 * s, (232, 214, 170), int(26 * s),
            font_name=constants.FONT_BODY, anchor_y="center",
        )

        self.status = arcade.Text(
            "", constants.SCREEN_WIDTH / 2, 220 * s, (190, 178, 158), int(20 * s),
            font_name=constants.FONT_BODY, anchor_x="center", anchor_y="center",
        )

        self.buttons.append(MenuButton("Retour", constants.SCREEN_WIDTH / 2, 120 * s, 320 * s, 76 * s,
                                       self.on_back, int(26 * s)))
        self.refresh_key_buttons()

    # ---------- Affichage ----------

    def on_draw(self):
        self.clear()
        s = self.scale
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            pixelated=True,
        )
        arcade.draw_lbwh_rectangle_filled(
            0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT, (8, 6, 10, 170)
        )
        panel_w, panel_h = 1000 * s, 990 * s
        panel_left = (constants.SCREEN_WIDTH - panel_w) / 2
        panel_bottom = 45 * s
        arcade.draw_lbwh_rectangle_filled(panel_left, panel_bottom, panel_w, panel_h, (18, 14, 20, 235))
        arcade.draw_lbwh_rectangle_outline(panel_left, panel_bottom, panel_w, panel_h, (214, 200, 168), 2)

        self.title.draw()
        for label in self.key_labels:
            label.draw()
        self.language_label.draw()
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

    def on_language(self):
        pass  # TODO : changement de langue (implémenté par une autre personne)

    def on_key_press(self, key, modifiers):
        if self.waiting_action is not None:
            self.assign_key(key)
        elif key == arcade.key.ESCAPE:
            self.on_back()

    def on_mouse_press(self, x, y, button, modifiers):
        if self.waiting_action is not None:
            return
        for menu_button in self.buttons:
            if menu_button.contains(x, y):
                menu_button.on_click()

    def on_mouse_motion(self, x, y, dx, dy):
        for button in self.buttons:
            button.hovered = button.contains(x, y)

    def on_back(self):
        self.window.show_view(self.previous_view)