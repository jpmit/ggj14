import pygame
from const import *
from basescene import Scene

def get_special_stuff(level, game):
    """Return list of special stuff for the level with this name.  Special
stuff should be derived from scene.
    """
    
    if not TUTORIAL_ON:
        return []

    # empty list is default
    specobjs = _SPECIAL.get(level.name, [])

    return [s(level, game) for s in specobjs]

# text, appearance time (in secs), disappearance time (in secs)
DISCUSSIONS = {'1': [(["Hi Kid!"], 3.5, 4.5),
                     (["Things aren't quite as simple",
                       "as they seem to be around here"], 5.5, 7.5),
                     (["But don't worry"], 8, 11.5),
                     (["I'll help you out"], 9.5, 11.5),
                     (["Use the left and right arrow",
                        "keys to run around"], 14, 17),
                     (["Or your Gamepad"], 17, 20),
                     (["If it works!"], 18.5, 20),
                     (["You need to get to",
                       "the portal, kid"], 23, 26),
                     (["That's the glowing",
                       "orange fireball"],
                      27, 28.5),
                     (["You'll need to use a technique",
                       "I call 'switching'"],
                      30, 33),
                     (["Press the 'X' key",
                       "on your keyboard",
                       "(or your gamepad)"], 36, 39),
                     (["Watch out for spikes",
                       "though kid"], 42, 44),
                     (["This is a video game",
                       "after all"], 45, 47)
                    ],
               '2': [(["Did I mention you can jump?"], 1, 3),
                     (["Press SPACEBAR to jump",
                        "(or your gamepad)"], 6, 8),
                     (["Just don't jump",
                        "off the screen"], 10, 12),
                     ],
               '3': [(["There could be something",
                       "interesting here"], 1, 3),
                     (["Try shifting while",
                        "in a hollow box"], 6, 12),
                     (["Try shifting while",
                        "in a hollow box"], 20, 25),
                     (["Try shifting while",
                        "in a hollow box"], 60, 80)],
               '4': [(["It's going to get harder",
                       "from here kid"], 1, 3),
                     (["They tell me there are",
                      "12 levels in total"], 5, 7),
                     (["But then"], 8, 11.5),
                     (["Who am I to know?"], 10, 11.5)]
}

class LevelTutorial(Scene):
    def __init__(self, level, game):
        self.level = level
        self.game = game
        self.jukebox = self.level.game.jukebox
        self.txtfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 22)

        # List of discussions active at the present time
        self.active_disc = []

        # stored time passed
        self.tpassed = 0.0

        self.discussions = DISCUSSIONS.get(self.level.name, [])

        # remove any discussions (dialogs) that have been seen in the
        # game already for this level
        if self.discussions:
            self.discussions = [list(s) for s in self.discussions]
            ndel = self.game.del_dialogs[level.name]
            # subtract the end time of the last seen dialog from all
            # of the dialogs.
            if ndel > 0:
                etime = self.discussions[ndel - 1][2]
                for d in self.discussions:
                    d[1] -= etime
                    d[2] -= etime

                # we only want the dialogs that haven't yet been deleted.
                self.discussions = self.discussions[ndel:]
        print self.discussions

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
        deleted = 0
        for d in self.discussions:
            if self.tpassed < d[2]:
                new_discussions.append(d)
            else:
                deleted += 1

        # we store the number of deleted discussions in the game, so
        # that we can resume at the right place when/if the player
        # character dies on the level.
        if deleted:
            self.game.increment_deleted_dialogs(self.level.name, 
                                                deleted)


        self.discussions = new_discussions

        cur_disc = []
        for  d in self.discussions:
            if self.tpassed > d[1]:
                cur_disc.append(d)
        
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
_SPECIAL = {'1' : [LevelTutorial],
            '2' : [LevelTutorial],
            '3': [LevelTutorial],
            '4': [LevelTutorial]
}
