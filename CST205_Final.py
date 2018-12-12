# Crypts of Chelon
# By Team SCSI Logic
# Nathan Warren-Acord, Sara Kazemi, Ryan Dorrity, and Cody Young
# Completed for CST 205

# a rougelike game created in JES
# use the console for user input
# w a s d keys are used to move
# e is used to examine a grave
# q is used to dig a grave

# objective is to dig up the target grave before the necromancer gets you
# lose condition: necromancer gets you three times (your health is 0)
# win condition - you dig up the target grave

from time import *
from random import randrange
from thread import *

#Local directory where game files are located.
showInformation("On the next screen, select the CST205_Final_Project directory on your local machine")
file = setMediaPath()
imageFile = file+"/CST205_Final_Images"

coords = {} # Coordinates 

# Soundtrack for the game 
tracks = {
  "Intro" : makeSound(file+"/Piano_Intro.wav"),
  "Main" : makeSound(file+"/Main_Piano.wav"),
  "Game Over" : makeSound(file+"/Game_Over_Full.wav"),
  "Player hit" : makeSound(file+"/Player_Hit.wav"),
  "Necro Laugh" : makeSound(file+"/Necro_Laugh.wav"),
  "Grave Dig Sound" : makeSound(file+"/Grave_Dig_Sound.wav"),
  "Win" : makeSound(file+"/Game_Over_Single_Chord.wav")
}

# get_turtle takes x, y coordinates and w (world) as parameters
def get_turtle(x,y,w):
  t = makeTurtle(w) # creates turtle in this world
  penUp(t) # turtle does not draw a line
  moveTo(t,x,y) # just moves to the specified coords
  return t # retur turtle object

# deletes turtle t in the world w
def remove_turtle(t,w):
  w.getTurtleList().remove(t) 

def coin_toss():
  return randrange(0,2) # used to determine chance of moving extra

def audio_player(mode,track): 
  if mode == "play":
    play(tracks[track])
    return
  stopPlaying(tracks[track])
  return

# returns a sprite to change the background
# given a sprite's key and a position
def change_background(name,position):
  sprite = pics.get_sprite(name)
  map_x = position[0]
  map_y = position[1]
  for x in range(0,getWidth(sprite)):
    for y in range(0,getHeight(sprite)):
      current = getPixel(sprite,x,y)
      if getColor(current) == makeColor(255,174,201):
        setColor(current, getColor(getPixel(graveyard.get_map().getPicture(),map_x,map_y)))
      map_y += 1
    map_y = position[1]
    map_x += 1
  return sprite

# Character superclass inherited by hero and necro
class character:
  # constructor initializes name, position, map, draws sprite to position
  # and initializes a dictionary of moves.
  def __init__(self,map):
    self.name = ""
    self.position = {"x":0,"y":0}
    self.map = map
    self.draw_self(self.position["x"],self.position["y"])
    self.movement = {}
    #self.update_movement()
    
  # draw the character's sprite to background at x, y coordinate
  # using a turtle
  def draw_self(self,x,y):
    #redraw = self.change_background(self.name)
    redraw = change_background(self.name,[x,y])
    sprite = get_turtle(x,y,self.map)
    drop(sprite,redraw)
    remove_turtle(sprite,self.map)
    ##repaint(self.map)
    
  # returns the character's x, y position  
  def get_pos(self):
    return [self.position["x"],self.position["y"]]
  
  # changes the character's x, y posiion  
  def set_position(self,move):
    current = self.position
    current["x"] = move[0]
    current["y"] = move[1]
  #def change_background(self,name):
    #sprite = pics.get_sprite(name)
    #map_x = self.position["x"]
    #map_y = self.position["y"]
    #for x in range(0,getWidth(sprite)):
      #for y in range(0,getHeight(sprite)):
        #current = getPixel(sprite,x,y)
        #if getColor(current) == makeColor(255,174,201):
          #setColor(current, getColor(getPixel(self.map.getPicture(),map_x,map_y)))
        #map_y += 1
      #map_y = self.position["y"]
      #map_x += 1
    #return sprite
    
  # moves sprite on the map by redrawing it
  # checks to see if the movement is valid
  # if it's not, the "wrong way" sprite is displayed instead  
  def move(self,direction):
    path = self.movement[direction]
    open = graveyard.check_valid(path)
    if open is False:
      pic = pics.get_sprite("Wrong Way")
      show(pic)
      sleep(.7)
      pic.getPictureFrame().close()
      return
    self.set_position(self.movement[direction])
    graveyard.reset_map()
    self.map = graveyard.get_map()
    self.draw_self(self.position["x"],self.position["y"])
    self.update_movement()
    #repaint(self.map)
    
  # updates the movement dictionary -- mapping wasd
  # to tile on map.  
  def update_movement(self):
    current = self.get_pos()
    self.movement["w"] = [current[0],current[1]-64]
    self.movement["a"] = [current[0]-64,current[1]]
    self.movement["s"] = [current[0],current[1]+64]
    self.movement["d"] = [current[0]+64,current[1]]

