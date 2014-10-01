#! /usr/bin/python

import noise
import numpy
import tiles
import random
from math import hypot
import time

def new_map(w, h):
  time_start = time.clock()

  thght = numpy.empty((w, h), numpy.float32)
  tiles = numpy.empty((w, h), numpy.uint8)
  metad = numpy.empty((w, h), numpy.uint8)
  xseed = random.random()*10000
  yseed = random.random()*10000
  for i in range(w):
    for j in range(h):
      height = noise.snoise2(xseed+i*.01, yseed+j*.01, 8)
      thght[i,j] = height
      metad[i,j] = 0
      if height < -.2:
        tiles[i,j] = 3
      elif height < -.16:
        tiles[i,j] = 2
      elif height < .5:
        if height > 0 and random.random() > .99:
          tiles[i,j] = 4
        elif random.random() > .995:
          tiles[i,j] = 11
          if random.random() > .5:
            metad[i,j] = 1
        else:
          tiles[i,j] = 1
      elif height < .6:
        tiles[i,j] = 5
      else:
        tiles[i,j] = 6

  time_tile_end = time.clock()

  # VERY SLOW, ALSO BAD
  #_generate_watershed(tiles, thght, w, h)

  placed_rivers = 0
  placed_lakes  = 0
  peaks = _find_peaks(thght, w,h)
  for p in peaks:
    if placed_rivers >= 500: break # Cap Rivers
    r = _place_river(tiles, thght, metad, w, h, 15, p[0], p[1])
    if r != False:
      placed_rivers += 1
      if r == "Lake": placed_lakes += 1

  time_river_end = time.clock()

  placed_cities = 0
  while placed_cities < 30:
    if _try_place_random_city(tiles, w, h):
      placed_cities += 1

  time_city_end = time.clock()

  placed_groves = 0
  for i in range(100):
    _place_tree_grove(tiles, metad, w, h)
    placed_groves += 1

  time_trees_end = time.clock()

  map_info = ("%sx%s World Generated" % (w, h),
              "| %s Tiles generated in %s seconds" % (w*h, time_tile_end-time_start),
              "| %s Rivers and %s Lakes generated in %s seconds" % (placed_rivers, placed_lakes , time_river_end-time_tile_end),
              "| %s Cities generated in %s seconds" % (placed_cities, time_city_end-time_river_end),
              "| %s Forests generated in %s seconds" % (placed_groves, time_trees_end-time_city_end),
              "| TOTAL:   %s seconds" % (time_trees_end-time_start))

  return (tiles, metad, map_info)

def _find_peaks(thght, w, h):
  peaks = []
  for i in range(w-2):
    for j in range(h-2):
      p = thght[i+1, j+1]
      if (p > thght[i+1, j] and
          p > thght[i+2, j+1] and
          p > thght[i+1, j+2] and
          p > thght[i, j+1]):
        peaks.append((i+1, j+1))
  random.shuffle(peaks)
  return peaks

def _place_river(tiles, thght, metad, w, h, min_length, x=None, y=None):
  if x==None: x = int(random.random()*w)
  if y==None: y = int(random.random()*w)

  r_tiles = []
  prev_h = None
  curr_x = x
  curr_y = y
  into_water = False
  while True:
    min_dir = (0, 0)
    min_height = thght[curr_x, curr_y]
    t = tiles[curr_x, curr_y]
    if t == 3 or t == 12:
      into_water = True
      break #Don't generate rivers in ocean
    for p in ((1,0), (0,1), (-1,0), (0,-1)):
      nx = curr_x+p[0]
      ny = curr_y+p[1]
      if nx >= 0 and ny >= 0 and nx < w and ny < h:
        hght = thght[nx, ny]
        if (tiles[nx, ny] in (3, 12) and
            hght < prev_h): # always flow into nearby rivers/water
          into_water = True
          break
        if hght < min_height:
          min_height = hght
          min_dir = p
    if into_water:
      r_tiles.append((curr_x, curr_y))
      break
    if min_dir == (0, 0): break
    r_tiles.append((curr_x, curr_y))
    prev_h = thght[curr_x, curr_y]
    curr_x += min_dir[0]
    curr_y += min_dir[1]
  if len(r_tiles) < min_length: return False
  l_tiles = []
  if not into_water:
    l_tiles =_get_lake(thght, curr_x, curr_y, w, h, len(r_tiles))
    if len(l_tiles) <= 0:
      return False
  for t in r_tiles:
    metad[t[0], t[1]] = tiles[t[0], t[1]]
    tiles[t[0],t[1]] = 12
  for t in l_tiles:
    tiles[t[0], t[1]] = 3
  return "Other" if into_water else "Lake"

