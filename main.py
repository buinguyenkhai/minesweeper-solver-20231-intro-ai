import pygame
import settings
from sprites import *
from minesweeperAI import *
from time import sleep
from button import Button
import sys

pygame.init()

SCREEN = pygame.display.set_mode((1280, 720))
pygame.display.set_caption(settings.TITLE)

class Minesweeper:
    '''Class for running Minesweeper game.'''
    def __init__(self):
        self.screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Game result
        self.win = None

    def new_game(self):
        '''Start a new game.'''
        self.board = Board()

    def run_game(self, ai = None, automated = False, end_screen = True, display = True):
        '''Run the game and print its state on the screen.'''
        self.playing = True
        
        while self.playing:
            if display:
                self.clock.tick(settings.FPS)
                
            self.events(ai = ai, automated = automated)
            
            if display:
                self.draw()
            # Run auto mode (only for AI games)
            if automated:
                for event in pygame.event.get():
                    self.check_quit(event)
                
        # Immediately start new game after finishing previous one
        if end_screen:        
            self.end_screen()

    def draw(self):
        '''Print game state on the screen.''' 
        self.screen.fill(settings.BGCOLOR)
        self.board.draw(self.screen)
        pygame.display.flip()
        
    def check_button(self, button, mx, my, ai = None):
        '''Check clicked button and the game's state after the click.'''
        if button == 1:
            if not self.board.board_list[mx][my].flagged:
                # Check first left click
                if not self.board.first_click:
                    self.board.place_mines(mx, my)
                    self.board.place_clues()
                    self.board.first_click = True
                    
                # dig and check if exploded
                if not self.board.dig(mx, my, ai = ai):
                    # explode and reveal all mines (and wrong flags)
                    for row in self.board.board_list:
                        for tile in row:
                            if tile.flagged and tile.type != "X":
                                tile.flagged = False
                                tile.revealed = True
                                tile.image = settings.tile_not_mine
                                
                            elif tile.type == "X":
                                tile.revealed = True
                                
                        self.playing = False    
                    
                    self.win = False
                    print('You lost!')
                    
        if button == 3:
            # Right click to flag/unflag
            if not self.board.board_list[mx][my].revealed:
                self.board.board_list[mx][my].flagged = not self.board.board_list[mx][my].flagged

    def check_win(self):
        '''Check win conditions.'''
        for row in self.board.board_list:
            for tile in row:
                # Check whether if all tiles (not mines) are dug or flagged
                if tile.type != 'X' and not tile.revealed:
                    return False
        return True
    
    def check_quit(self, event):
        '''Check if the user want to quit the game.'''
        if event.type == pygame.QUIT:
            pygame.quit()
            quit(0)
            
        if event.type == pygame.KEYDOWN: # ESC to return to main menu
            if event.key == pygame.K_ESCAPE:
                SCREEN = pygame.display.set_mode((1280, 720))
                main_menu()

    def events(self, ai = None, automated = False):
        '''Handle game events.'''
        # If an agent is used:
        if ai != None:
            # If auto mode is enabled: Continously perform moves until the game ends
            if automated:
                (mx, my), button = ai.make_move()
                self.check_button(button, mx, my, ai = ai)
            
            # If auto mode is disabled: Wait for the user to click the board to perform moves    
            else:
                for event in pygame.event.get():
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        (mx, my), button = ai.make_move()
                        self.check_button(button, mx, my, ai = ai)
                        
                    self.check_quit(event)
        
        # If no agent available: Play the game as normal
        else:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    mx //= settings.TILESIZE
                    my //= settings.TILESIZE
                    self.check_button(event.button, mx, my)
                    
                self.check_quit(event)
        
        # Check win condition
        if self.check_win():
            self.win = True
            self.playing = False
            
            for row in self.board.board_list:
                for tile in row:
                    # flagged all mines when won
                    if not tile.revealed:
                        tile.flagged = True
                        
            print('You won!')
                
    def end_screen(self):
        '''Check user's action: quit the game or start a new game.'''
        while True:
            for event in pygame.event.get():
                self.check_quit(event)
                
                # left click to restart
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return


