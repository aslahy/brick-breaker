import pygame
import math
import random
from button import Button  # Import the Button class from the 'button' module

# Initialize pygame and set up the game window
pygame.init()
pygame.font.init()
WIDTH, HEIGHT = 1280, 720
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Menu")
BG = pygame.image.load("brick_breaker/Background.png")

# Define a function to get a font with a specific size
def get_font(size):
    return pygame.font.Font("brick_breaker/font.ttf", size)

# Constants and settings for the game
FPS = 60
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 15
BALL_RADIUS = 10
SCORE = 0
HITSFX = pygame.mixer.Sound("brick_breaker/hit.mp3")
WINSFX = pygame.mixer.Sound("brick_breaker/win.mp3")
LOSESFX = pygame.mixer.Sound("brick_breaker/lose.mp3")
LIVES_FONT = pygame.font.SysFont("Ariel", 50)

# Define the Paddle class
class Paddle:
    VEL = 8

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y - 25  # Adjust the y-coordinate for the paddle
        self.width = width
        self.height = height
        self.color = color

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.color, (self.x, self.y, self.width, self.height))

    def move(self, direction=1):
        self.x = self.x + self.VEL * direction

# Define the Ball class
class Ball:
    VEL = 7

    def __init__(self, x, y, radius, color):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.x_vel = 0
        self.y_vel = -self.VEL

    def move(self):
        self.x += self.x_vel
        self.y += self.y_vel

    def set_vel(self, x_vel, y_vel):
        self.x_vel = x_vel
        self.y_vel = y_vel

    def draw(self, SCREEN):
        pygame.draw.circle(SCREEN, self.color, (self.x, self.y), self.radius)

# Define the Brick class
class Brick:
    def __init__(self, x, y, width, height, health, colors):
        self.x = x
        self.y = y + 100  # Adjust the y-coordinate for the brick
        self.width = width
        self.height = height
        self.health = health
        self.colors = colors

    def draw(self, SCREEN):
        pygame.draw.rect(SCREEN, self.colors, (self.x, self.y, self.width, self.height))

    def collide(self, ball):
        # Check if the ball's x-coordinate is within the brick's x-range
        if not (ball.x + ball.radius >= self.x and ball.x - ball.radius <= self.x + self.width):
            return False

        # Check if the ball's y-coordinate is within the brick's y-range
        if not (ball.y + ball.radius >= self.y and ball.y - ball.radius <= self.y + self.height):
            return False

        # Collision detected, handle it
        self.hit()

        # Determine the direction of the collision
        if ball.x < self.x or ball.x > self.x + self.width:
            # Collision is from the sides
            ball.set_vel(ball.x_vel * -1, ball.y_vel)
        else:
            # Collision is from the top or bottom
            ball.set_vel(ball.x_vel, ball.y_vel * -1)

        return True

    def hit(self):
        self.health -= 1
        HITSFX.play()

# Define the draw function to render the game elements
def draw(SCREEN, paddle, ball, bricks, lives):
    SCREEN.fill((21, 23, 20))
    paddle.draw(SCREEN)
    ball.draw(SCREEN)

    # Create a "BACK" button and display the score
    PLAY_MOUSE_POS = pygame.mouse.get_pos()
    PLAY_BACK = Button(image=None, pos=(120, 50), text_input="BACK", font=get_font(50), base_color="White", hovering_color="Green")
    PLAY_BACK.changeColor(PLAY_MOUSE_POS)
    PLAY_BACK.update(SCREEN)
    SCORE_TXT = get_font(50).render(str(SCORE), True, (255, 255, 255))
    SCREEN.blit(SCORE_TXT, (1100, 25))

    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                main_menu()

    for brick in bricks:
        brick.draw(SCREEN)

    # Display the remaining lives
    lives_text = LIVES_FONT.render(f"Lives: {lives}", 1, "white")
    SCREEN.blit(lives_text, (10, HEIGHT - lives_text.get_height() - 10))

    pygame.display.update()

# Define functions for handling ball collisions
def ball_collision(ball):
    if ball.x - BALL_RADIUS <= 0 or ball.x + BALL_RADIUS >= WIDTH:
        ball.set_vel(ball.x_vel * -1, ball.y_vel)
    if ball.y + BALL_RADIUS >= HEIGHT or ball.y - BALL_RADIUS <= 0:
        ball.set_vel(ball.x_vel, ball.y_vel * -1)

def ball_paddle_collision(ball, paddle):
    if not (ball.x <= paddle.x + paddle.width and ball.x >= paddle.x):
        return
    if not (ball.y + ball.radius >= paddle.y):
        return

    paddle_center = paddle.x + paddle.width/2
    distance_to_center = ball.x - paddle_center

    percent_width = distance_to_center / paddle.width
    angle = percent_width * 90
    angle_radians = math.radians(angle)

    x_vel = math.sin(angle_radians) * ball.VEL
    y_vel = math.cos(angle_radians) * ball.VEL * -1

    ball.set_vel(x_vel, y_vel)