# Player extends character
class player(character):
  def __init__(self,map):
    # initializes instance variables
    self.name = "Player"
    self.health = 3 # health starts at 3
    self.TK = 2
    self.position = {"x":256,"y":512} # starting position on map
    self.map = map
    self.draw_self(self.position["x"],self.position["y"])
    self.movement = {}
    self.update_movement()
    self.health_meter() # draws the appropriate sprite based on health
  
 # draws the appropriate sprite based on health 
  def health_meter(self):
    hearts = get_turtle(64,64,self.map)
    sprite = pics.get_hearts(self.health)
    drop(hearts,sprite)
    remove_turtle(hearts,self.map)
    #repaint(self.map)
  
  # subtracts from health and redraws the hero at a new position
  # if they are still alive    
  def hit(self):
    self.set_position([256,512])
    self.update_movement()
    self.health -= 1
    if self.health >= 1:
      graveyard.reset_map()
      self.map = graveyard.get_map()
      self.draw_self(256,512)
      
  # Turtle draws the arrow sprite facing the direction of
  # the target grave    
  def arrow(self,grave):
    hero = self.get_pos()
    arrow = get_turtle((hero[0]+128),hero[1],self.map)
    #sprite = pics.get_sprite("Arrow")
    #self.change_background()
    turnToFace(arrow,grave[0],grave[1]) # turtle faces direction of target
    redraw = change_background("Arrow",[hero[0]+128,hero[1]]) # arrow drawn near hero
    drop(arrow,redraw)
    remove_turtle(arrow,self.map)
    
  # Examine the grave. Provides a hint arrow in the
  # direction of the correct grave
  def examine(self):
    hero = self.get_pos()
    coords = str(hero[0])+str(hero[1])
    closest = 0
    if coords in gamestate.graves: 
      # Target grave reached
      if gamestate.graves[coords].target == True: 
        return
        
      # We haven't reached the target yet, so search for the target
      # and point to the closest grave between the player and the target     
      else:
        for grave in gamestate.graves.values():
          if grave.target == True:
            if closest == 0:
              closest = grave
            elif closest.grave_distance(hero) > grave.grave_distance(hero):
              closest = grave
        if closest == 0:
          print("Head to the pillar")
          return ##Prompt that tells player to head for the pillar!
        else:
          self.arrow(closest.get_grave_loc())
          
  # dig the grave        
  def dig(self):
    hero = self.get_pos()
    coords = str(hero[0])+str(hero[1]) #needs to convert to string
    # Play the digging sound and drop the open grave sprite
    # as long as we are at a valid grave
    if coords in gamestate.graves:
      if gamestate.graves[coords].dig_grave():
        audio_player("play","Grave Dig Sound")
        grave = get_turtle(hero[0],hero[1],self.map)
        sprite = pics.get_sprite("Open Grave")
        drop(grave,sprite)
        remove_turtle(grave,self.map)
        self.draw_self(hero[0],hero[1])
        if gamestate.graves[coords].target == True:
          win()
        return
      ##Will be a prompt that appears and says "You can't dig there!"
      
    else:
      print self.position ##Will be a prompt that appears and says "You can't dig there!"
"""
 # Updates movement dictionary with wasd keys referring to position values on the map
  def update_movement(self):
    current = self.get_pos()
    self.movement["w"] = [current[0],current[1]-128]
    self.movement["a"] = [current[0]-128,current[1]]
    self.movement["s"] = [current[0],current[1]+128]
    self.movement["d"] = [current[0]+128,current[1]]
"""

