import random
import pygame
import cv2
import numpy as np
from cvzone.HandTrackingModule import HandDetector
import time
import warnings


warnings.filterwarnings("ignore", category=UserWarning, module="google.protobuf.symbol_database")
pygame.init()


width, height = 1280, 720
window = pygame.display.set_mode((width, height))
pygame.display.set_caption("Balloon Pop")

fps = 30
clock = pygame.time.Clock()
cap = cv2.VideoCapture(0)
cap.set(3, 1280)  
cap.set(4, 720)  


if not cap.isOpened():
    print("Error: Could not open webcam")
    pygame.quit()
    exit()


try:
    imgBalloon = pygame.image.load(r"C:\Users\svelo\Downloads\baloon_1new.png").convert_alpha()
    imgBlackBalloon = pygame.image.load(r"C:\Users\svelo\Downloads\baloonblack-removebg-preview (2).png").convert_alpha()
except pygame.error as e:
    print(f"Error loading image: {e}")
    cap.release()  
    pygame.quit()
    exit()

rectBalloon = pygame.Rect(500, 300, imgBalloon.get_width(), imgBalloon.get_height())
rectBlackBalloon = pygame.Rect(-100, -100, imgBlackBalloon.get_width(), imgBlackBalloon.get_height())


initial_speed = 10
max_speed = 30
speed_increase_interval = 3  
speed = initial_speed
score = 0
startTime = time.time()
totalTime = 60
pop_display_time = 0.4  
last_pop_time = 0
pop_position = None
black_balloon_time = 0
show_black_balloon = False
black_balloon_popped = False

detector = HandDetector(detectionCon=0.8, maxHands=1)

def resetBalloon():
    rectBalloon.x = random.randint(100, width - 100)
    rectBalloon.y = height + 50

def resetBlackBalloon():
    rectBlackBalloon.x = random.randint(100, width - 100)
    rectBlackBalloon.y = -100
    global black_balloon_time, show_black_balloon, black_balloon_popped
    black_balloon_time = time.time()
    show_black_balloon = True
    black_balloon_popped = False

def get_current_speed(elapsed_time):
    """Return speed based on elapsed time."""
    new_speed = initial_speed + (elapsed_time // speed_increase_interval) * 2
    return min(new_speed, max_speed)

start = True
try:
    while start:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                start = False

        elapsed_time = time.time() - startTime
        timeRemain = int(totalTime - elapsed_time)

        if timeRemain < 0:
            window.fill((255, 255, 255))

            font = pygame.font.Font(None, 50)
            textScore = font.render(f'Your Score: {score}', True, (50, 50, 255))
            textTime = font.render(f'Time UP', True, (50, 50, 255))
            window.blit(textScore, (450, 350))
            window.blit(textTime, (530, 275))

        else:
            success, img = cap.read()
            if not success:
                print("Failed to capture image")
                continue
            
            img = cv2.flip(img, 1)
            hands, img = detector.findHands(img, flipType=False)

            speed = get_current_speed(elapsed_time)
            rectBalloon.y -= speed 

            if rectBalloon.y < height // 2 and not show_black_balloon:
                resetBlackBalloon()

            if rectBalloon.y < 0:
                resetBalloon()
                speed = get_current_speed(elapsed_time)

            if hands:
                hand = hands[0]
                x, y = hand['lmList'][8][0:2]
                if rectBalloon.collidepoint(x, y):
                    resetBalloon()
                    score += 10
                    speed = get_current_speed(elapsed_time)
                    last_pop_time = time.time()
                    pop_position = (x, y)

                if rectBlackBalloon.collidepoint(x, y) and show_black_balloon:
                    # Black Balloon is popped
                    resetBlackBalloon()
                    score -= 10
                    black_balloon_popped = True
                    last_pop_time = time.time()
                    pop_position = (x, y)

            if show_black_balloon:
                rectBlackBalloon.y += speed
                if rectBlackBalloon.y > height:  
                    resetBlackBalloon()

            imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            imgRGB = np.rot90(imgRGB)
            frame = pygame.surfarray.make_surface(imgRGB).convert()
            frame = pygame.transform.flip(frame, True, False)
            window.blit(frame, (0, 0))
            window.blit(imgBalloon, rectBalloon)
            if show_black_balloon:
                window.blit(imgBlackBalloon, rectBlackBalloon)

            font = pygame.font.Font(None, 50)
            textScore = font.render(f'Score: {score}', True, (50, 50, 255))
            textTime = font.render(f'Time: {timeRemain}', True, (50, 50, 255))
            window.blit(textScore, (35, 35))
            window.blit(textTime, (1000, 35))

            if pop_position and time.time() - last_pop_time < pop_display_time:
                textPop = font.render(f'{"+10" if not black_balloon_popped else "-10"}', True, (255, 0, 0))
                window.blit(textPop, pop_position)

        pygame.display.update()
        clock.tick(fps)

finally:
    print("Releasing camera...")
    cap.release()
    print("Camera released.")
    pygame.quit()
 