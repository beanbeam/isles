#! /usr/bin/python

import scurses.window as window
import scurses.colors as colors
import worldgame.tiles as tiles
import worldgame.player as player
import worldgame.world as world
import worldgame.generator as generator
import worldgame.definitions as definitions
import time
import numpy
import os

SAVE_PATH = os.path.join(os.path.expanduser("~"), "world.dat")

def init(win):
  colors.init(definitions.color_list)
  tiles.init(definitions.tile_list(win))
  main_menu(win)

def main_menu(win):
  win.clear()
  for i, line in enumerate(definitions.menu_icon):
    win.draw_string_centered(i+2, line)
  
  ver = definitions.version_string
  win.draw_string(win.width-len(ver), win.height-1, ver)

  options = ["New Game", "Load World", "Instructions", "Change Log", "Quit"]
  if not os.path.exists(SAVE_PATH): options.remove("Load World")
  selected = options[win.do_menu(8, options, 0, 1, 0)]
  if selected == "New Game": main_game(win)
  elif selected == "Load World": main_game(win, SAVE_PATH)
  else:
    if selected == "Instructions": win.do_text_area(definitions.help_page, "Instructions")
    elif selected == "Change Log": win.do_text_area(definitions.changelog, "Change Log")
    elif selected == "Quit": return
    main_menu(win)

def pause_menu(win):
  for y in range(16):
    win.draw_string(30, 4+y, " "*20)
  win.draw_string_centered(6, "-PAUSED-")
  options = ("Resume", "Save", "Menu", "Quit")
  selected = win.do_menu(8, options, 0, 1, 0)
  return options[selected]

def main_game(win, load=None):
  mwidth = 500
  mheight = 500
  back_to_menu = False

  if load == None:
    w = world.World(win, generator.new_map(mwidth, mheight),
                         player.Player(win, mwidth/2, mheight/2, player.Stats(100, 100), 30, 30))
    w.spawn_player_near(mwidth/2,mheight/2, 25)
  elif os.path.exists(load):
    w = world.load(win, load)
  else: back_to_menu = True

  win.clear
  while not back_to_menu:
    w.draw()
    win.refresh()
    while True: # Accept input until boumd key is pressed.
      key = win.read_key(True)
      if   key in definitions.key_bindings["Move Left"] and w.try_move_player(-1, 0): break
      elif key in definitions.key_bindings["Move Right"] and w.try_move_player(1, 0): break
      elif key in definitions.key_bindings["Move Up"]   and w.try_move_player(0, -1): break
      elif key in definitions.key_bindings["Move Down"]  and w.try_move_player(0, 1): break
      elif key in definitions.key_bindings["Interact"]       and w.player_interact(): break
      elif key in definitions.key_bindings["Quit"]: exit()
      elif key in definitions.key_bindings["Pause"]:
        p = pause_menu(win)
        if p == "Save":
          w.save(SAVE_PATH)
        elif p == "Menu":
          back_to_menu = True
          break
        elif p == "Quit": exit()
        w.draw()
        win.refresh()

  main_menu(win)

window.CursesWindow(init, 80, 24)
