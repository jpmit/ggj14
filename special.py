import pygame
from const import *
from basescene import Scene

def get_special_stuff(level, game):
    """Return list of special stuff for the level with this name.  Special
stuff should be derived from scene.
    """
    
    if not TUTORIAL_ON:
        return []

    slist = []
    if level.name in DISCUSSIONS:
        return [LevelTutorial(level, game)]
    else:
        # no special stuff
        return []

# text, appearance time (in secs), disappearance time (in secs)
DISCUSSIONS = {'1': [(["Hi Kid!"], 3.5, 5.5),
                     (["Things aren't quite as simple",
                       "as they seem around here"], 7.5, 10.5),
                     (["But don't worry"], 12, 15.5),
                     (["I'll help you out"], 13.5, 15.5),
                     (["Use the left and right arrow",
                        "keys to run around"], 18, 20),
                     (["Or your Gamepad"], 22, 25.5),
                     (["If it works!"], 23.5, 25.5),
                     (["You need to get to",
                       "the portal, kid"], 28, 31),
                     (["That's the glowing",
                       "orange fireball"],
                      34, 36.5),
                     (["You'll need to use a technique",
                       "I call 'switching'"],
                      39, 42),
                     (["Press the 'X' key",
                       "on your keyboard",
                       "(or either shoulder button",
                       "on your gamepad)"], 44, 47),
                     (["Watch out for spikes",
                       "though kid"], 48, 50),
                     (["This is a video game",
                       "after all"], 52, 54.5)
                    ],
               '2': [(["Did I mention you can jump?"], 1, 3),
                     (["Press SPACEBAR to jump",
                        "(or the 'A' button",
                       " on your gamepad)"], 6, 8),
                     (["Just don't jump",
                        "off the screen"], 10, 12),
                     ],
               '3': [(["There could be something",
                       "interesting here"], 1, 3),
                     (["Try shifting while",
                        "in a hollow box"], 10, 14),
                     (["Two shifts",
                        "in close succession..."], 20, 28),
                     (["You can do it kid"], 50, 55),
                     (["Jump towards the", "top of the tower"],
                      57, 67),
                     (["And rapidly switch twice"], 62, 67)],
               '5': [(["It's going to get harder",
                       "from here kid"], 1, 3),
                     (["They tell me there are",
                      "12 levels in total"], 5, 7),
                     (["But then"], 8, 11.5),
                     (["Who am I to know?"], 10, 11.5),
                     (["Quite Frankly, it's the",
                       "Global Gam Jam at the moment"], 13, 15),
                     (["And I'm at least half asleep"],
                       16, 20),
                     (["Probably more like 90% actually"], 
                       18, 20)],
               '6': [(["Good luck kid"], 1, 3.5),
                     (["You're on your own now"], 1.5, 3.5),
                     (["I'm off to sleep"], 5, 6.5),
                     (["I never did figure out"], 8, 11),
                     (["Why I called you kid"], 9.5, 11)]
}

class LevelTutorial(Scene):
    def __init__(self, level, game):
        self.level = level
        self.game = game
        self.jukebox = self.level.game.jukebox
        self.txtfont = pygame.font.Font('fonts/ShareTechMono-Regular.ttf' , 22)


        self.discussions = DISCUSSIONS.get(self.level.name, [])

        # get time passed in dialog
        self.tpassed = self.game.dialog_dts[level.name]

        # List of discussions active at the present time
        self.active_disc = self.get_current_discussions()

    def get_text(self):
        tlines = []
        for d in self.active_disc:
            for line in d[0]:
                tlines.append(line)
        return tlines

    def get_current_discussions(self):
        cur_disc = []
        for d in self.discussions:
            if self.tpassed > d[1] and self.tpassed < d[2]:
                cur_disc.append(d)

        return cur_disc

    def update(self, dt):

        self.tpassed += dt

        # increment global time spent in dialog
        self.game.dialog_dts[self.level.name] += dt

        cur_disc = self.get_current_discussions()
        
        # have the active discussions changed ?
        if cur_disc != self.active_disc:
            self.active_disc = cur_disc
            if cur_disc:
                self.jukebox.play_sfx('talk')

    def render(self, screen):
        for (i, tline) in enumerate(self.get_text()):
            txt = self.txtfont.render(tline, True, WHITE)
            screen.blit(txt, (TEXT_POS[0], TEXT_POS[1] + 30*i))
