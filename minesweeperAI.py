from itertools import combinations

class Sentence():
    '''
    Base unit containing information about the game.
    Consist of two main components: a set of tile and the number of mines in it.
    Provide knowledge for Minesweeper solver to decide future moves.
    '''
    def __init__(self, cells, count):
        # Set of cells
        self.cells = set(cells)
        
        # Number of mines in self.cells
        self.count = count

    def __eq__(self, other):
        '''Check equivalent sentences.'''
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        '''Print the sentence in the form: {(0, 0), (0, 1), (0, 2)} = 1'''
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        '''
        Examine mines that can be identified from a single sentence.
        Example: {(0, 0), (0, 1), (0, 2)} = 3 ==> all tiles in set are mines.
        '''
        # If number of tiles = number or mines ==> all tiles are mines
        # else nothing can be inferred from the sentence
        if len(self.cells) == self.count:
            return self.cells.copy()
        return set()

    def known_safes(self):
        '''
        Examine safe tiles that can be identified from a single sentence.
        Example: {(0, 0), (0, 1), (0, 2)} = 0 ==> all tiles in set are safe.
        '''
        # If number of mines = 0 ==> all tiles are safe
        # else nothing can be inferred from the sentence
        if self.count == 0:
            return self.cells.copy()
        return set()

    def mark_mine(self, cell):
        '''Mark tile as mine and remove it from the sentence.'''
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        '''Mark tile as safe and remove it from the sentence.'''
        if cell in self.cells:
            self.cells.remove(cell)
            
            
