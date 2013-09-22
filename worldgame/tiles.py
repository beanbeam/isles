class Tile(object):
  _TILES = None

  def __init__(self, window, name_when, char_when, color_when, solid_when,
               interactions_when = None, actions_when = None):
    if interactions_when is None: interactions_when = lambda md, bs: ()
    if actions_when is None:      actions_when      = lambda md, bs: ()

    self._window           = window
    self.name_when         = name_when
    self.char_when         = char_when
    self.color_when        = color_when
    self.solid_when        = solid_when
    self.interactions_when = interactions_when
    self.actions_when      = actions_when
  
  def interact(self, player, meta, near):
    interactions = self.interactions_when(meta, near)
    if len(interactions) <= 0: return meta
    if len(interactions) == 1:
      return interactions[0](player, meta, near)
  
  def draw(self, x, y, meta, near):
    self._window.draw_string(x, y, self.char_when(meta, near),
                                   self.color_when(meta, near))

def init(tile_list):
  Tile._TILES = tile_list
def get(tile_id):
  if Tile._TILES is None: raise Exception("Tiles have not been initialized. Call init(tile_list) first!")
  return Tile._TILES[tile_id]
