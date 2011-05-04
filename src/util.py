"""Methods to support general graphics features."""
__author__ = "Micah Larson"
__date__   = "$Mar 26, 2011 4:31:51 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

import math

def print_to_screen(text, color=[0.5, 1.0, 0.5], position=[2, 2]):
    """Print text to the specified 2D position on the screen (window)."""
    glPushMatrix()
    glWindowPos2i(*position)
    print_text(text, color)
    glPopMatrix()

def print_to_scene(text, color=[1.0, 1.0, 1.0], position=[0, 0, 0]):
    """Print text to the specified 3D position in the scene."""
    glPushMatrix()
    glRasterPos3d(*position)
    print_text(text, color)
    glPopMatrix()

def print_text(text, color):
    """Set color and print text."""
    glColor3fv(color)
    for char in text:
        glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(char))
        
def upper_power_of_two(number):
    """Return the power of 2 greater than or equal to the input number."""
    return 2**math.ceil(math.log(number, 2))
