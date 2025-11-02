"""
Game objects: Gate, LavaPit, Button
"""
import pygame
import random
import math
from constants import *
from utils import world_to_screen, get_font
from operations import Operation

class Gate:
    def __init__(self, z, level):
        self.z = z  # ความลึก 0.0 - 1.0
        self.depth = GATE_DEPTH
        self.used = False
        self.level = level
        
        # Cache screen position
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
        
        # สุ่ม operation แบบ "ซ้าย-ขวา ตรงข้ามกันเสมอ"
        
        # กำหนดประเภท operation ที่มีในแต่ละระดับ
        if level == 1:
            op_types = ['add_subtract']
        elif level == 2:
            op_types = ['multiply_divide']
        else:  # level 3
            op_types = ['add_subtract', 'multiply_divide', 'power_sqrt', 'extreme_divide']
        
        # สุ่มเลือกประเภท operation
        op_type = random.choice(op_types)
        
        # สร้าง operation ตามประเภทที่เลือก
        if op_type == 'add_subtract':
            # ซ้าย: บวก / ขวา: ลบ (ค่าต่างกัน)
            left_value = random.choice([10, 20, 30, 40, 50])
            right_value = random.choice([10, 20, 30, 40, 50])
            if random.random() < 0.5:
                self.left_op = Operation(f'+{left_value}', lambda c, v=left_value: c.add_people(v))
                self.right_op = Operation(f'-{right_value}', lambda c, v=right_value: c.remove_people(v))
            else:
                self.left_op = Operation(f'-{left_value}', lambda c, v=left_value: c.remove_people(v))
                self.right_op = Operation(f'+{right_value}', lambda c, v=right_value: c.add_people(v))
        
        elif op_type == 'multiply_divide':
            # ซ้าย: คูณ / ขวา: หาร (ค่าต่างกัน)
            left_factor = random.choice([2, 3, 4, 5])
            right_factor = random.choice([2, 3, 4, 5])
            if random.random() < 0.5:
                self.left_op = Operation(f'x{left_factor}', lambda c, f=left_factor: c.multiply_people(f))
                self.right_op = Operation(f'÷{right_factor}', lambda c, f=right_factor: c.divide_people(f))
            else:
                self.left_op = Operation(f'÷{left_factor}', lambda c, f=left_factor: c.divide_people(f))
                self.right_op = Operation(f'x{right_factor}', lambda c, f=right_factor: c.multiply_people(f))
        
        elif op_type == 'power_sqrt':
            # ซ้าย: ยกกำลัง / ขวา: รากที่สอง (หรือตรงกันข้าม)
            power_val = random.choice([2, 3])
            if random.random() < 0.5:
                self.left_op = Operation(f'^{power_val}', lambda c, p=power_val: c.power_people(p))
                self.right_op = Operation('√', lambda c: c.sqrt_people())
            else:
                self.left_op = Operation('√', lambda c: c.sqrt_people())
                self.right_op = Operation(f'^{power_val}', lambda c, p=power_val: c.power_people(p))
        
        elif op_type == 'extreme_divide':
            # ระดับ 3: หารจำนวนมาก vs คูณเล็กน้อย (ค่าต่างกัน)
            left_divide = random.choice([10, 15, 20])
            right_divide = random.choice([10, 15, 20])
            left_multiply = random.choice([2, 3])
            right_multiply = random.choice([2, 3])
            if random.random() < 0.5:
                self.left_op = Operation(f'÷{left_divide}', lambda c, d=left_divide: c.divide_people(d))
                self.right_op = Operation(f'x{right_multiply}', lambda c, m=right_multiply: c.multiply_people(m))
            else:
                self.left_op = Operation(f'x{left_multiply}', lambda c, m=left_multiply: c.multiply_people(m))
                self.right_op = Operation(f'÷{right_divide}', lambda c, d=right_divide: c.divide_people(d))
    
    def update_screen_position(self):
        """คำนวณตำแหน่งบนหน้าจอ (เรียกครั้งเดียวต่อ frame)"""
        self.screen_x, self.screen_y, self.scale = world_to_screen(0.5, self.z)
    
    def check_collision(self, crowd):
        if self.used or len(crowd.people) == 0:
            return False
        
        if abs(crowd.people[0].z - self.z) < 0.08:
            if crowd.center_x < 0.5:  # ซ้าย
                self.left_op.apply(crowd)
                self.used = True
                return True
            else:  # ขวา
                self.right_op.apply(crowd)
                self.used = True
                return True
        return False
    
    def draw(self, screen):
        if not self.used:
            gate_color = CYAN
            
            # วาดประตูซ้าย
            top_left_x, top_y, _ = world_to_screen(0.0, self.z - self.depth/2)
            top_mid_x, _, _ = world_to_screen(0.5, self.z - self.depth/2)
            bottom_left_x, bottom_y, _ = world_to_screen(0.0, self.z + self.depth/2)
            bottom_mid_x, _, _ = world_to_screen(0.5, self.z + self.depth/2)
            
            left_gate_points = [
                (top_left_x, top_y),
                (top_mid_x - 5, top_y),
                (bottom_mid_x - 5, bottom_y),
                (bottom_left_x, bottom_y)
            ]
            pygame.draw.polygon(screen, gate_color, left_gate_points)
            pygame.draw.polygon(screen, BLACK, left_gate_points, 5)
            
            # วาดข้อความซ้าย (ใช้ font cache)
            center_x = (top_left_x + top_mid_x + bottom_left_x + bottom_mid_x) / 4
            center_y = (top_y + bottom_y) / 2
            font_size = int(72 * self.scale)
            dynamic_font = get_font(font_size)
            text = dynamic_font.render(self.left_op.symbol, True, WHITE)
            text_rect = text.get_rect(center=(int(center_x), int(center_y)))
            screen.blit(text, text_rect)
            
            # วาดประตูขวา
            top_right_x, _, _ = world_to_screen(1.0, self.z - self.depth/2)
            bottom_right_x, _, _ = world_to_screen(1.0, self.z + self.depth/2)
            
            right_gate_points = [
                (top_mid_x + 5, top_y),
                (top_right_x, top_y),
                (bottom_right_x, bottom_y),
                (bottom_mid_x + 5, bottom_y)
            ]
            pygame.draw.polygon(screen, gate_color, right_gate_points)
            pygame.draw.polygon(screen, BLACK, right_gate_points, 5)
            
            # วาดข้อความขวา
            center_x = (top_right_x + top_mid_x + bottom_right_x + bottom_mid_x) / 4
            text = dynamic_font.render(self.right_op.symbol, True, WHITE)
            text_rect = text.get_rect(center=(int(center_x), int(center_y)))
            screen.blit(text, text_rect)
            
            # วาดเส้นแบ่งกลาง
            pygame.draw.line(screen, WHITE, (top_mid_x, top_y), (bottom_mid_x, bottom_y), 8)