class Solver():
    '''Base class for a Minesweeper solver.'''
    
    def __init__(self, width, height, amount_mines, print_progress = True):
        # Set initial height and width and initial amount of mines
        self.width = width
        self.height = height
        self.amount_mines = amount_mines

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []
        
        # Set next uncertain move to make
        self.next_uncertain_move = None
        
        # Print game progress
        self.print_progress = print_progress
        
        # Number of guesses in a game
        self.guess = -1
        
    def mark_mine(self, cell):
        '''Mark tile as mine and remove it from every sentence in the agent's knowledge.'''
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        '''Mark tile as safe and remove it from every sentence in the agent's knowledge.'''
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)
            
    def add_sentence(self, cell, count):
        '''
        Examine tile's neighbourhood and number of surrounding mines, 
        form new sentence and add it to the agent's knowledge.
        '''
        cells = set()
        for x in range(cell[0] - 1, cell[0] + 2):
            for y in range(cell[1] - 1, cell[1] + 2):
                if (x, y) == cell:
                    continue
                
                if 0 <= x < self.width and 0 <= y < self.height:
                    if (x, y) in self.mines:
                        count -= 1
                        
                    else:
                        if (x, y) not in self.safes:
                           cells.add((x, y))
                           
        new_sentence = Sentence(cells, count)
        self.knowledge.append(new_sentence)
        
    def remove_null_sentence(self):
        '''Remove sentence with the form: set() = 0 (contain no information)'''
        for i in range(len(self.knowledge) - 1, -1, -1):
            if len(self.knowledge[i].cells) == 0:
                del self.knowledge[i]
  
    def remove_duplicated_sentence(self):
        '''Remove sentence that is equivalent to another one.'''
        duplicated_sentence_pos = set()
        
        # Store the position of duplicated sentences
        for i in range(len(self.knowledge) - 1):
            for j in range(i + 1, len(self.knowledge)):
                if self.knowledge[i] == self.knowledge[j]:
                    duplicated_sentence_pos.add(j)
        
        # Remove duplicated sentences           
        for pos in sorted(duplicated_sentence_pos, reverse = True):
            del self.knowledge[pos]
            
    def check_sentence(self):
        '''
        Traverse through every sentence, and mark any mines or safe tiles that can be
        identified from only the given sentence.
        '''
        mark_cell = True
        # The loop runs until there is no tile left to mark
        while mark_cell:
            mark_cell = False                 
            safe_cell = set() 
            mine_cell = set()
            
            # Collect info about mines and safe tiles
            for sentence in self.knowledge:
                safe_cell.update(sentence.known_safes())
                mine_cell.update(sentence.known_mines())
                
            # Mark safe tiles    
            for cell in safe_cell:
                mark_cell = True
                self.mark_safe(cell)
            # Mark mines    
            for cell in mine_cell:
                mark_cell = True
                self.mark_mine(cell) 
            
    def print_sentence(self):
        '''Display agent's knowledge.'''
        if self.print_progress:
            for sentence in self.knowledge:
                print(sentence)
            
    def add_knowledge(self, cell, count):
        '''
        Make change to the agent's knowledge and exploit as much information as possible from every sentence, 
        as well as remove all unnecessary sentences for further guesses.
        This may add, remove, merge or perform other actions with sentences the knowledge base.
        '''
        return NotImplementedError
    
    def analyze_knowledge(self):
        '''
        Perform further methods to identify any safe tiles or mines if no safe move can be made, 
        or choose uncertain move with lowest risk possible. 
        '''
        return NotImplementedError
    
    def make_safe_move(self):
        '''Perform a safe move if available, or return None if no such move can be made.'''
        allowed = list(self.safes.difference(self.moves_made))
        return allowed[0] if len(allowed) > 0 else None
    
    def choose_uncertain_move(self, best_informed_move, best_informed_move_risk, prob_dict):
        '''
        Choose uncertain move with lowest risk possible, by comparing the probability of containing
        a mine of the best tile that appears in at least one sentence vs. a random tile that does not
        appear in any sentences.
        '''
        # Estimate the average probability of hitting a mine if a totally random move is made
        unknown_tile = self.height * self.width - len(self.moves_made)
        unknown_mine = self.amount_mines - len(self.mines)
        estimated_average_risk = unknown_mine / unknown_tile
            
        # If the chosen tile's risk are lower than average risk, or every tile is flagged/revealed/contained in knowledge base:
        # that tile will be revealed in the next uncertain move
        if best_informed_move_risk <= estimated_average_risk or unknown_tile == len(prob_dict):
            self.next_uncertain_move = best_informed_move
        
        # else: a tile that does not appear in any sentences will be revealed
        else:
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in self.moves_made and (x, y) not in prob_dict:
                        self.next_uncertain_move = (x, y)
                        return
    
    
    def make_uncertain_move(self):
        '''Make uncertain move if all attempts for finding safe moves fail.'''
        # If the agent's knowledge is empty: traverses through the board until a hidden tile is found and returns it
        if len(self.knowledge) == 0:
            for y in range(self.height):
                for x in range(self.width):
                    if (x, y) not in self.moves_made and (x, y) not in self.mines:
                        return (x, y)
                    
        # else return move with lowest risk after calculation            
        return self.next_uncertain_move
    
    def make_move(self):
        '''Making next move and display it on the screen.'''
        # Check if all mines are flagged and flag if one isn't
        for mine in self.mines:
            if mine not in self.moves_made:
                self.moves_made.add(mine)
                
                if self.print_progress:
                    print("Flag mine: {}".format(mine))
                    print('---------------------')
                    
                return mine, 3
        
        # Perform a safe move if possible, or analyze knowledge base to find one
        if self.make_safe_move() == None:
            self.analyze_knowledge()
        
        move = self.make_safe_move()
        
        # Perform uncertain move if no safe move can be made
        if move == None:
            if self.print_progress:
                print("No known safe moves, AI making random move.")
                
            move = self.make_uncertain_move()
            self.guess += 1    
            
        else:
            if self.print_progress:
                print("AI making safe move.")
        
        # Display and return move
        if self.print_progress:    
            print("Move made: {}".format(move))
            print('---------------------')
            
        return move, 1
    
    def reset(self):
        '''Reset the solver for playing new games.'''
        self.moves_made.clear()
        self.mines.clear()
        self.safes.clear()
        self.knowledge.clear()
        self.next_uncertain_move = None
        self.guess = -1
    

class ProbabilitySolver(Solver):
    '''Solver that choose next move based on the probability of hitting mines of tiles.'''
    def add_knowledge(self, cell, count):
        '''
        Actions made:
        1. Mark previously revealed tile as safe and record new move.
        2. Add new sentence based on information about previous move.
        3. Check if new mines/safe tiles can be identified from individual sentence.
        4. Remove unnecessary sentence.
        '''
        # Mark previously revealed tile as safe and record new move
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        if count == 0:
            return
        
        # Add new sentence based on information about previous move
        self.add_sentence(cell, count)
        
        # Check if new mines/safe tiles can be identified from individual sentence
        self.check_sentence()
        
        # Remove unnecessary sentence
        self.remove_null_sentence()
        self.remove_duplicated_sentence()
        
        self.print_sentence()

        
