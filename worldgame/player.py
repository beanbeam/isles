# coding=UTF-8

class Player(object):
  def __init__(self, window, x, y, stats, health=None, mana=None, effects=None, facing="n"):
    self._window = window
    
    if facing == 0: facing = "n"
    elif facing == 1: facing = "e"
    elif facing == 2: facing = "s"
    elif facing == 3: facing = "w"
    
    self._facing = facing
    
    self._health = health
    self._mana = mana
    
    self._effects = effects
    self._stats = stats
    self.x = x
    self.y = y

  def _facing_as_int(self):
    if self._facing == "e": return 1
    if self._facing == "s": return 2
    if self._facing == "w": return 3
    return 0

  def draw(self, x, y):
    draw_char = "^"
    if self._facing in ("down", "d", "south", "s"):   draw_char = "▼"
    elif self._facing in ("left", "l", "west", "w"):  draw_char = "◄"
    elif self._facing in ("right", "r", "east", "e"): draw_char = "►"
    else:                                             draw_char = "▲"

    self._window.draw_string(x, y, draw_char, 1)
 
  def front(self):
    if self._facing in ("down", "d", "south", "s"):
      return (self.x, self.y+1)
    elif self._facing in ("left", "l", "west", "w"):
      return (self.x-1, self.y)
    elif self._facing in ("right", "r", "east", "e"):
      return (self.x+1, self.y)
    else:
      return (self.x, self.y-1)

  def move(self, dx, dy):
    self.x += dx
    self.y += dy

    self.rotate_toward(dx, dy)

  def rotate_toward(self, dx, dy):
    old_facing = self._facing
    if abs(dx) > abs(dy):
      if   dx > 0: self._facing = "e"
      else:        self._facing = "w"
    else:
      if   dy > 0: self._facing = "s"
      elif dy < 0: self._facing = "n"
    return not old_facing == self._facing

  def as_tuple(self):
    return (self.x, self.y, self._facing_as_int())
