"""
Utility functions for Math Crowd Runner
"""
import pygame
from constants import *

# ============================================
# Font Cache - ลดการสร้าง font ซ้ำ
# ============================================
FONT_CACHE = {}

def init_font_cache():
    """Initialize font cache after pygame.init()"""
    global FONT_CACHE
    if not FONT_CACHE:
        FONT_CACHE = {i: pygame.font.Font(None, i) for i in range(20, 90, 2)}

def get_font(size):
    """ดึง font จาก cache"""
    if not FONT_CACHE:
        init_font_cache()
    
    size = max(20, min(88, int(size)))
    # ปัดเป็นเลขคู่ที่ใกล้ที่สุด
    size = size if size % 2 == 0 else size + 1
    return FONT_CACHE.get(size, FONT_CACHE[40])

def world_to_screen(x, z):
    """
    แปลงพิกัด world (x: ซ้าย-ขวา, z: ไกล-ใกล้) เป็นพิกัดหน้าจอ
    z = 0 (ไกลสุด ด้านหลัง) ถึง z = 1 (ใกล้สุด ด้านหน้า)
    """
    # คำนวณตำแหน่ง x บนหน้าจอตาม perspective
    screen_left = ROAD_TOP_LEFT + (ROAD_BOTTOM_LEFT - ROAD_TOP_LEFT) * z
    screen_right = ROAD_TOP_RIGHT + (ROAD_BOTTOM_RIGHT - ROAD_TOP_RIGHT) * z
    screen_x = screen_left + (screen_right - screen_left) * x
    
    # คำนวณตำแหน่ง y บนหน้าจอ
    screen_y = ROAD_TOP_Y + (ROAD_BOTTOM_Y - ROAD_TOP_Y) * z
    
    # คำนวณขนาดตาม perspective (ไกล = เล็ก, ใกล้ = ใหญ่)
    scale = 0.3 + 0.7 * z  # scale จาก 0.3 (ไกล) ถึง 1.0 (ใกล้)
    
    return screen_x, screen_y, scale

def get_road_bounds(z):
    """คืนค่าขอบซ้าย-ขวาของถนนที่ระดับความลึก z"""
    left = ROAD_TOP_LEFT + (ROAD_BOTTOM_LEFT - ROAD_TOP_LEFT) * z
    right = ROAD_TOP_RIGHT + (ROAD_BOTTOM_RIGHT - ROAD_TOP_RIGHT) * z
    return left, right

def load_resources():
    """โหลดรูปภาพและเสียงทั้งหมดครั้งเดียว"""
    assets = {}
    
    def safe_load_image(name, scale=None):
        try:
            img = pygame.image.load(f'assets/{name}')
            if scale:
                img = pygame.transform.scale(img, scale)
            return img
        except:
            return None
    
    # โหลดรูปภาพ
    assets['ai_hoshino'] = safe_load_image('ai_hoshino.jpg', (30, 30))
    assets['knife'] = safe_load_image('knife.png', (20, 20))
    assets['stage'] = safe_load_image('stage.png', (800, 800))
    assets['ai_dead'] = safe_load_image('ai_dead.jpg', (800, 800))
    assets['ai_win'] = safe_load_image('ai_win.png', (800, 800))
    assets['game_over'] = safe_load_image('images.png', (400, 300))
    
    # Pre-scale sprites สำหรับ Person (ลด lag จาก transform ทุก frame)
    if assets['ai_hoshino']:
        assets['ai_sprites'] = {
            10: pygame.transform.scale(assets['ai_hoshino'], (20, 20)),
            15: pygame.transform.scale(assets['ai_hoshino'], (30, 30)),
            20: pygame.transform.scale(assets['ai_hoshino'], (40, 40)),
            25: pygame.transform.scale(assets['ai_hoshino'], (50, 50)),
            30: pygame.transform.scale(assets['ai_hoshino'], (60, 60)),
        }
    else:
        assets['ai_sprites'] = {}
    
    # Pre-scale sprites สำหรับ Enemy
    if assets['knife']:
        assets['knife_sprites'] = {
            10: pygame.transform.scale(assets['knife'], (20, 20)),
            15: pygame.transform.scale(assets['knife'], (30, 30)),
            20: pygame.transform.scale(assets['knife'], (40, 40)),
        }
    else:
        assets['knife_sprites'] = {}
    
    # โหลดเพลง
    try:
        pygame.mixer.music.load('assets/bg_song.mp3')
        assets['music_loaded'] = True
    except:
        assets['music_loaded'] = False
    
    return assets