class LavaPit:
    """บ่อลาวาที่จะทำให้สูญเสียคน"""
    def __init__(self, x, z):
        self.x = x  # 0.0 - 1.0 (ซ้าย-ขวา)
        self.z = z  # 0.0 - 1.0 (ไกล-ใกล้)
        self.base_width = LAVA_BASE_WIDTH
        self.base_height = LAVA_BASE_HEIGHT
        self.damage = random.randint(5, 15)
        self.active = True
        self.color = (255, 165, 0)  # ORANGE
        self.offset_phase = random.uniform(0, 360)  # สำหรับ smooth animation
        
        # Cache screen position
        self.screen_x = 0
        self.screen_y = 0
        self.scale = 1.0
        
    def update_screen_position(self):
        """คำนวณตำแหน่งบนหน้าจอ (เรียกครั้งเดียวต่อ frame)"""
        self.screen_x, self.screen_y, self.scale = world_to_screen(self.x, self.z)
        
    def draw(self, screen):
        """วาดบ่อลาวา"""
        if self.active:
            width = int(self.base_width * self.scale)
            height = int(self.base_height * self.scale)
            
            # Smooth animation แทน random jump
            self.offset_phase = (self.offset_phase + 0.15) % 360
            offset_x = math.sin(math.radians(self.offset_phase)) * 2
            offset_y = math.cos(math.radians(self.offset_phase)) * 2
            
            pygame.draw.ellipse(screen, self.color, 
                              (int(self.screen_x - width//2 + offset_x), 
                               int(self.screen_y - height//2 + offset_y), 
                               width, height))
            pygame.draw.ellipse(screen, RED, 
                              (int(self.screen_x - width//2 + offset_x + 5), 
                               int(self.screen_y - height//2 + offset_y + 5), 
                               max(10, width - 10), max(10, height - 10)))
    
    def check_collision(self, crowd):
        """เช็คชนกับฝูงชน"""
        if not self.active or len(crowd.people) == 0:
            return False
        
        hit = False
        for person in crowd.people[:]:
            dist_x = abs(person.x - self.x)
            dist_z = abs(person.z - self.z)
            
            if dist_x < 0.08 and dist_z < 0.08:
                hit = True
                break
        
        if hit:
            crowd.remove_people(min(self.damage, crowd.count))
            self.active = False
            return True
        return False


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover = False
        
    def draw(self, screen, font):
        color = self.color if not self.hover else tuple(min(c + 30, 255) for c in self.color)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, WHITE, self.rect, 3)
        
        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
    
    def check_click(self, pos):
        self.hover = self.rect.collidepoint(pos)
        return self.hover