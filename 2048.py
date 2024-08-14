import pygame
import random
import math

pygame.init()

FPS = 60

width,height = 800,800
rows = 4
cols = 4
rect_height = height//rows
rect_width = width//cols

out_color = (187,173,160)
out_thickness = 10
bg_color = (205,192,180)#(211,211,211)
font_color = (112, 103, 94)

font = pygame.font.SysFont("comicsans",60,bold = True)
Move_vel = 20

WINDOW = pygame.display.set_mode((width,height))
pygame.display.set_caption("  2048 by Naman  ")

class Tile:
    colors = [(237, 229, 218),
              (238, 225, 201),
              (243, 178, 122), 
              (246, 150, 101), 
              (247, 124, 95),           #DEFAULT COLORS OF 2048 TILES
              (247, 95, 59), 
              (237, 208, 115),
              (237, 204, 99), 
              (236, 202, 80)]
    
    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * rect_width
        self.y = row * rect_height

    def get_color(self):
        color_index = int(math.log2(self.value)) - 1
        color = self.colors[color_index]
        return color
    
    def draw(self,window):
        color = self.get_color()
        pygame.draw.rect(window,color,(self.x,self.y,rect_width,rect_height))

        text = font.render(str(self.value), 1 ,font_color)
        window.blit(text, 
                    (
                self.x + (rect_width / 2 - text.get_width() / 2),
                self.y + (rect_height / 2 - text.get_height() / 2),
            ),
        )               #blit is used to put surface in the screen

    def set_pos(self,ceil = False):
        if ceil:
            self.row = math.ceil(self.y / rect_height)
            self.col = math.ceil(self.x / rect_width)
        else:
            self.row = math.floor(self.y / rect_height)
            self.col = math.floor(self.x / rect_width)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

def draw_grid(window):
    for row in range(1,rows):
        y = row* rect_height
        pygame.draw.line(window,out_color,(0,y), (width,y),out_thickness)

    for col in range(1,cols):
        x = col* rect_width
        pygame.draw.line(window,out_color,(x,0), (x,height),out_thickness)

    pygame.draw.rect(window, out_color, (0,0,width,height),out_thickness)

def draw(window,tiles):               #DOES THE DRAWING STUFF AND IS UPDATED IN WHOLE AT THE END 
    window.fill(bg_color)       #BG COLOR IS BEING FILLED

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)

    pygame.display.update()

def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0,rows)
        col = random.randrange(0,cols)
        if  f"{row}{col}" not in tiles:
            break
    return row,col

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()

    if direction == 'left':
        sort_func = lambda x: x.col
        reverse = False
        delta = (-Move_vel,0)
        boundary_check = lambda tile: tile.col == 0 
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col - 1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + Move_vel   
        move_check = (lambda tile, next_tile: tile.x > next_tile.x + rect_width + Move_vel)
        ceil = True
    elif direction == 'right':
        sort_func = lambda x: x.col
        reverse = True
        delta = (Move_vel, 0)
        boundary_check = lambda tile: tile.col == cols - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col + 1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - Move_vel
        move_check = (
            lambda tile, next_tile: tile.x + rect_width + Move_vel < next_tile.x)
        ceil = False
    elif direction == 'up':
        sort_func = lambda x: x.row
        reverse = False
        delta = (0, -Move_vel)
        boundary_check = lambda tile: tile.row == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row - 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + Move_vel
        move_check = (
            lambda tile, next_tile: tile.y > next_tile.y + rect_height + Move_vel
        )
        ceil = True 
    elif direction == 'down':
        sort_func = lambda x: x.row
        reverse = True
        delta = (0, Move_vel)
        boundary_check = lambda tile: tile.row == rows - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row + 1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - Move_vel
        move_check = (
            lambda tile, next_tile: tile.y + rect_height + Move_vel < next_tile.y
        )
        ceil = False
    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key = sort_func, reverse = reverse)

        for i,tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue

            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif (
                tile.value == next_tile.value
                and tile not in blocks
                and next_tile not in blocks
            ):
                if merge_check(tile,next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue

            tile.set_pos(ceil)
            updated = True

        updates_tiles(window,tiles,sorted_tiles)
    return end_moves(tiles)


def end_moves(tiles):
    if len(tiles) == 16:
        return "lost"
    row,col = get_random_pos( tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]),row,col)
    return 'continue'

def updates_tiles(window,tiles,sorted_tiles ):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile 
    draw(window,tiles)

def generate_tiles():
    tiles  = {}
    for _ in range(2):
        row,col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2,row,col)

    return tiles


def main(window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    move_tiles(window,tiles,clock,"left")
                if event.key == pygame.K_RIGHT:
                    move_tiles(window,tiles,clock,"right")
                if event.key == pygame.K_UP:
                    move_tiles(window,tiles,clock,"up")
                if event.key == pygame.K_DOWN:
                    move_tiles(window,tiles,clock,"down") 

            
        draw(window,tiles)
    pygame.quit()  


if __name__ == "__main__":
    main(WINDOW)
    