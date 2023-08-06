from worldgame.tiles import Tile
from scurses.colors import *
from random import random

version_string = "0.2.0"

menu_icon = ("...                  ",
             " :  ... .   ... ... :",
             " :  :.. :   :.. :.. :",
             ".:. ..: :.. :.. ..: .")

help_page = ("Arrow Keys / WASD - Move",
             "Tilde  / Q / P    - Pause",
             "Space      / E    - Interact",
             "Shift-Q           - Quit",
             "",
             "A description of the tile you are",
             "facing shows up in the bottom right.",
             "If you can interact with it, it will",
             "be preceded by a white box.")

changelog = ("0.2.0 - 2023/08/06",
             " • Added Python3 support.",
             " • Added Poetry support for running with the necessary dependencies.",
             "0.1.5 - 2013/06/21",
             " • Fixed the issue where rivers could flow parallel, which caused",
             "    them to visually connect at each tile and look bad. There",
             "    should be no more of this now: ├┬┬┬┬┬┬────",
             "    If you see any, tell me.       ┴┴┴┴┴┴┤",
             " • You can now save in the pause menu, and load from the main menu.",
             "    It is pretty fragile right now, and it always saves to your home dir.",
             " • These text areas can now have headers.",
             "",
             "0.1.4",
             " • Menu items can now be clicked!",
             " • Wrote a new core function to handle displaying chunks of text,",
             "    - Clips text to fit areas (may add wrapping eventually)",
             "    - Long text can now be scrolled with arrow keys.",
             "    - Both instructions and changelog(this screen) use this now.",
             "0.1.3",
             " • Rivers that don't run into another river or the ocean",
             "    will now attempt to generate a lake at their end.",
             "    If a large enough lake can generate, the river stays.",
             " • Made Q bring up menu again since I kept trying to use it",
             "    and made Shift-Q just quit immediately. Might change this.",
             " • Made a pretty cool core change to my window api that allows",
             "    you to jump to items in a menu by starting to type the label.",
             "    It also can automatically press the button when a single match",
             "    is found, but this is currently disabled in all in game menus.",
             "",
             "0.1.2",
             " • Added world generation info off the right of the window.",
             " • Improved river generation,",
             "    still working on forcing nearby rivers together.",
             "",
             "0.1.1",
             " • Rivers added. World generation takes much longer.",
             "",
             "0.1.0",
             " • Changelog and version information added.",
             " • City spawning fixed, # per map upped to 30.",
             " • Pause menu added, quit keybinds changed, now open menu.",
             " • Trees added",
             " • Walking into solid block will now rotate you to it.",
             " • Metadata is now initialized by world generator.")

key_bindings = {"Move Left":  ("KEY_LEFT",  "a"),
                "Move Right": ("KEY_RIGHT", "d"),
                "Move Up":    ("KEY_UP",    "w"),
                "Move Down":  ("KEY_DOWN",  "s"),
                "Interact":   (" ",         "e"),
                "Pause":      ("`","~", "q","p"),
                "Quit":       ("Q")}

color_list = ((BLACK, WHITE),
              (RED,   YELLOW),
              (RED,   GREEN),
              (WHITE, BLUE),
              (WHITE, YELLOW),
              (241,   245),
              (BROWN, 245),
              (245,   94),
              (BROWN, GREEN),
              (22,    GREEN),
              (BLUE,  GREEN),
              (BLUE,  YELLOW),
              (BLUE,  245),
              (BLUE,  WHITE),
              (WHITE, RED),
              (WHITE, 52),
              (WHITE, 17))

def tile_list(win):
  return (Tile(win,
               lambda md, bs: "Void",
               lambda md, bs: " ",
               lambda md, bs: 0,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "Grass",
               lambda md, bs: " ",
               lambda md, bs: 3,
               lambda md, bs: False),
          Tile(win,
               lambda md, bs: "Sand",
               lambda md, bs: "⢕",
               lambda md, bs: 5,
               lambda md, bs: False),
          Tile(win,
               lambda md, bs: "Water",
               lambda md, bs: "~" if random() > .6 else " ",
               lambda md, bs: 4,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "Flowers",
               lambda md, bs: "༶",
               lambda md, bs: 3,
               lambda md, bs: False),
          Tile(win,
               lambda md, bs: "Mountains",
               lambda md, bs: "▲",
               lambda md, bs: 6,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "Snow",
               lambda md, bs: " ",
               lambda md, bs: 1,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "Closed Gate" if md%2 == 0 else "Open Gate",
               _gate_char,
               lambda md, bs: 7,
               lambda md, bs: md%2 == 0,
               lambda md, bs: (lambda pl, md, bs: (md+1)%2,)),
          Tile(win,
               lambda md, bs: "Stone Wall",
               lambda md, bs: _connect_char(md, bs, (8,), DOUBLE_LINES),
               lambda md, bs: 8,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "Cobble Street",
               lambda md, bs: "#",
               lambda md, bs: 6,
               lambda md, bs: False),
          Tile(win,
               lambda md, bs: "Building",
               lambda md, bs: "⌂",
               lambda md, bs: 9,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "Tree",
               lambda md, bs: "Y" if md%2 == 0 else "T",
               lambda md, bs: 10,
               lambda md, bs: True),
          Tile(win,
               lambda md, bs: "River",
               lambda md, bs: _connect_char(md, bs, (12,3), SINGLE_LINES),
               _river_color,
               _river_collide))



_WALL_ID = 8
_GATE_ID = 7

def _river_color(md, bs):
  if md == 2: return 12
  if md == 5: return 13
  if md == 6: return 14
  return 11

def _river_collide(md, bs):
  if md in (5, 6):
    return True
  return False

def _gate_char(md, bs):
  n = bs[0]
  e = bs[1]
  s = bs[2]
  w = bs[3]

  if md%2 == 0: return "#"
  if ((n == _GATE_ID or n == _WALL_ID) and
      (s == _GATE_ID or s == _WALL_ID)):
      return "┊"
  return "┈"


DOUBLE_LINES = ("▫", "║", "═", "╚", "╔", "╗", "╝", "╩", "╠", "╦", "╣", "╬")
SINGLE_LINES = ("·", "│", "─", "└", "┌", "┐", "┘", "┴", "├", "┬", "┤", "┼")
HEAVY_LINES  = ("·", "┃", "━", "┗", "┏", "┓", "┛", "┻", "┣", "┳", "┫", "╋")

def _connect_char(md, bs, connect_to, chars):
  n = bs[0] in connect_to
  e = bs[1] in connect_to
  s = bs[2] in connect_to
  w = bs[3] in connect_to

  if n:
    if e:
      if s:
        if w: return chars[11]
        return chars[8]
      if w: return chars[7]
      return chars[3]
    if s:
      if w: return chars[10]
      return chars[1]
    if w: return chars[6]
    return chars[1]
  if e:
    if s:
      if w: return chars[9]
      return chars[4]
    return chars[2]
  if s:
    if w: return chars[5]
    return chars[1]
  if w: return chars[2]
  return chars[0]
