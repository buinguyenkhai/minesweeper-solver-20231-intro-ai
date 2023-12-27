import pygame 
import os

# Background Color
BGCOLOR = (40, 40, 40) # Dark Grey

# Game Setting
TILESIZE = 30
FPS = 60
TITLE = "Minesweeper"
ROWS, COLS, AMOUNT_MINES = 16, 30, 99
WIDTH = TILESIZE * COLS
HEIGHT = TILESIZE * ROWS

def difficulty_settings(mode):
    global ROWS, COLS, AMOUNT_MINES, WIDTH, HEIGHT
    if mode == 1:
        ROWS = 10
        COLS = 10
        AMOUNT_MINES = 10
        
    elif mode == 2:
        ROWS = 16
        COLS = 16
        AMOUNT_MINES = 40
        
    elif mode == 3:
        ROWS = 16
        COLS = 30
        AMOUNT_MINES = 99
        
    WIDTH = TILESIZE * COLS
    HEIGHT = TILESIZE * ROWS

# Create Different Tiles Image
tile_numbers = []
for i in range(1, 9):
    tile_numbers.append(pygame.transform.scale(pygame.image.load(os.path.join("assets", f"Tile{i}.png")), (TILESIZE, TILESIZE)))
tile_empty = pygame.transform.scale(pygame.image.load(os.path.join("assets", "TileEmpty.png")), (TILESIZE, TILESIZE))
tile_exploded = pygame.transform.scale(pygame.image.load(os.path.join("assets", "TileExploded.png")), (TILESIZE, TILESIZE))
tile_flag = pygame.transform.scale(pygame.image.load(os.path.join("assets", "TileFlag.png")), (TILESIZE, TILESIZE))
tile_mine = pygame.transform.scale(pygame.image.load(os.path.join("assets", "TileMine.png")), (TILESIZE, TILESIZE))
tile_unknown = pygame.transform.scale(pygame.image.load(os.path.join("assets", "TileUnknown.png")), (TILESIZE, TILESIZE))
tile_not_mine = pygame.transform.scale(pygame.image.load(os.path.join("assets", "TileNotMine.png")), (TILESIZE, TILESIZE))

# Menu Settings
BG = pygame.image.load("assets/Background.png")

def get_font(size):
    return pygame.font.Font("assets/font.ttf", size)