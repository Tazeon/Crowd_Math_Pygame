"""
Constants and configuration for Math Crowd Runner
"""
import pygame

# ============================================
# Game Constants
# ============================================
WIDTH, HEIGHT = 800, 800 
FPS = 60

# ความเร็ว
SCROLL_SPEED = 4
PLAYER_SPEED = 13 
BULLET_SPEED = 15
ENEMY_SPEED = 1.5  

# ขอบเขตถนน (3D Perspective)
# ด้านหลัง (ไกล) - แคบ
ROAD_TOP_LEFT = WIDTH // 2 - 80
ROAD_TOP_RIGHT = WIDTH // 2 + 80
ROAD_TOP_Y = 50

# ด้านหน้า (ใกล้) - กว้าง
ROAD_BOTTOM_LEFT = 50
ROAD_BOTTOM_RIGHT = WIDTH - 50
ROAD_BOTTOM_Y = HEIGHT - 80

# Gate และ Lava
GATE_DEPTH = 0.15
LAVA_BASE_WIDTH = 80
LAVA_BASE_HEIGHT = 50

# สี
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (100, 150, 255)
CYAN = (0, 200, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 100)
YELLOW = (255, 255, 100)
ORANGE = (255, 165, 0)
GRAY = (40, 40, 40)
DARK_GRAY = (30, 30, 30)