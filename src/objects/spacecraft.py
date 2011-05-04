"""Module for spacecraft models (hand-built)."""
__author__ = "Micah Larson"
__date__   = "Apr 22, 2011 7:21:13 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

import itertools
import math

import gl_objects
import textures

class TIEFighter(gl_objects.GLMobileObject):
    """Twin Ion Engine (TIE) Fighter, the basic unit of the Imperial Fleet."""
    def __init__(self,
                 speed=1.0,
                 ambient=[1.0, 1.0, 1.0],
                 diffuse=[0.3, 0.3, 0.3],
                 specular=[1.0, 1.0, 1.0],
                 shininess=30.0):
        """Constructor"""
        super(TIEFighter, self).__init__(
                speed=speed,
                translation=[0.0, 0.0, 0.0],
                rotation=[1, 0, 0, 0,
                          0, 1, 0, 0,
                          0, 0, 1, 0,
                          0, 0, 0, 1],
                scale=[1.0, 1.0, 1.0],
                ambient=ambient,
                diffuse=diffuse,
                specular=specular,
                emissive=[0.0, 0.0, 0.0],
                shininess=shininess)
        self.agility = 5
        
        self.build()
    
    def build(self):
        """Render the spacecraft with primitive shapes."""
        glPushAttrib(GL_LIGHTING_BIT)
        glPushMatrix()
        
        #create call list for better performance
        self.callList = glGenLists(1)
        glNewList(self.callList, GL_COMPILE)
        
        #command pod
        glPushMatrix()
        glRotatef(90.0, 0.0, 0.0, 1.0)
        gl_objects.Sphere([-math.pi * 0.3, math.pi / 2], [0, math.pi * 2]).draw()
        glPopMatrix()
        
        glPushMatrix()
        glRotatef(90.0, 0.0, 1.0, 0.0)
        gl_objects.Cylinder(32, False, True, ambient=[0.0, 0.0, 0.0],
                diffuse=[0.0, 0.0, 0.0], specular=[0.0, 0.0, 0.0],
                scale=[0.6, 0.6, 0.8]).draw()
        glPopMatrix()
        
        #viewport
        glPushMatrix()
        glTranslatef(0.8, 0.0, 0.0)
        glRotatef(90.0, 0.0, 1.0, 0.0)
        gl_objects.Torus(0.1, 8, False, None, scale=[0.2, 0.2, 0.2]).draw() #inner
        gl_objects.Torus(0.05, 32, False, None, scale=[0.6, 0.6, 0.6]).draw() #outer
        glPopMatrix()
        
        glPushMatrix()
        glTranslatef(0.8, 0.0, 0.0)
        glRotatef(90.0, 0.0, 0.0, 1.0)
        for x in range(8):
            glPushMatrix()
            glTranslatef(0.0, 0.0, 0.2)
            gluCylinder(gluNewQuadric(), 0.02, 0.02, 0.4, 16, 4)
            glPopMatrix()
            glRotatef(45.0, 0.0, 1.0, 0.0)
        glPopMatrix()
        
        #blasters
        for yCoord in (-0.4, 0.4):
            glPushMatrix()
            glRotatef(90.0, 0.0, 1.0, 0.0)
            glTranslatef(0.7, yCoord, 0.0)
            gluCylinder(gluNewQuadric(), 0.05, 0.025, 0.8, 25, 1)
            glPopMatrix()
        
        #wings
        for angle in (-90.0, 90.0):
            glPushMatrix()
            glRotatef(angle, 0.0, 0.0, 1.0)
            glTranslatef(2.0, 0.0, 0.0)
            
            glPushMatrix()
            glRotatef(-90.0, 0.0, 1.0, 0.0)
            gluCylinder(gluNewQuadric(), 0.25, 0.25, 1.0, 25, 4) #pylon
            glPopMatrix()
            
            Wing().draw() #panel
            glPopMatrix()
        
        #engines
        for angle in (-30.0, 30.0):
            glPushMatrix()
            glRotatef(angle, 0.0, 0.0, 1.0)
            glTranslatef(-1.0, 0.0, 0.0)
            Engine().draw()
            glPopMatrix()
        
        glEndList()
        glPopMatrix()
        glPopAttrib()
    
    def render(self):
        """Render this TIE fighter using a call list."""
        glCallList(self.callList)
    
    def turn(self, direction, modifiers):
        """Turn the spacecraft based on key input."""
        if direction in (GLUT_KEY_DOWN, GLUT_KEY_RIGHT):
            theta = -self.agility
        else:
            theta = self.agility
        if direction in (GLUT_KEY_UP, GLUT_KEY_DOWN):
            rotation = [theta] + self.rotation[4:7]
        elif direction in (GLUT_KEY_LEFT, GLUT_KEY_RIGHT):
            if modifiers & GLUT_ACTIVE_CTRL:
                rotation = [theta] + [-n for n in self.rotation[0:3]]
            else:
                rotation = [theta] + self.rotation[8:11]
        else:
            print >> sys.stderr, 'invalid direction'
        
        #apply attitude adjustment
        glPushMatrix()
        glLoadIdentity()
        glRotatef(*rotation)
        glMultMatrixf(self.rotation)
        self.rotation = list(itertools.chain(*glGetFloatv(GL_MODELVIEW_MATRIX)))
        glPopMatrix()


