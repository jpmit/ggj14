"""Example of main loop and using Scenes to manage the game flow."""

import pygame
import sys
from control import get_events, ALL_ACTIONS
from scene import PlayScene, TitleScene
from const import *

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
        print joysticks
        for j in joysticks:
            j.init()

    def mainloop(self):
        
        # first scene of the game
#        ascene = TitleScene()
        ascene = PlayScene('1')

        # initialize clock
        dt = self.clock.tick(FPS)

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
