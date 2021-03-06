import pygame
from const import *
from control import LEFT, RIGHT, UP, DOWN, JUMP

def RelRect(actor, camera):
    return pygame.Rect(actor.rect.x - camera.rect.x, 
                       actor.rect.y - camera.rect.y, 
                       actor.rect.w, actor.rect.h)

class Camera(object):
    """Class for center screen on the player"""

    # we allow the player to move this many pixels either left, right,
    # up or down from center before moving camera.
    _OFFC = 25
    def __init__(self, player, level_width, level_height):
        self.player = player
        self.rect = pygame.Rect(0, 0, WIDTH, HEIGHT)
        self.rect.center = self.player.center
        self.level_rect = pygame.Rect(0, 0, level_width, level_height)

    def update(self):
        pl = self.player
        re = self.rect
        off = self._OFFC
        if pl.centerx > re.centerx + off:
            re.centerx = pl.centerx - off
        if pl.centerx < re.centerx - off:
            re.centerx = pl.centerx + off
        if pl.centery > re.centery + off:
            re.centery = pl.centery - off
        if pl.centery < re.centery - off:
            re.centery = pl.centery + off
    
        # this means we can't go off the edge of the level
        re.clamp_ip(self.level_rect)

class Block(pygame.sprite.Sprite):
    """The square blocks that comprise the level"""
    
    # dictionary mapping symbols to images these are all (except for
    # 'D' and 'Q') placeholders (not used) now, hence using 'pink.png'
    # for all !
    _IMG = {'X' : 'artwork/pink.png', # x block
            'Y' : 'artwork/pink.png', # y block
            'D' : 'artwork/portal2.png', # door (portal to next level)
            'S' : 'artwork/pink.png', # switch button on level x
            'T' : 'artwork/pink.png', # swith button on level y
            'Q':  'artwork/spikes2.png', # spike 
            #NB: Z and U will be over-ridden, this is just a
            #placeholder
            'Z':  'artwork/pink.png',
            'U':  'artwork/pink.png'
           }
    # use rgb colors for the changing blocks
    _COLORS = {'X' : (223, 220, 166),
               'Y' : (47, 46, 25),
               'S' : (0, 0, 255),
               'T' : (255, 0, 0)
               }

    # border width in pixels for 'image other'
    _BWIDTH = 5

    def __init__(self, symbol, x, y):
        # symbol can be either:
        # 'X' - levelX (start level)
        # 'Y' - levelY (switch level)
        # 'D' - door   (to next level)
        # 'S' - switch button on level X (switches from X to Y)
        # 'T' - switch button on level Y (switches from Y to X)
        
        self.x = x
        self.y = y
        self.symbol = symbol
        pygame.sprite.Sprite.__init__(self)
        
        self.image = pygame.image.load(self._IMG[symbol]).convert_alpha()

        # image_other is for when block is in background (this is a placeholder for now.
        self.image_other = pygame.image.load(self._IMG[symbol]).convert_alpha()

        # set the blocks that switch differently for now
        if self.symbol in ["X", "Y", "S", "T"]:
            self.set_images()
#        wsurf = pygame.Surface((40, 40), pygame.SRCALPHA).convert_alpha()
#        wsurf.fill(WHITE)
#        self.image_other = wsurf
#        self.image_other = wsurf
#        self.image_other.blit(wsurf, (5, 5))
#        self.image_other.set_alpha(255)

        self.rect = self.image.get_rect()
        self.rect.topleft = [self.x, self.y]

        # this is all a bit hacky, no?
        if self.symbol == "Q":
            self.isspike = True
        else:
            self.isspike = False

        # collision with door handled differently to other blocks
        if self.symbol == "D":
            self.collidable = False
        else:
            self.collidable = True
    
    def set_images(self):
        """Set self.image and self.image_other"""

        # rgb tuple for this image
        col = self._COLORS[self.symbol]

        # the main image is just a single color
        im_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))        
        im_surface.fill(col)

        self.image = im_surface
        
        # build up the other image (border) from an initial
        # transparent surface
        other_surface = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE), 
                                       pygame.SRCALPHA)
        bw = self._BWIDTH
        hbar = pygame.Surface((BLOCK_SIZE, bw))
        vbar = pygame.Surface((bw, BLOCK_SIZE))
        hbar.fill(col)
        vbar.fill(col)

        other_surface.blit(hbar, (0, 0))
        other_surface.blit(hbar, (0, BLOCK_SIZE - bw))
        other_surface.blit(vbar, (0, 0))
        other_surface.blit(vbar, (BLOCK_SIZE - bw, 0))
        
        self.image_other = other_surface

