from time import *
from random import randrange
from thread import *

#Local directory where game files are located.
showInformation("On the next screen, select the CST205_Final_Project directory on your local machine")
file = setMediaPath()
imageFile = file+"/CST205_Final_Images"
coords = {}

tracks = {
  "Intro" : makeSound(file+"/Piano_Intro.wav"),
  "Main" : makeSound(file+"/Main_Piano.wav"),
  "Game Over" : makeSound(file+"/Game_Over_Full.wav")
}

def get_turtle(x,y,w):
  t = makeTurtle(w)
  penUp(t)
  moveTo(t,x,y)
  return t

def remove_turtle(t,w):
  w.getTurtleList().remove(t)

def coin_toss():
  return randrange(0,2)

def audio_player(mode,track):
  if mode == "play":
    play(tracks[track])
    return
  stopPlaying(tracks[track])
  return

class character:
  def __init__(self,map):
    self.name = ""
    self.position = {"x":0,"y":0}
    self.map = map
    self.draw_self(self.position["x"],self.position["y"])
    self.movement = {}
    #self.update_movement()
  def draw_self(self,x,y):
    redraw = self.change_background(self.name)
    sprite = get_turtle(x,y,self.map)
    drop(sprite,redraw)
    remove_turtle(sprite,self.map)
    ##repaint(self.map)
  def get_pos(self):
    return [self.position["x"],self.position["y"]]
  def set_position(self,move):
    current = self.position
    current["x"] = move[0]
    current["y"] = move[1]
  def change_background(self,name):
    sprite = pics.get_sprite(name)
    map_x = self.position["x"]
    map_y = self.position["y"]
    for x in range(0,getWidth(sprite)):
      for y in range(0,getHeight(sprite)):
        current = getPixel(sprite,x,y)
        if getColor(current) == makeColor(255,174,201):
          setColor(current, getColor(getPixel(self.map.getPicture(),map_x,map_y)))
        map_y += 1
      map_y = self.position["y"]
      map_x += 1
    return sprite
  def move(self,direction):
    path = self.movement[direction]
    open = graveyard.check_valid(path)
    if open is False:
      pic = pics.get_sprite("Wrong Way")
      show(pic)
      sleep(.7)
      pic.getPictureFrame().close()
      #print "You can't go that way!" #Will replace with a graphic prompt if able
      return
    self.set_position(self.movement[direction])
    graveyard.reset_map()
    self.map = graveyard.get_map()
    self.draw_self(self.position["x"],self.position["y"])
    self.update_movement()
    #repaint(self.map)
  def update_movement(self):
    current = self.get_pos()
    self.movement["w"] = [current[0],current[1]-64]
    self.movement["a"] = [current[0]-64,current[1]]
    self.movement["s"] = [current[0],current[1]+64]
    self.movement["d"] = [current[0]+64,current[1]]

class player(character):
  def __init__(self,map):
    self.name = "Player"
    self.health = 3
    self.TK = 2
    self.position = {"x":256,"y":512}
    self.map = map
    self.draw_self(self.position["x"],self.position["y"])
    self.movement = {}
    self.update_movement()
    self.health_meter()
  def health_meter(self):
    hearts = get_turtle(64,64,self.map)
    sprite = pics.get_hearts(self.health)
    drop(hearts,sprite)
    remove_turtle(hearts,self.map)
    #repaint(self.map)
  def hit(self):
    self.set_position([256,512])
    self.update_movement()
    self.health -= 1
    if self.health >= 1:
      graveyard.reset_map()
      self.map = graveyard.get_map()
      self.draw_self(256,512)
  def examine(self):
    pass
  def dig(self):
    coords = "".join(self.get_pos()) #needs to convert to string
    if coords in gamestate.graves:
      gamestate.graves[coords].dig_grave()
      grave = get_turtle(384,256,self.map)
      sprite = pics.get_sprite("Open Grave")
      drop(grave,sprite)
      remove_turtle(grave,self.map)
      #pass
    else:
      print self.position
