import arcade

from src import constants

STYLES = {
    "title": {
        "size": 86,
        "color": (236, 220, 178),
        "font": constants.FONT_TITLE,
        "bold": True,
        "italic": False,
        "space_before": 0,
        "space_after": 10,
    },
    "tagline": {
        "size": 32,
        "color": (196, 176, 152),
        "font": constants.FONT_TITLE,
        "bold": False,
        "italic": True,
        "space_before": 0,
        "space_after": 150,
    },
    "section": {
        "size": 24,
        "color": (214, 170, 96),
        "font": constants.FONT_BODY,
        "bold": True,
        "italic": False,
        "space_before": 64,
        "space_after": 26,
    },
    "name": {
        "size": 34,
        "color": (240, 236, 228),
        "font": constants.FONT_TITLE,
        "bold": False,
        "italic": False,
        "space_before": 0,
        "space_after": 14,
    },
    "outro": {
        "size": 24,
        "color": (206, 194, 176),
        "font": constants.FONT_BODY,
        "bold": False,
        "italic": True,
        "space_before": 190,
        "space_after": 0,
    },
}

CREDITS_CONTENT = (
    ("title", "LogLine"),
    ("tagline", "Mourir pour mieux avancer"),

    ("section", "DÉVELOPPEURS"),
    ("name", "Alexis BERNARD"),
    ("name", "Camélia ANTOINE"),
    ("name", "Julie ZHAN"),
    ("name", "Killian MAUGE"),
    ("name", "Théo PETRECO"),

    ("section", "CHEF DE PROJET"),
    ("name", "Alexis BERNARD"),

    ("section", "GAME DESIGN"),
    ("name", "Camélia ANTOINE"),
    ("name", "Julie ZHAN"),

    ("section", "SCÉNARISTE"),
    ("name", "Toute l'équipe Logline"),

    ("section", "ARTISTE 2D"),
    ("name", "Camélia ANTOINE"),
    ("name", "Julie ZHAN"),

    ("section", "BACKGROUNDS"),
    ("name", "Killian MAUGE"),

    ("section", "SONS"),
    ("name", "Théo PETRECO"),

    (
        "outro",
        "Un projet développé pour la Game Jam ESIEE Paris 2026,\n"
        "entre les filières INFO et FI,\n"
        "supervisé par Nicolas Borie et Rémi Forax.",
    ),

    (
        "outro",
        "Merci d'avoir joué à la démo,\n"
        "-- L'équipe LogLine.",
    ),
)


class CreditsView(arcade.View):
    def __init__(self, previous_view=None):
        super().__init__()
        constants.load_fonts()
        self.previous_view = previous_view
        self._background = arcade.load_texture(str(constants.CREDITS_BACKGROUND))

        self._entries = []
        self._roll_height = 0.0
        self._loop_length = 1.0
        self._scroll = 0.0
        self._build_roll()

        self._hint = arcade.Text(
            "Échap ou clic pour revenir au menu",
            constants.SCREEN_WIDTH - constants.scale_h(30),
            constants.scale_h(26),
            (178, 166, 150, 205),
            int(constants.scale_h(18)),
            font_name=constants.FONT_BODY,
            anchor_x="right",
        )

    # Mise en page

    def _build_roll(self):
        depth = 0.0
        for index, (style_name, text) in enumerate(CREDITS_CONTENT):
            style = STYLES[style_name]
            if index > 0:
                depth += constants.scale_h(style["space_before"])
            label = self._make_label(style, text)
            self._entries.append((label, depth, label.color[:3]))
            depth += label.content_height + constants.scale_h(style["space_after"])

        self._roll_height = depth

        self._loop_length = (
            self._roll_height + constants.SCREEN_HEIGHT + constants.CREDITS_LOOP_GAP
        )

    def _make_label(self, style, text):
        return arcade.Text(
            text,
            constants.SCREEN_WIDTH / 2,
            0,
            style["color"],
            int(constants.scale_h(style["size"])),
            font_name=style["font"],
            bold=style["bold"],
            italic=style["italic"],
            width=constants.CREDITS_TEXT_WIDTH,
            align="center",
            multiline=True,
            anchor_x="center",
            anchor_y="top",
        )

    # Cycle de vie Arcade

    def on_show_view(self):
        self.window.background_color = (8, 6, 10)
        self._scroll = 0.0

    def on_update(self, delta_time):
        self._scroll = (
            self._scroll + constants.CREDITS_SCROLL_SPEED * delta_time
        ) % self._loop_length

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self._background,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
        )
        arcade.draw_lrbt_rectangle_filled(
            0,
            constants.SCREEN_WIDTH,
            0,
            constants.SCREEN_HEIGHT,
            constants.CREDITS_VEIL_COLOR,
        )

        roll_top = self._scroll - constants.CREDITS_START_OFFSET
        for label, depth, rgb in self._entries:
            top = roll_top - depth
            bottom = top - label.content_height
            if top < 0 or bottom > constants.SCREEN_HEIGHT:
                continue
            label.y = top
            label.color = rgb + (self._edge_alpha(top, bottom),)
            label.draw()

        self._hint.draw()

    # Entrées joueur

    def on_key_press(self, key, modifiers):
        if key == constants.KEY_BACK:
            self._leave()

    def on_mouse_press(self, x, y, button, modifiers):
        self._leave()

    def _leave(self):
        if self.previous_view is not None:
            self.window.show_view(self.previous_view)
            return
        # TODO: remplacer par self.window.show_view(MenuView()).
        self.window.close()

    # Outils

    @staticmethod
    def _edge_alpha(top, bottom):
        """Fait apparaître et disparaître la ligne en douceur aux bords."""
        margin = constants.CREDITS_FADE_MARGIN
        entering = top / margin
        leaving = (constants.SCREEN_HEIGHT - bottom) / margin
        return int(255 * max(0.0, min(1.0, entering, leaving)))
