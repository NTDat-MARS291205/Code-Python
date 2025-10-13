import pygame
from random import randint

pygame.init()

screen = pygame.display.set_mode((601, 601), pygame.DOUBLEBUF, vsync=1)

pygame.display.set_caption('Snake')
running = True
GREEN = (0, 255, 0)
BLACK = (0,0,0)
WHITE = (255,255,255)
RED = (255,0,0)

clock = pygame.time.Clock()

# --- ADDED: Timer di chuyển cố định (không phụ thuộc FPS) ---
MOVE_EVENT = pygame.USEREVENT + 1
MOVE_MS = 100  # rắn di chuyển mỗi 100ms (10 bước/giây). Tăng/giảm để nhanh/chậm.
pygame.time.set_timer(MOVE_EVENT, MOVE_MS)
should_move = False  # cờ báo đến nhịp bước

# Snake position
# tail - head
snakes = [[5,10]]
direction = "right"

apple = [randint(0,19), randint(0,19)]
font_small = pygame.font.SysFont('sans', 20)
font_big = pygame.font.SysFont('sans', 50)
score = 0

pausing = False

while running:
    clock.tick(120)
    screen.fill(BLACK)

    # Draw snake
    for snake in snakes:
        pygame.draw.rect(screen, GREEN, (snake[0]*30, snake[1]*30, 30, 30))

    # Draw apple
    pygame.draw.rect(screen, RED, (apple[0]*30, apple[1]*30, 30, 30))

    # Draw score
    score_txt = font_small.render("Score: " + str(score), True, WHITE)
    screen.blit(score_txt, (5,5))

    # --- XỬ LÝ SỰ KIỆN ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and direction != "down":
                direction = "up"
            elif event.key == pygame.K_DOWN and direction != "up":
                direction = "down"
            elif event.key == pygame.K_LEFT and direction != "right":
                direction = "left"
            elif event.key == pygame.K_RIGHT and direction != "left":
                direction = "right"
            elif event.key == pygame.K_SPACE and pausing:
                pausing = False
                score = 0
                snakes = [[5,10]]
                apple = [randint(0, 19), randint(0, 19)]
                while any(apple == seg for seg in snakes):
                    apple = [randint(0, 19), randint(0, 19)]
                should_move = False

        # --- ADDED: đánh dấu đến nhịp di chuyển ---
        elif event.type == MOVE_EVENT:
            should_move = True

    # --- LOGIC MOVE THEO NHỊP (không theo FPS) ---
    if not pausing and should_move:
        should_move = False

        # lấy đuôi trước khi di chuyển (để khi ăn táo còn chèn đuôi)
        tail_x = snakes[0][0]
        tail_y = snakes[0][1]

        # Snake move
        
        if direction == "right":
            snakes.append([(snakes[-1][0]+1) % 20, snakes[-1][1]])
            snakes.pop(0)
        elif direction == "left":
            snakes.append([(snakes[-1][0]-1) % 20, snakes[-1][1]])
            snakes.pop(0)
        elif direction == "up":
            snakes.append([snakes[-1][0], (snakes[-1][1]-1) % 20])
            snakes.pop(0)
        elif direction == "down":
            snakes.append([snakes[-1][0], (snakes[-1][1]+1) % 20])
            snakes.pop(0)

        # point (ăn táo) – xử lý ngay sau khi bước xong
        if snakes[-1][0] == apple[0] and snakes[-1][1] == apple[1]:
            snakes.insert(0, [tail_x, tail_y])  # dài thêm 1 ô
            apple = [randint(0,19), randint(0,19)]
            while any(apple == seg for seg in snakes):
                    apple = [randint(0, 19), randint(0, 19)]
            score += 1

        # check crash with edge
        # if snakes[-1][0] < 0 or snakes[-1][0] > 19 or snakes[-1][1] < 0 or snakes[-1][1] > 19:
        #     pausing = True

        # check crash with body
        if not pausing:
            for i in range(len(snakes)-1):
                if snakes[-1][0] == snakes[i][0] and snakes[-1][1] == snakes[i][1]:
                    pausing = True
                    should_move = False
                    break

    # Draw game over
    if pausing:
        game_over_txt = font_big.render("Game over, score: " + str(score), True, WHITE)
        press_space_txt = font_big.render("Press Space to continue", True, WHITE)
        screen.blit(game_over_txt, (50,200))
        screen.blit(press_space_txt, (50,300))
        pygame.display.flip()
        continue
        
    pygame.display.flip()

pygame.quit()
