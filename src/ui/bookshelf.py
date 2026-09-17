import arcade

from src import constants
from src.ui.key_names import key_name

OUTLINE_COLOR = (232, 214, 170)
HINT_BG = (18, 14, 20, 215)


class BookshelfOverlay:
    """Vue rapprochée d'une étagère : on choisit un livre pour le lire."""

    def __init__(self):
        self.active = False
        self.texture = None
        self.books = []
        self.selected = 0
        self._textures = {}
        self._hint = arcade.Text(
            "",
            constants.SCREEN_WIDTH / 2,
            constants.SCREEN_HEIGHT - 42,
            (232, 214, 170),
            22,
            font_name=constants.FONT_BODY,
            anchor_x="center",
            anchor_y="center",
        )

    def open(self, spec):
        path = spec.get("image")
        if path not in self._textures:
            self._textures[path] = arcade.load_texture(constants.PROJECT_ROOT / path)
        self.texture = self._textures[path]
        self.books = spec.get("books", [])
        self.selected = 0
        self.active = bool(self.books)
        return self.active

    def close(self):
        self.active = False

    def move(self, direction):
        if self.books:
            self.selected = (self.selected + direction) % len(self.books)

    def selected_book(self):
        if not self.active or not self.books:
            return None
        return self.books[self.selected]

    def book_at(self, x, y):
        for index, book in enumerate(self.books):
            left, right, bottom, top = book["hitbox"]
            if left <= x <= right and bottom <= y <= top:
                return index
        return None

    def draw(self):
        if not self.active:
            return
        arcade.draw_texture_rect(
            self.texture,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            pixelated=True,
        )
        left, right, bottom, top = self.books[self.selected]["hitbox"]
        arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, OUTLINE_COLOR, 5)

        self._hint.text = (
            f"{key_name(constants.KEY_LEFT)} / {key_name(constants.KEY_RIGHT)} : choisir"
            f"     {key_name(constants.KEY_INTERACT)} : lire"
            f"     {key_name(constants.KEY_BACK)} : fermer"
        )
        width = self._hint.content_width + 48
        arcade.draw_lbwh_rectangle_filled(
            (constants.SCREEN_WIDTH - width) / 2,
            constants.SCREEN_HEIGHT - 76,
            width,
            68,
            HINT_BG,
        )
        self._hint.draw()
