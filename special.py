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

# text, appearance time (in secs), disappearance time (in secs)
DISCUSSIONS = {'1': [(["Hi Kid!"], 1.5, 2.5),
                     (["Things aren't quite as simple",
                       "as they seem to be around here"], 3.5, 5),
                     (["But don't worry"], 6, 9),
                     (["I'll help you out"], 7.5, 9),
                     (["Use the left and right arrow",
                        "keys to run around"], 12, 15),
                     (["Or your Gamepad"], 15, 18),
                     (["If it works!"], 16.5, 18),
                     (["You need to get to",
                       "the portal, kid"], 21, 24),
                     (["That's the glowing",
                       "orange fireball"],
                      25, 26),
                     (["You'll need to use a technique",
                       "I call 'switching'"],
                      28, 31),
                     (["Press the 'X' key",
                       "on your keyboard",
                       "(or your gamepad)"], 34, 37),
                     (["Watch out for spikes",
                       "though kid"], 40, 42),
                     (["This is a video game",
                       "after all"], 43, 46)
                     
]}

class Level1Tutorial(Scene):
    def __init__(self, level):
        self.level = level
        self.jukebox = self.level.game.jukebox
        self.txtfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 22)

        # List of discussions active at the present time
        self.active_disc = []

        # stored time passed
        self.tpassed = 0.0

        self.discussions = DISCUSSIONS.get(self.level.name, [])
        # last discussion deleted (finished)
        self.deleted = None

    def get_text(self):
        tlines = []
        for d in self.active_disc:
            for line in d[0]:
                tlines.append(line)
        return tlines

    def update(self, dt):
        self.tpassed += dt
        
        # get rid of any old text (a bit inefficient, like a lot of
        # the code in this game! - sorry)
        new_discussions = []
        for d in self.discussions:
            if self.tpassed < d[2]:
                new_discussions.append(d)
            else:
                self.deleted = d
        self.discussions = new_discussions

        cur_disc = []
        for  d in self.discussions:
            if self.tpassed > d[1]:
                cur_disc.append(d)
        
        print cur_disc
        # have the active discussions changed ?
        if cur_disc != self.active_disc:
            self.active_disc = cur_disc
            if cur_disc:
                self.jukebox.play_sfx('talk')

    def render(self, screen):
        for (i, tline) in enumerate(self.get_text()):
            txt = self.txtfont.render(tline, True, WHITE)
            screen.blit(txt, (TEXT_POS[0], TEXT_POS[1] + 30*i))
    
# dictionary of special stuff, with level names as keys
_SPECIAL = {'1' : [Level1Tutorial]}