def play_multiple_games(agent_type, iter, guess_method = 1):
    '''Perform multiple games and record AI agents' perfomance.'''
    win = 0
    lose = 0
    guess = 0
    win_guess = 0
    minesweeper = Minesweeper()
    
    if agent_type == 1:
        ai = GenerateConfigurationSolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, print_progress = False)
    elif agent_type == 2:
        ai = ProbabilityTheorySolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, print_progress = False)
    elif agent_type == 3:
        ai = SetBasedSolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, guess_method, print_progress = False)
    
    for game in range(1, iter + 1):
        minesweeper.new_game()
        minesweeper.run_game(ai = ai, automated = True, end_screen = False, display = False)
        
        if minesweeper.win:
            win += 1
            win_guess += ai.guess
        else:
            lose += 1
            
        guess += ai.guess
        
        print('Total number of games: %d' % game)
        print('Win: %d' % win)
        print('Lose: %d' % lose)
        print('Win percentage: %.4f' % (win / game))
        print('Average guess: %.3f' % (guess / game))
        if win > 0:
            print('Average guess when won: %.3f' % (win_guess / win))
        print('------------------------')
        
        if ai != None:
            ai.reset()
            
def main_menu():
    '''Main menu screen.'''
    while True:
        SCREEN.blit(settings.BG, (0, 0))

        MENU_MOUSE_POS = pygame.mouse.get_pos()

        MENU_TEXT = settings.get_font(100).render("MINESWEEPER", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 100))

        
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Play Rect.png"), pos=(640, 300), 
                            text_input="PLAY", font=settings.get_font(75), base_color="#d7fcd4", hovering_color="White")
        QUIT_BUTTON = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 500), 
                            text_input="QUIT", font=settings.get_font(75), base_color="#d7fcd4", hovering_color="White")

        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    choose_difficulty()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    quit(0)
        
        pygame.display.update()

def choose_difficulty():
    '''Choose Minesweeper game's difficulty.'''
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(settings.BG, (0, 0))

        DIFF_TEXT = settings.get_font(50).render("CHOOSE DIFFICULTY", True, "White")
        DIFF_RECT = DIFF_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(DIFF_TEXT, DIFF_RECT)

        BACK = Button(image=None, pos=(640, 600), 
                            text_input="BACK", font=settings.get_font(50), base_color="White", hovering_color="Green")

        BACK.changeColor(PLAY_MOUSE_POS)
        BACK.update(SCREEN)

        BEGINNER = Button(image=None, pos=(640, 260), 
                            text_input="Beginner", font=settings.get_font(45), base_color="White", hovering_color="Green")

        BEGINNER.changeColor(PLAY_MOUSE_POS)
        BEGINNER.update(SCREEN)


        INTER = Button(image=None, pos=(640, 360), 
                            text_input="Intermediate", font=settings.get_font(45), base_color="White", hovering_color="Green")

        INTER.changeColor(PLAY_MOUSE_POS)
        INTER.update(SCREEN)

        EXPERT = Button(image=None, pos=(640, 460), 
                            text_input="Expert", font=settings.get_font(45), base_color="White", hovering_color="Green")

        EXPERT.changeColor(PLAY_MOUSE_POS)
        EXPERT.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if BEGINNER.checkForInput(PLAY_MOUSE_POS):
                    settings.difficulty_settings(1)
                    choose_solver()
                if INTER.checkForInput(PLAY_MOUSE_POS):
                    settings.difficulty_settings(2)
                    choose_solver()
                if EXPERT.checkForInput(PLAY_MOUSE_POS):
                    settings.difficulty_settings(3)
                    choose_solver()
                if BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                    
        pygame.display.update()
        
