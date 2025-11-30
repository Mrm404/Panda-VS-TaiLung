import os
import pygame
from os.path import join
import sys
pygame.init()
# ---- Screen ----
WIDTH, HEIGHT = 800, 600
FPS = 60
PLAYER_WIDTH, PLAYER_HEIGHT = 70, 70
PLAYER_VEL = 5
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Platformer - Panda Player")
# Fonts
try:
    font = pygame.font.SysFont("Times New Roman", 50)
except Exception:
    font = pygame.font.Font(None, 30)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

def safe_load_image(path, size=None):
    base_path = os.path.dirname(__file__)
    full_path = os.path.join(base_path, path)
    
    if not os.path.exists(full_path):
        print(f"⚠️ Missing image: {full_path}")
        surf = pygame.Surface((WIDTH, HEIGHT))
        surf.fill((200, 200, 200))
        return surf
    
    image = pygame.image.load(full_path).convert()
    if size:
        image = pygame.transform.scale(image, size)
    return image

menu_bg = safe_load_image("assets/using assets/Menu_BG.png", (WIDTH, HEIGHT))

def draw_text(text, x, y):
    label = font.render(text, True, BLACK)
    window.blit(label, (x, y))



# ---- Colors ----
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# ---- Helper functions ----
def load_image(folder, name, scale_to=None):
    path = os.path.join("assets", folder, name)
    img = pygame.image.load(path).convert_alpha()
    if scale_to:
        img = pygame.transform.smoothscale(img, scale_to)
    return img

def load_frames(folder, filename, frame_count, scale=(80,80)):
    path = os.path.join("assets", folder, filename)
    sheet = pygame.image.load(path).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // frame_count
    frames = []
    for i in range(frame_count):
        frame = sheet.subsurface(pygame.Rect(i*frame_width,0,frame_width,sheet_height))
        frame = pygame.transform.scale(frame, scale)
        frames.append(frame)
    return frames

# ---- Tilemap ----
block_size = 64  
TILE_SIZE = 32

tiles = {
    1: load_image("tiles","1.png"),
    2: load_image("tiles","2.png"),
    3: load_image("tiles","3.png"),
    5: load_image("tiles","5.png"),
    8: load_image("tiles","red_tiles.png"),
    7: load_image("tiles","black_tiles.JPG "),
    14: load_image("tiles","14.png"),
    15: load_image("tiles","15.png"),
    16: load_image("tiles","16.png"),
}

TILEMAP01= [
    [0]*25,
    [0]*25,
    [2,3,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,15,15,15,15,15,15],
    [0]*25,
    [0]*25,
    [0,0,0,0,0,0,15,15,15,15,15,15,15,15,15,15,15,0,0,0,0,0,0,0,0],
    [0]*25,
    [0]*25,
    [0]*25,
    [0,0,0,14,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2],
    [2,2,2]+[0]*22
]
# --- LEVEL 2 TILEMAP (your beautiful staircase design) ---
TILEMAP02 = [
    [0]*25,
    [0]*25,
    [0]*25,
    [0]*25,
    [0]*25,
    [0]*25,
    [0]*25,
    [0]*25,
    [0]*25,
    [0,0,0,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,8,],
    [8,8,8]+[0]*22
]

# ---- Blocks ----
class Object(pygame.sprite.Sprite):
    def __init__(self,x,y,w,h,name=None):
        super().__init__()
        self.rect = pygame.Rect(x,y,w,h)
        self.image = pygame.Surface((w,h),pygame.SRCALPHA)
        self.name = name
        self.mask = pygame.mask.from_surface(self.image)
    def draw(self,win,offset_x):
        win.blit(self.image,(self.rect.x-offset_x,self.rect.y))

class Block(Object):
    def __init__(self,x,y,size):
        super().__init__(x,y,size,size)
        self.image.fill((150,150,150))
        self.mask = pygame.mask.from_surface(self.image)

    def build_tilemap_level1():
        objects = []
        tile_w = 33
        tile_h = 56

        for row_index, row in enumerate(TILEMAP01):
            for col_index, tile_id in enumerate(row):
                if tile_id == 0:
                     continue
                if tile_id in tiles:
                    x = col_index * tile_w
                    y = row_index * tile_h
                    block = Object(x, y, tile_w, tile_h)
                    block.image.blit(tiles[tile_id], (0, 0))
                    block.mask = pygame.mask.from_surface(block.image)
                    objects.append(block)
        return objects
    
    def  build_tilemap_level2():
        objects = []
        tile_w = 33
        tile_h = 56

        for row_index, row in enumerate(TILEMAP02):
            for col_index, tile_id in enumerate(row):
                if tile_id == 0:
                    continue
                if tile_id in tiles:
                    x = col_index * tile_w
                    y = row_index * tile_h
                    block = Object(x, y, tile_w, tile_h)
                    block.image.blit(tiles[tile_id], (0, 0))
                    block.mask = pygame.mask.from_surface(block.image)
                    objects.append(block)
        return objects
