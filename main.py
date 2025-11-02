"""
Math Crowd Runner - Main executable file
"""
import pygame
from constants import *
from utils import load_resources, init_font_cache
from game import Game
from game_objects import Button

class MathCrowdRunner:
    def __init__(self):
        pygame.init()
        
        # Initialize font cache after pygame.init()
        init_font_cache()
        
        # ตั้งค่าหน้าจอ
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Math Crowd Runner")
        self.clock = pygame.time.Clock()
        
        # โหลดทรัพยากรและฟอนต์
        self.assets = load_resources()
        self.fonts = {
            'font': pygame.font.Font(None, 48),
            'small_font': pygame.font.Font(None, 28),
            'big_font': pygame.font.Font(None, 72),
            'huge_font': pygame.font.Font(None, 36)
        }
        
        # Game State
        self.game_state = "MENU"
        self.current_level = 1
        self.game = None
        self.running = True
    
    def draw_menu(self):
        """วาดหน้าเมนู"""
        if self.assets.get('stage'):
            self.screen.blit(self.assets['stage'], (0, 0))
        else:
            self.screen.fill(BLACK)
        
        # กล่องโปร่งแสงสำหรับ title
        title_box = pygame.Surface((700, 100))
        title_box.set_alpha(150)
        title_box.fill(BLACK)
        self.screen.blit(title_box, (WIDTH//2 - 350, 130))
        
        title = self.fonts['big_font'].render("MATH CROWD RUNNER", True, CYAN)
        self.screen.blit(title, (WIDTH//2 - 320, 150))
        
        play_btn = Button(WIDTH//2 - 150, 300, 300, 100, "PLAY", GREEN)
        exit_btn = Button(WIDTH//2 - 150, 440, 300, 100, "EXIT", RED)
        
        play_btn.draw(self.screen, self.fonts['font'])
        exit_btn.draw(self.screen, self.fonts['font'])
        
        inst_font = pygame.font.Font(None, 24)
        inst1 = inst_font.render("Level 1: Basic Math (+, -, x)", True, BLACK)
        inst2 = inst_font.render("Level 2: Advanced (x, ÷, √, ^)", True, BLACK)
        inst3 = inst_font.render("Level 3: Mixed (all operations)", True, BLACK)
        
        self.screen.blit(inst1, (WIDTH//2 - 150, 560))
        self.screen.blit(inst2, (WIDTH//2 - 160, 590))
        self.screen.blit(inst3, (WIDTH//2 - 140, 620))
        
        return play_btn, exit_btn
    
    def handle_menu_events(self, event, play_btn, exit_btn):
        """จัดการ event ในหน้าเมนู"""
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if play_btn.check_click(mouse_pos):
                self.game_state = "PLAYING"
                self.current_level = 1
                self.game = Game(self.current_level, self.assets)
                self.game.start_game()
                # เล่นเพลง
                if self.assets.get('music_loaded'):
                    try:
                        pygame.mixer.music.play(-1)
                        pygame.mixer.music.set_volume(0.5)
                    except:
                        pass
            elif exit_btn.check_click(mouse_pos):
                self.running = False
    
    def handle_game_events(self, event):
        """จัดการ event ในเกม"""
        if event.type == pygame.KEYDOWN:
            if self.game:
                # เคลื่อนที่เฉพาะตอนกดปุ่ม (step-by-step)
                if not self.game.game_over and not self.game.won:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.game.crowd.move(-PLAYER_SPEED)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.game.crowd.move(PLAYER_SPEED)
                
                # ปุ่มเมื่อแพ้เกม
                if self.game.game_over:
                    if event.key == pygame.K_r:
                        # Restart ด่านปัจจุบัน
                        self.current_level = 1
                        self.game = Game(self.current_level, self.assets)
                        self.game.start_game()
                        # เล่นเพลงใหม่
                        if self.assets.get('music_loaded'):
                            try:
                                pygame.mixer.music.play(-1)
                                pygame.mixer.music.set_volume(0.5)
                            except:
                                pass
                    elif event.key == pygame.K_m:
                        # กลับเมนู
                        self.game_state = "MENU"
                        self.game = None
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
                
                # ปุ่มเมื่อชนะ
                if self.game and self.game.won:
                    if event.key == pygame.K_n and self.current_level < 3:
                        self.current_level += 1
                        self.game = Game(self.current_level, self.assets)
                        self.game.start_game()
                    elif event.key == pygame.K_m:
                        # กลับเมนู
                        self.game_state = "MENU"
                        self.game = None
                        try:
                            pygame.mixer.music.stop()
                        except:
                            pass
    
    def run(self):
        """ลูปหลักของเกม"""
        while self.running:
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.game_state == "MENU":
                    play_btn, exit_btn = self.draw_menu()
                    self.handle_menu_events(event, play_btn, exit_btn)
                elif self.game_state == "PLAYING":
                    self.handle_game_events(event)
            
            if self.game_state == "MENU":
                play_btn, exit_btn = self.draw_menu()
                play_btn.check_click(mouse_pos)
                exit_btn.check_click(mouse_pos)
            elif self.game_state == "PLAYING":
                if self.game:
                    self.game.update()
                    self.game.draw(self.screen, self.fonts)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    game = MathCrowdRunner()
    game.run()