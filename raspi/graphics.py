from geom import Point

from pygame import Surface
from pygame.sprite import Sprite
import pygame.image
import pygame.display
import pygame.draw

class Background (pygame.sprite.Sprite):

  # create a background image using Background("bg.jpg", [0,0])
  def __init__(self, image_file, coords):
    # call the parent's initialization
    pygame.sprite.Sprite.__init__(self)
    # load the image
    self.image = pygame.image.load(image_file)
    self.image = pygame.transform.scale(self.image, (800,480) )
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
    self.pos.inst_move_to(x,y)

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
