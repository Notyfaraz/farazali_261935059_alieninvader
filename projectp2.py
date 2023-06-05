import pygame
import os
import random

pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SPACE INVADER")

# Loading images
hero_spaceship = pygame.image.load(os.path.join("game", "hero.png"))
villan_ship1 = pygame.image.load(os.path.join("game", "villan1.png"))
villan_ship2 = pygame.image.load(os.path.join("game", "villan2.png"))
villan_ship3 = pygame.image.load(os.path.join("game", "villan3.png"))
astroid = pygame.image.load(os.path.join("game", "astroid.png"))
bullet = pygame.image.load(os.path.join("game", "bullet.png"))


# Background
background = pygame.transform.scale(pygame.image.load(os.path.join("game", "background.png")), (WIDTH, HEIGHT))

# Background music
pygame.mixer.music.load(os.path.join("game", "background.wav"))
pygame.mixer.music.set_volume(0.2)  # Set the volume level (0.0 to 1.0)
pygame.mixer.music.play(-1)  # Play the music in a loop

# Explosion sound
explosion_sound = pygame.mixer.Sound(os.path.join("game", "explosion.wav"))
#the secondary class of this function it shows composition with ship and enemy ship class
class Bullet:
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
        self.mask = pygame.mask.from_surface(self.image)

    def display(self, window):
        window.blit(self.image, (self.x, self.y))

    def off_screen(self, height):
        return self.y < 0 or self.y > height

#the overlap function removes one object when they collide with each other
    def collide(self, obj):
        offset_x = obj.x - self.x
        offset_y = obj.y - self.y
        return self.mask.overlap(obj.mask, (offset_x, offset_y)) is not None

#parent class
class Ship:
    Cooldown = 30 #cool down for bullet

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.bullet_img = None
        self.bullets = [] #composition it is another class object
        self.cool_down_counter = 0

    def display(self, window):
        window.blit(self.ship_img, (self.x, self.y)) #window.blit function draws in on the background
        for bullet in self.bullets:
            bullet.display(window)

    def cooldown(self):
        if self.cool_down_counter >= self.Cooldown: #cool down counter is a built in function
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1
#allows user to shoot bullet when the cooldown counter is clear it will create a class and whenever user shoots it will append it
    def shoot(self):
        if self.cool_down_counter == 0:
            bullet1 = Bullet(self.x + self.get_width() // 2, self.y, self.bullet_img)
            self.bullets.append(bullet1)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()

    def get_height(self):
        return self.ship_img.get_height()

class EnemyShip(Ship): #inheritence
    villan_colour = {"blue": (villan_ship1, bullet), "orange": (villan_ship2, bullet), "red": (villan_ship3, bullet)} #class created to store all spaceship images

    def __init__(self, x, y, colour, health=100, speed=1):
        super().__init__(x, y, health)
        self.ship_img, self.bullet_img = self.villan_colour[colour]
        self.mask = pygame.mask.from_surface(self.ship_img) #mask function stops collision for happening outside the frsme
        self.speed = speed

    def move(self):
        self.y += self.speed

    def move_bullets(self, speed, player_ship):
        self.cooldown()

# for loop applied on bullet code which applement the bullet speed and reduces 10 percent health if it goes out of the frame
        for bullet in self.bullets:
            bullet.y += speed
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            elif bullet.collide(player_ship):
                player_ship.health -= 10
                self.bullets.remove(bullet)
#interits from the ship class
class Asteroid(Ship):

    def __init__(self, x, y, health=100, speed=1):
        super().__init__(x, y, health)
        self.ship_img = astroid #applying image
        self.bullet_img = None #because it doesnt shoot
        self.mask = pygame.mask.from_surface(self.ship_img) #collision of pixels
        self.speed = speed

    def move(self):
        self.y += self.speed
#inherits from ship class
class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = hero_spaceship
        self.bullet_img = bullet
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_bullets(self, speed, objs):
        self.cooldown()

#applies a for loop on bullet list it implement the speed of the code
        for bullet in self.bullets:
            bullet.y += speed
            if bullet.off_screen(HEIGHT):
                self.bullets.remove(bullet)
            else:
                for obj in objs:
                    if bullet.collide(obj): #(aggregation) collide was created outside any class
                        objs.remove(obj)
                        self.bullets.remove(bullet)
                        explosion_sound.play()  # Play explosion sound
                        break

    def display(self, window):
        super().display(window)
        self.health_bar(window)

    def health_bar(self, window):
        pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health / self.max_health), 10))

def collide(obj1, obj2): #function created outside the class which removes one object when obj1 and obj2 crash
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) is not None