"""
  def update_movement(self):
    current = self.get_pos()
    self.movement["w"] = [current[0],current[1]-128]
    self.movement["a"] = [current[0]-128,current[1]]
    self.movement["s"] = [current[0],current[1]+128]
    self.movement["d"] = [current[0]+128,current[1]]
"""

class necro(character):
  sleeping = True
  visible = True
  def __init__(self,map):
    self.name = "Necro left"
    self.map = map
    self.position = {"x": 1280,"y": 256}
    self.draw_self(self.position["x"],self.position["y"])
    self.movement = {}
    self.update_movement()
  def awake(self):
    if self.sleeping:
      self.sleeping = False
      return
    hero = artemis.get_pos()
    path = self.pathfinding(hero)
    self.move(path)
    if self.attack():
      self.sleeping = True
      return
  def pathfinding(self,hero):
    path = [[hero[0],hero[1],0]]
    found = False
    enemy = self.get_pos()
    counter = 0
    while not found:
      current = path[counter]
      value = current[2]+1
      adjacent = [[current[0],current[1]+64,value],[current[0]+64,current[1],value],[current[0],current[1]-64,value],[current[0]-64,current[1],value]]
      for tile in adjacent:
        check_bounds = [tile[0],tile[1]]
        check_bounds = graveyard.check_valid(check_bounds)
        check_path = self.in_path(path,tile)
        if check_bounds == True and check_path == False:
          path.append(tile)
        if tile[0] == enemy[0] and tile[1] == enemy[1]:
            found = tile[2]-1
            break
      counter += 1
    found = self.trace_path(found,path)
    if coin_toss():
      self.move([found[0],found[1]])
      found = found[2]-1
      found = self.trace_path(found,path)
    return [found[0],found[1]]
  def move(self,direction):
    self.set_position(direction)
    graveyard.reset_map()
    self.map = graveyard.get_map()
    self.draw_self(self.position["x"],self.position["y"])
    hero = artemis.get_pos()
    artemis.draw_self(hero[0],hero[1])
    self.update_movement()
    ##repaint(self.map)
  def in_path(self, path, tile):
    for item in path:
      if tile[0] == item[0] and tile[1] == item[1] and item[2] <= tile[2]:
        return True
    return False
  def trace_path(self,value,path):
    for tile in path:
      adjacent = [tile[0],tile[1]]
      if tile[2] == value and adjacent in self.movement.values():
        return tile
  def attack(self):
    if artemis.get_pos() in self.movement.values() or artemis.get_pos() == self.get_pos():
      artemis.hit()
      return True
    return False

class map:
  coords = {}
  def __init__(self):
    self.graveyard = makeWorld(1920,1024)
    self.graveyard.hideFrame()
    self.graveyard.setPicture(pics.get_sprite("Map base"))
    self.graveyard.showFrame()
    self.set_map()
  def get_map(self):
    return self.graveyard
  def reset_map(self):
    self.graveyard.setPicture(pics.get_sprite("Map base"))
    artemis.health_meter()
    if erebus.visible:
      pos = erebus.get_pos()
      erebus.draw_self(pos[0],pos[1])
  def check_valid(self,check):
    if str(check[0]) in self.coords:
      if check[1] in self.coords[str(check[0])]:
        return True
    return False
  def set_TK(self,spot):
    TK = get_turtle(spot[0],spot[1],self.graveyard)
    drop(TK,images.get_sprite(TK))
    self.graveyard.getTurtleList.remove(TK)
  def set_map(self):
    for x in range(256,1984,256):
      self.coords[str(x)] = []
      for y in range(256,832,64):
        if (x == 768 and y == 384) or (x == 1536 and (384 <= y <= 512)) or ((1408 <= x <= 1536) and y == 576):
          continue
        else:
          self.coords[str(x)].append(y)
    for x in range(256,1856,64):
      if str(x) not in self.coords:
        self.coords[str(x)] = []
      self.coords[str(x)].append(256)
      self.coords[str(x)].append(768)
      if not(1472 <= x <= 1600):
        self.coords[str(x)].append(512)