class Cannon:
    def __init__(self, x, y, attack_range=300):
        self.width = 50
        self.height = 50
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.image = pygame.transform.scale(
            pygame.image.load("assets/using assets/cannon.png").convert_alpha(),
            (self.width, self.height)
        )

        self.cannonballs = []
        self.last_fired = pygame.time.get_ticks()
        self.fire_rate = 1500          # ms between shots
        self.attack_range = attack_range   # vertical-only range check

    class CannonBall:
        def __init__(self, x, y, vel_x):
            self.rect = pygame.Rect(x, y, 16, 12)
            self.vel_x = vel_x
            self.image = pygame.Surface((16, 12), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (0, 0, 0), (8, 6), 6)
            self.used = False

        def update(self):
            self.rect.x += self.vel_x

    def update(self, player):
        # Check vertical range ONLY
        if abs(player.rect.centery - self.rect.centery) > self.attack_range:
            return  # Player too high/low → do not fire

        # Fire rate timing
        now = pygame.time.get_ticks()
        if now - self.last_fired >= self.fire_rate:
            self.last_fired = now
            direction = -1 if self.rect.x > player.rect.x else 1
            ball = Cannon.CannonBall(
                self.rect.centerx,
                self.rect.centery,
                vel_x=6 * direction
            )
            self.cannonballs.append(ball)

        # Update balls
        for ball in self.cannonballs:
            ball.update()
            if player.rect.colliderect(ball.rect):
                player.health -= 0.5
                ball.used = True

        # Remove used/out of screen
        screen_width = pygame.display.get_surface().get_width()
        self.cannonballs = [
            b for b in self.cannonballs
            if not b.used and 0 < b.rect.x < screen_width
        ]

    def draw(self, surface):
        # Draw the cannon image
        surface.blit(self.image, self.rect.topleft)

        # Update and draw cannonballs
        for ball in self.cannonballs:
            surface.blit(ball.image, ball.rect.topleft)



