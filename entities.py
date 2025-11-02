"""
Game entities: Person, Enemy, Bullet, Crowd
"""
import pygame
import random
import math
from constants import *
from utils import world_to_screen

class Person:
    """คนหนึ่งคนในทีม มีปืน"""
    def __init__(self, x, z, crowd_size=10, assets=None):
        self.x = x  # 0.0 - 1.0 (ซ้าย-ขวา)
        self.z = z  # 0.0 - 1.0 (ไกล-ใกล้)
        self.base_size = 10
        self.crowd_size = crowd_size
        self.update_size()
        self.color = BLUE
        self.has_gun = True
        self.shoot_cooldown = 0
        self.shoot_rate = 20
        self.assets = assets or {}
        
        # Cache screen position
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
    
    def update_size(self):
        """ปรับขนาดตามจำนวนคนในทีม"""
        if self.crowd_size <= 10:
            self.base_size = 15
        elif self.crowd_size <= 50:
            self.base_size = 12
        elif self.crowd_size <= 100:
            self.base_size = 10
        else:
            self.base_size = max(8, 15 - int(self.crowd_size / 50))
    
    def update_screen_position(self):
        """คำนวณตำแหน่งบนหน้าจอ (เรียกครั้งเดียวต่อ frame)"""
        self.screen_x, self.screen_y, self.scale = world_to_screen(self.x, self.z)
        
    def update(self, target_x, target_z):
        """เคลื่อนที่ไปหาตำแหน่งในฟอร์เมชั่น"""
        dx = target_x - self.x
        dz = target_z - self.z
        dist = math.sqrt(dx*dx + dz*dz)
        
        if dist > 0.01:
            speed = 0.02
            self.x += (dx / dist) * speed
            self.z += (dz / dist) * speed
        
        # จำกัดขอบเขต
        self.x = max(0.05, min(0.95, self.x))
        self.z = max(0.1, min(0.95, self.z))
        
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
    
    def can_shoot(self):
        return self.has_gun and self.shoot_cooldown == 0
    
    def shoot(self, target):
        if self.can_shoot():
            self.shoot_cooldown = self.shoot_rate
            return Bullet(self.x, self.z, target)
        return None
    
    def draw(self, screen):
        size = int(self.base_size * self.scale)
        
        # ใช้ pre-scaled sprites แทนการ scale ทุก frame
        if self.assets.get('ai_sprites'):
            # เลือกขนาดที่ใกล้เคียงที่สุด
            closest_size = min(self.assets['ai_sprites'].keys(), 
                             key=lambda k: abs(k - size))
            sprite = self.assets['ai_sprites'][closest_size]
            img_rect = sprite.get_rect(center=(int(self.screen_x), int(self.screen_y)))
            screen.blit(sprite, img_rect)
        else:
            pygame.draw.circle(screen, self.color, 
                             (int(self.screen_x), int(self.screen_y)), size)
            if self.has_gun:
                gun_length = max(8, int(size * 1.2))
                pygame.draw.line(screen, WHITE, 
                               (int(self.screen_x), int(self.screen_y)), 
                               (int(self.screen_x), int(self.screen_y - gun_length)), 2)