class Player(pygame.sprite.Sprite):
    """Class for player and collision."""
    
    # number of pixels per second
    _JMP_SPEED = 800
    _FALL_SPEED = 1000
    _WALK_SPEED = 500

    # frame time (in s) for each running frame
    _F_TIME = 0.02

    # in seconds (note this won't give 'pixel perfect' jumping)
    _MAX_JMP_TIME = 0.2

    def __init__(self, level, x, y):
        pygame.sprite.Sprite.__init__(self)

        # reference to current sprites in (level)
        self.level = level
        self.x = x
        self.y = y
        self.contact = False
        self.isjumping = False
        self.isfalling = False
        self.jmppx = 0.0

        # store sprite we are currently standing on top of (if any)
        self.contact_sprite = None

        # colliding with door
        # scaled rect ensures we overlap the door a little bit
        self.collide_door_fn = pygame.sprite.collide_rect_ratio(0.5)
        self.collidedoor = False

        # images - keep it simple for now
        self.images = {'idle_right' : pygame.image.load('actions/idle_right.png').convert_alpha(),
                       'idle_left' : pygame.image.load('actions/idle_left.png').convert_alpha(),
                       'jump_right' : pygame.image.load('actions/jump_right.png').convert_alpha(),
                       'jump_left' : pygame.image.load('actions/jump_left.png').convert_alpha(),
        }
        # running images
        for i in range(8):
            rl = 'run_left{0}'.format(i)
            rr = 'run_right{0}'.format(i)
            self.images[rl] = pygame.image.load('actions/run_left00{0}.png'.format(i)).convert_alpha()
            self.images[rr] = pygame.image.load('actions/run_right00{0}.png'.format(i)).convert_alpha()
        self.frame = 0 # for running frames
        self.dtframe = 0.0

        # start the level facing right               
        self.image = self.images['idle_right']
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]
        self.direction = "right"

        # angle is for level completion
        self.angle = 0

    def rotate(self, angle):
        self.angle += angle

        rescale = 100.0/self.angle**0.8
        # rotate
        self.image = pygame.transform.rotate(self.complete_image, self.angle)
        # resize
        isize = self.image.get_size()
        self.image = pygame.transform.scale(self.image, (int(isize[0]*rescale),
                                                         int(isize[1]*rescale)))
        self.rect = self.image.get_rect(center = self.rect.center)
        #self.angle+=10

    def process_input(self, events, pressed, dt):
        # this routine: 
        # (i) sets, dx and dy, the number of pixels the
        # input suggests we should move in the x and y directions.
        # (ii) ensures that the correct image (self.image) is displayed
        # the actual updating (collision checking etc.) is performed in the 
        # update function.
        self.dx = 0
        self.dy = 0

        if pressed[JUMP]:
            if not self.isjumping and not self.isfalling:
                self.level.game.jukebox.play_sfx('jump')
                self.isjumping = True
                self.dtjump = 0.0

        if self.isjumping:
            self.dtjump += dt
            if self.dtjump > self._MAX_JMP_TIME:
                self.isjumping = False
                self.isfalling = True
            else:
                self.dy = -self._JMP_SPEED*dt
        elif self.isfalling:
            self.dy = self._FALL_SPEED*dt
            
            if self.contact:
                self.isfalling = False

        if not self.contact:
            self.isfalling = True

        if pressed[LEFT]:
            self.direction = "left"
            self.dx = - self._WALK_SPEED*dt
            if self.contact:
                # cycle through proper running frames here
                self.dtframe += dt
                if self.dtframe > self._F_TIME:
                    self.frame += 1
                    self.dttime = 0
                if self.frame == 8: self.frame = 0                
                self.image = self.images['run_left{0}'.format(self.frame)]
            else:
                'jump image'
                self.image = self.images['jump_left']

        # not elif since left and right could be pressed
        # simultaneously.
        if pressed[RIGHT]: 
            self.direction = "right"
            self.dx = self._WALK_SPEED*dt
            if self.contact:
                # cycle through proper running frames here
                self.dtframe += dt
                if self.dtframe > self._F_TIME:
                    self.frame += 1
                    self.dttime = 0
                if self.frame == 8: self.frame = 0                
                self.image = self.images['run_right{0}'.format(self.frame)]
            else:
                self.image = self.images['jump_right']

        if not pressed[RIGHT] and not pressed[LEFT] and self.contact:
            if self.direction == "right":
                self.image = self.images['idle_right']
            else:
                self.image = self.images['idle_left']

    def update(self):
        # move this?
        self.isdead = False

        # move and possibly replace in x direction
        self.rect.right += self.dx
        # collision with both current sprites (the current level) and
        # permanent sprites
        self.collide(self.dx, 0, self.level.current_sprites)
        self.collide(self.dx, 0, self.level.permanent_sprites)
        
        # move and possibly replace in y direction
        self.rect.top += self.dy
        self.contact = False
        self.collide(0, self.dy, self.level.current_sprites)
        self.collide(0, self.dy, self.level.permanent_sprites)

        # if we are in contact in the y direction check if it is a
        # spike, and if so die.
        if self.contact:
