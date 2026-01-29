import arcade
import os

SPEED = 5
GRAVITY = 0.5
GRAVITY_SUPER = 0.45
PLAYER_JUMP_SPEED = 16
CAMERA_LERP = 0.1
ENEMY_SPEED = 1.5
BOUNCE_SPEED = 10

screen_width, screen_height = arcade.get_display_size()

SCREEN_WIDTH = screen_width
SCREEN_HEIGHT = screen_height


class Level_3(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Level_3", fullscreen=True)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        tmx_path = os.path.join(current_dir, "..", "Level_3", "Level_3.tmx")
        tile_map = arcade.load_tilemap(tmx_path, scaling=1)

        self.map_pixel_width = tile_map.width * tile_map.tile_width
        self.map_pixel_height = tile_map.height * tile_map.tile_height

        self.player_facing_direction = 1

        self.timer = 0

        self.explosions = []
        self.explosion = None
        self.explosion_1 = None

        self.timer_pause = 0

        self.player_is_dead = False

        self.timer_block = 0

        self.super = False

        images_dir = os.path.join(current_dir, "..", "images")
        sound_dir = os.path.join(current_dir, "..", "Sounds")

        self.cell_size = 16
        self.all_sprites = arcade.SpriteList()
        self.coins = arcade.SpriteList()
        self.player_texture_dviz_right = arcade.load_texture(os.path.join(images_dir, "Small_Perzonaz_Dviz.png"))
        self.player_texture_right = arcade.load_texture(os.path.join(images_dir, "Small_Perzonaz.png"))
        self.player_texture_dead = arcade.load_texture(os.path.join(images_dir, "Small_Personaz_Dead.png"))
        self.player_texture_left = self.player_texture_right.flip_horizontally()
        self.player_texture_dviz_left = self.player_texture_dviz_right.flip_horizontally()

        self.super_mario_right = arcade.load_texture(os.path.join(images_dir, "Super_Mario.png"))
        self.super_mario_dviz_left = arcade.load_texture(os.path.join(images_dir, "Super_Mario_Dviz.png"))
        self.super_mario_left = self.super_mario_right.flip_horizontally()
        self.super_texture_dviz_right = self.super_mario_dviz_left.flip_horizontally()

        self.jump_sound = arcade.load_sound(os.path.join(sound_dir, "Jump.mp3"))
        self.dead_sound = arcade.load_sound(os.path.join(sound_dir, "Dead.mp3"))
        self.coin_sound = arcade.load_sound(os.path.join(sound_dir, "Coin_farm.mp3"))
        self.breaks = arcade.load_sound(os.path.join(sound_dir, "Break.mp3"))
        self.track_game = arcade.load_sound(os.path.join(sound_dir, "track_game_1.mp3"))
        self.dead_mob = arcade.load_sound(os.path.join(sound_dir, "Dead_Mob.mp3"))
        self.baff = arcade.load_sound(os.path.join(sound_dir, "Baff.mp3"))
        self.unbaff = arcade.load_sound(os.path.join(sound_dir, "UnSuper.mp3"))

        self.world_camera = arcade.camera.Camera2D()
        self.gui_camera = arcade.camera.Camera2D()
        self.DEAD_ZONE_W = 200
        self.DEAD_ZONE_H = 150

        self.animation_timer = 0
        self.animation_timer_player = 0
        self.current_texture = 0

        self.textures = [[arcade.load_texture(os.path.join(images_dir, "Grib_1.png")),
                          arcade.load_texture(os.path.join(images_dir, "Grib_2.png"))]]

        self.textures_turtle = [[arcade.load_texture(os.path.join(images_dir, "Tutle_1_R.png")),
                                 arcade.load_texture(os.path.join(images_dir, "Turtle_2_R.png"))]]

        self.grib_baff = arcade.load_texture(os.path.join(images_dir, "Grib_Baff.png"))

        self.grib_life = arcade.load_texture(os.path.join(images_dir, "Grib_Life.png"))

        self.active_grib_baff = arcade.SpriteList()
        self.active_grib_life = arcade.SpriteList()

        self.texture_block = arcade.load_texture(os.path.join(images_dir, "secret_block.png"))

        self.font_name = "Super Mario Bros. 2"
        self.selected_option = 1

        self.x = self.width // 2

        self.Coins_Sum = 0

        self.dead_sound_played = False
        self.music_started = False
        self.music_player = None

        self.death_count = 0
        self.max_deaths = 2

        self.window_title = "Level 3"

    def setup(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tmx_path = os.path.join(current_dir, "..", "Level_3", "Level_3.tmx")
        tile_map = arcade.load_tilemap(tmx_path, scaling=1)

        self.screen_width = self.width
        self.screen_height = self.height

        self.Ground = tile_map.sprite_lists["Ground"]
        self.Sky = tile_map.sprite_lists["Sky"]
        self.Coins = tile_map.sprite_lists["Coins"]
        self.secret_blocks_grib_life = tile_map.sprite_lists["secret_blocks_grib_life"]
        self.secret_blocks_coins = tile_map.sprite_lists["secret_blocks_coins"]
        self.Mob_Grib = tile_map.sprite_lists["Mob_Grib"]
        self.secret_blocks_grib_baff = tile_map.sprite_lists["secret_blocks_grib_baff"]
        self.BG = tile_map.sprite_lists["BackGround"]
        self.Truba = tile_map.sprite_lists["Truba"]
        self.Mob_Turtle = tile_map.sprite_lists["Mob_Turtle_Red"]
        self.Black = tile_map.sprite_lists["Black"]
        self.Sky_Blocks = tile_map.sprite_lists["Sky_Blocks"]
        self.Trofey = tile_map.sprite_lists["Trofey"]
        self.Dead = tile_map.sprite_lists["Dead"]
        self.Brick = tile_map.sprite_lists["Brick"]

        self.secret_blocks_coins_check = 0
        self.secret_blocks_grib_life_check = 0
        self.secret_blocks_grib_baff_check = 0

        for block_coins in self.secret_blocks_coins:
            block_coins.original_y = block_coins.center_y
            block_coins.sound_timer = 0
            block_coins.coins_given = False

        for block_baff in self.secret_blocks_grib_baff:
            block_baff.original_y = block_baff.center_y
            block_baff.sound_timer = 0

        for block_life in self.secret_blocks_grib_life:
            block_life.original_y = block_life.center_y
            block_life.sound_timer = 0

        for block_dead in self.Dead:
            block_dead.sound_timer = 0

        self.player = arcade.Sprite(self.player_texture_right, scale=1)

        self.player.center_x = 64
        self.player.center_y = 9 * 64

        self.all_sprites = (self.Ground, self.Brick, self.secret_blocks_grib_baff,
                            self.secret_blocks_grib_life, self.Truba, self.Sky_Blocks, self.secret_blocks_coins)

        self.physics_engine = arcade.PhysicsEnginePlatformer(
            self.player,
            platforms=self.all_sprites,
            gravity_constant=GRAVITY
        )

        arcade.set_background_color(arcade.color.SKY_BLUE)

        for enemy in self.Mob_Grib:
            enemy.patrol_distance = 0
            enemy.direction = 1
            enemy.speed = ENEMY_SPEED

        for enemy_turtle in self.Mob_Turtle:
            enemy_turtle.patrol_distance = 0
            enemy_turtle.direction = 1
            enemy_turtle.speed = ENEMY_SPEED

        self.collision_sprites = arcade.SpriteList()
        self.collision_sprites.extend(self.Ground)
        self.collision_sprites.extend(self.Brick)
        self.collision_sprites.extend(self.Truba)
        self.collision_sprites.extend(self.secret_blocks_grib_baff)
        self.collision_sprites.extend(self.secret_blocks_grib_life)
        self.collision_sprites.extend(self.secret_blocks_coins)
        self.collision_sprites.extend(self.Sky_Blocks)

        self.active_grib_baff.clear()

    def on_draw(self):
        from Level_1.Level_1 import Level_1
        Level_1.on_draw(self)

    def on_update(self, delta_time: float):
        from Level_1.Level_1 import Level_1
        Level_1.on_update(self, delta_time)

    def on_key_press(self, key, modifiers):
        from Level_1.Level_1 import Level_1
        Level_1.on_key_press(self, key, modifiers)

    def on_key_release(self, key, modifiers):
        from Level_1.Level_1 import Level_1
        Level_1.on_key_release(self, key, modifiers)


def main():
    game = Level_3()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()