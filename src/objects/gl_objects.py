"""A collection of OpenGL 'objects' that can be rendered in a scene."""
__author__ = "Micah Larson"
__date__   = "$Mar 20, 2011 10:06:47 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

import math
import random

import models
import util

library = models.ModelLibrary()

def init():
    """Initialize the module by loading models."""
    library.init()

class GLObject(object):
    """Encapsulates various properties shared by OpenGL renderables."""
    def __init__(self,
                 translation,
                 rotation,
                 scale,
                 ambient,
                 diffuse,
                 specular,
                 emissive,
                 shininess):
        """Constructor"""
        super(GLObject, self).__init__()
        self.translation = translation
        self.rotation = rotation
        self.scale = scale
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.emissive = emissive
        self.shininess = shininess
    
    def draw(self):
        """Apply properties and call render(), which draws the shapes."""
        glPushAttrib(GL_LIGHTING_BIT)
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT,  self.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE,  self.diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
        glMaterialfv(GL_FRONT, GL_EMISSION, self.emissive)
        
        glMaterialf(GL_FRONT, GL_SHININESS, self.shininess)
        
        glTranslatef(*self.translation) #translate
        glMultMatrixf(self.rotation)    #rotate
        glScalef(*self.scale)           #scale
        
        self.render()
        
        glPopMatrix()
        glPopAttrib()
    
    def render(self):
        """Override this method to render your GLObject."""
        raise NotImplementedError('%s has not yet been implemented' % __name__)


class GLMobileObject(object):
    """Encapsulates various properties shared by mobile (i.e. non-stationary)
    OpenGL renderables.
    
    """
    def __init__(self,
                 speed,
                 translation,
                 rotation,
                 scale,
                 ambient,
                 diffuse,
                 specular,
                 emissive,
                 shininess):
        """Constructor"""
        super(GLMobileObject, self).__init__()
        self.speed = speed
        self.translation = translation
        self.rotation = rotation
        self.scale = scale
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.emissive = emissive
        self.shininess = shininess
    
    def draw(self):
        """Apply properties and call render(), which draws the shapes."""
        glPushAttrib(GL_LIGHTING_BIT)
        glPushMatrix()
        glMaterialfv(GL_FRONT, GL_AMBIENT,  self.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE,  self.diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
        glMaterialfv(GL_FRONT, GL_EMISSION, self.emissive)
        glMaterialf(GL_FRONT, GL_SHININESS, self.shininess)
        
        glTranslatef(*self.translation)    #translate
        glMultMatrixf(self.rotation) #rotate
        glScalef(*self.scale)              #scale
        
        self.render()
        
        glPopMatrix()
        glPopAttrib()
        
    def move(self):
        """Advance position according to current attitude and return position
        delta as a vector.
        
        """
        velocity = [x * self.speed for x in self.rotation[0:3]]
        self.translation = map(sum, zip(self.translation, velocity))
        return velocity
    
    def render(self):
        """Override this method to render your GLObject."""
        raise NotImplementedError('%s has not yet been implemented' % __name__)


class PlasmaBolts(GLMobileObject):
    """The blasts that shoot out of a spacecraft."""
    def __init__(self,
                 speed,
                 translation,
                 rotation,
                 scale=[1.0, 1.0, 1.0],
                 emissive=[0.0, 1.0, 0.0],
                 shininess=0.0):
        """Constructor"""
        super(PlasmaBolts, self).__init__(
                speed,
                translation,
                rotation,
                scale,
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0],
                emissive,
                shininess)
        self.length = 5
    
    def render(self):
        """Draw this PlasmaBolts as a pair of cones."""
        glRotatef(-90.0, 0.0, 1.0, 0.0)
        glTranslatef(-0.7, 0.4, -self.length)
        glutSolidCone(0.1, self.length, 10, 1)
        glTranslatef(0.0, -0.8, 0)
        glutSolidCone(0.1, self.length, 10, 1)