#            print self.contact_sprite.symbol
            # spike
            if self.contact_sprite.symbol == 'Q':
                self.isdead = True

        # check for collision with door
        self.collide_door()

    def collide(self, movx, movy, sprites):
        #self.contact = False
        re = self.rect
        for o in sprites:
            # allow some sprites to be 'non-collidable', so the player
            # can go through them.
            if o.collidable:
                if re.colliderect(o):
                    if movx > 0:
                        re.right = o.rect.left
                    if movx < 0:
                        re.left = o.rect.right
                    if movy > 0:
                        re.bottom = o.rect.top
                        self.movy = 0
                        self.contact = True
                        # store the contact sprite
                        self.contact_sprite = o
                    if movy < 0:
                        re.top = o.rect.bottom
                        self.movy = 0

    def collide_door(self):
        """Check for collision with door and set attribute if so."""
        # use ratio so we need to be overlapping a bit
        if self.collide_door_fn(self, self.level.doorsprite):
            self.collidedoor = True

class Level(object):
    """Read map and create level."""
    
    ALL_SYMBOLS = ["X", "Y", "Z", "D", "S", "T", "U", "Q"]

    def __init__(self, name, game):
        
        # name e.g. '1', '2'
        self.name = name

        self.game = game

        self.level1 = []
        
        # x sprites and y sprites
        self.x_sprites = pygame.sprite.Group()
        self.y_sprites = pygame.sprite.Group()

        # permanent sprites for the level
        self.permanent_sprites = pygame.sprite.Group()

        self.current_sprites = self.x_sprites
        self.other_sprites = self.y_sprites
        
        # build level from text file
        dfile = 'level/' + name
        self.create_level(dfile, 0, 0)

    def switch(self):
        if self.current_sprites == self.x_sprites:
            self.current_sprites = self.y_sprites
            self.other_sprites = self.x_sprites
        elif self.current_sprites == self.y_sprites:
            self.current_sprites = self.x_sprites
            self.other_sprites = self.y_sprites

    def create_level(self, name, x, y):
        #for l in self.level:
        #    self.level1.append(l)
        lrows = open(name, "r").readlines()
        self.lines = lrows
        for row in lrows:
            for col in list(row):
                if col in self.ALL_SYMBOLS:
                    block = Block(col, x, y)
                    # level 1 blocks
                    if col in ["X", "S"]:
                        self.x_sprites.add(block)
                    # level 2 blocks
                    elif col in ["Y", "T"]:
                        self.y_sprites.add(block)
                    # these blocks appear in both levels
                    elif col in ["Z", "U"]:
                        # Z is X and Y 
                        if col == "Z":
#                            print "Z block!!"
                            block = Block("X", x, y)
                            self.x_sprites.add(block)
                            block = Block("Y", x, y)
                            self.y_sprites.add(block)
                        elif col == "U":
                            # no "U" blocks for now
                            self.x_sprites.add(Block("S", x, y))
                            self.y_sprites.add(Block("T", x, y))
                           
                    # permanent blocks (present in both levels)
                    elif col in ["D", "Q"]:
                        self.permanent_sprites.add(block)
                        # only one door per level please!
                        if col == "D":
                            self.doorsprite = block

                # P is where the player starts, only one of these on map
                if col == "P":
                    # player gets a reference to the level here
                    self.player = Player(self, x, y)
                # each block has dims BLOCK_SIZE*BLOCK_SIZE (defined
                # in const.py)
                x += BLOCK_SIZE
            y += BLOCK_SIZE
            x = 0
                    
    def get_size(self):
        lines = self.lines
        line = max(lines, key=len)
        self.width = (len(line))*BLOCK_SIZE
        self.height = (len(lines))*BLOCK_SIZE
        return (self.width, self.height)
