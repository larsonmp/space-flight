"""The skybox provides the "backround" for the scene."""
__author__ = "Micah Larson"
__date__   = "$Mar 20, 2011 10:43:20 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

import math

def draw_skybox(translation, bounds):
    """Draw a box surrounding the scene using the current texture in the
    cube map.
    
    """
    scale = math.sqrt(bounds**2 / 3) #scale to just within bounds
    
    planes = (
        ([ 1,  1,  1], [ 1,  1, -1], [ 1, -1, -1], [ 1, -1,  1]), #POSITIVE X
        ([-1,  1,  1], [-1,  1, -1], [ 1,  1, -1], [ 1,  1,  1]), #POSITIVE Y
        ([-1,  1,  1], [ 1,  1,  1], [ 1, -1,  1], [-1, -1,  1]), #POSITIVE Z
        ([-1, -1,  1], [-1, -1, -1], [-1,  1, -1], [-1,  1,  1]), #NEGATIVE X
        ([ 1, -1,  1], [ 1, -1, -1], [-1, -1, -1], [-1, -1,  1]), #NEGATIVE Y
        ([ 1,  1, -1], [-1,  1, -1], [-1, -1, -1], [ 1, -1, -1])) #NEGATIVE Z
    
    glPushAttrib(GL_LIGHTING_BIT)
    glPushMatrix()
    glTranslatef(*translation)
    glMaterialfv(GL_FRONT, GL_EMISSION, [1.0, 1.0, 1.0])
    
    glEnable(GL_TEXTURE_CUBE_MAP)
    for plane in planes:
        glBegin(GL_QUADS)
        for vertex in plane:
            vector = [scale * point for point in vertex]
            glTexCoord3fv(vertex); glVertex3fv(vector)
        glEnd()
    glDisable(GL_TEXTURE_CUBE_MAP)
    glPopMatrix()
    glPopAttrib()
