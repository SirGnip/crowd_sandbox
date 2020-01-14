import arcade


class FpsScanner(arcade.Sprite):
    """Simple actor that slowly moves along bottom of screen to help visually identify frame rate hitches"""
    def __init__(self):
        super().__init__()
        self.append_texture(arcade.make_circle_texture(10, arcade.color.GRAY))
        self.set_texture(0)
        self.change_x = 3
        self.center_x = 0
        self.center_y = 10

    def update(self):
        super().update()
        if self.center_x > 800:
            self.center_x = 0