class ParticleField(GLObject):
    """A dispersion of point objects (particles)."""
    def __init__(self,
                 n=10000,
                 mu=0.0,
                 sigma=400,
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
                 shininess=1.0):
        """Constructor"""
        super(ParticleField, self).__init__(translation, rotation, scale,
                ambient, diffuse, specular, emissive, shininess)
        self.build(mu, sigma, n)
    
    def build(self, mu, sigma, n):
        glPushAttrib(GL_LIGHTING_BIT)
        glPushMatrix()
        #set up particle field (locations of particles)
        random.seed()
        d = lambda: random.normalvariate(mu, sigma)
        field = [(d(), d(), d()) for x in xrange(n)]
        
        #create call list for better performance
        self.callList = glGenLists(1)
        glNewList(self.callList, GL_COMPILE)
        glBegin(GL_POINTS)
        for vertex in field:
            glVertex3f(*vertex)
        glEnd()
        glEndList()
        glPopMatrix()
        glPopAttrib()
    
    def render(self):
        """Render this ParticleField using a call list."""
        glCallList(self.callList)


class Asteroid(object):
    """A (real) asteroid loaded from .obj and .mtl files."""
    def __init__(self, name, translation=[0.0, 0.0, 0.0], scale=[1.0, 1.0, 1.0]):
        """Constructor"""
        super(Asteroid, self).__init__()
        self.translation = translation
        self.scale = scale
        self.model = library.models[name]
    
    def draw(self):
        """Draw this Asteroid using a call list."""
        glPushAttrib(GL_LIGHTING_BIT)
        glPushMatrix()
        glTranslatef(*self.translation)
        glScalef(*self.scale)
        glCallList(self.model)
        glPopMatrix()
        glPopAttrib()


class Sphere(GLObject):
    """Texture-ready Sphere, courtesy of Paul Bourke (ported from C):
      http://paulbourke.net/texture_colour/texturemap/
    
    """
    def __init__(self,
                 phi=[],
                 theta=[],
                 applyTexture=False,
                 texture=None,
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
                 shininess=5.0):
        """Constructor"""
        super(Sphere, self).__init__(translation, rotation, scale,
                ambient, diffuse, specular, emissive, shininess)
        self.phi = phi
        self.theta = theta
        self.center = [0.0, 0.0, 0.0]
        self.radius = 1.0
        self.n = 32
        self.applyTexture = applyTexture
        self.texture = texture
        
    def render(self):
        """Render this Sphere in whole or in part, based on phi/theta."""
        if not self.phi or not self.theta:
            self.render_complete()
        else:
            self.render_partial(self.phi, self.theta)
    
    def render_complete(self):
        """Render this Sphere as a series of triangle strips."""
        if self.applyTexture and self.texture is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        for j in range(self.n / 2):
            theta = [j      * 2 * math.pi / self.n - (math.pi / 2),
                    (j + 1) * 2 * math.pi / self.n - (math.pi / 2),
                    0.0]
            glBegin(GL_TRIANGLE_STRIP)
            for i in range(self.n + 1):
                theta[2] = i * 2 * math.pi / self.n
                self.set_point(theta[1], theta[2], i, j + 1)
                self.set_point(theta[0], theta[2], i, j)
            glEnd()
        if self.applyTexture:
            glDisable(GL_TEXTURE_2D)
    
    def render_partial(self, phi, theta):
        """Render a portion of this Sphere as a series of triangle strips."""
        if self.applyTexture and self.texture is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        for j in range(self.n / 2):
            t1 = phi[0] +  j      * (phi[1] - phi[0]) / (self.n / 2)
            t2 = phi[0] + (j + 1) * (phi[1] - phi[0]) / (self.n / 2)
            
            glBegin(GL_TRIANGLE_STRIP)
            for i in range(self.n + 1):
                t3 = theta[0] + i * (theta[1] - theta[0]) / self.n
                self.set_point(t1, t3, i, j)
                self.set_point(t2, t3, i, j + 1)
            glEnd()
        if self.applyTexture:
            glDisable(GL_TEXTURE_2D)
    
    def set_point(self, t0, t1, x, y):
        """Calculate a vertex and normal from t0, t1, x, and y; use them to
        to set glNormal, glTexCoord, and glVertex."""
        normal = [math.cos(t0) * math.cos(t1),
                  math.sin(t0),
                  math.cos(t0) * math.sin(t1)]
        vertex = [self.center[0] + self.radius * normal[0],
                  self.center[1] + self.radius * normal[1],
                  self.center[2] + self.radius * normal[2]]
        glNormal3f(*normal)
        glTexCoord2f(x / float(self.n), 2 * y / float(self.n))
        glVertex3f(*vertex)


