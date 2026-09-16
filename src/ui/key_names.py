import arcade

SPECIAL_NAMES = {
    arcade.key.LEFT: "Flèche gauche",
    arcade.key.RIGHT: "Flèche droite",
    arcade.key.UP: "Flèche haut",
    arcade.key.DOWN: "Flèche bas",
    arcade.key.SPACE: "Espace",
    arcade.key.ENTER: "Entrée",
    arcade.key.TAB: "Tab",
    arcade.key.LSHIFT: "Maj gauche",
    arcade.key.RSHIFT: "Maj droite",
    arcade.key.ESCAPE: "Échap",
}


def key_name(key):
    if key in SPECIAL_NAMES:
        return SPECIAL_NAMES[key]
    for name in dir(arcade.key):
        if name.startswith(("MOD_", "MOTION_")) or not name.isupper():
            continue
        if getattr(arcade.key, name) == key:
            return name.replace("KEY_", "")
    return f"Touche {key}"