class Engine(gl_objects.GLObject):
    """Ion Engine, One of Two"""
    def __init__(self,
                 translation=[0.0, 0.0, 0.0],
                 rotation=[1, 0, 0, 0,
                           0, 1, 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 1],
                 scale=[1.0, 1.0, 1.0],
                 ambient=[ 0.0, 0.0, 0.0],
                 diffuse=[ 0.0, 0.0, 0.0],
                 specular=[0.0, 0.0, 0.0],
                 emissive=[1.0, 0.0, 0.0],
                 shininess=0.0):
        """Constructor"""
        super(Engine, self).__init__(translation, rotation, scale, ambient,
                diffuse, specular, emissive, shininess)
    
    def render(self):
        """Render this Engine as a primitive sphere."""
        glPushMatrix()
        glutSolidSphere(0.05, 10, 10)
        glPopMatrix()

class Wing(gl_objects.GLObject):
    """Hexagonal wing that gives TIE fighters their characteristic look."""
    def __init__(self,
                 translation=[0.0, 0.0, 0.0],
                 rotation=[1, 0, 0, 0,
                           0, 1, 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 1],
                 scale=[1.0, 1.0, 1.0],
                 ambient=[ 1.0, 1.0, 1.0],
                 diffuse=[ 1.0, 1.0, 1.0],
                 specular=[1.0, 1.0, 1.0],
                 emissive=[0.0, 0.0, 0.0],
                 shininess=120.0):
        """Constructor"""
        super(Wing, self).__init__(translation, rotation, scale, ambient,
                diffuse, specular, emissive, shininess)
        self.polygonVertices = [
           [0.0,  0.0,  0.0], #center
           [0.0, -1.5,  3.0], #upper  left
           [0.0, -2.0,  0.0], #middle left
           [0.0, -1.5, -3.0], #lower  left
           [0.0,  1.5, -3.0], #lower  right
           [0.0,  2.0,  0.0], #middle right
           [0.0,  1.5,  3.0], #upper  right
           [0.0, -1.5,  3.0]  #upper  left (again, completing the fan)
        ]
        self.textureVertices = [
            [0.5, 0.5], #center
            [0.0, 1.0], #upper  left
            [0.0, 0.5], #middle left
            [0.0, 0.0], #lower  left
            [1.0, 0.0], #lower  right
            [1.0, 0.5], #middle right
            [1.0, 1.0], #upper  right
            [0.0, 1.0]  #upper  left (again, completing the fan)
        ]
        
    def render_panel(self, polygonVertices, textureVertices):
        """Render a large, flat hexagon (an inner/outer panel of this Wing."""
        glBegin(GL_TRIANGLE_FAN)
        glNormal3f(-1.0, 0.0, 0.0)
        for index in range(len(polygonVertices)):
            glTexCoord2f(*textureVertices[index])
            glVertex3f(*polygonVertices[index])
        glEnd()
    
    def render(self):
        """Render this Wing in 3 parts: inner panel, outer panel, edge."""
        glPushMatrix()
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, textures.textures['wing'])
        glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        self.render_panel(self.polygonVertices, self.textureVertices) #inner
        glTranslatef(0.1, 0.0, 0.0)
        glRotatef(180.0, 0.0, 0.0, 1.0)
        self.render_panel(self.polygonVertices, self.textureVertices) #outer
        glBindTexture(GL_TEXTURE_2D, 0)
        glPopMatrix()
        
        #edge
        glPushMatrix()
        v = self.polygonVertices + [self.polygonVertices[0]]
        edges = lambda v: itertools.izip(v,
                [(x + 0.1, y, z) for (x, y, z) in v])
        glBegin(GL_QUAD_STRIP)
        for vertex in [a for b in edges(v) for a in b]:
            glVertex3f(*vertex);
        glEnd()
        glDisable(GL_TEXTURE_2D)
        glPopMatrix()