class Cylinder(GLObject):
    """Texture-ready cube."""
    def __init__(self,
                 n=8,
                 renderTop=True,
                 renderBottom=True,
                 applyTexture=False,
                 texture=None,
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
                 shininess=5.0):
        """Constructor"""
        super(Cylinder, self).__init__(translation, rotation, scale,
                ambient, diffuse, specular, emissive, shininess)
        self.renderTop = renderTop
        self.renderBottom = renderBottom
        self.applyTexture = applyTexture
        self.texture = texture
        self.n = 16
    
    def render(self):
        """Render this cube as a series of quads."""
        if self.applyTexture and self.texture is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        glPushMatrix()
        
        ends = []
        if self.renderBottom:
            ends.append(-1)
        if self.renderTop:
            ends.append(1)
        
        for j in ends:
            glNormal3d(0, 0, j)
            glBegin(GL_TRIANGLE_FAN)
            glTexCoord2d(0, 0); glVertex3d(0, 0, j)
            for i in range(self.n + 1):
                th = j * i * 360.0 / self.n
                cth = math.cos(math.radians(th))
                sth = math.sin(math.radians(th))
                glTexCoord2d(cth, sth); glVertex3d(cth, sth, j)
            glEnd()
        
        glBegin(GL_QUADS)
        for i in range(self.n):
            th0 =  i    * 360.0 / self.n
            th1 = (i+1) * 360.0 / self.n
            cth0 = math.cos(math.radians(th0))
            sth0 = math.sin(math.radians(th0))
            cth1 = math.cos(math.radians(th1))
            sth1 = math.sin(math.radians(th1))
            glNormal3d(cth0, sth0, 0); glTexCoord2d(0, th0 / 90.0); glVertex3d(cth0, sth0,  1)
            glNormal3d(cth0, sth0, 0); glTexCoord2d(2, th0 / 90.0); glVertex3d(cth0, sth0, -1)
            glNormal3d(cth1, sth1, 0); glTexCoord2d(2, th1 / 90.0); glVertex3d(cth1, sth1, -1)
            glNormal3d(cth1, sth1, 0); glTexCoord2d(0, th1 / 90.0); glVertex3d(cth1, sth1,  1)
        glEnd()
        glPopMatrix()
        
        if self.applyTexture:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)


class Cube(GLObject):
    """Texture-ready cube."""
    def __init__(self,
                 applyTexture=False,
                 texture=None,
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
                 shininess=5.0):
        """Constructor"""
        super(Cube, self).__init__(translation, rotation, scale,
                ambient, diffuse, specular, emissive, shininess)
        self.applyTexture = applyTexture
        self.texture = texture
    
    def render(self):
        """Render this cube as a series of quads."""
        if self.applyTexture and self.texture is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        glBegin(GL_QUADS)
        #  Front
        glNormal3f(0, 0, 1)
        glTexCoord2f(0, 0); glVertex3f(-1, -1, 1)
        glTexCoord2f(1, 0); glVertex3f( 1, -1, 1)
        glTexCoord2f(1, 1); glVertex3f( 1,  1, 1)
        glTexCoord2f(0, 1); glVertex3f(-1,  1, 1)
        #  Back
        glNormal3f(0, 0, -1)
        glTexCoord2f(0, 0); glVertex3f( 1, -1, -1)
        glTexCoord2f(1, 0); glVertex3f(-1, -1, -1)
        glTexCoord2f(1, 1); glVertex3f(-1,  1, -1)
        glTexCoord2f(0, 1); glVertex3f( 1,  1, -1)
        #  Right
        glNormal3f(1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f( 1, -1,  1)
        glTexCoord2f(1, 0); glVertex3f( 1, -1, -1)
        glTexCoord2f(1, 1); glVertex3f( 1,  1, -1)
        glTexCoord2f(0, 1); glVertex3f( 1,  1,  1)
        #  Left
        glNormal3f(-1, 0, 0)
        glTexCoord2f(0, 0); glVertex3f(-1, -1, -1)
        glTexCoord2f(1, 0); glVertex3f(-1, -1,  1)
        glTexCoord2f(1, 1); glVertex3f(-1,  1,  1)
        glTexCoord2f(0, 1); glVertex3f(-1,  1, -1)
        #  Top
        glNormal3f(0, 1, 0)
        glTexCoord2f(0, 0); glVertex3f(-1,  1,  1)
        glTexCoord2f(1, 0); glVertex3f( 1,  1,  1)
        glTexCoord2f(1, 1); glVertex3f( 1,  1, -1)
        glTexCoord2f(0, 1); glVertex3f(-1,  1, -1)
        #  Bottom
        glNormal3f(0, -1, 0)
        glTexCoord2f(0, 0); glVertex3f(-1, -1, -1)
        glTexCoord2f(1, 0); glVertex3f( 1, -1, -1)
        glTexCoord2f(1, 1); glVertex3f( 1, -1,  1)
        glTexCoord2f(0, 1); glVertex3f(-1, -1,  1)
        glEnd()
        
        if self.applyTexture:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)