def choose_solver():
    '''Choose Solver to play Minesweeper.'''
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(settings.BG, (0, 0))

        SOLV_TEXT = settings.get_font(55).render("CHOOSE SOLVER", True, "White")
        SOLV_RECT = SOLV_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(SOLV_TEXT, SOLV_RECT)

        BACK = Button(image=None, pos=(640, 600), 
                            text_input="BACK", font=settings.get_font(50), base_color="White", hovering_color="Green")

        BACK.changeColor(PLAY_MOUSE_POS)
        BACK.update(SCREEN)

        NO_AI = Button(image=None, pos=(640, 200), 
                            text_input="None", font=settings.get_font(45), base_color="White", hovering_color="Green")

        NO_AI.changeColor(PLAY_MOUSE_POS)
        NO_AI.update(SCREEN)


        GEN_CON = Button(image=None, pos=(640, 300), 
                            text_input="Generate Configuration Solver", font=settings.get_font(40), base_color="White", hovering_color="Green")

        GEN_CON.changeColor(PLAY_MOUSE_POS)
        GEN_CON.update(SCREEN)

        PROB = Button(image=None, pos=(640, 400), 
                            text_input="Probability Theory Solver", font=settings.get_font(40), base_color="White", hovering_color="Green")

        PROB.changeColor(PLAY_MOUSE_POS)
        PROB.update(SCREEN)

        SETB = Button(image=None, pos=(640, 500), 
                            text_input="Set Based Solver", font=settings.get_font(40), base_color="White", hovering_color="Green")

        SETB.changeColor(PLAY_MOUSE_POS)
        SETB.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if NO_AI.checkForInput(PLAY_MOUSE_POS):
                    minesweeper = Minesweeper()
                    while True:
                        minesweeper.new_game()
                        minesweeper.run_game()
                        
                if GEN_CON.checkForInput(PLAY_MOUSE_POS):
                    minesweeper = Minesweeper()
                    ai = GenerateConfigurationSolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, print_progress = True)
                    while True:
                        minesweeper.new_game()
                        minesweeper.run_game(ai, automated = True, end_screen=True)
                        ai.reset()
                        
                if PROB.checkForInput(PLAY_MOUSE_POS):
                    minesweeper = Minesweeper()
                    ai = ProbabilityTheorySolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, print_progress = True)
                    while True:
                        minesweeper.new_game()
                        minesweeper.run_game(ai, automated = True, end_screen=True)
                        ai.reset()
                        
                if SETB.checkForInput(PLAY_MOUSE_POS):
                    choose_guess_method()
                    
                if BACK.checkForInput(PLAY_MOUSE_POS):
                    choose_difficulty()
                    
        pygame.display.update()

def choose_guess_method():
    '''Choose method to perform uncertain move (only for SetBasedSolver).'''
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()

        SCREEN.blit(settings.BG, (0, 0))

        SOLV_TEXT = settings.get_font(55).render("CHOOSE GUESS METHOD", True, "White")
        SOLV_RECT = SOLV_TEXT.get_rect(center=(640, 100))
        SCREEN.blit(SOLV_TEXT, SOLV_RECT)

        BACK = Button(image=None, pos=(640, 600), 
                            text_input="BACK", font=settings.get_font(50), base_color="White", hovering_color="Green")

        BACK.changeColor(PLAY_MOUSE_POS)
        BACK.update(SCREEN)

        G_GENCON = Button(image=None, pos=(640, 300), 
                            text_input="Generate Configuration", font=settings.get_font(45), base_color="White", hovering_color="Green")

        G_GENCON.changeColor(PLAY_MOUSE_POS)
        G_GENCON.update(SCREEN)

        G_PROB = Button(image=None, pos=(640, 400), 
                            text_input="Probability Theory", font=settings.get_font(45), base_color="White", hovering_color="Green")

        G_PROB.changeColor(PLAY_MOUSE_POS)
        G_PROB.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit(0)
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if G_GENCON.checkForInput(PLAY_MOUSE_POS):
                    minesweeper = Minesweeper()
                    ai = SetBasedSolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, 1, print_progress=True)
                    while True:
                        minesweeper.new_game()
                        minesweeper.run_game(ai, automated = True, end_screen=True)
                        ai.reset()
                        
                if G_PROB.checkForInput(PLAY_MOUSE_POS):
                    minesweeper = Minesweeper()
                    ai = SetBasedSolver(settings.COLS, settings.ROWS, settings.AMOUNT_MINES, 2, print_progress=True)
                    while True:
                        minesweeper.new_game()
                        minesweeper.run_game(ai, automated = True, end_screen=True)
                        ai.reset()
                        
                if BACK.checkForInput(PLAY_MOUSE_POS):
                    choose_solver()
                    
        pygame.display.update()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main_menu()
    elif len(sys.argv) == 3:
        agent_type = int(sys.argv[1])
        iter = int(sys.argv[2])
        play_multiple_games(agent_type, iter)
    elif len(sys.argv) == 4:
        agent_type = int(sys.argv[1])
        iter = int(sys.argv[2])
        guess_method = int(sys.argv[3])
        play_multiple_games(agent_type, iter, guess_method)
    else:
        print('InvalidParameterError: Invalid number of parameters')
