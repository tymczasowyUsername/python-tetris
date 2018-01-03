import pygame
import numpy as np
import random
import copy
from time import time, sleep

#----------------------------------------------------------------------------------
white = (255, 255, 255)
black = (0, 0, 0)
#----------------------------------------------------------------------------------
gameboard_W = 500                                   # <300; 1500>  
blocks_in_line = 20                                 # <4; gameboard_W / 3> 
block_size = gameboard_W / blocks_in_line           # default = 25
blocks_in_column = 25                               # <4; 1000 / (gameboard_W / blocks_in_line)>

screen_W = int (gameboard_W + 0.5 * gameboard_W)    # gameboard - 500, scoreboard - 250
screen_H = int (block_size * blocks_in_column)
x = int (blocks_in_line / 2 - 2)                    # blocks spawn coordinates
                                                    # see class Items
assert 300 <= gameboard_W <= 1500, '300 < {} < 1500 - statement must be true'.format (gameboard_W)
assert 4 <= blocks_in_line <= 150, '4 < {} < 1500 - statement must be true'.format (blocks_in_line)
assert 4 <= blocks_in_column <= block_size, '4 < {} < {}  - statement must be true'.format (blocks_in_line, block_size)
#----------------------------------------------------------------------------------
pygame.init()
Display = pygame.display.set_mode ((screen_W, screen_H))
Time = pygame.time.Clock()
Event = pygame.event
font = pygame.font.Font ('freesansbold.ttf', 25)
font2 = pygame.font.Font ('freesansbold.ttf', 15)
#----------------------------------------------------------------------------------

class Board:
    """Board is game model. Array attribute controls values in each cell (every item
       is assigned to different value). Item is falling element which consists of 4 blocks.
       View is displaying game on screen."""

    def __init__ (self):

        self.array = np.zeros ((blocks_in_column, blocks_in_line), dtype = np.int8).view (Myarray)
        self.item = Items()
        self.view = Board_View (self.item)
        self.level = 1
        self.score = 0


    def generate_item (self):

        self.item = Items()
        

    def test_if_possible (self, x_inc, y_inc, list_to_test = None):
        ''' Test if movement or rotation or new item is not blocked by other blocks or borders'''

        if list_to_test is None: list_to_test = self.item.blocks

        try:
            new_list = [self.array[y + y_inc, x + x_inc] for (x, y) in list_to_test]
        except Exception:
            return 0, 0, 0, 1

        return new_list


    def move_item (self, direc):
        '''Moves item if possible, otherwise puts an item's number in array.'''

        if blocks_in_column in ([y for (x, y) in self.item.blocks]):
            self.save_to_array()
            self.generate_item()

        self.old_blocks = copy.copy (self.item.blocks)

        if direc == 'none':
            inc = (0, 1)

            if not any (self.test_if_possible (*inc)):
                self.item.update_blocks_XYs ([(x + inc[0], y + inc[1]) for (x, y) in self.item.blocks])
                self.view.display_item (self.old_blocks, self.item.blocks, self.item.colour)

            else:
                self.save_to_array()
                self.generate_item()
                self.view.display_item (self.item.blocks, self.item.blocks, self.item.colour)

                full_lines = self.get_full_lines()
                if full_lines:
                    self.update_board (full_lines)
                    self.update_scoreboard (len (full_lines), tick)
            return

        elif direc == 'left': 
            inc = (-1, 0)

        elif direc == 'right': 
            inc = (1, 0)

        if not any (self.test_if_possible (*inc)):
            self.item.update_blocks_XYs ([(x + inc[0], y + inc[1]) for (x, y) in self.item.blocks])
            self.view.display_item (self.old_blocks, self.item.blocks, self.item.colour)


    def save_to_array (self):
                
        for (x, y) in self.item.blocks:
            self.array[y, x] = self.item.id
        return 1         


    def rotate_item (self, key):
        
        to_test = self.item.get_post_rotation_XYs (key)

        if not any (self.test_if_possible (0, 0, to_test)):
            self.view.display_item (self.item.blocks, to_test, self.item.colour)
            self.item.update_blocks_XYs (to_test)


    def get_full_lines (self):

        full_lines = []

        for z in reversed (range (0, blocks_in_column)):
            if all (self.array[z]):
                full_lines.append(z)

            if len(full_lines) == 4:
                break

        if len (full_lines) > 0:
            return full_lines
        else:
            return 0


    def update_board (self, lines):
           
        j = lines[0]          
        
        for i in range (lines[0] - 1, 0, -1):
            if i in lines:
                continue

            if any (self.array[i]):
                copy_line = self.array[i]
            else:
                for x in range (i + len(lines), i, -1):
                    self.array[x] = blocks_in_line * [0]

                self.view.redraw_board ((self.array[i+1:lines[0]+1]), lines[0])
                return

            self.array[j] = copy_line
            j -= 1


    def update_scoreboard (self, num_of_lines_cleared, tick):

        self.score += 50 * num_of_lines_cleared ** 2
        self.view.view_scoreboard (self.level, self.score, black)        

        if self.score > self.level * 500:
            self.level += 1
            tick[0] *= 0.9
            pygame.time.set_timer (EVENT_MOVEDOWN, int(tick[0]))