# Define a function to generate bricks
def generate_bricks(rows, cols):
    gap = 2
    brick_width = WIDTH // cols - gap
    brick_height = 25

    bricks = []
    for row in range(rows):
        for col in range(cols):
            brick = Brick(col * brick_width + gap * col, row * brick_height + gap * row, brick_width, brick_height, 1, clr[random.randint(0, 5)])
            bricks.append(brick)

    return bricks

# Define a list of brick colors
clr = [(255, 85, 255), (85, 255, 255), (255, 0, 0), (170, 170, 255), (85, 255, 85), (255, 102, 102)]

# Define the main game loop
def main():
    clock = pygame.time.Clock()
    paddle_x = WIDTH/2 - PADDLE_WIDTH/2
    paddle_y = HEIGHT - PADDLE_HEIGHT - 5
    paddle = Paddle(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT, "white")
    ball = Ball(WIDTH/2, paddle_y - BALL_RADIUS, BALL_RADIUS, "white")
    bricks = generate_bricks(5, 10)
    lives = 3

    # Define a function to reset the paddle and ball positions
    def reset():
        paddle.x = paddle_x
        paddle.y = paddle_y
        ball.x = WIDTH/2
        ball.y = paddle_y - BALL_RADIUS

    run = True
    while run:
        clock.tick(FPS)
        global SCORE
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT] and paddle.x - paddle.VEL >= 0:
            paddle.move(-1)
        if keys[pygame.K_RIGHT] and paddle.x + paddle.width + paddle.VEL <= WIDTH:
            paddle.move(1)

        ball.move()
        ball_collision(ball)
        ball_paddle_collision(ball, paddle)

        for brick in bricks[:]:
            brick.collide(ball)

            if brick.health <= 0:
                bricks.remove(brick)
                SCORE += 1

        # Check for losing a life
        if ball.y + ball.radius >= HEIGHT:
            lives -= 1
            ball.x = paddle.x + paddle.width/2
            ball.y = paddle.y - BALL_RADIUS
            ball.set_vel(0, ball.VEL * -1)

        if lives <= 0:
            lose()

        if len(bricks) == 0:
            win()

        draw(SCREEN, paddle, ball, bricks, lives)

    pygame.quit()
    quit()

# Define the lose function
def lose():
    LOSESFX.play()
    pygame.time.delay(1500)
    LOSESFX.stop()
    while True:
        SCREEN.fill((21, 23, 20))
        LOSE_TXT = get_font(70).render("YOU LOSE", True, '#ff0000')
        SCREEN.blit(LOSE_TXT, (360, 100))

        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BACK = Button(image=None, pos=(640, 350), text_input="MAIN MENU", font=get_font(75), base_color="White", hovering_color="Green")
        RETRY = Button(image=None, pos=(640, 500), text_input="RETRY", font=get_font(75), base_color="White", hovering_color="Green")

        for button in [PLAY_BACK, RETRY]:
            button.changeColor(PLAY_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                if RETRY.checkForInput(PLAY_MOUSE_POS):
                    main()

        pygame.display.update()

# Define the win function
def win():
    WINSFX.play()
    pygame.time.delay(1000)
    WINSFX.stop()
    while True:
        SCREEN.fill((21, 23, 20))
        LOSE_TXT = get_font(70).render("YOU WIN", True, '#a4de02')
        SCREEN.blit(LOSE_TXT, (360, 100))

        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BACK = Button(image=None, pos=(640, 350), text_input="MAIN MENU", font=get_font(75), base_color="White", hovering_color="Green")
        RETRY = Button(image=None, pos=(640, 500), text_input="RETRY", font=get_font(75), base_color="White", hovering_color="Green")

        for button in [PLAY_BACK, RETRY]:
            button.changeColor(PLAY_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()
                if RETRY.checkForInput(PLAY_MOUSE_POS):
                    main()

        pygame.display.update()

# Define the play function
def play():
    while True:
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BACK = Button(image=None, pos=(640, 460), text_input="BACK", font=get_font(75), base_color="White", hovering_color="Green")
        PLAY_BACK.changeColor(PLAY_MOUSE_POS)
        PLAY_BACK.update(SCREEN)
        main()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    main_menu()

        pygame.display.update()

# Define the main menu function
def main_menu():
    while True:
        SCREEN.blit(BG, (0, 0))
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        MENU_TEXT = get_font(70).render("MAIN MENU", True, "#b68f40")
        MENU_RECT = MENU_TEXT.get_rect(center=(640, 150))
        PLAY_BUTTON = Button(image=pygame.image.load("block breaker/Play Rect.png"), pos=(640, 400), text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="#ffba00")
        QUIT_BUTTON = Button(image=pygame.image.load("block breaker/Quit Rect.png"), pos=(640, 600), text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="#ffba00")
        SCREEN.blit(MENU_TEXT, MENU_RECT)

        for button in [PLAY_BUTTON, QUIT_BUTTON]:
            button.changeColor(MENU_MOUSE_POS)
            button.update(SCREEN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    play()
                if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                    pygame.quit()
                    quit()

        pygame.display.update()

# Start the main menu loop when the script is executed
main_menu()
