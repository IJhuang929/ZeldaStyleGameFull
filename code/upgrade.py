import pygame
from settings import *

class UpgradeLogic:
    def __init__(self, player):
        # general setup
        self.player = player
        # number of attribute
        self.num_attributes = len(player.stats)

        # selection system
        self.selection_index = 0
        self.selection_time = -1
        self.upgrade_time = True
    
    
    def input(self):
        """set the control to attributes : (health, energy,attack,magic,speed),
        press m get into setting mode, than use left anf right to change it"""
        keys = pygame.key.get_pressed()

        if not self.upgrade_time:
            return
        
        if keys[pygame.K_RIGHT] and self.selection_index < self.num_attributes - 1:
            self.selection_index += 1
            self.upgrade_time = False
        elif keys[pygame.K_LEFT] and self.selection_index >= 1:
            self.selection_index -= 1
            self.upgrade_time = False
        elif keys[pygame.K_DOWN]:
            self._trigger(self.selection_index, -1)
            self.upgrade_time = False
        elif keys[pygame.K_UP]:
            self._trigger(self.selection_index, 1)
            self.upgrade_time = False
            
        if self.upgrade_time is False:
            self.selection_time = pygame.time.get_ticks()
        
    def selection_cooldown(self):
        """selection timer"""
        if self.upgrade_time:
            return
        current_time = pygame.time.get_ticks()
        if current_time - self.selection_time >= 300:
            self.upgrade_time = True
    
    def _trigger(self, index, value):
        upgrade_attribute = list(self.player.stats.keys())[index]
        # print(upgrade_attribute)
        if (
            self.player.exp >= self.player.upgrade_cost[upgrade_attribute]
            and self.player.stats[upgrade_attribute] < self.player.max_stats[upgrade_attribute]
        ):
            self.player.exp -= self.player.upgrade_cost[upgrade_attribute]
            scale = 1.2 if value == 1 else 1/1.2
            self.player.stats[upgrade_attribute] *= scale
            scale = 1.4 if value == 1 else 1/1.4
            self.player.upgrade_cost[upgrade_attribute] *= scale

        if self.player.stats[upgrade_attribute] > self.player.max_stats[upgrade_attribute]:
            self.player.stats[upgrade_attribute] = self.player.max_stats[upgrade_attribute]


class UpgradeUI:
    def __init__(self, upgrade_logic: UpgradeLogic):
        self.upgrade_logic = upgrade_logic
        
        # general setup
        self.display_surface = pygame.display.get_surface()
        # number of attribute
        self.num_attributes = self.upgrade_logic.num_attributes
        self.attribute_names = list(self.upgrade_logic.player.stats.keys())
        self.max_values = list(self.upgrade_logic.player.max_stats.values())
        self.font = pygame.font.Font(UI_FONT, UI_FONT_SIZE)

        # item creation
        self.height = self.display_surface.get_size()[1] * 0.8
        self.width = self.display_surface.get_size()[0] // 6

        self.create_items()
        
    def create_items(self):
        self.item_list = []

        for index in range(self.num_attributes):
            # honrizontal position
            full_width = self.display_surface.get_size()[0]
            increment = full_width // self.num_attributes
            left = (index * increment) + (increment - self.width) // 2

            # verticle position
            top = self.display_surface.get_size()[1] * 0.1

            # create the object
            self.item_list.append(ItemUI(left, top, self.width, self.height, index, self.font))

    def display(self):
        # self.display_surface.fill("black")
        self.upgrade_logic.input()
        self.upgrade_logic.selection_cooldown()
        
        for index, item in enumerate(self.item_list):
            # get attribute
            name = self.attribute_names[index]
            value = self.upgrade_logic.player.get_value_by_index(index)
            max_value = self.max_values[index]
            cost = self.upgrade_logic.player.get_cost_by_index(index)
            item.display(
                self.display_surface, self.upgrade_logic.selection_index, name, value, max_value, cost
            )


class ItemUI:
    """create the item of attribute"""

    # (left, top, width, height, index, font)
    def __init__(self, l, t, w, h, index, font):
        self.rect = pygame.Rect(l, t, w, h)
        self.index = index
        self.font = font

    def display_names(self, surface, name, cost, selected):
        color = TEXT_COLOR_SELECTED if selected else TEXT_COLOR

        # title
        title_surf = self.font.render(name, False, color)
        title_rect = title_surf.get_rect(
            midtop=self.rect.midtop + pygame.math.Vector2(0, 20)
        )
        # cost
        cost_surf = self.font.render(f"{int(cost)}", False, color)
        cost_rect = cost_surf.get_rect(
            midbottom=self.rect.midbottom - pygame.math.Vector2(0, 20)
        )
        # draw
        surface.blit(title_surf, title_rect)
        surface.blit(cost_surf, cost_rect)

    def display_bar(self, surface, value, max_value, selected):

        # drawing setup
        top = self.rect.midtop + pygame.math.Vector2(0, 60)
        bottom = self.rect.midbottom - pygame.math.Vector2(0, 60)
        color = BAR_COLOR_SELECTED if selected else BAR_COLOR

        # bar setup
        full_height = bottom[1] - top[1]
        relative_number = (value / max_value) * full_height
        value_rect = pygame.Rect(top[0] - 15, bottom[1] - relative_number, 30, 10)

        # draw element
        pygame.draw.line(surface, color, top, bottom, 5)
        pygame.draw.rect(surface, color, value_rect)


    def display(self, surface, selection_num, name, value, max_value, cost):
        if self.index == selection_num:
            pygame.draw.rect(surface, UPGRADE_BG_COLOR_SELECTED, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)
        else:
            pygame.draw.rect(surface, UI_BG_COLOR, self.rect)
            pygame.draw.rect(surface, UI_BORDER_COLOR, self.rect, 4)

        self.display_names(surface, name, cost, self.index == selection_num)
        self.display_bar(surface, value, max_value, self.index == selection_num)