def main():
    run = True
    FPS = 60 #framerate
    clock = pygame.time.Clock() #builtin
    level = 0 #inital level
    enemy_speed = 1 #define enemyship speed
    player_speed = 5 #define player speed
    lives = 5 #set lives
    main_font = pygame.font.SysFont("comicsansms", 50) #this adds a font to the code lines
    lose_font = pygame.font.SysFont("comicsansms", 50) #same but to the you lose line
    enemies = [] # enemy ship list
    wave_length = 5 # the amount of enemy each level

#this code is applying the for loop an list and randomly generating space ship and with given speed
    for i in range(wave_length):
        enemy = EnemyShip(
            random.randrange(50, WIDTH - 100), # x axis location
            random.randrange(-1500, -100), # y axis location
            random.choice(["orange", "blue", "red"]), # direct asks the dictionry for space ship
            speed=enemy_speed
        )
        enemies.append(enemy)
# creates a asteroid list and generates asteroid by apllying for loop to that list
    asteroids = []
    for i in range(wave_length):
        asteroid = Asteroid(
            random.randrange(50, WIDTH - 100),random.randrange(-1500, -100),
            speed=enemy_speed
        )
        asteroids.append(asteroid)

    player = Player(300, 650) #player spaceship size
    bullet_speed = 4 #speed of the bullet user shoots
    lose = False
    lose_count = 0 #inital value

    def redraw_window():
        WIN.blit(background, (0, 0)) #setting background image
        lives_label = main_font.render(f"Lives: {lives}", 1, (255, 0, 255)) #adding live label to game
        level_label = main_font.render(f"Level: {level}", 1, (255, 0, 255)) #adding level label to the game
        WIN.blit(lives_label, (10, 10)) #wetting position in mid
        WIN.blit(level_label, (WIDTH - level_label.get_width() - 10, 10))

#for loop applied to display enemy for enemies list
        for enemy in enemies:
            enemy.display(WIN)


#for loop applied to display asteroid from asteroids list
        for asteroid in asteroids:
            asteroid.display(WIN)

        player.display(WIN)

# if we run out of lives it will show a you lost line written
        if lose:
            lost = lose_font.render("YOU LOST", 1, (255, 0, 0))
            WIN.blit(lost, (WIDTH/2 - lost.get_width()/2, 350))

        pygame.display.update() #updates the display

#applying while loop in main function
    while run:
        clock.tick(FPS)
        redraw_window()

#breaks the game if player runs out of health or lives
        if lives <= 0 or player.health <= 0:
            lose = True
            lose_count += 1

#waits for 3 seconds afer breaking the game
        if lose:
            if lose_count > FPS * 3:
                break
            else:
                continue

#this code is adding levels to the game when we finish one level the next will become a bit harder by extending the wavelength
        if len(enemies) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                enemy = EnemyShip(
                    random.randrange(50, WIDTH - 100),
                    random.randrange(-1500, -100),
                    random.choice(["orange", "blue", "red"]),
                    speed=enemy_speed
                )
                enemies.append(enemy)

#this is the same function just for asteroids
        if len(asteroids) == 0:
            level += 1
            wave_length += 5
            for i in range(wave_length):
                asteroid = Asteroid(random.randrange(50, WIDTH - 100),random.randrange(-1500, -100))
                asteroids.append(asteroid)

#this code quits game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

# this function adds keys to functions for game running
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player.x - player_speed > 0:
            player.x -= player_speed
        if keys[pygame.K_RIGHT] and player.x + player.get_width() < WIDTH:
            player.x += player_speed
        if keys[pygame.K_UP] and player.y - player_speed > 0:
            player.y -= player_speed
        if keys[pygame.K_DOWN] and player.y + player.get_height() < HEIGHT:
            player.y += player_speed
        if keys[pygame.K_SPACE]:
            player.shoot()

#functions make the anemy and enemy bullet move
        for enemy in enemies:
            enemy.move()
            enemy.move_bullets(bullet_speed, player)

            if random.randrange(0, 3*60) == 1:
                enemy.shoot()

            if collide(enemy, player): #reduced player health if it collide with enemy ship
                player.health -= 10
                enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
#applying same loop for enemy
        for asteroid in asteroids:
            asteroid.move()

            if collide(asteroid, player): #reduces player health after collision
                player.health -= 10
                asteroids.remove(asteroid)

            elif asteroid.y + asteroid.get_height() > HEIGHT:
                lives -= 1
                asteroids.remove(asteroid)

        player.move_bullets(-bullet_speed, enemies) #this code will remove enemies ship if they collide with player bullet and this is polymorphism
        player.move_bullets(-bullet_speed, asteroids)

    pygame.quit()

main()
