#Import modules/libraries.
import pyxel
from collections import namedtuple
from random import randint

#Named tuple for convenience.
Point = namedtuple("Point", ["x", "y"])

#Constants
COL_BACKGROUND = 0
COL_DEATH_SCREEN = 10
COL_SPACESHIP = 7
COL_LASER =  8
COL_ENEMY_LASER = 11
COL_SCORE = 11

TEXT_DEATH = ["GAME OVER", "(Q)UIT", "(R)ESTART"]
COL_TEXT_DEATH = 0
HEIGHT_DEATH = 5

WIDTH = 120
HEIGHT = 120

HEIGHT_SCORE = FONT_HEIGHT = pyxel.constants.FONT_HEIGHT

START = Point((WIDTH/2) - 2, HEIGHT - 11)

class Space:

    #Initialization.
    def __init__(self):
        pyxel.init(WIDTH, HEIGHT, caption = "SpaceShooter!", fps = 60)
        self.assets = pyxel.load("assets.pyxel")
        self.reset()
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.location = START
        pyxel.play(ch = 0, snd = 2, loop = True)
        pyxel.play(ch = 1, snd = 3, loop = True)
        self.user_bullet_location = []
        self.bullet_key = 0
        self.enemy_bullet_location = []
        self.death = False
        self.score = 0
        self.enemy_locations = []
        for i in range(0, 5):
            self.generate_enemy()

    def generate_enemy(self):
        valid = False
        while not valid:
            x = randint(0, WIDTH - 8)
            y = randint(HEIGHT_SCORE + 1, HEIGHT - 21)
            new = Point(x, y)
            valid = True
            for j in self.enemy_locations:
                if (x >= j.x and x <= j.x + 5) or (y >= j.y and y <= j.y + 5) or (x <= j.x and x >= j.x - 5) or (y <= j.y and y >= j.y - 5):
                    valid = False
            if valid:
                self.enemy_locations.append(new)

    #Update Logic.
    def update(self):
        if not self.death:
            self.update_location()
            self.update_user_bullet_location()
            self.add_enemy_bullet_location()
            self.update_enemy_bullet_location()
            self.check_death_user()
            self.check_death_enemy()

        if pyxel.btn(pyxel.KEY_Q):
            pyxel.quit()
        elif pyxel.btnp(pyxel.KEY_R):
            self.reset()

    def update_location(self):
        if pyxel.btn(pyxel.KEY_RIGHT) and not pyxel.btn(pyxel.KEY_LEFT):
            if self.location.x < WIDTH - 11:
                old = self.location
                new = Point(old.x + 1, old.y)
                self.location = new
        elif pyxel.btn(pyxel.KEY_LEFT) and not pyxel.btn(pyxel.KEY_RIGHT):
            if self.location.x > 0:
                old = self.location
                new = Point(old.x - 1, old.y)
                self.location = new
        elif pyxel.btn(pyxel.KEY_SPACE):
            self.shoot()

    def shoot(self):
        new = Point(self.location.x + 5, self.location.y)
        self.user_bullet_location.append(new)

    def update_user_bullet_location(self):
        for index, location in enumerate(self.user_bullet_location):
            new = Point(location.x, location.y - 1)
            self.user_bullet_location[index] = new
        for i in self.user_bullet_location:
            if i.y < HEIGHT_SCORE:
                self.user_bullet_location.remove(i)

    def add_enemy_bullet_location(self):
        if self.bullet_key == 0:
            for i in self.enemy_locations:
                self.enemy_bullet_location.append(Point(i.x + 4, i.y + 11))
            self.bullet_key += 1
        elif self.bullet_key == 100:
            self.bullet_key = 0
        else:
            self.bullet_key += 1

    def update_enemy_bullet_location(self):
        for index, location in enumerate(self.enemy_bullet_location):
            new = Point(location.x, location.y + 1)
            self.enemy_bullet_location[index] = new
        for i in self.enemy_bullet_location:
            if i.y > HEIGHT:
                self.enemy_bullet_location.remove(i)

    def check_death_enemy(self):
        for i in self.user_bullet_location:
            for j in self.enemy_locations:
                if (i.x >= j.x and i.x <= j.x + 9) and (i.y >= j.y and i.y <= j.y + 11):
                    self.enemy_locations.remove(j)
                    pyxel.play(ch = 3, snd = 1)
                    self.score += 1
                    self.generate_enemy()

    def check_death_user(self):
        for i in self.enemy_bullet_location:
            if (i.x >= self.location.x and i.x <= self.location.x + 9) and (i.y >= self.location.y and i.y <= self.location.y + 11):
                pyxel.play(ch = 3, snd = 0)
                pyxel.stop(0)
                pyxel.stop(1)
                self.death = True
    #Draw Logic.
    def draw(self):
        if not self.death:
            pyxel.cls(COL_BACKGROUND)
            self.draw_spacship()
            self.draw_user_bullet()
            self.draw_enemy_bullet()
            self.draw_enemy()
            self.draw_score()
        else:
            self.draw_death()

    def draw_spacship(self):
        pyxel.blt(x = self.location.x, y = self.location.y, img = 0, u = 0, v = 0, w = 11, h = 11, colkey = 0)

    def draw_enemy(self):
        for i in self.enemy_locations:
            pyxel.blt(x = i.x, y = i.y, img = 1, u = 0, v = 0, w = 9, h = 11, colkey = 0)

    def draw_user_bullet(self):
        for i in self.user_bullet_location:
            pyxel.pix(i.x, i.y, COL_LASER)

    def draw_enemy_bullet(self):
        for i in self.enemy_bullet_location:
            pyxel.pix(i.x, i.y, COL_ENEMY_LASER)

    def draw_score(self):
        score = "{:04}".format(self.score)
        pyxel.rect(0, 0, WIDTH, HEIGHT_SCORE, COL_BACKGROUND)
        pyxel.text(1, 1, score, COL_SCORE)

    def draw_death(self):
        pyxel.cls(COL_DEATH_SCREEN)
        display_text = TEXT_DEATH[:]
        display_text.insert(1, "{:04}".format(self.score))
        for i, text in enumerate(display_text):
            y_offset = (FONT_HEIGHT + 2) * (i + 5)
            text_x = self.center_text(text, WIDTH)
            pyxel.text(text_x, HEIGHT_DEATH + y_offset, text, COL_TEXT_DEATH)

    @staticmethod
    def center_text(text, page_width, char_width=pyxel.constants.FONT_WIDTH):
        text_width = len(text) * char_width
        return (page_width - text_width) // 2

#Call Application
Space()
