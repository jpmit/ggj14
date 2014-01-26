import pygame
from basescene import Scene
from control import LEFT, RIGHT, UP, DOWN, JUMP, SWITCH, ALL_ACTIONS
from const import *
from gameobjects import Level, Camera, RelRect, Player
from time import sleep
import special # includes tutorial stuff
import random
import copy
from level import LEVEL_NAMES

class GameCompleteScene(Scene):
    _STIME = 8.5
    def __init__(self, game):
        self.next = self

        self.game = game
        # play completion scene music
#        self.game.jukebox.play_music_if('gamecomplete')        
        
#        pass
        self.font = pygame.font.Font('fonts/ShareTechMono-Regular.ttf', 100)
        self.sfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf', 30)
        self.comptxt = self.font.render("Game Complete", True,
                                          WHITE)
        self.wstxt = self.sfont.render("good job, thanks for playing!", True,
                                      WHITE)

        self.player = Player(None, 30, 400)

        self.telapsed = 0.0

        # stop main music and play victory sound effect
        self.game.jukebox.stop_music()
        self.game.jukebox.play_sfx('victory')

    def render(self, screen):
        screen.blit(self.game.bg, (0, 0))
        screen.blit(self.comptxt, (180, 40))
        screen.blit(self.wstxt, (180, 180))
        screen.blit(self.player.image, self.player.rect)

    def process_input(self, events, pressed, dt):
        # hacky (sorry) assume the player aint pressing any keys (he
        # can move the player if he is!)
        pressed = {}
        for action in ALL_ACTIONS:
            pressed[action] = False
        pressed[RIGHT] = True
        self.player.contact = True
        self.player.process_input(None, pressed, dt)
        self.player.rect.x += dt*240

    def update(self, dt):
        self.telapsed += dt
        if self.telapsed > self._STIME:
            self.next = TitleScene(self.game)

class DeadScene(Scene):
    # time to spend in this scene
    _STIME = 2.0

    def __init__(self, pscene, game):
        self.next = self

        self.game = game
        self.pscene = pscene

        self.player = self.pscene.player

        # store time elapsed in this scene
        self.telapsed = 0.0

        # set player image to none, so scene won't draw it
        self.player.image = None

        # initial rendering position
        self.initrect = RelRect(self.player, 
                                self.pscene.camera)
        if self.player.direction == 'right':
            self.pimage = self.pscene.player.images['idle_right']
        else:
            self.pimage = self.pscene.player.images['idle_left']

        self.pimages = []
        self.vels = []
        self.xoffset = []
        self.yoffset = []
        self.rects = []

        # one rect per pixel:
        # NB: this loop could be perilously slow (sorry!)
        img_size = 2
        for x in range(32/img_size):
            for y in range(58/img_size):
                image = pygame.Surface((img_size, img_size),
                                       pygame.SRCALPHA).convert_alpha()
                image.blit(self.pimage, (0, 0), (x, y, img_size, img_size))
                self.pimages.append(image)
                self.vels.append((random.random() - 0.5, random.random() - 0.5))
                self.xoffset.append(x * img_size)
                self.yoffset.append(y * img_size)
                rec = copy.deepcopy(self.initrect)
                rec.centerx += x*img_size
                rec.centery += y*img_size
                self.rects.append(rec)

    def update(self, dt):
        self.telapsed += dt

        if self.telapsed > self._STIME:
            # go back to start of level
            self.next = PlayScene(self.pscene.level.name, self.game)

    def render(self, screen):
        self.pscene.render(screen)

        # render all of the exploding player images
        for pimage, vel, rec in zip(self.pimages, self.vels, self.rects):
            # this should really be in update function
            #brec = self.initrect
            rec.centerx += self.telapsed*100*vel[0]
            rec.centery += self.telapsed*100*vel[1]
            screen.blit(pimage, rec)#self.initrect)

class LevelCompleteScene(Scene):
    # time to spend in this scene
    _STIME = 2.0

    # controls speed of rotation
    _ROT_DEG = 1800.0

    def __init__(self, pscene, game):
        self.pscene = pscene
        self.game = game
        self.next = self
        
        # next pscene name
        self.nname = str(int(self.pscene.name) + 1)
        
        # store time elapsed in this scene
        self.telapsed = 0.0

    def update(self, dt):
        self.telapsed += dt

        # rotate the player
        self.pscene.player.rotate(dt*self._ROT_DEG*self.telapsed)

        if self.telapsed > self._STIME:
            if int(self.nname) > self.game.nlevels:
                self.next = GameCompleteScene(self.game)
            else:
                self.next = PlayScene(self.nname, self.game)

    def render(self, screen):
        # this will ensure the rotating player is rendered
        self.pscene.render(screen)

