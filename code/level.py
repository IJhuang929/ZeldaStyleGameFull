import pygame
from settings import *
from tile import Tile
from player import Player
from debug import debug
from support import *
from random import choice, randint
from weapon import Weapon
from ui import UI
from enemy import Enemy
from particles import AnimationEffects
from magic import MagicEffects
from upgrade import UpgradeUI, UpgradeLogic


class Level:
    def __init__(self):

        # get the display surface
        self.display_surface = pygame.display.get_surface()
        self.game_paused = False

        # sprite group setup
        self.visible_sprites = YSortCameraGroup()
        self.obstacle_sprites = pygame.sprite.Group()

        # attack sprites
        self.current_attack = None
        self.attack_sprites = pygame.sprite.Group()
        self.attackable_sprites = pygame.sprite.Group()

        # sprite setup
        self.player = self.create_map()

        # user interface
        self.ui = UI()
        self.upgrade_ui = UpgradeUI(UpgradeLogic(self.player))

        # display different special effect about the enemy attack and they being attack
        self.animation_effects = AnimationEffects()
        self.magic_effects = MagicEffects()
        
    def create_boundary_obstacle(self, x, y):
        Tile((x, y), [self.obstacle_sprites], "invisible")

    def create_grass_objects(self, graphics, x, y):
        random_grass_image = choice(graphics["grass"])
        Tile(
            (x, y),
            [
                self.visible_sprites,
                self.obstacle_sprites,
                self.attackable_sprites,
            ],
            "grass",
            random_grass_image,
        )
        
    def create_unattackable_objects(self, graphics, x, y, value):
        """Create unattackable objects, e.g. trees, rocks, statues.

        Args:
            graphics (_type_): _description_
            x (_type_): _description_
            y (_type_): _description_
            value (_type_): _description_
        """
        surf = graphics["objects"][int(value)]
        Tile(
            (x, y),
            [self.visible_sprites, self.obstacle_sprites],
            "object",
            surf,
        )
    
    def create_player(self, x, y):
        player = Player(
            (x, y),
            [self.visible_sprites],
            self.obstacle_sprites,
            self.create_attack,
            self.destroy_attack,
            self.create_magic,
        )
        return player

    
    def create_enemy(self, monster_names, x, y, value):
        Enemy(
            monster_names[value],
            (x, y),
            [self.visible_sprites, self.attackable_sprites],
            self.obstacle_sprites,
            self.damage_player,
            self.trigger_death_particles,
            self.add_exp,
        )
    
    def create_entity(self, entity_names, x, y, value):
        if entity_names[value] == "player":
            return self.create_player(x, y)
        else:
            self.create_enemy(entity_names, x, y, value)
            return None

    def create_map(self):
        layouts = {
            "boundary": import_csv_layout("../map/map_FloorBlocks.csv"),
            "grass": import_csv_layout("../map/map_Grass.csv"),
            "object": import_csv_layout("../map/map_Objects.csv"),
            "entities": import_csv_layout("../map/map_Entities.csv"),
        }
        graphics = {
            "grass": import_folder("../graphics/grass"),
            "objects": import_folder("../graphics/objects"),
        }
        
        entity_names = {
            "390": "bamboo",
            "391": "spirit",
            "392": "raccoon",
            "393": "squid",
            "394": "player",
        }
        
        player = None
        UNDEFINED = "-1"
        
        for style in layouts.keys():
            layout = layouts[style]
            row_len, col_len = layout.shape
            for row_index in range(row_len):
                for col_index in range(col_len):
                    value = layout[row_index, col_index]
                    
                    if value == UNDEFINED:
                        continue
                    x = col_index * TILESIZE
                    y = row_index * TILESIZE
                    if style == "boundary":
                        self.create_boundary_obstacle(x, y)
                    elif style == "grass":
                        self.create_grass_objects(graphics, x, y)
                    elif style == "object":
                        self.create_unattackable_objects(graphics, x, y, value)
                    elif style == "entities":
                        result = self.create_entity(entity_names, x, y, value)
                        if result is not None:
                            player = result
                    else:
                        pass
        
        return player

    def create_attack(self):
        self.current_attack = Weapon(
            self.player, [self.visible_sprites, self.attack_sprites]
        )

    def create_magic(self, style, strength, cost):
        if style == "heal":
            self.magic_effects.heal(self.player, strength, cost, [self.visible_sprites])

        if style == "flame":
            self.magic_effects.flame(
                self.player, cost, [self.visible_sprites, self.attack_sprites]
            )
        # print(style)
        # print(strength)
        # print(cost)

    def destroy_attack(self):
        if self.current_attack:
            self.current_attack.kill()
        self.current_attack = None

    def player_attack_logic(self):
        if self.attack_sprites:
            for attack_sprite in self.attack_sprites:
                collision_sprites = pygame.sprite.spritecollide(
                    attack_sprite, self.attackable_sprites, False
                )
                if collision_sprites:
                    for target_sprite in collision_sprites:
                        if target_sprite.sprite_type == "grass":
                            pos = target_sprite.rect.center
                            offset = pygame.math.Vector2(0, 70)
                            for leaf in range(randint(3, 6)):
                                self.animation_effects.create_grass_particles(
                                    pos - offset, [self.visible_sprites]
                                )
                            target_sprite.kill()
                        else:
                            target_sprite.get_damage(
                                self.player, attack_sprite.sprite_type
                            )

    def damage_player(
        self, amount, attack_type
    ):  # amount = the damage of enemy can deal for each attack, attack_type for different response
        if self.player.vulnerable:
            self.player.health -= amount
            self.player.vulnerable = False
            self.player.hurt_time = pygame.time.get_ticks()
            # spawn particles
            self.animation_effects.create_particles(
                attack_type, self.player.rect.center, [self.visible_sprites]
            )

    def trigger_death_particles(self, pos, particle_type):
        self.animation_effects.create_particles(
            particle_type, pos, [self.visible_sprites]
        )

    def add_exp(self, amount):
        self.player.exp += amount

    def toggle_menu(self):

        self.game_paused = not self.game_paused

    def update(self):
        self.visible_sprites.custom_draw(self.player)
        # debug(self.player.status)
        self.ui.display(self.player)

        #   if pause game not update
        if self.game_paused:
            self.upgrade_ui.display()
        else:
            # update and draw the game
            self.visible_sprites.update()
            # knowing the detail status
            self.visible_sprites.enemy_update(self.player)
            self.player_attack_logic()


