import arcade

from src import constants


class DebugGrid:
    def __init__(self):
        self.visible = True
        self.mouse_x = 0.0
        self.mouse_y = 0.0
        self.anchor = None
        self.last_hitbox = None
        self._item_labels = {}
        self._cursor = arcade.Text(
            "",
            16,
            constants.SCREEN_HEIGHT - 28,
            (180, 255, 210),
            16,
            font_name=constants.FONT_BODY,
        )
        self._hint = arcade.Text(
            "G  grille    clic  coin1 / coin2    clic droit  annuler    C  afficher JSON",
            16,
            constants.SCREEN_HEIGHT - 52,
            (170, 210, 190),
            14,
            font_name=constants.FONT_BODY,
        )
        self._hitbox_label = arcade.Text(
            "",
            16,
            constants.SCREEN_HEIGHT - 76,
            (255, 230, 140),
            16,
            font_name=constants.FONT_BODY,
        )
        self._axis_labels = []
        for x in range(0, constants.SCREEN_WIDTH + 1, constants.DEBUG_GRID_MAJOR):
            self._axis_labels.append(
                arcade.Text(str(x), x + 4, 6, (160, 220, 190, 180), 11, font_name=constants.FONT_BODY)
            )
        for y in range(constants.DEBUG_GRID_MAJOR, constants.SCREEN_HEIGHT + 1, constants.DEBUG_GRID_MAJOR):
            self._axis_labels.append(
                arcade.Text(str(y), 6, y + 4, (160, 220, 190, 180), 11, font_name=constants.FONT_BODY)
            )

    def toggle(self):
        self.visible = not self.visible
        if not self.visible:
            self.anchor = None

    def on_mouse_motion(self, x, y):
        self.mouse_x = x
        self.mouse_y = y

    def on_mouse_press(self, x, y, button):
        if not self.visible:
            return False
        if button == arcade.MOUSE_BUTTON_RIGHT:
            self.anchor = None
            return True
        if button != arcade.MOUSE_BUTTON_LEFT:
            return False
        point = (round(x), round(y))
        if self.anchor is None:
            self.anchor = point
        else:
            self.last_hitbox = self._rect(self.anchor, point)
            self.anchor = None
            print(self._json(self.last_hitbox))
            self._refresh_hitbox_label()
        return True

    def copy_last(self):
        if self.last_hitbox is None:
            return
        print(self._json(self.last_hitbox))
        self._refresh_hitbox_label()

    def draw(self, room_manager=None, player=None):
        if not self.visible:
            return

        self._draw_lines()
        for label in self._axis_labels:
            label.draw()

        if room_manager is not None:
            arcade.draw_line(
                0,
                room_manager.floor_y,
                constants.SCREEN_WIDTH,
                room_manager.floor_y,
                (255, 180, 80, 200),
                2,
            )
            for item in room_manager.interactables:
                left, right, bottom, top = item.hitbox
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (80, 180, 255, 220), 2)
                label = self._item_labels.get(item.name)
                if label is None:
                    label = arcade.Text(
                        item.name,
                        left + 6,
                        top - 22,
                        (80, 180, 255),
                        14,
                        font_name=constants.FONT_BODY,
                    )
                    self._item_labels[item.name] = label
                else:
                    label.x = left + 6
                    label.y = top - 22
                label.draw()

        if player is not None:
            arcade.draw_line(
                player.center_x,
                0,
                player.center_x,
                constants.SCREEN_HEIGHT,
                (255, 120, 160, 140),
                1,
            )

        if self.anchor is not None:
            preview = self._rect(self.anchor, (self.mouse_x, self.mouse_y))
            left, right, bottom, top = preview
            arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (255, 230, 120, 230), 2)

        if self.last_hitbox is not None:
            left, right, bottom, top = self.last_hitbox
            arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, (255, 210, 80, 230), 2)

        self._cursor.text = f"x={round(self.mouse_x)}   y={round(self.mouse_y)}"
        if player is not None:
            self._cursor.text += f"   joueur_x={round(player.center_x)}"
        self._cursor.draw()
        self._hint.draw()
        if self.last_hitbox is not None:
            self._hitbox_label.draw()

    def _refresh_hitbox_label(self):
        if self.last_hitbox is None:
            self._hitbox_label.text = ""
            return
        self._hitbox_label.text = self._json(self.last_hitbox)

    def _draw_lines(self):
        minor = (70, 160, 130, 45)
        major = (110, 220, 170, 110)
        step = constants.DEBUG_GRID_STEP
        major_step = constants.DEBUG_GRID_MAJOR
        width = constants.SCREEN_WIDTH
        height = constants.SCREEN_HEIGHT
        for x in range(0, width + 1, step):
            color = major if x % major_step == 0 else minor
            arcade.draw_line(x, 0, x, height, color, 1)
        for y in range(0, height + 1, step):
            color = major if y % major_step == 0 else minor
            arcade.draw_line(0, y, width, y, color, 1)

    @staticmethod
    def _rect(a, b):
        x1, y1 = a
        x2, y2 = b
        left, right = sorted((round(x1), round(x2)))
        bottom, top = sorted((round(y1), round(y2)))
        return (left, right, bottom, top)

    @staticmethod
    def _json(hitbox):
        left, right, bottom, top = hitbox
        return f'"hitbox": [{left}, {right}, {bottom}, {top}]'