class Torus(GLObject):
    """Texture-ready cube."""
    def __init__(self,
                 thickness=1.0,
                 n=8,
                 applyTexture=False,
                 texture=None,
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
                 shininess=5.0):
        """Constructor"""
        super(Torus, self).__init__(translation, rotation, scale,
                ambient, diffuse, specular, emissive, shininess)
        self.applyTexture = applyTexture
        self.texture = texture
        self.n = n
        self.thickness = thickness
    
    def render(self):
        """Render this cube as a series of quads."""
        if self.applyTexture and self.texture is not None:
            glEnable(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        glBegin(GL_QUADS)
        r = self.thickness
        for i in range(self.n):
            th0 =  i      * 360.0 / self.n
            th1 = (i + 1) * 360.0 / self.n
            #loop around ring
            for j in range(self.n):
                ph0 =  j      * 360.0 / self.n
                ph1 = (j + 1) * 360.0 / self.n
                cth0 = math.cos(math.radians(th0))
                cth1 = math.cos(math.radians(th1))
                cph0 = math.cos(math.radians(ph0))
                cph1 = math.cos(math.radians(ph1))
                sth0 = math.sin(math.radians(th0))
                sth1 = math.sin(math.radians(th1))
                sph0 = math.sin(math.radians(ph0))
                sph1 = math.sin(math.radians(ph1))
                glNormal3d(cth1*cph0,-sth1*cph0,sph0); glTexCoord2d(th1/30.0,ph0/180.0); glVertex3d(cth1*(1+r*cph0),-sth1*(1+r*cph0),r*sph0)
                glNormal3d(cth0*cph0,-sth0*cph0,sph0); glTexCoord2d(th0/30.0,ph0/180.0); glVertex3d(cth0*(1+r*cph0),-sth0*(1+r*cph0),r*sph0)
                glNormal3d(cth0*cph1,-sth0*cph1,sph1); glTexCoord2d(th0/30.0,ph1/180.0); glVertex3d(cth0*(1+r*cph1),-sth0*(1+r*cph1),r*sph1)
                glNormal3d(cth1*cph1,-sth1*cph1,sph1); glTexCoord2d(th1/30.0,ph1/180.0); glVertex3d(cth1*(1+r*cph1),-sth1*(1+r*cph1),r*sph1)
        glEnd()
        
        if self.applyTexture:
            glBindTexture(GL_TEXTURE_2D, 0)
            glDisable(GL_TEXTURE_2D)


class Axes(GLObject):
    """Positive X, Y, and Z axis (helpful for debug)."""
    def __init__(self,
                 len=100.0, 
                 translation=[0.0, 0.0, 0.0],
                 rotation=[1, 0, 0, 0,
                           0, 1, 0, 0,
                           0, 0, 1, 0,
                           0, 0, 0, 1],
                 scale=[1.0, 1.0, 1.0],
                 ambient=[ 1.0, 1.0, 1.0],
                 diffuse=[ 1.0, 1.0, 1.0],
                 specular=[1.0, 1.0, 1.0],
                 emissive=[1.0, 1.0, 1.0],
                 shininess=120.0):
        """Constructor"""
        super(Axes, self).__init__(translation, rotation, scale, ambient,
                diffuse, specular, emissive, shininess)
        self.axes = {
            'X': [len, 0.0, 0.0],
            'Y': [0.0, len, 0.0],
            'Z': [0.0, 0.0, len]
        }
    
    def render(self):
        """Render this Axes as a series of lines."""
        glBegin(GL_LINES)
        for axis in self.axes.keys():
            glVertex3fv([0.0, 0.0, 0.0])
            glVertex3fv(self.axes[axis])
        glEnd()
        for axis in self.axes.keys():
            util.print_to_scene(axis, position=self.axes[axis]) #label axis
    