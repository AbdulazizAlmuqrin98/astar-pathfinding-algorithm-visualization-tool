import pygame
import math
from queue import PriorityQueue

WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding Algorithm")

RED = (255, 0 ,0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQOUISE = (64, 224, 208)

class Spot:

    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_opened(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQOUISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQOUISE

    def make_path(self):
        self.color = PURPLE


    def draw(self, win):
        """ colors a spot on the screen with its self color """

        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        """ Checks each side of the spot whether they are barriers or not..... if not, add them to neighbors list"""

        self.neighbors = []

        # Check IF not the last row AND IF spot BELOW current spot is not a barrier.... if not, then add to neighbors
        # list
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        # Check IF not the first row AND IF spot ABOVE the current spot is not a barrier.... if not, then add to
        # neighbors list
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():
            self.neighbors.append(grid[self.row - 1][self.col])

        # Check IF not the last column AND IF spot to the RIGHT of the current spot is barrier.... if not,
        # then add to neighbors list
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col + 1])

        # Check IF not the first column AND IF spot to the LEFT of the current spot is barrier.... if not,
        # then add to neighbors list
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():
            self.neighbors.append(grid[self.row][self.col - 1])


    def __lt__(self, other):
        return False

def h(p1, p2):
    """ The Manhattan distance heuristic function for the algorithm.
    It takes in a tuple of points p1 & p2 """

    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def reconstruct_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    came_from = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_pos(), end.get_pos())

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(came_from, end, draw)
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1

            if temp_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        draw()

        if current != start:
            current.make_closed()

    return False


def make_grid(rows, width):
    """ Builds a 2D list of nodes (not the gridlines)..... does not draw in the display window... just used as a
    reference by the display window """
    grid = []
    gap = width // rows
    for i in range(rows):
        # create a list for each row, resulting in a 2D list
        grid.append([])
        for j in range(rows):
            # fills each column in the list with spot objects
            spot = Spot(i, j, gap, rows)
            grid[i].append(spot) # append at the last position of the list so no need to specify the col index (j)

    # return 2D list of spot objects
    return grid

def draw_gridlines(win, rows, width):
    """ Draws the gridlines in the display window (not the nodes) """

    gap = width // rows
    for i in range(rows):
        # draws the horizontal lines ( specify start and end points (x,y) )
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(win, GREY, (j*gap, 0), (j*gap, width))

def draw(win, grid, rows, width):
    """ Main draw function that draws the gridlines (calls draw_gridlines) and colors the nodes in the display window based on the 2D list
    of nodes (that was built in make_grid function) """

    win.fill(WHITE)

    # color that position in the grid with the spot object color
    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_gridlines(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    """ Return the position of the spot we clickedd on """
    gap = width // rows
    y, x = pos

    row = y // gap
    col = x // gap

    return row, col

def main(win, width):
    ROWS = 50
    grid = make_grid(ROWS, width) # grid is just a 2D list of spot objects

    # start and end index to reference spot positions in the grid
    start = None
    end = None

    # some flags
    # run = if main loop is running
    # started = if algorithm started

    run = True
    started = False

    while run:

        draw(win, grid, ROWS, width)

        # for evry iteration of the while loop, check for events that happened (mouse clicked, keyboard pressed, etc...)
        for event in pygame.event.get():

            # if close button was pressed
            if event.type == pygame.QUIT:
                run = False

            # if algorithm started running
            if started:
                continue

            # Left mouse button press
            if pygame.mouse.get_pressed()[0]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()


            # Right mouse button press
            elif pygame.mouse.get_pressed()[2]:
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None
                elif spot == end:
                    end = None

            # Keyboard pressed event
            if event.type == pygame.KEYDOWN:
                # If spacebar key pressed, update neighbors then start the algorithm
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for spot in row:
                            spot.update_neighbors(grid)

                    algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)
    pygame.quit()

main(WIN, WIDTH)




