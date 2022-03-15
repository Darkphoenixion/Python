import pygame as pg

import sys
import random
import time

import copy

FPS = 60
CASE_SIZE = 32
WINDOW_WIDTH = 20
WINDOW_HEIGHT = 24
WINDOW_SIZE = (CASE_SIZE * WINDOW_WIDTH, CASE_SIZE * (WINDOW_HEIGHT+1))

MAX_MOVE_TIME = 400
MIN_MOVE_TIME = 100
STEP_DECREASE = 25
SPEED_TIME = 10000
SUPER_FOOD_TIME = 6500
ALPHA_TIME = 500

FONT_COLOR = (1, 1, 1)
GREEN_COLOR = (92, 242, 0)
GRASS_COLOR = (50, 192, 0)
SNAKE_HEAD_COLOR = (85, 85, 85)
SNAKE_BODY_COLOR = (125, 125, 125)
FOOD_COLOR = (200, 150, 20)
SUPER_FOOD_COLOR = (235, 0, 0)
ALPHA = 235
ALPHA_TRANSP = 150

NORTH = pg.math.Vector2((0, -1))
SOUTH = pg.math.Vector2((0, 1))
EAST = pg.math.Vector2((1, 0))
WEST = pg.math.Vector2((-1, 0))
ZERO = pg.math.Vector2((0, 0))

SUPER_FOOD = 5
FOOD = 1

pg.init()
window = pg.display.set_mode(WINDOW_SIZE)
pg.display.set_caption("Snake")

clock = pg.time.Clock()


def quit_game():
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()


def generate_grid():
    _grid = []
    for x in range(WINDOW_WIDTH):
        for y in range(WINDOW_HEIGHT):
            _grid.append([x, y])
    return copy.deepcopy(_grid)


def key_input(direction: pg.Vector2):
    keys_pressed = pg.key.get_pressed()
    if keys_pressed[pg.K_UP] and direction != SOUTH:
        return NORTH
    elif keys_pressed[pg.K_DOWN] and direction != NORTH:
        return SOUTH
    elif keys_pressed[pg.K_RIGHT] and direction != WEST:
        return EAST
    elif keys_pressed[pg.K_LEFT] and direction != EAST:
        return WEST
    else:
        return direction


def touch_border(snake: list):
    snake_head = snake[0]
    return snake_head.x < 0 or snake_head.x >= WINDOW_WIDTH or snake_head.y < 0 or snake_head.y >= WINDOW_HEIGHT


def pop_food(grid: list, snake: list):
    _snake = copy.deepcopy(snake)
    _grid = copy.deepcopy(grid)
    for body in snake:
        if [body.x, body.y] in _grid:
            _grid.pop(_grid.index([body.x, body.y]))
    return pg.math.Vector2(random.choice(_grid)) if len(_grid) > 0 else None


def move_snake(snake: list, direction: pg.math.Vector2):
    body = snake.copy()
    snake = [body[0].copy()]
    snake[0] += direction
    for b in body[:-1]:
        snake.append(b.copy())
    return snake[:]


def snake_eat_food(snake, food):
    if food:
        return snake[0] == food
    return False


def snake_eat_body(snake: list):
    head = snake[0]
    for body in snake[1:]:
        if body == head:
            return True
    return False


def display(value):
    font = pg.font.Font(None, 28)
    render_surface = font.render(str(value), True, FONT_COLOR)
    return render_surface


def main():
    grid = generate_grid()

    x_snake = WINDOW_WIDTH // 2
    snake = [pg.math.Vector2(x_snake, 12), pg.math.Vector2(x_snake+1, 12), pg.math.Vector2(x_snake+2, 12)]

    direction = WEST
    old_direction = WEST

    move_timer = int(time.time() * 1000)
    super_food_timer = int(time.time() * 1000)
    alpha_timer = int(time.time() * 1000)
    change_move_timer = int(time.time() * 1000)

    snake_move_time = MAX_MOVE_TIME

    food_is_present = False
    food_position = None
    is_super_food = False
    counter_super_food = 0
    alpha_color = ALPHA

    score = 0

    game_over = False

    while True:
        clock.tick(FPS)
        quit_game()

        current_time = int(time.time() * 1000)

        if current_time - change_move_timer >= SPEED_TIME:
            snake_move_time -= STEP_DECREASE
            if snake_move_time <= MIN_MOVE_TIME:
                snake_move_time = MIN_MOVE_TIME
            change_move_timer = current_time

        if snake_eat_body(snake) or touch_border(snake):
            game_over = True

        if not game_over:
            if old_direction == direction:
                direction = key_input(direction)
        else:
            direction = ZERO

        if current_time - move_timer >= snake_move_time and direction != ZERO:
            snake = move_snake(snake, direction)
            old_direction = direction  # permet de bien prendre en compte la direction
            move_timer = current_time

        if snake_eat_food(snake, food_position):
            food_is_present = False
            if is_super_food:
                score += SUPER_FOOD
                is_super_food = False
            else:
                snake.append(snake[-1])
                score += FOOD

        if not food_is_present:
            food_position = pop_food(grid, snake)
            if food_position:
                food_is_present = True
                if not is_super_food:
                    counter_super_food += 1

        if counter_super_food > 5:  # à voir, si garde 5
            is_super_food = True
            counter_super_food = 0
            super_food_timer = current_time

        actual_food_color = FOOD_COLOR
        if is_super_food:
            if current_time - alpha_timer >= ALPHA_TIME:
                alpha_timer = current_time
                if alpha_color == ALPHA:
                    alpha_color = ALPHA_TRANSP
                else:
                    alpha_color = ALPHA

            actual_food_color = pg.color.Color(SUPER_FOOD_COLOR)
            actual_food_color.a = alpha_color
            if current_time - super_food_timer >= SUPER_FOOD_TIME:
                is_super_food = False
                food_is_present = False

        window.fill("Grey")

        for elem in grid:
            case_surface = pg.Surface((CASE_SIZE, CASE_SIZE))
            case_surface.fill(GRASS_COLOR)
            if (elem[0] % 2 == 0 and elem[1] % 2 == 0) or (elem[0] % 2 != 0 and elem[1] % 2 != 0):
                case_surface.fill(GREEN_COLOR)
            window.blit(case_surface, (elem[0] * CASE_SIZE, elem[1] * CASE_SIZE))

        if food_is_present:
            food_surface = pg.Surface((CASE_SIZE, CASE_SIZE)).convert_alpha()
            food_surface.fill(actual_food_color)
            window.blit(food_surface, food_position * CASE_SIZE)

        for index, elem in enumerate(snake):
            snake_surface = pg.Surface((CASE_SIZE, CASE_SIZE))
            snake_surface.fill(SNAKE_BODY_COLOR)
            if index == 0:
                snake_surface.fill(SNAKE_HEAD_COLOR)
            window.blit(snake_surface, elem * CASE_SIZE)

        score_surface = display(score)
        window.blit(score_surface, (8, WINDOW_HEIGHT*CASE_SIZE + 6))

        if game_over:
            game_over_surface = display("GAME OVER")
            rect = game_over_surface.get_rect()
            x_game_over = WINDOW_SIZE[0] - rect.size[0] - 4
            window.blit(game_over_surface, (x_game_over, WINDOW_HEIGHT * CASE_SIZE + 6))

        if is_super_food:
            super_food_surf = display("SUPER FOOD!")
            rect = super_food_surf.get_rect()
            x_super_food = WINDOW_SIZE[0] // 2 - rect.size[0] // 2
            window.blit(super_food_surf, (x_super_food, WINDOW_HEIGHT * CASE_SIZE + 6))

        pg.display.flip()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
