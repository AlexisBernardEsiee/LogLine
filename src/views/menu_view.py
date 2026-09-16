import json

import arcade

from src import constants


class MenuView(arcade.View):
    def __init__(self):                    
        super().__init__()
        scenes = json.loads(constants.DATA_SCENES.read_text(encoding="utf-8"))
        path = constants.PROJECT_ROOT / scenes[constants.SCENE_MENU]["path"]
        self.background = arcade.load_texture(path)
        self.title = arcade.Text(
            constants.SCREEN_TITLE,      
            140, 800,                    
            (232, 214, 170),             
            110,                         
            font_name=constants.FONT_TITLE,
            bold=True,
        )
        self.subtitle = arcade.Text(
            "Mourir pour mieux avancer",
            146, 740,
            (210, 198, 176),
            30,
            font_name=constants.FONT_TITLE,
            italic=True,
        )

    def on_show_view(self):
        self.window.background_color = (8, 8, 10)

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(0, 0, constants.SCREEN_WIDTH, constants.SCREEN_HEIGHT),
            pixelated=True,
        )
        self.title.draw()
        self.subtitle.draw()