import arcade
import os
import sqlite3
from arcade.particles import Emitter, FadeParticle, EmitBurst

SPEED = 5
GRAVITY = 0.5
GRAVITY_SUPER = 0.47
PLAYER_JUMP_SPEED = 16
CAMERA_LERP = 0.1
ENEMY_SPEED = 1.5
BOUNCE_SPEED = 10

screen_width, screen_height = arcade.get_display_size()

SCREEN_WIDTH = screen_width
SCREEN_HEIGHT = screen_height


class Level_1(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, "Levels_1", fullscreen=True)

        current_dir = os.path.dirname(os.path.abspath(__file__))

        tmx_path = os.path.join(current_dir, "..", "Level_1", "Level_1.tmx")
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
        self.player_size_changed = False

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

        self.window_title = "Level 1"

    def setup(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        tmx_path = os.path.join(current_dir, "..", "Level_1", "Level_1.tmx")
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
        self.clear()
        self.world_camera.use()

        option1_y = self.screen_height // 2 - 500

        self.BG.draw()
        self.Ground.draw()
        self.Sky.draw()
        self.Truba.draw()
        self.secret_blocks_grib_baff.draw()
        self.secret_blocks_grib_life.draw()
        self.secret_blocks_coins.draw()
        self.Mob_Grib.draw()
        self.Mob_Turtle.draw()
        self.Coins.draw()
        self.Brick.draw()
        self.Black.draw()
        self.Trofey.draw()
        self.Sky_Blocks.draw()
        self.active_grib_baff.draw()
        self.active_grib_life.draw()

        if self.explosion:
            self.explosion.draw()

        if self.explosion_1:
            self.explosion_1.draw()

        arcade.draw_sprite(self.player)

        self.gui_camera.use()

        # текст 2 с обводкой

        arcade.draw_text(
            f"Coins: {self.Coins_Sum}",
            self.x + 750,
            option1_y,
            arcade.color.BLACK,
            40,
            font_name=self.font_name,
            anchor_x="left",
            anchor_y="center"
        )
        arcade.draw_text(
            f"Coins: {self.Coins_Sum}",
            self.x + 757,
            option1_y,
            arcade.color.WHITE,
            40,
            font_name=self.font_name,
            anchor_x="left",
            anchor_y="center"
        )

        arcade.draw_text(
            f"Death: {self.death_count}/{self.max_deaths + 1}",
            self.x + 750,
            option1_y- 55,
            arcade.color.BLACK,
            40,
            font_name=self.font_name,
            anchor_x="left",
            anchor_y="center"
        )
        arcade.draw_text(
            f"Death: {self.death_count}/{self.max_deaths + 1}",
            self.x + 757,
            option1_y - 55,
            arcade.color.WHITE,
            40,
            font_name=self.font_name,
            anchor_x="left",
            anchor_y="center"
        )

    def on_update(self, delta_time: float):
        self.physics_engine.update()

        self.con = sqlite3.connect("Results.sqlite")
        self.cur = self.con.cursor()

        # создание таблицы БД

        self.cur.execute('''CREATE TABLE IF NOT EXISTS results(
                id INTEGER PRIMARY KEY, coins INTEGER)''')

        self.con.commit()

        # Сбор монет

        coins_hit_list = arcade.check_for_collision_with_list(self.player, self.Coins)
        for coin in coins_hit_list:
            coin.remove_from_sprite_lists()
            self.Coins_Sum += 1
            arcade.play_sound(self.coin_sound)

        # Проверка столкновения с врагами

        enemy_hit_list = arcade.check_for_collision_with_list(self.player, self.Mob_Grib)
        enemy_hit_list_turtle = arcade.check_for_collision_with_list(self.player, self.Mob_Turtle)

        for enemy in enemy_hit_list:
            # Проверяем, прыгнул ли игрок на врага сверху

            if self.player.bottom > enemy.center_y:
                # Отталкиваем вверх
                self.player.change_y = BOUNCE_SPEED

                # Удаляем врага

                if enemy in self.Mob_Grib:
                    enemy.remove_from_sprite_lists()
                    arcade.play_sound(self.dead_mob)

                    self.explosion = Emitter(
                        center_xy=(enemy.center_x, enemy.center_y),
                        emit_controller=EmitBurst(20),
                        particle_factory=lambda e: FadeParticle(
                            filename_or_texture=arcade.make_soft_circle_texture(10, arcade.color.GRAY),
                            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 6.0),
                            lifetime=0.6
                        )
                    )

            else:
                if self.super:
                    arcade.play_sound(self.unbaff)

                    # Уменьшаем игрока

                    old_x = self.player.center_x
                    old_y = self.player.center_y

                    # Меняем состояние

                    self.super = False

                    # Меняем текстуру в зависимости от направления

                    if self.player_facing_direction > 0:
                        self.player.texture = self.player_texture_right
                    else:
                        self.player.texture = self.player_texture_left

                    # Пересоздаём спрайт с меньшими размерами

                    new_player = arcade.Sprite(self.player.texture, scale=1)
                    new_player.center_x = old_x
                    new_player.center_y = old_y
                    new_player.change_x = self.player.change_x
                    new_player.change_y = self.player.change_y

                    # Заменяем спрайт

                    self.player = new_player

                    # Пересоздаём физ движок с обычной гравитацией

                    self.physics_engine = arcade.PhysicsEnginePlatformer(
                        self.player,
                        platforms=self.all_sprites,
                        gravity_constant=GRAVITY
                    )

                    # Даем игроку небольшой отскок

                    self.player.change_y = 5

                elif not self.player_is_dead:
                    self.player_is_dead = True
                    self.player.texture = self.player_texture_dead

                    if self.music_player:
                        arcade.stop_sound(self.music_player)

                    if not self.dead_sound_played:
                        arcade.play_sound(self.dead_sound)
                        self.dead_sound_played = True

        # Обновляем взрыв

        if self.explosion:
            self.explosion.update(delta_time)
            if self.explosion.can_reap():
                self.explosion = None

        for enemy_turtle in enemy_hit_list_turtle:
            # Проверяем, прыгнул ли игрок на врага сверху

            if self.player.bottom > enemy_turtle.center_y:
                # Отталкиваем вверх
                self.player.change_y = BOUNCE_SPEED

                # Удаляем врага

                if enemy_turtle in self.Mob_Turtle:
                    enemy_turtle.remove_from_sprite_lists()
                    arcade.play_sound(self.dead_mob)

                    self.explosion_1 = Emitter(
                        center_xy=(enemy_turtle.center_x, enemy_turtle.center_y),
                        emit_controller=EmitBurst(20),
                        particle_factory=lambda e: FadeParticle(
                            filename_or_texture=arcade.make_soft_circle_texture(10, arcade.color.GRAY),
                            change_xy=arcade.math.rand_in_circle((0.0, 0.0), 6.0),
                            lifetime=0.6
                        )
                    )

            # Столкновение сбоку или снизу - смерть игрока

            else:
                if self.super:
                    arcade.play_sound(self.unbaff)

                    # Уменьшаем игрока

                    old_x = self.player.center_x
                    old_y = self.player.center_y

                    # Меняем состояние

                    self.super = False

                    # Меняем текстуру в зависимости от направления

                    if self.player_facing_direction > 0:
                        self.player.texture = self.player_texture_right
                    else:
                        self.player.texture = self.player_texture_left

                    # Пересоздаём спрайт с меньшими размерами

                    new_player = arcade.Sprite(self.player.texture, scale=1)
                    new_player.center_x = old_x
                    new_player.center_y = old_y
                    new_player.change_x = self.player.change_x
                    new_player.change_y = self.player.change_y

                    # Заменяем спрайт

                    self.player = new_player

                    # Пересоздаём физ движок с обычной гравитацией

                    self.physics_engine = arcade.PhysicsEnginePlatformer(
                        self.player,
                        platforms=self.all_sprites,
                        gravity_constant=GRAVITY
                    )

                    # Даем игроку небольшой отскок

                    self.player.change_y = 5

                elif not self.player_is_dead:
                    self.player_is_dead = True
                    self.player.texture = self.player_texture_dead

                    if self.music_player:
                        arcade.stop_sound(self.music_player)

                    if not self.dead_sound_played:
                        arcade.play_sound(self.dead_sound)
                        self.dead_sound_played = True

        # Обновляем взрыв

        if self.explosion_1:
            self.explosion_1.update(delta_time)
            if self.explosion_1.can_reap():
                self.explosion_1 = None

        if self.player.center_x < 0:
            self.player.center_x = 0
            self.player.change_x = 0

        if self.player.center_x > self.map_pixel_width:
            self.player.center_x = self.map_pixel_width
            self.player.change_x = 0

        cam_x, cam_y = self.world_camera.position
        dz_left = cam_x - self.DEAD_ZONE_W // 2
        dz_right = cam_x + self.DEAD_ZONE_W // 2
        dz_bottom = cam_y - self.DEAD_ZONE_H // 2
        dz_top = cam_y + self.DEAD_ZONE_H // 2

        px, py = self.player.center_x, self.player.center_y
        target_x, target_y = cam_x, cam_y

        if px < dz_left:
            target_x = px + self.DEAD_ZONE_W // 2
        elif px > dz_right:
            target_x = px - self.DEAD_ZONE_W // 2
        if py < dz_bottom:
            target_y = py + self.DEAD_ZONE_H // 2
        elif py > dz_top:
            target_y = py - self.DEAD_ZONE_H // 2

        half_w = self.world_camera.viewport_width / 2
        half_h = self.world_camera.viewport_height / 2
        target_x = max(half_w, min(self.map_pixel_width - half_w, target_x))
        target_y = max(half_h, min(self.map_pixel_height - half_h, target_y))

        smooth_x = (1 - CAMERA_LERP) * cam_x + CAMERA_LERP * target_x
        smooth_y = (1 - CAMERA_LERP) * cam_y + CAMERA_LERP * target_y

        self.cam_target = (smooth_x, smooth_y)
        self.world_camera.position = (self.cam_target[0], self.cam_target[1])

        # Анимация гриба

        for enemy in self.Mob_Grib:
            enemy.change_x = enemy.speed * enemy.direction
            enemy.patrol_distance += enemy.change_x

            if enemy.patrol_distance >= 100:
                enemy.direction = -1
            elif enemy.patrol_distance <= -100:
                enemy.direction = 1

            enemy.center_x += enemy.change_x

            enemy.texture = (self.textures[0][self.current_texture])

        # Обновление таймера анимации
        self.animation_timer += 1
        if self.animation_timer == 10:
            self.current_texture = 1 - self.current_texture
            self.animation_timer = 0

        # Анимация черепахи

        for enemy_turtle in self.Mob_Turtle:
            enemy_turtle.change_x = enemy_turtle.speed * enemy_turtle.direction
            enemy_turtle.patrol_distance += enemy_turtle.change_x

            if enemy_turtle.patrol_distance >= 100:
                enemy_turtle.direction = -1
            elif enemy_turtle.patrol_distance <= -100:
                enemy_turtle.direction = 1

            enemy_turtle.center_x += enemy_turtle.change_x

            # Анимация черепахи с учетом направления

            if enemy_turtle.direction == -1:
                enemy_turtle.texture = self.textures_turtle[0][self.current_texture]
            else:
                texture = self.textures_turtle[0][self.current_texture]
                enemy_turtle.texture = texture.flip_horizontally()

        # Анимация игрока

        if abs(self.player.change_x) > 0:
            self.animation_timer_player += 1
            if self.animation_timer_player == 5:
                if self.super:
                    # Анимация для Супер Марио

                    if self.player.texture == self.super_mario_right:
                        self.player.texture = self.super_texture_dviz_right
                    elif self.player.texture == self.super_texture_dviz_right:
                        self.player.texture = self.super_mario_right
                    elif self.player.texture == self.super_mario_left:
                        self.player.texture = self.super_mario_dviz_left
                    elif self.player.texture == self.super_mario_dviz_left:
                        self.player.texture = self.super_mario_left
                else:
                    # Анимация для обычного Марио

                    if self.player.texture == self.player_texture_right:
                        self.player.texture = self.player_texture_dviz_right
                    elif self.player.texture == self.player_texture_dviz_right:
                        self.player.texture = self.player_texture_right
                    elif self.player.texture == self.player_texture_left:
                        self.player.texture = self.player_texture_dviz_left
                    elif self.player.texture == self.player_texture_dviz_left:
                        self.player.texture = self.player_texture_left

                # Сбрасываем таймер

                self.animation_timer_player = 0

        trofey_hit = arcade.check_for_collision_with_list(self.player, self.Trofey)

        if trofey_hit:
            import subprocess
            import sys

            if self.window_title == "Level 1":

                self.close()

                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                level_2_path = os.path.join(parent_dir, "Level_2", "Level_2.py")
                subprocess.Popen([sys.executable, level_2_path])

            elif self.window_title == "Level 2":

                self.close()

                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                level_3_path = os.path.join(parent_dir, "Level_3", "Level_3.py")
                subprocess.Popen([sys.executable, level_3_path])

            elif self.window_title == "Level 3":

                self.close()

                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                level_4_path = os.path.join(parent_dir, "Level_4", "Level_4.py")
                subprocess.Popen([sys.executable, level_4_path])

            elif self.window_title == "Level 4":

                self.close()

                current_dir = os.path.dirname(os.path.abspath(__file__))
                parent_dir = os.path.dirname(current_dir)
                Menu_1_path = os.path.join(parent_dir, "Menu", "Menu.py")
                subprocess.Popen([sys.executable, Menu_1_path])



        # Смерть игрока

        if self.player_is_dead:
            self.timer += 1
            if self.timer > 240:

                if self.death_count >= self.max_deaths:
                    import subprocess
                    import sys

                    self.cur.execute(
                        "INSERT INTO results (coins) VALUES (?)",
                        (self.Coins_Sum,)
                    )
                    self.con.commit()

                    # Закрываем окно
                    self.close()

                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    parent_dir = os.path.dirname(current_dir)
                    menu_path = os.path.join(parent_dir, "Menu", "Menu.py")
                    subprocess.Popen([sys.executable, menu_path])

                # Перезапуск всего уровня

                self.player_is_dead = False
                self.timer = 0
                self.dead_sound_played = False
                self.music_started = False

                # Сброс позиции игрока

                self.player.center_x = 64
                self.player.center_y = 9 * 64

                # Сброс текстуры

                self.player.texture = self.player_texture_right

                # Сброс скорости

                self.player.change_x = 0
                self.player.change_y = 0

                # Добовляем +1 к счетчику смертей

                self.death_count += 1

        # Обработка на столкновение игрока и блока с монетами

        for block_coins in self.secret_blocks_coins:

            if block_coins.sound_timer > 0:
                block_coins.sound_timer -= 1

            if self.player.top >= block_coins.bottom - 10 and self.player.top <= block_coins.bottom + 10 and \
                    self.player.left >= block_coins.left - 20 and \
                    self.player.right <= block_coins.right + 20 and self.player.bottom < block_coins.top:

                if not block_coins.coins_given:
                    block_coins.center_y += 5
                    self.Coins_Sum += 2
                    arcade.play_sound(self.coin_sound)
                    block_coins.coins_given = True

                else:
                    block_coins.texture = self.texture_block
                    block_coins.center_y += 5

                    if block_coins.sound_timer == 0:
                        arcade.play_sound(self.breaks)
                        block_coins.sound_timer = 30

            else:
                block_coins.center_y = block_coins.original_y

                # Обработка на столкновение игрока и блока с бафом

        for block_baff in self.secret_blocks_grib_baff:

            if block_baff.sound_timer > 0:
                block_baff.sound_timer -= 1

            if self.player.top >= block_baff.bottom - 10 and self.player.top <= block_baff.bottom + 10 and \
                    self.player.left >= block_baff.left - 20 and \
                    self.player.right <= block_baff.right + 20 and self.player.bottom < block_baff.top:
                if self.secret_blocks_grib_baff_check == 0:
                    block_baff.center_y += 5
                    self.secret_blocks_grib_baff_check = 1

                    grib_baff = arcade.Sprite()
                    grib_baff.texture = self.grib_baff
                    grib_baff.scale = 1.0
                    grib_baff.center_x = block_baff.center_x
                    grib_baff.center_y = block_baff.top + 30

                    grib_baff.change_x = 1.0
                    grib_baff.change_y = 3
                    grib_baff.direction = 1

                    # Добавляем в список активных грибов
                    self.active_grib_baff.append(grib_baff)

                else:
                    block_baff.texture = self.texture_block
                    block_baff.center_y += 5

                    if block_baff.sound_timer == 0:
                        arcade.play_sound(self.breaks)
                        block_baff.sound_timer = 30

            else:
                block_baff.center_y = block_baff.original_y

        # Движение самого гриба, если мы его выбили

        for grib in self.active_grib_baff:
            # Гравитация

            grib.change_y -= GRAVITY

            old_x = grib.center_x
            old_y = grib.center_y

            grib.change_x = 4 * grib.direction

            # Движение гриба по горизонтали

            grib.center_x += grib.change_x

            # Проверяем столкновения по горизонтали

            hit_list_x = arcade.check_for_collision_with_list(grib, self.collision_sprites)

            if hit_list_x:

                grib.center_x = old_x
                grib.direction *= -1

                if arcade.check_for_collision_with_list(grib, self.collision_sprites):
                    grib.center_x = old_x

            grib.center_y += grib.change_y

            hit_list_y = arcade.check_for_collision_with_list(grib, self.collision_sprites)

            if hit_list_y:
                grib.center_y = old_y
                grib.change_y = 0

            # Проверяем сбор гриба игроком

            if arcade.check_for_collision(self.player, grib):
                grib.remove_from_sprite_lists()
                arcade.play_sound(self.baff)

                if not self.super:
                    # Сохраняем позицию игрока

                    old_x = self.player.center_x
                    old_y = self.player.center_y

                    # Меняем состояние

                    self.super = True

                    # Меняем текстуру

                    if self.player_facing_direction > 0:
                        self.player.texture = self.super_mario_right
                    else:
                        self.player.texture = self.super_mario_left

                    # Пересоздаём спрайт с новыми размерами

                    new_player = arcade.Sprite(self.player.texture, scale=1)
                    new_player.center_x = old_x
                    new_player.center_y = old_y
                    new_player.change_x = self.player.change_x
                    new_player.change_y = self.player.change_y

                    # Заменяем спрайт

                    self.player = new_player

                    # Пересоздаём физ движок

                    self.physics_engine = arcade.PhysicsEnginePlatformer(
                        self.player,
                        platforms=self.all_sprites,
                        gravity_constant=GRAVITY_SUPER
                    )

        # Обработка на столкновение игрока и блока с доп жизнью

        for block_life in self.secret_blocks_grib_life:

            if block_life.sound_timer > 0:
                block_life.sound_timer -= 1

            if self.player.top >= block_life.bottom - 10 and self.player.top <= block_life.bottom + 10 and \
                    self.player.left >= block_life.left - 20 and \
                    self.player.right <= block_life.right + 20 and self.player.bottom < block_life.top:
                if self.secret_blocks_grib_life_check == 0:
                    block_life.center_y += 5
                    self.secret_blocks_grib_life_check = 1

                    grib_life = arcade.Sprite()
                    grib_life.texture = self.grib_life
                    grib_life.scale = 1.0
                    grib_life.center_x = block_life.center_x
                    grib_life.center_y = block_life.top + 30

                    grib_life.change_x = 1.0
                    grib_life.change_y = 3
                    grib_life.direction = 1

                    # Добавляем в список активных грибов
                    self.active_grib_life.append(grib_life)

                else:
                    block_life.texture = self.texture_block
                    block_life.center_y += 5

                    if block_life.sound_timer == 0:
                        arcade.play_sound(self.breaks)
                        block_life.sound_timer = 30

            else:
                block_life.center_y = block_life.original_y

        for grib in self.active_grib_life:
            # Гравитация

            grib.change_y -= GRAVITY

            old_x = grib.center_x
            old_y = grib.center_y

            grib.change_x = 4 * grib.direction

            # Движение гриба по горизонтали

            grib.center_x += grib.change_x

            # Проверяем столкновения по горизонтали

            hit_list_x = arcade.check_for_collision_with_list(grib, self.collision_sprites)

            if hit_list_x:

                grib.center_x = old_x
                grib.direction *= -1

                if arcade.check_for_collision_with_list(grib, self.collision_sprites):
                    grib.center_x = old_x

            grib.center_y += grib.change_y

            hit_list_y = arcade.check_for_collision_with_list(grib, self.collision_sprites)

            if hit_list_y:
                grib.center_y = old_y
                grib.change_y = 0

            # Забрали гриб = получили 1 дополнительную жизнь

            if arcade.check_for_collision(self.player, grib):
                grib.remove_from_sprite_lists()
                arcade.play_sound(self.baff)
                self.max_deaths += 1

        # Смерть игрока при падении в зону смерти

        for block_dead in self.Dead:
            if block_dead.sound_timer > 0:
                block_dead.sound_timer -= 1

            if arcade.check_for_collision(self.player, block_dead):
                if not self.player_is_dead:
                    self.player_is_dead = True
                    self.player.texture = self.player_texture_dead

                    # Уменьшаем игрока

                    old_x = self.player.center_x
                    old_y = self.player.center_y

                    # Меняем состояние

                    self.super = False

                    # Пересоздаём спрайт с меньшими размерами

                    new_player = arcade.Sprite(self.player.texture, scale=1)
                    new_player.center_x = old_x
                    new_player.center_y = old_y
                    new_player.change_x = self.player.change_x
                    new_player.change_y = self.player.change_y

                    # Заменяем спрайт

                    self.player = new_player

                    # Пересоздаём физ движок с обычной гравитацией

                    self.physics_engine = arcade.PhysicsEnginePlatformer(
                        self.player,
                        platforms=self.all_sprites,
                        gravity_constant=GRAVITY
                    )

                    if self.music_player:
                        arcade.stop_sound(self.music_player)

                    if block_dead.sound_timer == 0:
                        arcade.play_sound(self.dead_sound)
                        block_dead.sound_timer = 30

        # Проигрываем трек игры пока игрок жив

        if not self.player_is_dead and not self.music_started:
            self.music_player = arcade.play_sound(self.track_game, loop=True, volume=0.6)
            self.music_started = True

    def on_key_press(self, key, modifiers):
        if self.player_is_dead:
            return
        if key == arcade.key.UP:
            if self.physics_engine.can_jump():
                self.player.change_y = PLAYER_JUMP_SPEED
                arcade.play_sound(self.jump_sound)
        elif key == arcade.key.LEFT:
            self.player.change_x = -SPEED
            self.player_facing_direction = -1
            if self.super:
                self.player.texture = self.super_mario_left
            else:
                self.player.texture = self.player_texture_left
        elif key == arcade.key.RIGHT:
            self.player.change_x = SPEED
            self.player_facing_direction = 1
            if self.super:
                self.player.texture = self.super_mario_right
            else:
                self.player.texture = self.player_texture_right

    def on_key_release(self, key, modifiers):
        if key == arcade.key.LEFT:
            if self.player.change_x < 0:
                self.player.change_x = 0
        elif key == arcade.key.RIGHT:
            if self.player.change_x > 0:
                self.player.change_x = 0


def main():
    game = Level_1()
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()