import pygame

# named constants
LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'
JUMP = 'jump'
SWITCH = 'switch'
ALL_ACTIONS = [LEFT, RIGHT, UP, DOWN, JUMP, SWITCH]

class MyEvent(object):
    """Event class from NP."""

    def __init__(self, action, down):
        self.action = action
        self.down = down
        self.up = not down

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return '{0} {1}'.format(self.action, self.down)

def get_events(pressed):
    """Return list of events and dict of pressed keys that we care about."""
        
    # use roughly the event method used by NP to build event list.
    # will want to edit this later so we can configure a joystick.
    events = []
    quitevent = False
    for event in  pygame.event.get():
        if (event.type == pygame.KEYDOWN) or (event.type == pygame.KEYUP):
            down = (event.type == pygame.KEYDOWN)
            if (event.key == pygame.K_SPACE):
                events.append(MyEvent(JUMP, down))
                pressed[JUMP] = down
            if (event.key == pygame.K_RETURN):
                events.append(MyEvent(SWITCH, down))
                pressed[SWITCH] = down
            elif event.key == pygame.K_LEFT:
                events.append(MyEvent(LEFT, down))
                pressed[LEFT] = down
            elif event.key == pygame.K_RIGHT:
                events.append(MyEvent(RIGHT, down))
                pressed[RIGHT] = down
            elif event.key == pygame.K_UP:
                events.append(MyEvent(UP, down))
                pressed[UP] = down
            elif event.key == pygame.K_DOWN:
                events.append(MyEvent(DOWN, down))
                pressed[DOWN] = down
            # joystick events (a bit hacky for now, configured only for my gamepad)
        elif (event.type == pygame.JOYBUTTONDOWN) or (event.type == pygame.JOYBUTTONUP):
            down = (event.type == pygame.JOYBUTTONDOWN)
            # the 'A' button on my controller is jump
            if event.button == 1:
                events.append(MyEvent(JUMP, down))
                pressed[JUMP] = down
            if (event.button == 4) or (event.button == 5):
                events.append(MyEvent(SWITCH, down))
                pressed[SWITCH] = down
        elif event.type == pygame.JOYAXISMOTION:
            if event.axis == 0:
                if event.value > 0.3:
                    events.append(MyEvent(RIGHT, True))
                    pressed[RIGHT] = True
                elif event.value < -0.3:
                    events.append(MyEvent(LEFT, True))
                    pressed[LEFT] = True
                else: # we are in the central position
                    if pressed[RIGHT]:
                        pressed[RIGHT] = False
                    elif pressed[LEFT]:
                        pressed[LEFT] = False
            if event.axis == 1:
                if event.value > 0.3:
                    events.append(MyEvent(DOWN, True))
                    pressed[DOWN] = True
                elif event.value < -0.3:
                    events.append(MyEvent(UP, True))
                    pressed[UP] = True
                else: # we are in the central position
                    if pressed[UP]:
                        pressed[UP] = False
                    elif pressed[DOWN]:
                        pressed[DOWN] = False
        # quit game
        elif event.type == pygame.QUIT:
            quitevent = True

    return events, pressed, quitevent