class Crowd:
    def __init__(self, assets=None):
        self.assets = assets or {}
        self.people = [Person(0.5, 0.85, 1, self.assets)]  # เริ่มที่กลางถนน ด้านหน้า
        self.center_x = 0.5  # 0.0 - 1.0
        self.center_z = 0.85  # อยู่ด้านหน้า
        self.count = 1
        self.frame_count = 0
        self.current_target = None  # Shared target สำหรับยิง
        self.cached_targets = []  # Cache ตำแหน่งเป้าหมาย (แก้ปัญหาตัวละครสั่น)
        
    def add_people(self, amount):
        if amount > 0:
            current = len(self.people)
            amount = min(amount, 500 - current)
            
            for _ in range(amount):
                angle = random.uniform(0, math.pi * 2)
                radius = random.uniform(0.02, 0.06)
                x = self.center_x + math.cos(angle) * radius
                z = self.center_z + math.sin(angle) * radius * 0.3
                self.people.append(Person(x, z, len(self.people) + 1, self.assets))
            self.count = len(self.people)
            self.update_all_sizes()
    
    def remove_people(self, amount):
        if amount > 0 and len(self.people) > 0:
            amount = min(amount, len(self.people))
            self.people = self.people[:-amount]
            self.count = len(self.people)
            if self.count > 0:
                self.update_all_sizes()
    
    def update_all_sizes(self):
        for person in self.people:
            person.crowd_size = self.count
            person.update_size()
    
    def multiply_people(self, multiplier):
        if multiplier > 0:
            current = len(self.people)
            to_add = current * (multiplier - 1)
            to_add = min(to_add, 500 - current)
            if to_add > 0:
                self.add_people(to_add)
    
    def divide_people(self, divisor):
        if divisor > 0 and self.count > 0:
            new_count = max(1, self.count // divisor)
            to_remove = self.count - new_count
            if to_remove > 0:
                self.remove_people(to_remove)
    
    def power_people(self, power):
        current = len(self.people)
        if current > 0:
            new_count = min(500, int(current ** power))
            if new_count > current:
                self.add_people(new_count - current)
            elif new_count < current:
                self.remove_people(current - new_count)
    
    def sqrt_people(self):
        current = len(self.people)
        if current > 0:
            new_count = max(1, int(math.sqrt(current)))
            if new_count < current:
                self.remove_people(current - new_count)
    
    def move(self, dx):
        new_x = self.center_x + dx * 0.02
        self.center_x = max(0.1, min(0.9, new_x))
    
    def update(self):
        num = len(self.people)
        if num == 0:
            return
        
        # จัดฟอร์เมชั่นคนในฝูง (เวอร์ชันอ่านง่าย)
        self.cached_targets = []
        
        # ตั้งค่าพื้นฐานของ formation
        max_people_per_ring = 12
        person_index = 0
        ring = 0
        
        # วนสร้างวงกลมรอบ ๆ center
        while person_index < num:
            # จำนวนคนต่อวง — วงในสุดคนจะน้อย วงนอกมากขึ้น
            people_in_ring = min(max_people_per_ring + ring * 3, num - person_index)
            
            # ระยะห่างจากจุดกลาง
            radius = 0.03 + ring * 0.04
            
            # คำนวณตำแหน่งแต่ละคนในวง
            for i in range(people_in_ring):
                if person_index >= num:
                    break
                
                # มุมของคนนี้ในวง (กระจายเท่า ๆ กันรอบวง)
                angle = (i / people_in_ring) * math.pi * 2
                
                # แปลงเป็นพิกัด x, z
                target_x = self.center_x + math.cos(angle) * radius
                target_z = self.center_z + math.sin(angle) * radius * 0.3  # ยืดนิดให้วงรี
                
                # เก็บตำแหน่งนี้ไว้
                self.cached_targets.append((target_x, target_z))
                person_index += 1
            
            # ไปวงถัดไป
            ring += 1
        
        # เคลื่อนแต่ละคนไปยังเป้าหมาย
        for i, person in enumerate(self.people):
            if i < len(self.cached_targets):
                target_x, target_z = self.cached_targets[i]
                person.update(target_x, target_z)
        
        # อัปเดต screen position สำหรับทุกคน (cache)
        for person in self.people:
            person.update_screen_position()
    
    def try_shoot(self, enemies):
        """ใช้ shared target system - ลด O(n²) เหลือ O(n)"""
        bullets = []
        
        # หาเป้าหมายใหม่ถ้าไม่มีหรือตายแล้ว หรือหลุดเฟรมไปแล้ว
        if (self.current_target is None or 
            not self.current_target.alive or 
            not self.current_target.active or
            self.current_target.z >= self.center_z):  # เพิ่มเงื่อนไข: ถ้าศัตรูหลุดไปด้านหลังแล้ว
            
            # กรองเฉพาะศัตรูที่อยู่ด้านหน้า (z < center_z)
            alive_enemies = [e for e in enemies 
                           if e.alive and e.active and e.z < self.center_z]
            
            if alive_enemies:
                # เลือกศัตรูที่ใกล้ที่สุด (ด้านหน้า)
                self.current_target = min(alive_enemies, 
                                        key=lambda e: abs(e.z - self.center_z))
            else:
                self.current_target = None
        
        # ให้ทุกคนยิงใส่เป้าหมายเดียวกัน
        if self.current_target:
            for person in self.people:
                if person.can_shoot():
                    bullet = person.shoot(self.current_target)
                    if bullet:
                        bullets.append(bullet)
                        break  # ยิงทีละคนต่อ frame (ประหยัด bullets)
        
        return bullets
    
    def draw(self, screen):
        # เรียงตาม z เพื่อวาดจากไกลไปใกล้
        sorted_people = sorted(self.people, key=lambda p: p.z)
        for person in sorted_people:
            person.draw(screen)


class Enemy:
    def __init__(self, x, z, assets=None):
        self.x = x  # 0.0 - 1.0
        self.z = z  # 0.0 - 1.0
        self.base_size = 10
        self.color = RED
        self.hp = 1
        self.speed = 0.006  # ลดความเร็วจาก 0.008 → 0.006
        self.alive = True
        self.active = False
        self.assets = assets or {}
        
        # Cache screen position
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
        
    def activate(self):
        self.active = True
    
    def update_screen_position(self):
        """คำนวณตำแหน่งบนหน้าจอ (เรียกครั้งเดียวต่อ frame)"""
        self.screen_x, self.screen_y, self.scale = world_to_screen(self.x, self.z)
        
    def update(self, crowd):
        if not self.alive or not self.active:
            return
        
        if len(crowd.people) > 0:
            target = min(crowd.people, key=lambda p: 
                        math.sqrt((p.x - self.x)**2 + (p.z - self.z)**2))
            
            dx = target.x - self.x
            dz = target.z - self.z
            dist = math.sqrt(dx*dx + dz*dz)
            
            if dist > 0.01:
                self.x += (dx / dist) * self.speed
                self.z += (dz / dist) * self.speed
            
            if dist < 0.03:
                crowd.remove_people(1)
                self.alive = False
    
    def take_damage(self):
        self.hp -= 1
        if self.hp <= 0:
            self.alive = False
    
    def draw(self, screen):
        if self.alive:
            size = int(self.base_size * self.scale)
            
            # ใช้ pre-scaled sprites
            if self.assets.get('knife_sprites'):
                closest_size = min(self.assets['knife_sprites'].keys(), 
                                 key=lambda k: abs(k - size))
                sprite = self.assets['knife_sprites'][closest_size]
                knife_rect = sprite.get_rect(center=(int(self.screen_x), int(self.screen_y)))
                screen.blit(sprite, knife_rect)
            else:
                pygame.draw.circle(screen, self.color, 
                                 (int(self.screen_x), int(self.screen_y)), size)
                pygame.draw.line(screen, WHITE, 
                               (int(self.screen_x - size), int(self.screen_y)), 
                               (int(self.screen_x + size), int(self.screen_y)), 2)


class Bullet:
    def __init__(self, x, z, target):
        self.x = x
        self.z = z
        self.speed = 0.03
        self.active = True
        self.target = target
        
        # Cache screen position
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
        
    def update_screen_position(self):
        """คำนวณตำแหน่งบนหน้าจอ (เรียกครั้งเดียวต่อ frame)"""
        self.screen_x, self.screen_y, self.scale = world_to_screen(self.x, self.z)
        
    def update(self):
        if not self.active:
            return
            
        if not self.target or not self.target.alive:
            self.active = False
            return
        
        dx = self.target.x - self.x
        dz = self.target.z - self.z
        dist = math.sqrt(dx*dx + dz*dz)
        
        if dist > 0.01:
            self.x += (dx / dist) * self.speed
            self.z += (dz / dist) * self.speed
        
        if self.z < -0.1 or self.z > 1.1 or self.x < -0.1 or self.x > 1.1:
            self.active = False
    
    def check_hit_zone(self, enemy_zones):
        """ใช้ zone-based collision detection (เร็วกว่า O(n²))"""
        zone = int(self.z * 10)  # แบ่งเป็น 10 zones
        enemies_in_zone = enemy_zones.get(zone, [])
        
        for enemy in enemies_in_zone:
            if enemy.alive:
                dist = math.sqrt((enemy.x - self.x)**2 + (enemy.z - self.z)**2)
                if dist < 0.03:
                    enemy.take_damage()
                    self.active = False
                    return True
        return False
    
    def draw(self, screen):
        if self.active:
            size = int(4 * self.scale)
            pygame.draw.circle(screen, YELLOW, 
                             (int(self.screen_x), int(self.screen_y)), max(2, size))