# Necro extends character
class necro(character):
  sleeping = True # When sleeping, he's not moving
  visible = True # Can we see him? Spooky!
  
  # Constructor
  def __init__(self,map):
    self.name = "Necro left"
    self.map = map
    self.position = {"x": 1280,"y": 256}
    self.draw_self(self.position["x"],self.position["y"])
    self.movement = {}
    self.update_movement()
  
  # Wakes up the necro if he is sleeping
  # Uses pathfinding to move towards our hero
  def awake(self):
    if self.sleeping:
      self.sleeping = False
      return
    hero = artemis.get_pos()
    path = self.pathfinding(hero)
    self.move(path)
    # Goes back to sleep if he attacks the hero
    if self.attack():
      self.sleeping = True
      return
  
  # Finds a path from the necro to the hero 
  def pathfinding(self,hero):
    path = [[hero[0],hero[1],0]] # path to hero
    found = False # Have we found the path to the hero?
    enemy = self.get_pos()
    counter = 0
    # Pathfinding algorithm to move towards our hero   
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
    found = self.trace_path(found,path) # path to hero
    # Allows necro to move twice towards hero if coin toss is won
    if coin_toss():
      self.move([found[0],found[1]])
      found = found[2]-1
      found = self.trace_path(found,path)
    return [found[0],found[1]]
  
  #     
  def move(self,direction):
    self.set_position(direction)
    graveyard.reset_map()
    self.map = graveyard.get_map()
    self.draw_self(self.position["x"],self.position["y"])
    hero = artemis.get_pos()
    artemis.draw_self(hero[0],hero[1])
    self.update_movement()
    ##repaint(self.map)
    
  # Returns whether or not something is in the Necro's way
  # While traversing the path.  
  def in_path(self, path, tile):
    for item in path:
      if tile[0] == item[0] and tile[1] == item[1] and item[2] <= tile[2]:
        return True
    return False
  
  # Returns a game map tile that is a valid move    
  def trace_path(self,value,path):
    for tile in path:
      adjacent = [tile[0],tile[1]]
      if tile[2] == value and adjacent in self.movement.values():
        return tile
  
  # Attack the hero if close enough, or laugh if almost close enough           
  def attack(self):
    hero = artemis.get_pos()
    enemy = self.get_pos()
    if hero in self.movement.values() or hero == enemy:
      # Play the attack sound
      audio_player("play","Player hit")
      # Lower hero's health and move them to a different coordinate
      artemis.hit()
      return True
    elif abs((hero[0]+hero[1]) - (enemy[0]+enemy[1])) <= 128:
      audio_player("play","Necro Laugh")
      return True ##Don't know about this. Trying it out.
    return False

# Map class
class map:
  coords = {} # dictionary of coordinates
  def __init__(self):
    self.graveyard = makeWorld(1920,1024) # create the world
    # And draw it
    self.graveyard.hideFrame()
    self.graveyard.setPicture(pics.get_sprite("Map base"))
    self.graveyard.showFrame()
    self.set_map()
  
  # returns the map (world)   
  def get_map(self):
    return self.graveyard
  
   # resets the world map   
  def reset_map(self):
    self.graveyard.setPicture(pics.get_sprite("Map base"))
    artemis.health_meter()
    gamestate.print_open_graves()
    if erebus.visible:
      pos = erebus.get_pos()
      erebus.draw_self(pos[0],pos[1])
      
  # Checks to see if coordinates are valid on the map    
  def check_valid(self,check):
    if str(check[0]) in self.coords:
      if check[1] in self.coords[str(check[0])]:
        return True
    return False
    
  def set_TK(self,spot):
    TK = get_turtle(spot[0],spot[1],self.graveyard)
    drop(TK,images.get_sprite(TK))
    self.graveyard.getTurtleList.remove(TK)
  
  # Sets the tiles in the map    
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

# Gamestate class
class Gamestate:

  # Constructor initializes a dictionary of all graves,
  # a list of all the open graves, a list of targets, 
  # and sets the target grave and the map
  def __init__(self,map):
    self.graves = {}
    self.open_graves = []
    self.map = map
    self.undertaker() # ?
    self.targets = []
    self.set_target()

  
  # stretch?  
  def undertaker(self):
    for x in range(384, 1920, 256):
      for y in range(256, 1024, 256):
        self.graves[str(x)+str(y)] = grave(x,y)
  
  # set target graves      
  def set_target(self):
    for i in range(0,2):
      x = randrange(384,1920,256)
      y = randrange(256,1024,256)
      target = self.graves[str(x)+str(y)]
      if target.target is True:
        i -= 1
      else:
        target.target = True
        self.targets.append(target)
  
  # draw open graves if they appear in the list    
  def print_open_graves(self):
    for grave in self.open_graves:
      loc = grave.get_grave_loc()
      hole = get_turtle(loc[0],loc[1],self.map)
      drop(hole,pics.get_sprite("Open Grave"))
      remove_turtle(hole,self.map)
      
  # stretch?    
  def grave_digger(self,gravesite):
    pass
    