class GenerateConfigurationSolver(ProbabilitySolver):
    '''
    Solver that calculate mines probability by enumerating all possible configurations
    that satisfy every sentence in knowledge base.
    '''
    def analyze_knowledge(self):
        '''
        Enumerating all possible configurations, and record the number of appearence
        of every tile in those configurations.
        After that, the tile that has the lowest number of appearence will be chosen
        to calculate risk, and compared with a random tile that does not appear in any
        sentences to make the final decision.
        '''
        if len(self.knowledge) == 0:
            return
        
        # Create a histogram for tiles
        cell_histogram = dict()
        for sentence in self.knowledge:
            for cell in sentence.cells:
                cell_histogram[cell] = 0
        
        # Generate all possible configurations        
        given_configuration = []
        possible_configuration = [set()]
        invalid_cell = set()
        
        # Algorithm based on breadth-first search to generate configuration
        for sentence in self.knowledge:
            given_configuration, possible_configuration = possible_configuration, given_configuration
            possible_configuration.clear()
            
            # Generate all configurations that satisfy first n sentence, based on a configuration that satisfy n - 1 first sentence
            for configuration in given_configuration:
                valid_cell = sentence.cells - invalid_cell
                missing_cell_num = sentence.count - (len(sentence.cells & configuration))
                
                # Abandon configurations that have already violated n-th sentence if we cannot add tiles in it to generate a satisfied one
                if missing_cell_num < 0:
                    continue
                
                # Add tile to configurations for feasible solutions    
                else:
                    possible_missing_cell = combinations(valid_cell, missing_cell_num)
                    for choice in possible_missing_cell:
                        possible_configuration.append(configuration.union(choice))
            
            # Tile that appeared in sentences cannot be added again when considering next ones         
            invalid_cell = invalid_cell | sentence.cells
            
        # Record the number of appearances of every tile in every configuration
        for configuration in possible_configuration:
            for cell in configuration:
                cell_histogram[cell] += 1
        
        # Check if any mines/safe tiles can be identified
        certain_move_found = False
        for cell in cell_histogram:
            if cell_histogram[cell] == 0:
                self.mark_safe(cell)
                certain_move_found = True
                
            elif cell_histogram[cell] == len(possible_configuration):
                self.mark_mine(cell)
        
        # else calculating move risk and decide the tile to reveal        
        if not certain_move_found:
            best_informed_move = min(cell_histogram, key = lambda cell: cell_histogram[cell])
            best_informed_move_risk = cell_histogram[best_informed_move] / len(possible_configuration)
            
            self.choose_uncertain_move(best_informed_move, best_informed_move_risk, cell_histogram)
            

class Probability():
    '''
    Object storing mine probability of a tile.
    '''
    def __init__(self):
        self.prob = 1

class ProbabilityTheorySolver(ProbabilitySolver):
    '''
    Solver that calculate mines probability using probability theory.
    '''
    def analyze_knowledge(self):
        '''
        Estimating the probability of containing a mine of every tile using
        probability theory.
        After that, the tile that has the lowest risk of being a mine
        will be compared with a random tile that does not appear in any
        sentences to make the final decision.
        '''
        if len(self.knowledge) == 0:
            return
        
        # Creating a dictionary for storing tiles' mine probability
        prob_dict = {}
        for sentence in self.knowledge:
            for cell in sentence.cells:
                prob_dict[cell] = prob_dict.get(cell, Probability())
        
        # Creating a list for future probability calculation        
        constraint_list = []
        for sentence in self.knowledge:
            # Creating a list that store probability of cells in a sentence together
            prob_constraint = []
            for cell in sentence.cells:
                prob_constraint.append(prob_dict[cell])
            
            constraint_list.append(prob_constraint)
        
        # Estimating mine probability
        # Formula: A = 1 - (1 - A1)(1 - A2)...(1 - An)
        # A: mine probability of a tile
        # Ai: mine probability of a tile considering only n-th sentence
        # (assume that all constraints are conditionally independent) 
        for sentence in self.knowledge:
            if len(sentence.cells) != 0:
                r = 1 - sentence.count / len(sentence.cells)
                
            for cell in sentence.cells:
                prob_dict[cell].prob *= r
                
        for cell in prob_dict:
            prob_dict[cell].prob = 1 - prob_dict[cell].prob
            
        # Check if any mines/safe tiles can be identified
        certain_move_found = False
        for cell in prob_dict:
            if prob_dict[cell] == 0:
                self.mark_safe(cell)
                certain_move_found = True
                
            elif prob_dict[cell] == 1:
                self.mark_mine(cell)
                
        # Recalculating probability in a constraint such that sum of all probability equals to
        # corresponding sentence's mine count while maintaining ratio of mine probability of 
        # every two tiles in it.
        
        # Mine probability of a tile in every constraint must be the same, so the process is
        # repeated for a number of times for every constraint to make all probabilities in these
        # converges to certain numbers.
        if not certain_move_found:
            for _ in range(30):
                for i in range(len(self.knowledge)):
                    if self.knowledge[i].count == 0:
                        norm = 1
                    else:
                        norm = self.knowledge[i].count / sum(cell.prob for cell in constraint_list[i])
                        
                    for cell in constraint_list[i]:
                        cell.prob *= norm
            
            # calculating move risk and decide the tile to reveal
            best_informed_move = min(prob_dict, key = lambda cell: prob_dict[cell].prob)
            best_informed_move_risk = prob_dict[best_informed_move].prob
            
            self.choose_uncertain_move(best_informed_move, best_informed_move_risk, prob_dict)
            

