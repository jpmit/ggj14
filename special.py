import pygame
from const import *
from basescene import Scene

def get_special_stuff(level):
    """Return list of special stuff for the level with this name.  Special
stuff should be derived from scene.
    """
    
    # empty list is default
    specobjs = _SPECIAL.get(level.name, [])

    return [s(level) for s in specobjs]

class Level1Tutorial(Scene):
    def __init__(self, level):
        self.level = level
        self.jukebox = self.level.game.jukebox
        self.txtfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 20)        

        # initial text
        self.currenttext = None

        # stored time passed
        self.tpassed = 0.0

    def set_text(self, text):
        if self.currenttext is None:
            self.jukebox.play_sfx('talk')
        self.currenttext = self.txtfont.render(text, True, WHITE)

    def no_text(self):
        self.currenttext = None

    def update(self, dt):

        self.tpassed += dt
        if self.tpassed > 2:
            self.set_text("Hi Kid!")
        elif self.tpassed > 3:
            self.no_text()
        elif self.tpassed > 4:
            self.set_text("Things aren't quite as simple\nas they seem to be around here""")
        elif self.tpassed > 5:
            self.no_text()
#        if self.dt

#        pass

    def render(self, screen):
#        print self.currenttext
        if self.currenttext:
            screen.blit(self.currenttext, (600, 150))
    
# dictionary of special stuff, with level names as keys
_SPECIAL = {'1' : [Level1Tutorial]}