class gamestate:
  def __init__(self):
    self.undertaker()
    self.graves()
  def undertaker(self):
    for x in range(384, 1920, 256):
      for y in range(256, 1024, 256):
        graves[str(x)+str(y)] = grave(x,y)
  def set_target(self):
    for i in range(0,2):
      x = randrange(384,1920,256)
      y = randrange(256,1024,256)
      target = self.graves[str(x)+str(y)]
      if target.target is True:
        i -= 1
      else:
        target.target = True
  def grave_digger(self,gravesite):
    pass

class grave:
  def __init__(self, x, y):
    self.position = {"x": x, "y": y}
    self.activated = False
    self.target = False
  def get_grave_loc(self):
    return [self.position['x'],self.position['y']]
  def dig_grave(self):
    #self.activated = True
    #if self.target == False:
      #return self.get_grave_loc
    #return False
    pass

class images:
  def __init__(self):
    self.library = {
      "1 health" : imageFile+"/Health_One.png",
      "2 health" : imageFile+"/Health_Two.png",
      "3 health" : imageFile+"/Health_Full.png",
      "Player" : imageFile+"/Hero_Graveyard_2CK_3.png",
      "Necro front" : imageFile+"/Necromancer_front_face_CK.png",
      "Necro back" : imageFile+"/Necromancer_back_face_CK.png",
      "Necro left" : imageFile+"/Necromancer_left_face_CK.png",
      "Necro right" : imageFile+"/Necromancer_right_face_CK.png",
      "Map base" : imageFile+"/Graveyard.png",
      "Title 1" : imageFile+"/Game_Title_Screen.png",
      "Title 2" : imageFile+"/Game_Title_Screen_2.png",
      "Wrong Way" : imageFile+"/Wrong_Way.png",
      "Game Over" : imageFile+"/Game_Over_Screen.png",
      "Arrow" : imageFile+"/Graveyard_Arrow.png",
      "Open Grave": imageFile+"Dug_Grave.png"
      #"TK" : imageFile+"",
      #"Ghost" : imageFile+""
    }
  def get_hearts(self,health):
    return makePicture(self.library[str(health) + " health"])
  def get_sprite(self,sprite):
    return makePicture(self.library[sprite])

def game_start(check):
  raw_input()
  check.append(None)

def title_screen():
  check = []
  start_new_thread(game_start, (check,))
  title = makeWorld(1920,1024)
  screen_one = get_turtle(0,0,title)
  screen_two = get_turtle(0,0,title)
  drop(screen_one,pics.get_sprite("Title 1"))
  audio_player("play","Intro")
  remove_turtle(screen_one,title)
  while not check:
    sleep(.5)
    drop(screen_two,pics.get_sprite("Title 2"))
    remove_turtle(screen_two,title)
    sleep(.5)
    drop(screen_one,pics.get_sprite("Title 1"))
    remove_turtle(screen_one,title)
  title.hideFrame()
  audio_player("stop","Intro")

def game_over():
  dead = makeWorld(1920,1024)
  screen = get_turtle(0,0,dead)
  drop(screen,pics.get_sprite("Game Over"))
  audio_player("play","Game Over")
  remove_turtle(screen,dead)

pics = images()
title_screen()
graveyard = map()
artemis = player(graveyard.get_map())
erebus = necro(graveyard.get_map())

def main():
  audio_player("play","Main")
  while True:
    temp = raw_input(">>> ",)
    if temp == "exit":
      graveyard.get_map().hideFrame()
      audio_player("stop","Main")
      return
    elif temp not in ['w','a','s','d','e','q']:
      print "Invalid input!"
    elif temp == 'e':
      artemis.examine()
    elif temp == 'q':
      artemis.dig()
    else:
      artemis.move(temp)
      erebus.awake()
      if artemis.health == 0:
        audio_player("stop","Main")
        graveyard.get_map().hideFrame()
        game_over()
        return
main()                                                                          