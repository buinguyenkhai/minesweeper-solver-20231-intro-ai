import pygame
import random
import settings

# Types:
# ".": unknown
# "X": mine
# "C": Clue
# "/": empty

class Tile:
    '''
    A small square which contains mine or information about adjacent tiles.
    Base unit of Minesweeper game.
    '''
    def __init__(self, x, y, image, tile_type, nearby_mine = 0, revealed=False, flagged=False):
        # Tile coordinate
        self.x, self.y = x * settings.TILESIZE, y * settings.TILESIZE
        
        # Tile type and number of adjacent mines
        self.image = image
        self.type = tile_type
        self.nearby_mine = nearby_mine
        
        # Tile state
        self.revealed = revealed
        self.flagged = flagged

    def draw(self, board_surface):
        '''Draw the tile on the screen.'''
        # if not flagged and revealed -> draw the tile over the board
        if not self.flagged and self.revealed:
            board_surface.blit(self.image, (self.x, self.y))
            
        # if flagged and not already revealed -> draw the flag over the board
        elif self.flagged and not self.revealed:
            board_surface.blit(settings.tile_flag, (self.x, self.y))
            
        # unknown tiles
        elif not self.revealed:
            board_surface.blit(settings.tile_unknown, (self.x, self.y))
        

class Board:
    '''
    Rectangle board containing Tiles.
    Main component of a Minesweeper games.
    '''
    def __init__(self):
        self.board_surface = pygame.Surface((settings.WIDTH, settings.HEIGHT))
        
        # Create a board matrix with Tile object
        self.board_list = [[Tile(col, row, settings.tile_empty, ".") for row in range(settings.ROWS)] for col in range(settings.COLS)]
        
        # First click made or not
        self.first_click = False
        
        # List of revealed tiles
        self.dug = []

    def place_mines(self, fcx, fcy):
        '''Place mines on random tiles on the board.'''
        # Place mines
        for _ in range(settings.AMOUNT_MINES):
            # Loop to avoid duplicates
            while True:
                # get random pos for mines
                x = random.randint(0, settings.COLS-1)
                y = random.randint(0, settings.ROWS-1)
                
                # if tile is blank and its position is different from first click position -> create a mine tile
                if self.board_list[x][y].type == "." and (x,y) != (fcx, fcy):
                    self.board_list[x][y].image = settings.tile_mine
                    self.board_list[x][y].type = "X"
                    break

    def place_clues(self):
        '''Check and set the number of adjacent mines to tiles that are not mines.'''
        for x in range(settings.COLS):
            for y in range(settings.ROWS):
                if self.board_list[x][y].type != "X":
                    # get clues number based on adjecent mines
                    total_mines = self.check_neighbours(x, y)
                    
                    if total_mines > 0:
                        self.board_list[x][y].image = settings.tile_numbers[total_mines - 1]
                        self.board_list[x][y].type = "C"
                        self.board_list[x][y].nearby_mine = total_mines
                        
    @staticmethod
    def is_inside(x, y):
        '''Check if given coordinate is inside the board.'''
        return 0 <= x < settings.COLS and 0 <= y < settings.ROWS

    def check_neighbours(self, x, y):
        '''Check number of adjacent mines to a tile.'''
        total_mines = 0
        # get neighbours coordinates
        for x_offset in range(-1, 2):
            for y_offset in range(-1, 2):
                neighbour_x = x + x_offset
                neighbour_y = y + y_offset
                
                # if inside the box and is a mine -> count mines
                if self.is_inside(neighbour_x, neighbour_y) and self.board_list[neighbour_x][neighbour_y].type == "X":
                    total_mines += 1
                    
        return total_mines 
    
    def draw(self, screen):
        '''Display the game board on the screen.'''
        # draw a blank board
        for row in self.board_list:
            for tile in row:
                tile.draw(self.board_surface)
                
        screen.blit(self.board_surface, (0, 0))

    def dig(self, x, y, ai = None):
        '''Reveal tiles types after chosen.'''
        # Dig the chosen tile
        self.dug.append((x, y))
        self.board_list[x][y].revealed = True
        
        # If a mine is dug -> dig = False -> Game Over
        if self.board_list[x][y].type == "X":
            self.board_list[x][y].image = settings.tile_exploded
            return False
        
        # Provide information for agent if used
        if ai != None:
            ai.add_knowledge((x, y), self.board_list[x][y].nearby_mine)
        
        # Reveal clues
        if self.board_list[x][y].type == "C":
            return True
        
        # Reveal empty tiles
        for row in range(max(0, x-1), min(settings.COLS-1, x+1)+1):
            for col in range(max(0, y-1), min(settings.ROWS-1, y+1)+1):
                if (row, col) not in self.dug:
                    # Recursively reveal empty tiles until a clue tile is revealed
                    self.dig(row, col, ai = ai)
        return True