class SetBasedSolver(Solver):
    '''
    Solver that solve the board as a constraint satisfaction problem.
    Can use method from another ProbabilitySolver class to make uncertain move.
    '''
    def __init__(self, width, height, amount_mines, guess_method, print_progress = True):
        super().__init__(width, height, amount_mines, print_progress)
        
        # Guess method: 1: Generate all possible configurations, 2: Probability theory
        self.guess_method = guess_method
    
    def add_complement_sentence(self):
        '''
        Check if one sentence's cell set is a subset of another one,
        and update new sentence based on the complement of two cell set.
        Example: {(0, 1), (0, 2), (0, 3)} = 2, {(0, 1), (0, 2)} = 1 ==> {(0, 3)} = 1 
        '''
        for i in range(len(self.knowledge) - 1):
            for j in range(i + 1, len(self.knowledge)):
                s1 = self.knowledge[i]
                s2 = self.knowledge[j]
                
                # New sentence will have mine count = difference of two sentence' mine count
                if s1.count >= s2.count:
                    if s1.cells.issuperset(s2.cells):
                        s1.cells.difference_update(s2.cells)
                        s1.count -= s2.count
                        
                if s1.count <= s2.count:
                    if s1.cells.issubset(s2.cells):
                        s2.cells.difference_update(s1.cells)
                        s2.count -= s1.count
                        
    def add_intersection_sentence(self):
        '''
        Check if a new sentence can be made based on two sentences' intersection set of cells.
        New mines and safe tiles can also be found if such sentence exists.
        Example: {(0, 1), (0, 2), (0, 3)} = 2, {(0, 2), (0, 3), (0, 4)} = 1
        ==> {(0, 1)} - {(0, 4)} = 1 ==> (0, 1) is mine and (0, 4) is safe ==> {(0, 2), (0, 3)} = 1
        '''
        remove_set = set()
        for i in range(len(self.knowledge) - 1):
            for j in range(i + 1, len(self.knowledge)):
                if self.knowledge[i].count >= self.knowledge[j].count:
                    s1 = self.knowledge[i]
                    s2 = self.knowledge[j]
                    
                else:
                    s1 = self.knowledge[j]
                    s2 = self.knowledge[i]   
                     
                sub12 = s1.cells - s2.cells
                
                # New sentence will have the set cell = intersection of two sentences' cell set
                # and mine count = difference of two sentence' mine count
                if s1.count - s2.count == len(sub12):
                    for cell in sub12:
                        self.mark_mine(cell)
                    
                    sub21 = s2.cells - s1.cells
                    for cell in sub21:
                        self.mark_safe(cell)
                        
                    self.knowledge.append(Sentence(s1.cells.intersection(s2.cells), s2.count))
                    
                    # Add old sentences to remove set
                    remove_set.add(i)
                    remove_set.add(j)
        
        # Remove old sentence            
        for pos in sorted(remove_set, reverse = True):
            del self.knowledge[pos]
    
    def add_knowledge(self, cell, count):
        '''
        Actions made:
        1. Mark previously revealed tile as safe and record new move.
        2. Add new sentence based on information about previous move.
        3. Check if new mines/safe tiles can be identified from individual sentence.
        4. Check if new sentence can be made from old ones.
        5. Remove unnecessary sentence.
        '''
        # Mark previously revealed tile as safe and record new move
        self.moves_made.add(cell)
        self.mark_safe(cell)
        
        if count == 0:
            return
        
        # Add new sentence based on information about previous move
        self.add_sentence(cell, count)
        
        # Check if new sentence can be made from old ones
        # Remove unnecessary sentence
        self.remove_null_sentence()
        self.add_complement_sentence()
        
        # Check if new mines/safe tiles can be identified from individual sentence
        self.check_sentence()
        
        # Check if new sentence can be made from old ones
        # Remove unnecessary sentence
        self.remove_null_sentence()
        self.add_intersection_sentence()
        
        self.print_sentence()
        
    def analyze_knowledge(self):
        '''Perform further methods with the help of a ProbabilitySolver classes.'''
        self.remove_null_sentence()
        
        if self.guess_method == 1:
            GenerateConfigurationSolver.analyze_knowledge(self)
            
        elif self.guess_method == 2:
            ProbabilityTheorySolver.analyze_knowledge(self)