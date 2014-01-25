import pygame
from control import LEFT, RIGHT, UP, DOWN, JUMP, SWITCH
from const import *
from gameobjects import Level, Camera, RelRect
from time import sleep

class Scene(object):
    """Abstract base class."""

    def __init__(self):
        # the next property is accessed every iteration of the main
        # loop, to get the scene.  When we want to change to a new
        # scene, we simply set self.next = LevelCompleteScene() (for
        # example).  This should be done in the update() method below.
        self.next = self

    def process_input(self, events, pressed, dt):
        pass

    def update(self, dt):
        pass

    def render(self, screen):
        pass

# mapping of playscene name to background
# NB: this is not used at the moment
SCENE_BG = {'1' : 'artwork/7.png',
            '2' : 'artwork/7.png',
            '3' : 'artwork/7.png',
            '4' : 'artwork/7.png',
            '5' : 'artwork/7.png',
            '6' : 'artwork/7.png'}
SCENE_NAMES = {'1': 'nowhere to go',
               '2': 'jump',
               '3': 'be careful please'
               }

class DeadScene(Scene):
    # time to spend in this scene
    _STIME = 2.0

    def __init__(self, pscene, game):
        self.next = self

        self.game = game
        self.pscene = pscene

        # store time elapsed in this scene
        self.telapsed = 0.0

    def update(self, dt):
        self.telapsed += dt

        if self.telapsed > self._STIME:
            # go back to start of level
            self.next = PlayScene(self.pscene.level.name, self.game)

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
        self.bg = pygame.image.load(SCENE_BG[name])
        self.bg_rect = self.bg.get_rect()

        # get level data for this scene
        self.level = Level(name)

        self.player = self.level.player
        lsize = self.level.get_size()
        print "level size:", lsize
        self.camera = Camera(self.player.rect, lsize[0], lsize[1])

        # my name is the name displayed at the top of the screen
        self.myname = name + ':' + SCENE_NAMES[name]
        self.namefont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 20)
        self.nametxt = self.namefont.render(self.myname, True, 
                                            WHITE)

    def process_input(self, events, pressed, dt):
        # move the player 
        self.player.process_input(events, pressed, dt)

        for ev in events:
            if (ev.action == SWITCH and ev.down):
                self.level.switch()

    def update(self, dt):

        self.player.update()
        
        if self.player.isdead:
            self.next = DeadScene(self, self.game)

        if self.player.collidedoor:
            # level names are '1', '2', '3'

            self.player.complete_image = self.player.image
            self.next = LevelCompleteScene(self, self.game)

        # move camera
        self.camera.update()

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
        screen.blit(self.player.image, RelRect(self.player, self.camera))

        # name of the level
        screen.blit(self.nametxt, (400, 50))

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

    def process_input(self, events, pressed, dt):
        if pressed[JUMP]:
            # sleep so we don't begin first level with a jump
            sleep(0.5)
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
