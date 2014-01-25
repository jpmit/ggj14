import pygame
from control import LEFT, RIGHT, UP, DOWN, JUMP, SWITCH
from const import *
from gameobjects import Level, Camera, RelRect

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

class DeadScene(Scene):
    # time to spend in this scene
    _STIME = 2.0

    def __init__(self, pscene):
        self.next = self
        self.pscene = pscene

        # store time elapsed in this scene
        self.telapsed = 0.0

    def update(self, dt):
        self.telapsed += dt

        if self.telapsed > self._STIME:
            # go back to start of level
            self.next = PlayScene(self.pscene.level.name)

class LevelCompleteScene(Scene):
    # time to spend in this scene
    _STIME = 2.0

    def __init__(self, pscene):
        self.pscene = pscene
        self.next = self
        
        # next pscene name
        self.nname = str(int(self.pscene.name) + 1)
        
        # store time elapsed in this scene
        self.telapsed = 0.0

    def update(self, dt):
        self.telapsed += dt

        if self.telapsed > self._STIME:
            self.next = PlayScene(self.nname)

class PlayScene(Scene):
    def __init__(self, name):
        self.next = self
        
        # get background info for this scene (not currently used)
        self.bg = pygame.image.load(SCENE_BG[name])
        self.bg_rect = self.bg.get_rect()

        # get level data for this scene
        self.level = Level(name)

        self.player = self.level.player
        lsize = self.level.get_size()
        print "level size:", lsize
        self.camera = Camera(self.player.rect, lsize[0], lsize[1])

    def process_input(self, events, pressed, dt):
        # move the player 
        self.player.process_input(events, pressed, dt)

        for ev in events:
            if (ev.action == SWITCH and ev.down):
                self.level.switch()

    def update(self, dt):

        self.player.update()
        
        if self.player.isdead:
            self.next = DeadScene(self)

        if self.player.collidedoor:
            # level names are '1', '2', '3'
            self.next = LevelCompleteScene(self.level)

        # move camera
        self.camera.update()

    def render(self, screen):

        # background is white at the moment
        screen.fill(BLACK)
        
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

#        print self.level.permanent_sprites, self.level.current_sprites

class TitleScene(Scene):
    def __init__(self):
        self.next = self

        # really want to use a .ttf file here, not default font
        self.font = pygame.font.Font(pygame.font.get_default_font() , 30)
        self.titletxt = self.font.render("Two Worlds", True,
                                         BLACK)
        self.txt = self.font.render("Press Space to start!",
                                    True, BLACK)

    def process_input(self, events, pressed, dt):
        if pressed[JUMP]:
            self.next = PlayScene('1')
        pass

    def render(self, screen):
        screen.fill(WHITE)
        screen.blit(self.titletxt, (100, 100))
        screen.blit(self.txt, (100, 400))