# ---- Player ----  
# (Everything unchanged)
class Player(pygame.sprite.Sprite):
    GRAVITY = 1
    def __init__(self,x,y):
        super().__init__()
        self.rect = pygame.Rect(x,y,PLAYER_WIDTH,PLAYER_HEIGHT)
        self.x_vel=0
        self.y_vel=0
        self.direction="right"
        self.jump_count=0
        self.fall_count=0
        self.is_attacking=False
        self.attack_frames=[load_image("Po",f"attack{i}.png",(PLAYER_WIDTH,PLAYER_HEIGHT)) for i in range(1,5)]
        self.attack_frame_index=0
        self.attack_cooldown=0
        self.attack_speed=5
        self.attack_timer=0
        self.health=10
        self.max_health=10
        self.image=load_image("Po","idle.png",(PLAYER_WIDTH,PLAYER_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.sprite=self.image

    def move_left(self,vel): self.x_vel=-vel; self.direction="left"
    def move_right(self,vel): self.x_vel=vel; self.direction="right"
    def jump(self):
        if self.jump_count<2: self.y_vel=-self.GRAVITY*8; self.jump_count+=1
    def landed(self): self.y_vel=0; self.jump_count=0; self.fall_count=0
    def hit_head(self): self.y_vel=0
    def attack(self):
        if self.attack_cooldown==0: self.is_attacking=True; self.attack_frame_index=0; self.attack_timer=0; self.attack_cooldown=30
    def stop_attack(self): self.is_attacking=False; self.attack_frame_index=0; self.attack_timer=0
    def loop(self,fps):
        self.y_vel+=min(1,(self.fall_count/fps)*self.GRAVITY)
        self.rect.x+=self.x_vel
        self.rect.y+=self.y_vel
        self.fall_count+=1
        if self.attack_cooldown>0: self.attack_cooldown-=1
        self.update_sprite()
        self.mask=pygame.mask.from_surface(self.sprite)
    def update_sprite(self):
        if self.is_attacking:
            frames=self.attack_frames
            self.sprite=frames[self.attack_frame_index]
            self.attack_timer+=1
            if self.attack_timer>=self.attack_speed:
                self.attack_timer=0
                self.attack_frame_index+=1
                if self.attack_frame_index>=len(frames): self.attack_frame_index=0
        else: self.sprite=self.image
    def draw(self,win,offset_x):
        win.blit(self.sprite,(self.rect.x-offset_x,self.rect.y))
        bar_width = 100
        bar_height = 10
        bar_x = self.rect.x - offset_x
        bar_y = self.rect.y - 15
        pygame.draw.rect(win, RED, (bar_x, bar_y, bar_width, bar_height))
        current_width = int(bar_width * (self.health / self.max_health))
        pygame.draw.rect(win, GREEN, (bar_x, bar_y, current_width, bar_height))
        pygame.draw.rect(win, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)

# -------------------------------
# Enemy class - Lord Shen
# -------------------------------

class Enemy:
    def __init__(self, x, y):
        self.width = 68
        self.height = 150

        # Correct usage of load_frames
        self.frames = load_frames("using assets", "lordshen.png", 6, scale=(self.width, self.height))

        self.rect = pygame.Rect(x, y, self.width, self.height)

        self.frame_index = 0
        self.frame_timer = 0
        self.frame_delay = 12

        self.vx = 2
        self.direction = 1  # 1 = right, -1 = left
        self.min_x = x - 120
        self.max_x = x + 120

        self.alive = True
        self.health = 8
        self.max_health = 8

    def animate(self):
        self.frame_timer += 1
        if self.frame_timer >= self.frame_delay:
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.frame_timer = 0

    def update(self, player_rect):
        if not self.alive:
            return False

        # Movement (patrol)
        self.rect.x += self.vx * self.direction
        if self.rect.x >= self.max_x:
            self.direction = -1
        elif self.rect.x <= self.min_x:
            self.direction = 1

        # Collision with the player
        if self.rect.colliderect(player_rect.inflate(40, 40)):
            return True

        return False

    def draw(self, surface):
        frame = self.frames[self.frame_index]

        # Flip if moving left
        if self.direction < 0:
            frame = pygame.transform.flip(frame, True, False)

        surface.blit(frame, (self.rect.x, self.rect.y))

        # Health bar
        bar_width = self.width
        bar_height = 8
        bar_x = self.rect.x
        bar_y = self.rect.y - 10

        pygame.draw.rect(surface, (255, 0, 0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 255, 0),
                         (bar_x, bar_y, int(bar_width * (self.health / self.max_health)), bar_height))
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 2)

# ---- Tai Lung Boss ----
class TaiLungBoss:
    def __init__(self,pos):
        self.frames=load_frames("using assets","TaiLung.png",6,(85,155))
        self.pos=list(pos)
        self.speed=2; self.direction=1; self.min_x=150; self.max_x=600
        self.health=8; self.max_health=8; self.alive=True
        self.frame_index=0; self.frame_timer=0; self.frame_delay=10
        self.mode="walk"; self.attack_distance=120; self.alpha=255
    def update(self,player_rect,keys):
        if not self.alive: return
        player_center=player_rect.centerx; tai_center=self.pos[0]+75
        distance=abs(player_center-tai_center)
        self.mode="walk" if distance>self.attack_distance else "attack"
        self.frame_timer+=1
        if self.frame_timer>=self.frame_delay:
            self.frame_timer=0
            if self.mode=="walk": self.frame_index=0
            else: self.frame_index=(self.frame_index+1)%len(self.frames)
        if self.mode=="walk":
            self.pos[0]+=self.speed*self.direction
            if self.pos[0]>=self.max_x:self.direction=-1
            elif self.pos[0]<=self.min_x:self.direction=1
        else:
            if player_center<tai_center: self.pos[0]-=0.1; self.direction=-1
            else: self.pos[0]+=0.1; self.direction=1
    def attack_player(self,player_rect,player):
        if not self.alive: return
        tai_rect=pygame.Rect(self.pos[0],self.pos[1],90,90)
        if player_rect.colliderect(tai_rect):
            player.health=max(0,player.health-0.005)
    def take_damage(self,attack_rect,player):
        if not self.alive: return
        tai_rect=pygame.Rect(self.pos[0],self.pos[1],100,100)
        if attack_rect and attack_rect.colliderect(tai_rect):
            self.health-=0.2
            if self.health<=0: self.health=0; self.alive=False; self.alpha=255; player.health=player.max_health
    def draw(self,screen):
        if not self.alive: return
        frame=self.frames[self.frame_index]
        if self.mode=="walk" and self.direction<0: frame=pygame.transform.flip(frame,True,False)
        screen.blit(frame,self.pos)
        # Health bar
        bar_width=60; bar_height=6; bar_x=self.pos[0]+20; bar_y=self.pos[1]-10
        pygame.draw.rect(screen,RED,(bar_x,bar_y,bar_width,bar_height))
        current_width=int(bar_width*(self.health/self.max_health))
        pygame.draw.rect(screen,GREEN,(bar_x,bar_y,current_width,bar_height))
        pygame.draw.rect(screen,BLACK,(bar_x,bar_y,bar_width,bar_height),2)

# ---- Wolf Boss ----
class WolfBoss:
    def __init__(self,pos):
        self.frames=load_frames("using assets","WolfBOSS.png",2,(60,50))
        self.pos=list(pos)
        self.speed=1.5; self.direction=-1
        self.min_x=self.pos[0] - 200
        self.max_x=self.pos[0]-10
        self.health=8; self.max_health=8; self.alive=True
    def update(self,player_rect,keys):
        if not self.alive: return
        self.pos[0]+=self.speed*self.direction
        if self.pos[0]<=self.min_x:self.direction=1
        elif self.pos[0]>=self.max_x:self.direction=-1
    def attack_player(self,player_rect,player):
        if not self.alive: return
        wolf_rect=pygame.Rect(self.pos[0],self.pos[1],60,50)
        if player_rect.colliderect(wolf_rect): 
            player.health=max(0,player.health-0.005)
    def take_damage(self,attack_rect):
        if not self.alive: return
        wolf_rect=pygame.Rect(self.pos[0],self.pos[1],60,50)
        if attack_rect and attack_rect.colliderect(wolf_rect):
            self.health-=0.2
            if self.health<=0:self.alive=False
    def draw(self,screen):
        if not self.alive: return
        frame=self.frames[1] if self.direction>0 else self.frames[0]
        screen.blit(frame,self.pos)
        bar_width=60; bar_height=6; bar_x=self.pos[0]+10; bar_y=self.pos[1]-10
        pygame.draw.rect(screen,RED,(bar_x,bar_y,bar_width,bar_height))
        current_width=int(bar_width*(self.health/self.max_health))
        pygame.draw.rect(screen,GREEN,(bar_x,bar_y,current_width,bar_height))
        pygame.draw.rect(screen,BLACK,(bar_x,bar_y,bar_width,bar_height),2)

# ---- Key helpers ----  
def create_key(image_path,tile_pos,tile_size):
    key_img=pygame.image.load(image_path).convert_alpha()
    key_img=pygame.transform.scale(key_img,(tile_size,tile_size))
    key_rect=pygame.Rect(tile_pos[0]*tile_size,tile_pos[1]*tile_size,tile_size,tile_size)
    return {"image":key_img,"rect":key_rect,"collected":False}

def draw_key(screen,key):
    if not key["collected"]: screen.blit(key["image"],key["rect"])

def check_key_collision(key,player_rect):
    if not key["collected"] and player_rect.colliderect(key["rect"]): key["collected"]=True
    return key["collected"]



# ============================================================
#                           LEVEL 1
# ============================================================
def level1(window):
    clock = pygame.time.Clock()
    bg_image = load_image("using assets", "winter_bg.png", (WIDTH, HEIGHT))

    player = Player(10, HEIGHT - PLAYER_HEIGHT - 64)
    tailung = TaiLungBoss([150, HEIGHT - PLAYER_HEIGHT - 120])
    wolf = WolfBoss([400, HEIGHT - PLAYER_HEIGHT - 285])

    key = create_key("assets/using assets/KEY.png", (10, 8), 32)  # visible position
    door_closed = pygame.transform.scale(pygame.image.load("assets/using assets/prison_house.png"), (200, 200))
    door_open = pygame.transform.scale(pygame.image.load("assets/using assets/prison_door-opened.png"), (200, 200))
    door_rect = pygame.Rect(630, HEIGHT - 670, 80, 120)
    door_opened = False

    objects = Block.build_tilemap_level1()   # Fixed call

    offset_x = 0
    run = True

    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

        keys = pygame.key.get_pressed()
        player.x_vel = 0
        if keys[pygame.K_LEFT]:  player.move_left(PLAYER_VEL)
        if keys[pygame.K_RIGHT]: player.move_right(PLAYER_VEL)
        if keys[pygame.K_SPACE]: player.jump()
        if keys[pygame.K_a]:     player.attack()
        else:                    player.stop_attack()

        # Player movement & physics
        player.loop(FPS)
        player.rect.x += player.x_vel

        # Platform collision
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.y_vel > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                elif player.y_vel < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()

        # Update bosses (removed extra "keys" argument)
        tailung.update(player.rect, keys)
        wolf.update(player.rect, keys)

        # Attack & damage
        attack_rect = pygame.Rect(player.rect.x + 40, player.rect.y, 50, 80) if player.is_attacking else None
        tailung.take_damage(attack_rect, player)
        wolf.take_damage(attack_rect)
        tailung.attack_player(player.rect, player)
        wolf.attack_player(player.rect, player)

        # Key & door
        check_key_collision(key, player.rect)
        if player.rect.colliderect(door_rect) and key["collected"]:
            door_opened = True

        # Drawing
        window.blit(bg_image, (0, 0))
        for obj in objects:
            obj.draw(window, offset_x)
        player.draw(window, offset_x)
        tailung.draw(window)
        wolf.draw(window)
        draw_key(window, key)
        window.blit(door_open if door_opened else door_closed, door_rect.topleft)

        pygame.display.update()

        # Win / Lose
        if door_opened and player.rect.colliderect(door_rect):
            pygame.time.wait(1000)
            return "next"
        if player.health <= 0:
            pygame.time.wait(1000)
            return "dead"

    return "exit"

# ============================================================
#                           LEVEL 2 
# ============================================================
def level2(window):
    clock = pygame.time.Clock()
    bg_image = load_image("using assets", "red_sky.jpg", (WIDTH, HEIGHT))

    player = Player(50, HEIGHT - PLAYER_HEIGHT - 64)
    lord_shen = Enemy(300, HEIGHT - PLAYER_HEIGHT - 180)
    cannon = Cannon(650, HEIGHT - 200)

    key = create_key("assets/using assets/KEY.png", (5, 7), 32)


    objects = Block.build_tilemap_level2()

    offset_x = 0
    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

        keys = pygame.key.get_pressed()
        player.x_vel = 0

        if keys[pygame.K_LEFT]:  player.move_left(PLAYER_VEL)
        if keys[pygame.K_RIGHT]: player.move_right(PLAYER_VEL)
        if keys[pygame.K_SPACE]: player.jump()
        if keys[pygame.K_a]:     player.attack()
        else:                    player.stop_attack()

        player.loop(FPS)
        player.rect.x += player.x_vel

        # Platform collision
        for obj in objects:
            if pygame.sprite.collide_mask(player, obj):
                if player.y_vel > 0:
                    player.rect.bottom = obj.rect.top
                    player.landed()
                elif player.y_vel < 0:
                    player.rect.top = obj.rect.bottom
                    player.hit_head()

        # Lord Shen update
        if lord_shen.alive:
            lord_shen.animate()
            if lord_shen.update(player.rect):
                player.health -= 0.03

        # Cannon
        cannon.update(player)

        # Attack hit on Lord Shen
        attack_rect = pygame.Rect(player.rect.x + 40, player.rect.y, 50, 80) if player.is_attacking else None
        if attack_rect and lord_shen.alive:
            if attack_rect.colliderect(lord_shen.rect):
                lord_shen.health -= 0.3
                if lord_shen.health <= 0:
                    lord_shen.alive = False

        # Key (still working)
        check_key_collision(key, player.rect)


        # Drawing
        window.blit(bg_image, (0, 0))

        for obj in objects:
            obj.draw(window, offset_x)

        player.draw(window, offset_x)

        if lord_shen.alive:
            lord_shen.draw(window)

        cannon.draw(window)
        draw_key(window, key)

        # Removed drawing of door

        pygame.display.update()

        # Removed next-level condition (door collision)

        if player.health <= 0:
            pygame.time.wait(1000)
            return "dead"

    return "exit"


# ============================================================
#                           Main Menu
# ============================================================

def main_menu():
    clock = pygame.time.Clock()
    
    while True:
        window.blit(menu_bg, (0, 0))

        draw_text("Kung Fu Game", 250, 150)
        draw_text("1. Start Game", 230, 230)
        draw_text("2. Settings", 230, 330)
        draw_text("3. Exit", 230, 430)

        pygame.display.flip()

        for event in pygame.event.get():  # <-- KEYDOWN must be inside this loop
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    result = level1(window)
                    if result == "next":
                        pygame.time.delay(2000)
                        level2(window)

                elif event.key == pygame.K_2:
                    print("Settings selected (not implemented).")

                elif event.key == pygame.K_3:
                    pygame.quit()
                    sys.exit(0)

        clock.tick(30)

if __name__ == "__main__":
    main_menu()