class Board_View:
    '''Displays everything on screen.'''

    def __init__ (self, item):

        self.item = item
        Display.fill (black)    
        pygame.draw.rect (Display, (white), (gameboard_W, 0, int (1.5 * gameboard_W), screen_H))
        self.view_scoreboard (1, 0, black)
        self.display_item ([], self.item.blocks, self.item.colour)


    def display_block (self, x_start, y_start, color, x_inc = block_size, y_inc = block_size):

        pygame.draw.rect (Display, black, (x_start, y_start, x_inc, y_inc), 1)
        pygame.draw.rect (Display, color, (x_start + 1, y_start + 1, x_inc - 2, y_inc - 2))
        

    def display_item (self, old, new, color):

        for (a, b) in (old):
            self.display_block (a * block_size, b * block_size, black)

        for (c, d) in (new):
            self.display_block (c * block_size, d * block_size, color)


    def redraw_board (self, array, line_num):
        '''Redraws board after getting full line(s).'''
        
        rev_array = array[::-1]
        for y, line in enumerate(rev_array):
            for x in range (0, blocks_in_line):
                self.display_block (x * block_size, (line_num - y) * block_size, Items.shapes[rev_array[y, x]]['colour'])


    def view_scoreboard (self, level, score, colour):

        Display.blit (font.render (('Level ' + str (level)), True, colour), (int (gameboard_W * 1.1), 50))
        Display.blit (font.render (('Score: ' + str (score)), True, colour), (600, 150))

        
class Myarray (np.ndarray):

    def __getitem__ (self, n):

        if type (n) == tuple:
            y, x = n

            if (x < 0 or x > blocks_in_line - 1 or y < 0):
                raise Exception
            else:
                return np.ndarray.__getitem__ (self, n)
        else:
            return np.ndarray.__getitem__ (self, n)

        
class Items:
    ''' Items are falling objects, which consists of 4 blocks. Each has id - number stored in elements of array
        when item reaches any obstacle and different colour.'''
            
    shapes = [{'id':0,                                                    'colour': black},            # None
              {'id':1, 'blocks':[(x,   0), (x,   1), (x+1, 0), (x+1, 1)], 'colour': (205, 205, 122)},  # O-shape   
              {'id':2, 'blocks':[(x-1, 0), (x,   0), (x+1, 0), (x+2, 0)], 'colour': (54, 145, 174)},   # I-shape
              {'id':3, 'blocks':[(x,   1), (x+1, 1), (x+2, 1), (x+2, 0)], 'colour': (176, 196, 222)},  # L-shape
              {'id':4, 'blocks':[(x,   0), (x+1, 1), (x,   1), (x+2, 1)], 'colour': (152, 52, 80)},    # L-shape (reversed)
              {'id':5, 'blocks':[(x,   0), (x+1, 0), (x+1, 1), (x+2, 1)], 'colour': (1, 142, 52)},     # S-shape
              {'id':6, 'blocks':[(x,   1), (x+1, 1), (x+1, 0), (x+2, 0)], 'colour': (205, 99, 71)},    # S-shape (reversed)
              {'id':7, 'blocks':[(x,   0), (x+1, 0), (x+1, 1), (x+2, 0)], 'colour': (153, 85, 147)}]   # T-shape


    def __init__ (self):

        self.number = random.randint (1, 7)
        self.__dict__ = copy.deepcopy (Items.shapes[self.number])


    def get_post_rotation_XYs (self, key): 
        ''' Returns blocks' XYs after rotation; centre of rotation is second block in blocks attribute.'''

        dist_from_centre_of_rotation = [(x - self.blocks[1][0], y - self.blocks[1][1]) for (x, y) in self.blocks]

        if key == 'up':
            new_blocks = [(self.blocks[1][0] - y, self.blocks[1][1] + x) for (x, y) in dist_from_centre_of_rotation]
                 
        elif key == 'down':
            new_blocks = [(self.blocks[1][0] + y, self.blocks[1][1] - x) for (x, y) in dist_from_centre_of_rotation]                
        
        return new_blocks   


    def update_blocks_XYs (self, new_list):
        
        self.blocks[:] = new_list

        
board = Board()

tick = [1000]
previous_time = time()
EVENT_MOVEDOWN = pygame.USEREVENT + 1
pygame.time.set_timer (EVENT_MOVEDOWN, tick[0])

while 1:
    pygame.display.update()

    if time() - previous_time > 0.2:
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT]:
            board.move_item ('left')
            previous_time = time()    

        elif key[pygame.K_RIGHT]:
            board.move_item ('right')
            previous_time = time() 
            
        elif key[pygame.K_UP]:
            board.rotate_item ('up')
            previous_time = time()

        elif key[pygame.K_DOWN]:
            board.rotate_item ('down')
            previous_time = time()

    for event in Event.get():       
        if event.type == EVENT_MOVEDOWN:
            board.move_item ('none')

        if event.type == pygame.QUIT:
            quit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pygame.time.set_timer (EVENT_MOVEDOWN, int(tick[0]/20))

        if event.type  == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                pygame.time.set_timer (EVENT_MOVEDOWN, int(tick[0]))