class YSortCameraGroup(pygame.sprite.Group):
    def __init__(self):

        # general setup
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.half_width = self.display_surface.get_size()[0] // 2
        self.half_height = self.display_surface.get_size()[1] // 2
        self.offset = pygame.math.Vector2()

        # creating the floor
        self.floor_surf = pygame.image.load("../graphics/tilemap/ground.png").convert()
        self.floor_rect = self.floor_surf.get_rect(topleft=(0, 0))

    def custom_draw(self, player):

        # getting the offset
        self.offset.x = player.rect.centerx - self.half_width
        self.offset.y = player.rect.centery - self.half_height

        # drawing the floor
        floor_offset_pos = self.floor_rect.topleft - self.offset
        self.display_surface.blit(self.floor_surf, floor_offset_pos)

        # for sprite in self.sprites():
        for sprite in sorted(self.sprites(), key=lambda sprite: sprite.rect.centery):
            offset_pos = sprite.rect.topleft - self.offset
            self.display_surface.blit(sprite.image, offset_pos)

    def enemy_update(self, player):
        enemy_sprites = [
            sprite
            for sprite in self.sprites()
            if hasattr(sprite, "sprite_type") and sprite.sprite_type == "enemy"
        ]
        for enemy in enemy_sprites:
            enemy.enemy_update(player)
