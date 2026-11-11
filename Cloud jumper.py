import random
import sys
import pygame

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cloud Jumper - Floaty Cloud")
FPS = 60
clock = pygame.time.Clock()

# --- LOAD & PROPERLY SCALE ASSETS ---
starting_point_raw = pygame.image.load("starting_point.png").convert_alpha()
starting_point = pygame.transform.scale(starting_point_raw, (450, 300))

player_img = pygame.image.load("player_image.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (140, 120))

floaty_frames = [
    pygame.transform.scale(
        pygame.image.load("floaty_thing.png").convert_alpha(), (130, 60)
    ),
    pygame.transform.scale(
        pygame.image.load("floaty_thing_2.png").convert_alpha(), (130, 60)
    ),
]

rainy_cloud_img = pygame.transform.scale(
    pygame.image.load("rainy_cloud.png").convert_alpha(), (130, 70)
)

bird_frames = [
    pygame.transform.scale(
        pygame.image.load("frame_1_bird.png").convert_alpha(), (100, 65)
    ),
    pygame.transform.scale(
        pygame.image.load("frame_2_bird.png").convert_alpha(), (100, 65)
    ),
]

thunder_frames = [
    pygame.transform.scale(
        pygame.image.load("frame_1_thunder.png").convert_alpha(), (100, 100)
    ),
    pygame.transform.scale(
        pygame.image.load("frame_2_thunder.png").convert_alpha(), (100, 100)
    ),
]

SKY_BLUE = (30, 144, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)

Game = True
GameOver = False
game_started = False
Score = 0
score_timer = 0


class Player(pygame.sprite.Sprite):

  def __init__(self):
    super().__init__()
    self.image = player_img
    self.rect = self.image.get_rect()
    self.rect.x = 180
    self.rect.y = HEIGHT - 330
    self.velocity_y = 0
    self.jump_power = -7.5
    self.gravity = 0.35

  def update(self):
    global GameOver
    if game_started:
      self.velocity_y += self.gravity
      self.rect.y += self.velocity_y

      # If you hit the bottom of the screen, it's Game Over! (No more cheese)
      if self.rect.bottom >= HEIGHT:
        GameOver = True

      if self.rect.top < 0:
        self.rect.top = 0
        self.velocity_y = 0

  def jump(self):
    self.velocity_y = self.jump_power


class Obstacle(pygame.sprite.Sprite):

  def __init__(self, x, y):
    super().__init__()
    self.obs_type = random.choice(["floaty", "rainy", "bird", "thunder"])
    self.anim_timer = 0
    self.frame_index = 0

    self.original_y = y
    self.vertical_speed = 2
    self.moving_up = random.choice([True, False])

    if self.obs_type == "floaty":
      self.image = floaty_frames[0]
    elif self.obs_type == "rainy":
      self.image = rainy_cloud_img
    elif self.obs_type == "bird":
      self.image = bird_frames[0]
    elif self.obs_type == "thunder":
      self.image = thunder_frames[0]

    self.rect = self.image.get_rect()
    self.rect.x = x
    self.rect.y = y

  def update(self):
    # Thunder stays stationary horizontally; others move forward
    if self.obs_type != "thunder":
      self.rect.x -= 4

    # Rainy cloud goes up and down
    if self.obs_type == "rainy":
      if self.moving_up:
        self.rect.y -= self.vertical_speed
        if self.rect.y < self.original_y - 50:
          self.moving_up = False
      else:
        self.rect.y += self.vertical_speed
        if self.rect.y > self.original_y + 50:
          self.moving_up = True

    # Animation frame switching
    self.anim_timer += 1
    if self.anim_timer > 12:
      self.anim_timer = 0
      self.frame_index = 1 - self.frame_index
      if self.obs_type == "floaty":
        self.image = floaty_frames[self.frame_index]
      elif self.obs_type == "bird":
        self.image = bird_frames[self.frame_index]
      elif self.obs_type == "thunder":
        self.image = thunder_frames[self.frame_index]

    if self.rect.right < 0:
      self.kill()


# --- INITIALIZATION ---
all_sprites = pygame.sprite.Group()
obstacle_group = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

spawn_timer = 0
starting_platform_x = 0

# --- MAIN GAME LOOP ---
while Game:
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      Game = False
      pygame.quit()
      sys.exit()

    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_SPACE:
        if GameOver:
          GameOver = False
          game_started = False
          Score = 0
          score_timer = 0
          starting_platform_x = 0
          obstacle_group.empty()
          all_sprites.empty()
          player = Player()
          all_sprites.add(player)
        else:
          if not game_started:
            game_started = True
          player.jump()

  window.fill(SKY_BLUE)

  if not GameOver:
    if not game_started:
      hill_rect = starting_point.get_rect(bottomleft=(starting_platform_x, HEIGHT))
      window.blit(starting_point, hill_rect)
      window.blit(player.image, player.rect)
    else:
      score_timer += 1
      if score_timer >= 15:
        Score += 1
        score_timer = 0

      if starting_platform_x > -450:
        starting_platform_x -= 4
      if starting_platform_x > -450:
        hill_rect = starting_point.get_rect(
            bottomleft=(starting_platform_x, HEIGHT)
        )
        window.blit(starting_point, hill_rect)

      spawn_timer += 1
      if spawn_timer > 70:
        spawn_timer = 0
        obstacle_x = WIDTH
        obstacle_y = random.randint(100, HEIGHT - 150)
        new_obstacle = Obstacle(obstacle_x, obstacle_y)
        all_sprites.add(new_obstacle)
        obstacle_group.add(new_obstacle)

      all_sprites.update()

      if pygame.sprite.spritecollideany(player, obstacle_group):
        GameOver = True

      all_sprites.draw(window)
  else:
    window.fill((20, 20, 30))
    font = pygame.font.Font(None, 40)
    game_over_text = font.render("GAME OVER - Press SPACE to Restart", True, WHITE)
    score_display = font.render(f"Final Score: {Score}", True, YELLOW)
    window.blit(
        game_over_text,
        (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 30),
    )
    window.blit(
        score_display,
        (WIDTH // 2 - score_display.get_width() // 2, HEIGHT // 2 + 20),
    )

  score_text = pygame.font.Font(None, 36).render(f"Score: {Score}", True, WHITE)
  window.blit(score_text, (15, 15))

  pygame.display.flip()
  clock.tick(FPS)