"""
Main Game class
"""
import pygame
import random
from constants import *
from utils import world_to_screen, get_road_bounds
from entities import Crowd, Enemy, Bullet
from game_objects import Gate, LavaPit

class Game:
    def __init__(self, level, assets=None):
        self.level = level
        self.assets = assets or {}
        self.crowd = Crowd(self.assets)
        self.gates = []
        self.enemies = []
        self.bullets = []
        self.lava_pits = []
        self.distance = 0
        self.spawn_timer = 0
        self.game_over = False
        self.won = False
        self.gates_passed = 0
        self.gates_needed = 4
        
        # Randomized spawn timers (dynamic spawning)
        self.next_gate_time = 220
        self.next_enemy_time = 250
        self.next_lava_time = 350
    
    def reset(self):
        """รีเซ็ตเกมโดยสร้างใหม่"""
        self.__init__(self.level, self.assets)
        self.start_game()
        
    def spawn_gate(self):
        self.gates.append(Gate(0.0, self.level))  # เริ่มที่ด้านหลัง
    
    def spawn_enemies(self):
        num_enemies = random.randint(8, 15)
        z = random.uniform(-0.2, 0.0)  # spawn ด้านหลัง
        for _ in range(num_enemies):
            x = random.uniform(0.1, 0.9)
            self.enemies.append(Enemy(x, z, self.assets))
    
    def spawn_lava_pit(self):
        if self.level >= 2:
            x = random.uniform(0.2, 0.8)
            z = random.uniform(-0.3, 0.0)
            self.lava_pits.append(LavaPit(x, z))
    
    def start_game(self):
        """เริ่มเกมด้วย gate และ enemies ทันที"""
        self.spawn_gate()
        self.spawn_enemies()
        if self.level >= 2:
            self.spawn_lava_pit()
    
    def build_enemy_zones(self):
        """สร้าง zone-based spatial partition สำหรับ collision detection"""
        zones = {}
        for enemy in self.enemies:
            if enemy.alive and enemy.active:
                zone = int(enemy.z * 10)
                zones.setdefault(zone, []).append(enemy)
        return zones
    
    def update(self):
        if self.game_over or self.won:
            return
        
        # เลื่อนวัตถุเข้ามาหาผู้เล่น (เพิ่ม z)
        # ใช้ perspective-corrected speed: ช้าตอนอยู่ไกล เร็วตอนอยู่ใกล้
        for gate in self.gates:
            perspective_factor = 0.3 + 0.7 * max(0, gate.z)  # 0.3-1.0 based on depth
            gate.z += SCROLL_SPEED * 0.003 * perspective_factor
            gate.update_screen_position()
        
        for enemy in self.enemies:
            perspective_factor = 0.3 + 0.7 * max(0, enemy.z)
            enemy.z += SCROLL_SPEED * 0.003 * perspective_factor
            enemy.update_screen_position()
        
        for lava in self.lava_pits:
            perspective_factor = 0.3 + 0.7 * max(0, lava.z)
            lava.z += SCROLL_SPEED * 0.003 * perspective_factor
            lava.update_screen_position()
        
        # Randomized spawning (ไม่ predictable)
        self.spawn_timer += 1
        if self.spawn_timer >= self.next_gate_time:
            self.spawn_gate()
            self.next_gate_time = self.spawn_timer + random.randint(180, 260)
        
        if self.spawn_timer >= self.next_enemy_time:
            self.spawn_enemies()
            self.next_enemy_time = self.spawn_timer + random.randint(220, 280)
        
        if self.level >= 2 and self.spawn_timer >= self.next_lava_time:
            self.spawn_lava_pit()
            self.next_lava_time = self.spawn_timer + random.randint(300, 400)
        
        self.crowd.update()
        
        new_bullets = self.crowd.try_shoot(self.enemies)
        self.bullets.extend(new_bullets)
        
        # Zone-based collision detection
        enemy_zones = self.build_enemy_zones()
        
        for bullet in self.bullets:
            bullet.update()
            bullet.update_screen_position()
            bullet.check_hit_zone(enemy_zones)
        
        for enemy in self.enemies:
            enemy.update(self.crowd)
        
        for lava in self.lava_pits:
            lava.check_collision(self.crowd)
        
        for gate in self.gates:
            if gate.check_collision(self.crowd):
                self.gates_passed += 1
                for enemy in self.enemies:
                    enemy.activate()
        
        # ลบวัตถุที่ผ่านไปแล้ว (z > 1.2)
        self.gates = [g for g in self.gates if g.z < 1.2]
        self.enemies = [e for e in self.enemies if e.alive and e.z < 1.2]
        self.bullets = [b for b in self.bullets if b.active]
        self.lava_pits = [l for l in self.lava_pits if l.active and l.z < 1.2]
        
        self.distance += SCROLL_SPEED
        
        if self.crowd.count <= 0:
            self.game_over = True
        
        if self.gates_passed >= self.gates_needed:
            self.won = True
    
    def draw(self, screen, fonts):
        if self.assets.get('stage'):
            screen.blit(self.assets['stage'], (0, 0))
        else:
            screen.fill(BLACK)
        
        # วาดถนนแบบ 3D perspective
        road_points = [
            (ROAD_TOP_LEFT, ROAD_TOP_Y),      # บนซ้าย
            (ROAD_TOP_RIGHT, ROAD_TOP_Y),     # บนขวา
            (ROAD_BOTTOM_RIGHT, ROAD_BOTTOM_Y), # ล่างขวา
            (ROAD_BOTTOM_LEFT, ROAD_BOTTOM_Y)   # ล่างซ้าย
        ]
        pygame.draw.polygon(screen, GRAY, road_points)
        pygame.draw.polygon(screen, WHITE, road_points, 5)
        
        # วาดเส้นถนนตรงกลาง
        pygame.draw.line(screen, YELLOW, 
                        (WIDTH // 2, ROAD_TOP_Y), 
                        (WIDTH // 2, ROAD_BOTTOM_Y), 3)
        
        # วาดเส้นขอบถนนเพิ่มเติม
        for i in range(5):
            z = i * 0.25
            left, right = get_road_bounds(z)
            screen_y = ROAD_TOP_Y + (ROAD_BOTTOM_Y - ROAD_TOP_Y) * z
            pygame.draw.line(screen, (100, 100, 100), 
                           (int(left), int(screen_y)), 
                           (int(right), int(screen_y)), 1)
        
        # เรียง object ตาม z เพื่อวาดจากไกลไปใกล้
        all_objects = []
        
        for gate in self.gates:
            all_objects.append(('gate', gate, gate.z))
        
        for lava in self.lava_pits:
            all_objects.append(('lava', lava, lava.z))
        
        for enemy in self.enemies:
            all_objects.append(('enemy', enemy, enemy.z))
        
        for bullet in self.bullets:
            all_objects.append(('bullet', bullet, bullet.z))
        
        for person in self.crowd.people:
            all_objects.append(('person', person, person.z))
        
        # เรียงตาม z (ไกลไปใกล้)
        all_objects.sort(key=lambda x: x[2])
        
        # วาดทุก object
        for obj_type, obj, _ in all_objects:
            obj.draw(screen)
        
        # HUD with transparent overlay
        self._draw_hud(screen, fonts)
        
        if self.game_over:
            self._draw_game_over(screen, fonts)
        
        if self.won:
            self._draw_victory(screen, fonts)
    
    def _draw_hud(self, screen, fonts):
        """วาด HUD"""
        font, small_font, big_font = fonts['font'], fonts['small_font'], fonts['big_font']
        
        # Crowd Counter
        count_box = pygame.Surface((180, 80), pygame.SRCALPHA)
        count_box.fill((30, 30, 30, 180))  # โปร่งแสง
        screen.blit(count_box, (10, 10))
        pygame.draw.rect(screen, CYAN, pygame.Rect(10, 10, 180, 80), 3)
        count_label = small_font.render("CROWD", True, CYAN)
        screen.blit(count_label, (20, 15))
        count_text = big_font.render(f"{self.crowd.count}", True, WHITE)
        screen.blit(count_text, (25, 40))
        
        # Level Box
        level_box = pygame.Surface((180, 80), pygame.SRCALPHA)
        level_box.fill((30, 30, 30, 180))
        screen.blit(level_box, (WIDTH - 190, 10))
        pygame.draw.rect(screen, YELLOW, pygame.Rect(WIDTH - 190, 10, 180, 80), 3)
        level_label = small_font.render("LEVEL", True, YELLOW)
        screen.blit(level_label, (WIDTH - 175, 15))
        level_text = big_font.render(f"{self.level}", True, WHITE)
        screen.blit(level_text, (WIDTH - 155, 40))
        
        # Gates Counter
        gates_box = pygame.Surface((180, 60), pygame.SRCALPHA)
        gates_box.fill((30, 30, 30, 180))
        screen.blit(gates_box, (10, 100))
        pygame.draw.rect(screen, GREEN, pygame.Rect(10, 100, 180, 60), 3)
        gates_label = small_font.render("GATES", True, GREEN)
        screen.blit(gates_label, (20, 105))
        gates_text = font.render(f"{self.gates_passed}/{self.gates_needed}", True, WHITE)
        screen.blit(gates_text, (25, 125))
    
    def _draw_game_over(self, screen, fonts):
        """วาดหน้าจอ Game Over"""
        font, big_font = fonts['font'], fonts['big_font']
        
        # แสดง ai_dead.png เต็มจอก่อน
        if self.assets.get('ai_dead'):
            screen.blit(self.assets['ai_dead'], (0, 0))
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
        
        # ซ้อนทับด้วย game_over image ตรงกลาง
        if self.assets.get('game_over'):
            img_x = WIDTH // 2 - 200
            img_y = HEIGHT // 2 - 150
            screen.blit(self.assets['game_over'], (img_x, img_y))
        else:
            text = big_font.render("GAME OVER!", True, RED)
            screen.blit(text, (WIDTH//2 - 200, HEIGHT//2 - 50))
        
        # แสดงข้อความคำแนะนำ
        restart_text = font.render("Press R to Restart", True, GREEN)
        screen.blit(restart_text, (WIDTH//2 - 150, HEIGHT//2 + 180))
        
        menu_text = fonts['small_font'].render("Press M for Menu", True, WHITE)
        screen.blit(menu_text, (WIDTH//2 - 100, HEIGHT//2 + 230))
    
    def _draw_victory(self, screen, fonts):
        """วาดหน้าจอชนะ"""
        font, small_font, big_font = fonts['font'], fonts['small_font'], fonts['big_font']
        
        if self.assets.get('ai_win'):
            screen.blit(self.assets['ai_win'], (0, 0))
        else:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))
        
        info_box = pygame.Surface((500, 250))
        info_box.set_alpha(180)
        info_box.fill(BLACK)
        screen.blit(info_box, (WIDTH//2 - 250, HEIGHT//2 - 125))
        
        text = big_font.render("LEVEL COMPLETE!", True, GREEN)
        screen.blit(text, (WIDTH//2 - 280, HEIGHT//2 - 100))
        
        score_text = font.render(f"Survivors: {self.crowd.count}", True, WHITE)
        screen.blit(score_text, (WIDTH//2 - 130, HEIGHT//2 - 20))
        
        if self.level < 3:
            next_text = small_font.render("Press N for Next Level", True, GREEN)
            screen.blit(next_text, (WIDTH//2 - 135, HEIGHT//2 + 40))
        else:
            win_text = font.render("YOU WIN THE GAME!", True, YELLOW)
            screen.blit(win_text, (WIDTH//2 - 200, HEIGHT//2 + 40))
        
        menu_text = small_font.render("Press M for Menu", True, WHITE)
        screen.blit(menu_text, (WIDTH//2 - 100, HEIGHT//2 + 80))