class PlayScene(Scene):
    def __init__(self, name, game):
        self.next = self
        
        # this is the name of the level, which is '1', '2', etc.
        self.name = name
        
        self.game = game
        # get background info for this scene (not currently used)

        # get level data for this scene
        self.level = Level(name, self.game)

        self.player = self.level.player
        self.lsize = self.level.get_size()

#        print "level size:", lsize
        self.camera = Camera(self.player.rect, self.lsize[0], self.lsize[1])

        # my name is the name displayed at the top of the screen
        self.myname = name + ':' + LEVEL_NAMES[name]
        self.namefont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 20)
        self.nametxt = self.namefont.render(self.myname, True, 
                                            WHITE)
        
        # play music if not already going
        self.game.jukebox.play_music_if('game')

        # get special stuff, e.g. tutorial (this should be a list, and
        # empty if there is no special stuff).
        self.special_stuff = special.get_special_stuff(self)

    def process_input(self, events, pressed, dt):
        # move the player 
        self.player.process_input(events, pressed, dt)

        for ev in events:
            if (ev.action == SWITCH and ev.down):
                self.game.jukebox.play_sfx('switch')
                self.level.switch()

        # process special stuff (e.g. tutorial)
        for spec in self.special_stuff:
            spec.process_input(events, pressed, dt)

    def update(self, dt):

        self.player.update()
        
        # check for player going off the level
        ybot = self.player.rect.y + self.player.rect.h
        xleft = self.player.rect.x
        if ((xleft < 0) or (xleft > self.lsize[0]) 
            or (ybot < 0) or (ybot > self.lsize[1])):
            self.player.isdead = True
        
        if self.player.isdead:
            self.game.jukebox.play_sfx('dead')
            self.next = DeadScene(self, self.game)

        if self.player.collidedoor:
            self.player.complete_image = self.player.image
            self.game.jukebox.play_sfx('complete')
            self.next = LevelCompleteScene(self, self.game)

        # move camera
        self.camera.update()

        # process special stuff (e.g. tutorial)
        for spec in self.special_stuff:
            spec.update(dt)

    def render(self, screen):

        # background is white at the moment
        screen.blit(self.game.bg, (0, 0))
#        screen.fill(BLACK)
        
        # sprites in the foreground (current level)
        for s in self.level.current_sprites:
            if s.rect.colliderect(self.camera.rect):
                screen.blit(s.image, RelRect(s, self.camera))

        # sprites in the background (other level)
        for s in self.level.other_sprites:
            if s.rect.colliderect(self.camera.rect):
                screen.blit(s.image_other, RelRect(s, self.camera))

        # permanent sprites (e.g. spikes, doors)
        for s in self.level.permanent_sprites:
            if s.rect.colliderect(self.camera.rect):
                screen.blit(s.image, RelRect(s, self.camera))

        # player
        if self.player.image:
            screen.blit(self.player.image, RelRect(self.player, self.camera))

        # name of the level
        screen.blit(self.nametxt, NAME_POS)

        # render special stuff (e.g. tutorial)
        for spec in self.special_stuff:
            spec.render(screen)

class TitleScene(Scene):
    _FLASH_TIME = 0.7
    def __init__(self, game):
        self.next = self

        # reference to game is used for global assets/game state
        self.game = game

        # really want to use a .ttf file here, not default font
        self.lfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 100)
        self.mfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 30)
        self.sfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 20)
        self.titletxt = self.lfont.render("Two Levels", True,
                                          WHITE)
        self.desctxt = self.sfont.render("Things aren't always as they seem", True,
                                         WHITE)

        self.txt = self.mfont.render("Press Space to start!",
                                      True, WHITE)

        self.dt = 0
        self.blinkon = True

        # play menu scene music
        self.game.jukebox.play_music_if('menu')        

    def process_input(self, events, pressed, dt):
        if pressed[JUMP]:
            # sleep so we don't begin first level with a jump
            self.game.jukebox.play_sfx('newgame')
            sleep(2)
            self.next = PlayScene('1', self.game)
        pass

    def update(self, dt):
        self.dt += dt
        if self.dt > self._FLASH_TIME:
            self.blinkon = not self.blinkon
            self.dt = 0

    def render(self, screen):
        screen.blit(self.game.bg, (0, 0))
#        screen.fill(WHITE)
        screen.blit(self.titletxt, (210, 100))
        screen.blit(self.desctxt, (270, 230))

        if self.blinkon:
            screen.blit(self.txt, (310, 400))
