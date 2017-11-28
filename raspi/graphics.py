## graphics.py ##
## a few screen rendering-related classes ##

from geom import Point

from pygame import Surface
from pygame.sprite import Sprite
import pygame.image
import pygame.display
import pygame.draw

class Background (pygame.sprite.Sprite):

  # create a background image using Background("bg.jpg", [0,0])
  def __init__(self, image_file, coords, scale=(800,480)):
    # call the parent's initialization
    pygame.sprite.Sprite.__init__(self)
    # load the image
    self.image = pygame.image.load(image_file)
    self.image = pygame.transform.scale(self.image, scale )
    # set the image's coordinates on screen
    self.rect = self.image.get_rect()
    self.rect.left, self.rect.top = coords

  # draw the background on the given screen
  def draw (self, display):
    display.blit(self.image, self.rect)

class Transparent_Circle:
  def __init__(self, x=0, y=0, r=5):
    self.pos = Point(x,y)
    self.radius = r

  def move_to (self, x, y):
    self.pos.move_to(x,y)

  def set_radius (r):
    self.radius = r

  def draw  (self, display):
    # create a drawing surface
    s = pygame.Surface((800,480))

    # make it empty
    s.fill ( (0,0,0) )
    s.set_colorkey ( (0,0,0) )

    # create the circle
    r = pygame.draw.circle (s, (246,255,170), (self.pos.get_x(),self.pos.get_y()), self.radius)

    # render it
    s.set_alpha (75)
    display.blit(s, (0, 0) )

class Cross:
  def __init__ (self, x=0, y=0, r=5):
    self.pos = Point(x,y)
    self.radius = r

  def move_to (self, x, y):
    self.pos.move_to(x,y)

  def set_radius (self, r):
    self.radius = r

  def draw (self, display):
    xc = self.pos.get_x()
    xs = xc - self.radius
    xe = xc + self.radius
    yc = self.pos.get_y()
    ys = yc - self.radius
    ye = yc + self.radius

    s = pygame.Surface((800,480))
    s.fill( (0,0,0) )
    s.set_colorkey( (0,0,0) )
    # horizontal line
    pygame.draw.line(s, (255,0,0),(xs,yc),(xe,yc),4)
    # vertical line
    pygame.draw.line(s, (255,0,0),(xc,ys),(xc,ye),4)
    display.blit(s, (0,0) )

class Rectangle:
  def __init__ (self, x,y,w,h, text=None, color=(255,255,255) ):
    self.pos = Point(x,y)
    self.width  = w
    self.height = h
    self.text   = text
    self.color  = color
    if not (text is None):
      self.font = pygame.font.SysFont(None,24)

  def contains (self, coords):
    x = self.pos.get_x()
    y = self.pos.get_y()

    if  (x < coords[0] < x + self.width) and (y < coords[1] < y + self.height):
      return True
    # else
    return False

  def set_color (self, color):
    self.color = color

  def move_to (self, x, y):
    self.pos.move_to(x,y)

  def get_width (self):
    return self.width

  def set_width (self, w):
    self.width = w

  def set_height (self, h):
    self.height = h

  def get_height (self):
    return self.height

  def draw (self, display):
    s = pygame.Surface((800,480))
    s.fill( (0,0,0) )
    s.set_colorkey( (0,0,0) )
    pygame.draw.rect(s, self.color, (self.pos.get_x(),self.pos.get_y(),self.width,self.height) )
    display.blit(s, (0,0) )
    if not (self.text is None):
      # create a surface with the text, antialiased, and black
      words = self.font.render(self.text, True, (0,0,0) )
      word_rect = words.get_rect()
      # override the location of the text surface bounding box
      word_rect[0] = self.pos.get_x()
      word_rect[1] = self.pos.get_y()
      # render the text onto the main display
      display.blit(words, words_rect)

