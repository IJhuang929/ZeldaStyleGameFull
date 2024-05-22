import pygame
from particles import AnimationEffects
from settings import *
from random import randint


class MagicEffects(AnimationEffects):
    def __init__(self):
        super().__init__()
        self.sounds = {
            "heal": pygame.mixer.Sound("../audio/heal.wav"),
            "flame": pygame.mixer.Sound("../audio/Fire.wav"),
        }
        self.sounds["heal"].set_volume(0.3)
        self.sounds["flame"].set_volume(0.2)

    def heal(self, player, strength, cost, groups):
        if player.energy < cost:
            return

        self.sounds["heal"].play()
        player.health += strength
        player.energy -= cost
        if player.health >= player.stats["health"]:
            player.health = player.stats["health"]
        self.create_particles("aura", player.rect.center, groups)
        self.create_particles(
            "heal", player.rect.center + pygame.math.Vector2(0, -55), groups
        )

    def flame(self, player, cost, groups):
        """five stage for speacial effects, should know the direction currently face"""
        if player.energy < cost:
            return
        player.energy -= cost
        self.sounds["flame"].play()

        if player.status.split("_")[0] == "right":
            direction = pygame.math.Vector2(1, 0)
        elif player.status.split("_")[0] == "left":
            direction = pygame.math.Vector2(-1, 0)
        elif player.status.split("_")[0] == "up":
            direction = pygame.math.Vector2(0, -1)
        else:
            direction = pygame.math.Vector2(0, 1)
        # offset for five frame
        for i in range(1, 6):  # horizontal
            if direction.x:
                offset_x = (direction.x * i) * TILESIZE
                x = (
                    player.rect.centerx
                    + offset_x
                    + randint(-TILESIZE // 3, TILESIZE // 3)
                )
                y = player.rect.centery + randint(-TILESIZE // 3, TILESIZE // 3)
                self.create_particles("flame", (x, y), groups)
            else:  # verticle
                offset_y = (direction.y * i) * TILESIZE
                x = player.rect.centerx + randint(-TILESIZE // 3, TILESIZE // 3)
                y = (
                    player.rect.centery
                    + offset_y
                    + randint(-TILESIZE // 3, TILESIZE // 3)
                )
                self.create_particles("flame", (x, y), groups)
