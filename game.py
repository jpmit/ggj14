"""Example of main loop and using Scenes to manage the game flow."""

import pygame
import sys
from control import get_events, ALL_ACTIONS
from scene import PlayScene, TitleScene
from const import *

class JukeBox(object):
    def __init__(self):
        try:
            pygame.mixer.init()
        except: 
            self.soundon = False
        else:
            self.soundon = True

        if not self.soundon:
            # better, might be to make JukeBox into a dummy object
            # somehow (?)
            return
        
        # mapping of file names to sound effects
        self.sfx = {'newgame' : pygame.mixer.Sound('sounds/start.ogg'),
                    'dead' : pygame.mixer.Sound('sounds/atari.ogg'),
                    'complete' : pygame.mixer.Sound('sounds/beam2.ogg'),
                    'jump': pygame.mixer.Sound('sounds/jump_07.ogg'),
                    'switch': pygame.mixer.Sound('sounds/click.ogg'),
                    'talk' : pygame.mixer.Sound('sounds/turret2.ogg')
        }

        self.music = {'menu' : 'sounds/menu.ogg',
                      'game' : 'sounds/videogame7.ogg'}
        self.playing = None
    
    def play_music(self, name):
        if self.soundon:
            pygame.mixer.music.load(self.music[name])
            # -1 means repeat
            pygame.mixer.music.play(-1)
            self.playing = name

    def play_music_if(self, name):
        """Play music if not already playing."""

        if self.soundon:
            if self.playing != name:
                self.play_music(name)
    
    def play_sfx(self, name):
        if self.soundon:
            self.sfx[name].play()

class Game(object):
    def __init__(self):
        """Setup pygame, display, etc."""
        
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        
        # setup joystick (slightly hacky here)
        pygame.joystick.init()
        
        # there should only be one joystick plugged in, but let's
        # initialize all joysticks plugged in here.
        joysticks = [pygame.joystick.Joystick(x) 
                     for x in range(pygame.joystick.get_count())]

        for j in joysticks:
            j.init()

        # background image
        self.bg = pygame.image.load('artwork/background.png')

        # jukebox will store sfx and music
        self.jukebox = JukeBox()

    def mainloop(self):
        
        # first scene of the game
#        ascene = TitleScene(self)
        ascene = PlayScene('1', self)

        # initialize clock
        dt = self.clock.tick(FPS) / 1000.0

        # store 'pressed actions' to complement events
        pressed = {}
        for action in ALL_ACTIONS:
            pressed[action] = False

        while ascene != None:
            
            # get the events we are interested in as well as the
            # currently pressed keys, and whether we want to quit.
            events, pressed, quitevent = get_events(pressed)

            # scene specific updating based on events.
            ascene.process_input(events, pressed, dt)

            # update not based on events.
            ascene.update(dt)

            # draw to the screen.
            ascene.render(self.screen)

            # possible change to new scene.
            ascene = ascene.next

            # draw to the screen!
            pygame.display.flip()

            # delay for correct time here.
            dt = self.clock.tick(FPS) / 1000.0

            if quitevent:
                ascene = None
                pygame.quit()

if __name__ == "__main__":
    gm = Game()
    gm.mainloop()
