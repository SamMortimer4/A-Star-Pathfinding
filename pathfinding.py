import pygame
import math
from queue import PriorityQueue

WIDTH = 720
WIN = pygame.display.set_mode((WIDTH, WIDTH))
pygame.display.set_caption("A* Pathfinding")

class GridSquare:

    def __init__(self, row, col, width, total_rows, state):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.colour = [255,255,255]
        self.neighbours = []
        self.width = width
        self.total_rows = total_rows
        self.state = state

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.state == "closed"

    def is_open(self):
        return self.state == "open"

    def is_barrier(self):
        return self.state == "barrier"

    def is_start(self):
        return self.state == "start"

    def is_end(self):
        return self.state == "end"

    def reset(self):
        self.state = "init"
        self.colour = [255,255,255]

    def make_closed(self):
        self.state = "closed"
        self.colour = [200,200,200]

    def make_open(self):
        self.state = "open"
        self.colour = [170,200,170]

    def make_barrier(self):
        self.state = "barrier"
        self.colour = [0,0,0]

    def make_start(self):
        self.state = "start"
        self.colour = [255,255,0]

    def make_end(self):
        self.state = "end"
        self.colour = [0,255,255]

    def make_path(self):
        self.state = "path"
        self.colour = [255,0,0]

    def draw(self, win):
        pygame.draw.rect(win, self.colour, (self.x, self.y, self.width, self.width))

    def update_neighbours(self, grid):
        self.neighbours = []

        if self.row < self.total_rows - 1 and not grid[self.row+1][self.col].is_barrier(): # DOWN
            self.neighbours.append(grid[self.row+1][self.col])

        if self.row > 0 and not grid[self.row-1][self.col].is_barrier(): # UP
            self.neighbours.append(grid[self.row-1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col+1].is_barrier(): # RIGHT
            self.neighbours.append(grid[self.row][self.col+1])

        if self.col > 0 and not grid[self.row][self.col-1].is_barrier(): # LEFT
            self.neighbours.append(grid[self.row][self.col-1])

    def __lt__(self, other):
        return False


def h(p1,p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1-x2) + abs(y1-y2)

def paint_path(came_from, current, draw):
    while current in came_from:
        current = came_from[current]
        current.make_path()
        draw()

def a_star(draw,grid,start,end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0,count,start))
    came_from = {}
    g_score = {square: float("inf") for row in grid for square in row}
    g_score[start] = 0
    f_score = {square: float("inf") for row in grid for square in row}
    f_score[start] = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}
    while not open_set.empty():

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            paint_path(came_from, end, draw)
            return True

        for neighbour in current.neighbours:
            temp_g_score = g_score[current] +1
            if temp_g_score < g_score[neighbour]:
                came_from[neighbour] = current
                g_score[neighbour] = temp_g_score
                f_score[neighbour] - temp_g_score + h(neighbour.get_pos(), end.get_pos())
                if neighbour not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbour], count, neighbour))
                    open_set_hash.add(neighbour)
                    neighbour.make_open()

        draw()

        if current != start:
            current.make_closed()

    return None

def make_grid(rows,width):
    grid = []
    square_size = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            square = GridSquare(i,j,square_size,rows,"init")
            grid[i].append(square)
    return grid

def draw_grid(win, rows, width):
    square_size = width // rows
    for i in range(rows):
        pygame.draw.line(win, (50,50,50), (0, i*square_size), (width, i*square_size))
        for j in range(rows):
            pygame.draw.line(win, (50, 50, 50), (j * square_size, 0), (j * square_size, width))

def draw(win, grid, rows, width):
    win.fill((255,255,255))
    for row in grid:
        for square in row:
            square.draw(win)
    draw_grid(win, rows, width)
    pygame.display.update()

def get_clicked_pos(pos, rows, width):
    square_size = width // rows
    y, x = pos

    row = y // square_size
    col = x // square_size

    return row,col

def main(win,width):
    ROWS = 24
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while(run):
        draw(win,grid,ROWS,width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if started:
                continue

            if pygame.mouse.get_pressed()[0]: # LMB
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                if 0 <= row < ROWS and 0 <= col < ROWS:
                    square = grid[row][col]
                    if square!=start and square != end:
                        if not start:
                            start = square
                            start.make_start()
                        elif not end:
                            end = square
                            end.make_end()
                        else:
                            square.make_barrier()
            elif pygame.mouse.get_pressed()[2]: # RMB
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_pos(pos, ROWS, width)
                square = grid[row][col]
                square.reset()
                if square == start:
                    start = None
                elif square == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and not started:
                    for row in grid:
                        for square in row:
                            square.update_neighbours(grid)

                    a_star(lambda: draw(win, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


main(WIN, WIDTH)