# grave class defined by x, y coordinates, whether or not it is the target 
# (grave to be dug up to win) and whether or not it is activated (has been dug up)
class grave:
  # constructor
  def __init__(self, x, y):
    self.position = {"x": x, "y": y} # x, y coordinates on map
    self.activated = False # dug up?
    self.target = False # winning grave?
  
  # returns location on map    
  def get_grave_loc(self):
    return [self.position['x'],self.position['y']]
    
  # checks to see if you can dig up the grave
  # if it's already activated, you cannot  
  def dig_grave(self):
    if self.activated == True:
      return False
    self.activated = True
    gamestate.open_graves.append(self)
    return True
    #if self.target == False:
      #return self.get_grave_loc
    #return False
    #pass
    
  # returns the distance from another grave  
  def grave_distance(self,other):
    self_pos = self.get_grave_loc()
    return abs((self_pos[0]+self_pos[1])-(other[0]+other[1]))
    
# Image object stores all the images for the game map in a dictionary
class images:

  # constructor creates a dictionary. 
  # Keys are Strings that describe a sprite
  # Values are the file path to the sprite
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
      "Open Grave": imageFile+"/Dug_Grave.png",
      "Win": imageFile+"/Win.png"
      #"TK" : imageFile+"",
      #"Ghost" : imageFile+""
    }
    
  #  returns the appropriate health sprite to draw (as a Picture object)
  #  1 heart, 2 hearts, or 3 hearts, based on player's current health 
  def get_hearts(self,health):
    return makePicture(self.library[str(health) + " health"])
    
  # returns a sprite as a Picture object, given its key  
  def get_sprite(self,sprite):
    return makePicture(self.library[sprite])

# Starts the game and awaits user input
def game_start(check):
  raw_input()
  check.append(None)

# Displays title screen
def title_screen():
  check = []
  # run game_start function in new thread
  # exits when user presses Enter and None is returned
  start_new_thread(game_start, (check,)) 
  # Create title screen in our game window
  title = makeWorld(1920,1024)
  screen_one = get_turtle(0,0,title)
  screen_two = get_turtle(0,0,title)
  drop(screen_one,pics.get_sprite("Title 1"))
  audio_player("play","Intro") # play intro song
  remove_turtle(screen_one,title)
  while not check:
    # Keep looping the turtles dropping our two title
    # Screen images (sleeping for half a second between drops)
    # This creates an effect of "Press Enter" flashing
    sleep(.5)
    drop(screen_two,pics.get_sprite("Title 2"))
    # We're done with you, turtle, go away!
    remove_turtle(screen_two,title)
    sleep(.5)
    drop(screen_one,pics.get_sprite("Title 1"))
    # We're done with you, turtle, go away!
    remove_turtle(screen_one,title)
  # hide the title screen after the user presses Enter
  title.hideFrame()
  # Stop the intro music after the user presses Enter
  audio_player("stop","Intro") 

def game_over():
  # Create the game over screen in our window
  dead = makeWorld(1920,1024)
  screen = get_turtle(0,0,dead)
  # Draw the Game over image to the world
  drop(screen,pics.get_sprite("Game Over"))
  # Play game over music
  audio_player("play","Game Over")
  # We're done with you, turtle, go away!
  remove_turtle(screen,dead)
  
def win():
  champ = makeWorld(1920,1024)
  screen = get_turtle(0,0,champ)
  audio_player("stop","Main") # game over. stop playing music
  graveyard.get_map().hideFrame() # hide the frame
  # Draw the Win image to the world
  drop(screen,pics.get_sprite("Win"))
  # Play Win music
  audio_player("play","Win")
  audio_player("play","Necro Laugh")
  # We're done with you, turtle, go away!
  remove_turtle(screen,champ)
  quit()

pics = images() # constructs an image object (dictionary of game map images)
title_screen() # constructs the title screen (two images repeatedly dropped)
graveyard = map() # constructs the map
gamestate = Gamestate(graveyard.get_map()) # gets the state of our game
artemis = player(graveyard.get_map())  # constructs our hero
erebus = necro(graveyard.get_map())    # constructs our foe

# Runs the game after the title screen thread is exited
def main():
  audio_player("play","Main") # play the main bg music
  while True: 
    temp = raw_input(">>> ",) # wait for user input
    if temp == "exit": # exit game by hiding the frame and stopping music
      graveyard.get_map().hideFrame()
      audio_player("stop","Main")
      return
    elif temp not in ['w','a','s','d','e','q']: # only allowable "moves"
      print "Invalid input!"
    elif temp == 'e': # examine the grave
      artemis.examine()
    elif temp == 'q': # dig the grave
      artemis.dig()
    else:
      artemis.move(temp) # try to move in the direction indicated by wasd
      erebus.awake() # necro's turn
      if artemis.health == 0: # lose condition
        audio_player("stop","Main") # game over. stop playing music
        graveyard.get_map().hideFrame() # hide the frame
        game_over() # bye-bye
        return
main()                      