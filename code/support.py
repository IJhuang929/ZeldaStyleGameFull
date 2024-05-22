import numpy as np
from csv import reader
from os import walk
import pygame

# from pprint import pprint


def import_csv_layout(path):
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=",")
        for row in layout:
            terrain_map.append(list(row))
        return np.asarray(terrain_map)


def import_folder(path):
    surface_list = []
    file_names = []
    for _, __, img_files in walk(path):
        for image_path in img_files:
            file_names.append(image_path)

    for i, image_path in enumerate(sorted(file_names)):
        full_path = path + "/" + image_path
        image_surf = pygame.image.load(full_path).convert_alpha()
        surface_list.append(image_surf)

    return surface_list
