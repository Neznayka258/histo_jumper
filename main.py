

import arcade

SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
FPS = 60

PLAYER_SIZE = 32
RUN_SPEED = 220
GRAVITY = -1700
JUMP_SPEED = 620

GROUND_HEIGHT = 80
SPIKE_WIDTH = 56
SPIKE_HEIGHT = 22
COLUMN_WIDTH = 60

COLORS = {
    "bg": (16, 18, 22),
    "player": (240, 240, 240),
    "platform": (70, 80, 90),
    "spike": (210, 60, 60),
    "goal": (60, 200, 120),
}

LEVELS = [
    {
        "level name": "Introduction",
        "level width": 2300,
        "spikes": [300, 820, 1340, 1860],
        "columns": [(560, 80), (1080, 90), (1600, 85)],
        "goal": (2100, GROUND_HEIGHT, 80, 140)
    },
    {
        "level name": "Introduction copy",
        "level width": 2300,
        "spikes": [400, 820, 1340, 1860],
        "columns": [(560, 80), (1080, 90), (1600, 85)],
        "goal": (2100, GROUND_HEIGHT, 80, 140)
    },

]


def rects_overlap(ax, ay, aw, ah, bx, by, bw, bh):
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by


def draw_rect(left, right, bottom, top, color):
    if hasattr(arcade, "draw_lrbt_rectangle_filled"):
        arcade.draw_lrbt_rectangle_filled(left, right, bottom, top, color)
    else:
        arcade.draw_lrtb_rectangle_filled(left, right, top, bottom, color)


class RhythmCube(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Rhythm Cube")
        self.set_update_rate(1 / FPS)
        arcade.set_background_color(COLORS["bg"])
        self.player_list = arcade.SpriteList()
        self.player_sprite = arcade.Sprite("cube.png")
        self.player_list.append(self.player_sprite)
        self.level_number = 0
        self.reset()
        self.win = False

    def reset(self):
        self.level = LEVELS[self.level_number]
        self.player_x = 60.0
        self.player_y = float(GROUND_HEIGHT)
        self.vel_y = 0.0
        self.on_ground = True

        self.camera_x = 0.0
        self.column_width = COLUMN_WIDTH
        self.set_caption("Rhythm Cube")

    def on_key_press(self, key, modifiers):
        if key in (arcade.key.SPACE, arcade.key.UP) and self.on_ground and not self.win:
            self.vel_y = JUMP_SPEED
            self.on_ground = False

    def on_update(self, delta_time):
        if self.level_number >= len(LEVELS):
            return

        dt = delta_time
        self.vel_y += GRAVITY * dt
        self.player_x += RUN_SPEED * dt
        prev_y = self.player_y
        self.player_y += self.vel_y * dt
        self.on_ground = False

        if self.vel_y <= 0:
            for cx, ch in self.level["columns"]:
                col_top = GROUND_HEIGHT + ch
                if (
                        self.player_x + PLAYER_SIZE > cx
                        and self.player_x < cx + self.column_width
                        and prev_y >= col_top
                        and self.player_y <= col_top
                ):
                    self.player_y = float(col_top)
                    self.vel_y = 0.0
                    self.on_ground = True
                    break

        if not self.on_ground and self.player_y <= GROUND_HEIGHT:
            self.player_y = float(GROUND_HEIGHT)
            self.vel_y = 0.0
            self.on_ground = True

        px = self.player_x
        py = self.player_y
        pw = PLAYER_SIZE
        ph = PLAYER_SIZE

        for sx in self.level["spikes"]:
            if rects_overlap(
                    px,
                    py,
                    pw,
                    ph,
                    sx,
                    GROUND_HEIGHT,
                    SPIKE_WIDTH,
                    SPIKE_HEIGHT,
            ):
                self.reset()
                return

        gx, gy, gw, gh = self.level["goal"]
        if rects_overlap(px, py, pw, ph, gx, gy, gw, gh):
            self.win = True
            self.set_caption("Rhythm Cube - Victory!")

        if px > self.level["level width"] + 200:
            self.reset()
            return

        self.camera_x = self.player_x - SCREEN_WIDTH * 0.35
        if self.camera_x < 0:
            self.camera_x = 0.0
        max_x = self.level["level width"] - SCREEN_WIDTH
        if self.camera_x > max_x:
            self.camera_x = float(max_x)

    def on_draw(self):

        if hasattr(self, "clear"):
            self.clear()
        else:
            arcade.start_render()

        arcade.draw_text(
            f"LEVEL {self.level_number + 1}: {self.level['level name']}",
            10,
            SCREEN_HEIGHT,
            COLORS["player"],
            24,
            anchor_x="left",
            anchor_y="top"
        )

        offset_x = int(self.camera_x)

        draw_rect(
            0 - offset_x,
            self.level["level width"] - offset_x,
            0,
            GROUND_HEIGHT,
            COLORS["platform"],
        )

        for sx in self.level["spikes"]:
            left = (sx - offset_x, GROUND_HEIGHT)
            right = (sx + SPIKE_WIDTH - offset_x, GROUND_HEIGHT)
            apex = (
                sx + SPIKE_WIDTH / 2.0 - offset_x,
                GROUND_HEIGHT + SPIKE_HEIGHT,
            )
            arcade.draw_polygon_filled([left, apex, right], COLORS["spike"])

        for cx, ch in self.level["columns"]:
            draw_rect(
                cx - offset_x,
                cx + self.column_width - offset_x,
                GROUND_HEIGHT,
                GROUND_HEIGHT + ch,
                COLORS["platform"],
            )

        gx, gy, gw, gh = self.level["goal"]
        draw_rect(
            gx - offset_x,
            gx + gw - offset_x,
            gy,
            gy + gh,
            COLORS["goal"],
        )

        self.player_sprite.center_x = self.player_x + PLAYER_SIZE / 2.0 - offset_x
        self.player_sprite.center_y = self.player_y + PLAYER_SIZE / 2.0
        self.player_sprite.width = PLAYER_SIZE
        self.player_sprite.height = PLAYER_SIZE
        self.player_list.draw()

        if self.win:
            arcade.draw_text(
                "WIN",
                SCREEN_WIDTH / 2,
                SCREEN_HEIGHT / 2,
                COLORS["player"],
                48,
                anchor_x="center",
                anchor_y="center",
            )
            if self.level_number < len(LEVELS):
                self.level_number += 1
                self.win = False

                self.reset()


def main():
    RhythmCube()
    arcade.run()


if __name__ == "__main__":
    main()

