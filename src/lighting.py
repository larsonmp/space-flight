"""Lighting settings."""
__author__ = "Micah Larson"
__date__   = "$Mar 28, 2011 9:35:17 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

class Light:
    """An OpenGL light source."""
    DIRECTIONAL = 0.0  #infinitely far away
    POSITIONAL = 1.0   #"in scene"
    
    def __init__(self, id,
                 position=[0.0, 0.0, 0.0],
                 type=DIRECTIONAL,
                 ambient=[ 1.0, 1.0, 1.0],
                 diffuse=[ 1.0, 1.0, 1.0],
                 specular=[1.0, 1.0, 1.0]):
        """Constructor"""
        self.id = id
        self.position = position
        self.type = type
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
    
    def init(self):
        """Set up and enable this light."""
        self.commit_properties()
        self.enable()
    
    def commit_properties(self):
        """Commit the properties of this light to OpenGL state."""
        glLightfv(self.id, GL_AMBIENT, self.ambient)
        glLightfv(self.id, GL_DIFFUSE, self.diffuse)
        glLightfv(self.id, GL_SPECULAR, self.specular)
        glLightfv(self.id, GL_POSITION, self.position + [self.type])
    
    def enable(self, on=True):
        """Enable/disable this light."""
        if on:
            glEnable(self.id)
        else:
            glDisable(self.id)