def _get_lake(thght, x, y, w, h, amt, hper=.02):
  height = hper+thght[x, y]
  last_added = 1
  temp_tiles = [(x, y)]
  temp_filled = 1
  filled_tiles = []

  while True:
    while last_added > 0:
      last_tiles = temp_tiles[-last_added:]
      last_added = 0
      for t in last_tiles:
        for p in ((1,0), (0,1), (-1,0), (0,-1)):
          new_t = (t[0]+p[0], t[1]+p[1])
          if (new_t[0] >= 0 and new_t[0] < w and
              new_t[1] >= 0 and new_t[1] < h and
              not new_t in temp_tiles and
              thght[new_t[0], new_t[1]] < height):
            if temp_filled > amt: return filled_tiles
            temp_tiles.append(new_t)
            last_added+= 1
            temp_filled+= 1
    filled_tiles = temp_tiles
    last_added = len(temp_tiles)
    height+= hper
    temp_filled += last_added
    if temp_filled > amt: return filled_tiles


def _generate_watershed(tiles, thght, w, h):
  watershed = _process_watershed(thght, w, h)
  for i in range(w):
    for j in range(h):
      if watershed[i, j] > 25:
        tiles[i, j] = 12

def _process_watershed(thght, w, h):
  watershed = numpy.zeros((w, h), numpy.uint8)
  for i in range(w):
    for j in range(h):
      waterx = i
      watery = j

      while True:
        height = thght[waterx, watery]
        if height < 80: break
        min_height = height
        min_dir = (0,0)
        for p in ((1,0), (0,1), (-1,0), (0,-1)):
          chx = waterx+p[0]
          chy = watery+p[1]
          if chx >= 0 and chy >= 0 and chx < w and chy < h:
            hgt = thght[chx, chy]
            if min_height < hgt:
              min_height = hgt
              min_dir = p
        watershed[waterx, watery] += 1
        if min_dir == (0,0): break
        waterx += min_dir[0]
        watery += min_dir[1]
  return watershed


def _place_tree_grove(tiles, metad, w, h):
  x = int(random.random()*(w-30))+15
  y = int(random.random()*(h-20))+10

  for i in range(-10, 10):
    for j in range(-5, 5):
      prob = (hypot(i, j*2)/2)+5
      if (random.random()*10 > prob):
        place = True
        for t in _2d_range(x+i-1, y+j-1, 3, 3, tiles):
          if not (t == 1 or t == 4 or t == 11):
            place = False
            break
        if place:
          tiles[i+x, j+y] = 11
          if random.random() > .5:
            metad[i+x, j+y] = 1


def _try_place_random_city(tiles, w, h):
  x = int(random.random()*(w-25-4))+2
  y = int(random.random()*(h-15-2))+1

  w = int(random.random()*10)+15
  h = int(random.random()*5)+10

  for t in _2d_range(x-4, y-2, w+8, h+4, tiles):
    if not (t == 1 or t == 4 or t == 11): return False
  _place_city(x, y, w, h, tiles)
  return True

def _2d_range(x, y, w, h, tiles):
  for i in range(w):
    for j in range(h):
      yield tiles[x+i, y+j]

def _place_city(x, y, w, h, tiles):
  for i in range(w):
    for j in range(h):
      if i == 0 or i == w-1 or j == 0 or j == h-1:
        if i == w/2 or j == h/2:
          tiles[x+i, y+j] = 7
        else:
          tiles[x+i, y+j] = 8
      elif i == w/2 or j == h/2:
        tiles[x+i, y+j] = 9
      elif random.random() > .6:
        tiles[x+i, y+j] = 10

