import tiles
import numpy
import time
import player

def load(win, filename):
  with open(filename, "r") as f:
    load_start = time.clock()
    loaded = numpy.load(f)
    tiles = loaded["tiles"]
    metad = loaded["metad"]
    plyr = loaded["player"]
    load_end = time.clock()
    return World(win, (tiles, metad,
                       ["World loaded from %s in %s seconds" %
                         (filename, load_end-load_start)]),
                      player.Player(win, plyr[0], plyr[1],  player.Stats(100, 100), plyr[2], plyr[3], None, plyr[4]))  

class World(object):
  def __init__(self, window, wmap, player):
    self._window = window
    self._tile_map = numpy.array(wmap[0], dtype=int)
    self._meta_map = numpy.array(wmap[1], dtype=int)
    self._gen_info = wmap[2]
    self._player = player
  
  def tid_at(self, x, y):
    if (x < 0 or x >= self.map_width or
        y < 0 or y >= self.map_height):
      return 0
    return self._tile_map[x,y]

  def tile_at(self, x, y):
    return tiles.get(self.tid_at(x, y))

  def meta_at(self, x, y): 
    if (x < 0 or x >= self.map_width or
        y < 0 or y >= self.map_height):
      return 0
    return self._meta_map[x][y]

  def get_neighbors(self, x, y):
    return (self.tid_at(x, y-1),
            self.tid_at(x+1, y),
            self.tid_at(x, y+1),
            self.tid_at(x-1, y))

  def draw(self, x = None, y = None):
    # Generation info
    for i, line in enumerate(self._gen_info):
      self._window.draw_string(self._window.width+1, i, line)
    
    if x is None: x = self._player.x
    if y is None: y = self._player.y
    w = self._window.width
    h = self._window.height
    for i, j, tile, meta, neig in self._tiles_within(x-(w/2), y-(h/2), w, h-2):
      tile.draw(i, j, meta, neig)
    self._player.draw(w/2,h/2)
    self._window.draw_string(0,h-2, "(%s,%s)%s" % (x, y, " "*w))

    # Health bar
    hp_width = w/2
    hp = self._player.health
    hp_max = self._player._stats.max_health
    hp_filled = hp_width*hp/hp_max
    health_string = (" HP: %s/%s" % (hp, hp_max) + " "*hp_width)[:hp_width]
    self._window.draw_string(0,h-1, health_string[:hp_filled], 15)
    self._window.draw_string(hp_filled, h-1, health_string[hp_filled:], 16)
    
    # Mana bar
    mp_width = w-hp_width
    mp = self._player.mana
    mp_max = self._player._stats.max_mana
    mp_filled = mp_width*mp/mp_max
    mana_string = (" MP: %s/%s" % (mp, mp_max) + " "*mp_width)[:mp_width]
    self._window.draw_string(hp_width,h-1, mana_string[:mp_filled], 4) 
    self._window.draw_string(hp_width+mp_filled, h-1, mana_string[mp_filled:], 17)
    
    # Tile information
    facing_t = apply(self.tile_at, self._player.front())
    facing_m = apply(self.meta_at, self._player.front())

    tile_name = facing_t.name_when(facing_m, ())
    self._window.draw_string(w-len(tile_name), h-2, tile_name)
    
    tile_ints = 1 if len(facing_t.interactions_when(facing_m, ())) > 0 else 0
    self._window.draw_string(w-len(tile_name)-2, h-2, " ", tile_ints)


  def _tiles_within(self, x, y, w, h):
    for i in range(x, x+w):
      for j in range(y, y+h):
        yield (i-x, j-y, self.tile_at(i, j),
                         self.meta_at(i, j),
                         self.get_neighbors(i, j))

  def move_player_to(self, x, y):
    self._player.x = x
    self._player.y = y

  def try_move_player(self, dx, dy):
    newx = self._player.x+dx
    newy = self._player.y+dy
    if not self.tile_at(newx, newy).solid_when(self.meta_at(newx,newy), ()):
      self._player.move(dx, dy)
      return True
    return self._player.rotate_toward(dx, dy)

  def player_interact(self):
    p = self._player
    x = p.front()[0]
    y = p.front()[1]
    self._meta_map[x][y] = self.tile_at(x, y).interact(p, self.meta_at(x, y), ())
    return True

  #Try to place the player somewhere they can stand near (x,y).
  #Give up if there is nothing within maxr tiles.
  def spawn_player_near(self, x, y, maxr):
    for i, j in _spiral(x, y, maxr):
      if not self.tile_at(i,j).solid_when(0, ()):
        self.move_player_to(i,j)
        break

  def save(self, filename):
    with open(filename, "w") as f:
      numpy.savez(f, tiles = self._tile_map,
                     metad = self._meta_map,
                     player= numpy.asarray(self._player.as_tuple()))

  # PROPERTIES
  ############
  @property
  def map_width(self):
    return self._tile_map.shape[0]

  @property
  def map_height(self):
    return self._tile_map.shape[1]


# Yields an approximation of a square spiral outwards to maxr from x, y.
def _spiral(x, y, maxr):
  yield (x,y)
  for r in range(1, maxr+1):
    for s in range(4):
      for t in range(2*r):
        if s == 0:
          yield (x-r, y-r+t)
        elif s == 1:
          yield (x-r+t, y+r)
        elif s == 2:
          yield (x+r, y+r-t)
        elif s == 3:
          yield (x+r-t, y-r)

