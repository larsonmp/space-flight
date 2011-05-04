#!/bin/env python
"""Launch point for SpaceFlight."""
__author__ = "Micah Larson"
__date__   = "$Mar 20, 2011 4:25:31 PM$"

from OpenGL.GL import *                     #@UnusedWildImport
from OpenGL.GLU import *                    #@UnusedWildImport
from OpenGL.GLUT import *                   #@UnusedWildImport
from OpenGL.GL.framebufferobjects import *  #@UnusedWildImport

import math
import platform

import coordinates
import lighting
from objects import gl_objects, spacecraft
import skybox
import textures
import util


class SpaceFlight(object):
    """Main class."""
    def __init__(self, debug=False):
        """Set initial conditions."""
        super(SpaceFlight, self).__init__()
        #window
        self.title = 'Space Flight'
        self.width = 640
        self.height = 480
        
        #viewer orientation
        self.camera = [-10.0, 0.0, 0.0]
        self.center = [  0.0, 0.0, 0.0]
        self.up     = [  0.0, 0.0, 1.0]
        self.minCameraDistance =  10.0
        self.maxCameraDistance = 100.0
        self.firstPersonMode = False
        
        #UI
        self.mousePosition = [0.0, 0.0]
        self.moveMode = 'NONE'
        
        #lighting
        self.lightingDefaults = {
            'position': [0.0, 999.0, 0.0],
            'ambient':  [0.1, 0.1, 0.1], #space is dark
            'diffuse':  [1.0, 0.9, 0.8], #slight orange
            'specular': [1.0, 0.8, 0.2]  #more orange
        }
        self.lights = {
            'primary': lighting.Light(
                           GL_LIGHT0,
                           position=self.lightingDefaults['position'],
                           ambient=self.lightingDefaults['ambient'],
                           diffuse=self.lightingDefaults['diffuse'],
                           specular=self.lightingDefaults['specular'])
        }
        
        #shadows
        self.MultiTex = True
        self.shadowdim = 512
        self.Sdim = self.shadowdim
        self.Tdim = self.shadowdim
        self.ambienceNotSupported = False
        self.frameBufferID = 0
        self.S = []   #texture plane S
        self.T = []   #texture plane T
        self.R = []   #texture plane R
        self.Q = []   #texture plane Q
        
        #perspective
        self.zNear = 1.0
        self.zFar = 2000.0
        
        #objects
        self.spacecraft = None
        self.bolts = []
        self.scenery = []
        self.particles = None
        self.axes = None
        
        #miscellaneous
        self.debug = debug
        self.drawAxes = False
        self.dt = 50 #number of milliseconds between calls to glutTimerFunc
        self.plasmaBoltSpeed = 5.0
        
        #rendering shadows for the particles requires better hardware than is
        #available to me
        self.shadowedParticles = False
    
    def draw_objects(self):
        """Draw the objects in self.scenery."""
        try:
            for object in self.scenery:
                object.draw()
        except AttributeError as error:
            print >> sys.stderr, 'Invalid object: %s' % error
                
    def fire_blasters(self):
        """Append a pair of plasma bolts to self.bolts."""
        self.bolts.append(gl_objects.PlasmaBolts(self.plasmaBoltSpeed,
                self.spacecraft.translation, self.spacecraft.rotation))
    
    def diff(self, x, y):
        return x - y
    
    def adjust_camera(self, ds):
        """Move the camera based on position delta ds, spacecraft location,
        and camera mode (1st person or 3rd person)."""
        if self.firstPersonMode:
            self.camera = map(self.diff, self.spacecraft.translation,
                    [n *  0.5 for n in ds])
            self.center = map(self.diff, self.spacecraft.translation,
                    [n * -1 for n in ds])
            self.up = self.spacecraft.rotation[8:11]
        else:
            self.camera = map(sum, zip(self.camera, ds))
            self.center = map(sum, zip(self.center, ds))
    
    def timer(self, value):
        """Called when time triggers."""
        #update spacecraft position; ds is position delta as vector
        ds = self.spacecraft.move()
        
        #update position of camera and focal point (center) using ds
        self.adjust_camera(ds)
        
        for bolt in self.bolts:
            if coordinates.distance(*bolt.translation) > self.zFar:
                self.bolts.remove(bolt)
            else:
                bolt.move()
        
        self.draw_shadow_map()
        
        glutPostRedisplay()
        glutTimerFunc(self.dt, self.timer, value)
    
    def toggle_axes(self):
        """Toggle in-scene (x, y, z) axes."""
        self.drawAxes = not self.drawAxes
        
    def toggle_debug(self):
        """Toggle on-screen debug printouts."""
        self.debug = not self.debug
    
    def toggle_camera_mode(self):
        """Toggle 1st-person / 3rd-person mode."""
        self.firstPersonMode = not self.firstPersonMode
        if not self.firstPersonMode:
            #reset camera orientation for 3rd-person mode
            self.center = self.spacecraft.translation
            self.camera = map(self.diff, self.center,
                    [n * 10 for n in self.spacecraft.rotation[0:3]])
            self.up = [0.0, 0.0, 1.0]
        
    def toggle_particle_shadows(self):
        """Toggle whether particles cast shadows."""
        self.shadowedParticles = not self.shadowedParticles
    
    def init_scene(self):
        """Initialize lighting, textures, etc."""
        glEnable(GL_NORMALIZE)
        glEnable(GL_POLYGON_SMOOTH)
        glShadeModel(GL_SMOOTH)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glDisable(GL_COLOR_MATERIAL)
        glClearColor(0.0, 0.0, 0.0, 1.0)
        
        #enable Z-buffer
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glPolygonOffset(4, 0)
        
        #initialize textures
        textures.init()
        
        #initialize objects
        gl_objects.init()
        
        #place objects in scene
        self.scenery.append(gl_objects.Asteroid('bacchus',
                translation=[-100.0, -300.0, 200.0],
                scale=[30.0, 30.0, 30.0]))
        
        self.scenery.append(gl_objects.Asteroid('castalia',
                translation=[0.0, 30.0, -70.0],
                scale=[10.0, 10.0, 10.0]))
        
        self.scenery.append(gl_objects.Asteroid('geographos',
                translation=[-100.0, -300.0, -300.0],
                scale=[50.0, 50.0, 50.0]))
        
        self.scenery.append(gl_objects.Asteroid('golevka',
                translation=[100.0, 150.0, 100.0],
                scale=[30.0, 30.0, 30.0]))
        
        self.scenery.append(gl_objects.Asteroid('kleopatra',
                translation=[-120.0, -150.0, -280.0],
                scale=[20.0, 20.0, 20.0]))
        
        self.scenery.append(gl_objects.Asteroid('ky26',
                translation=[400.0, -20.0, 200.0],
                scale=[400.0, 400.0, 400.0]))
        
        self.scenery.append(gl_objects.Asteroid('toutatis',
                translation=[200.0, -200.0, 30.0],
                scale=[50.0, 50.0, 50.0]))
        
        self.scenery.append(gl_objects.Asteroid('bacchus',
                translation=[-400.0, 400.0, -200.0],
                scale=[50.0, 50.0, 50.0]))
        
        self.scenery.append(gl_objects.Asteroid('ky26',
                translation=[-20.0, -20.0, 30.0],
                scale=[300.0, 300.0, 300.0]))
        
        self.scenery.append(gl_objects.Asteroid('golevka',
                #translation=[-100.0, 200.0, -300.0],
                translation=[-50.0, -100.0, -250.0],
                scale=[150.0, 150.0, 150.0]))
        
        self.scenery.append(gl_objects.Asteroid('castalia',
                translation=[300.0, 100.0, -100.0],
                scale=[50.0, 50.0, 50.0]))
        
        self.scenery.append(gl_objects.Asteroid('geographos',
                translation=[200.0, 300.0, 300.0],
                scale=[30.0, 30.0, 30.0]))
        
        self.scenery.append(gl_objects.Asteroid('kleopatra',
                translation=[-100.0, 500.0, 100.0],
                scale=[150.0, 150.0, 150.0]))
        
        self.scenery.append(gl_objects.Sphere([], [], True,
                textures.textures['earth'],
                translation=[-100.0, 500.0, 100.0],
                scale=[10.0, 10.0, 10.0],
                emissive=[1.0, 1.0, 1.0]))
        
        self.spacecraft = spacecraft.TIEFighter()
        self.particles = gl_objects.ParticleField(sigma=500)
        
        self.axes = gl_objects.Axes()
        
        self.init_lighting()
        
        self.init_shadow_map()
    
    def init_shadow_map(self):
        """Initialize the shadow map."""
        #see if multi-textures are supported
        self.MultiTex = (glGetIntegerv(GL_MAX_TEXTURE_UNITS) > 1)
        
        #limit texture size to smallest of buffer size, texture size, and 4096
        self.shadowdim = min(glGetIntegerv(GL_MAX_TEXTURE_SIZE),
            glGetIntegerv(GL_MAX_RENDERBUFFER_SIZE_EXT), 4096)
        
        self.init_shadow_textures()
        
        #only use framebuffer if it is big enough
        if self.shadowdim > 512:
            powerOfTwo = util.upper_power_of_two(self.shadowdim)
            self.Sdim = self.Tdim = self.shadowdim = powerOfTwo
            
            self.frameBufferID = glGenFramebuffersEXT(1)
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.frameBufferID)
            
            #set render buffer size to shadow map
            renderBufferID = glGenRenderbuffersEXT(1)
            glBindRenderbufferEXT(GL_RENDERBUFFER_EXT, renderBufferID)
            glRenderbufferStorageEXT(GL_RENDERBUFFER_EXT, GL_DEPTH_COMPONENT32,
                int(self.shadowdim), int(self.shadowdim))
            glFramebufferRenderbufferEXT(GL_FRAMEBUFFER_EXT,
                GL_DEPTH_ATTACHMENT_EXT, GL_RENDERBUFFER_EXT, renderBufferID)
            
            glDrawBuffer(GL_NONE) #don't write to visible color
            glReadBuffer(GL_NONE) #don't read from visible color
            
            #sanity check (bail on fail)
            status = glCheckFramebufferStatusEXT(GL_FRAMEBUFFER_EXT)
            if status != GL_FRAMEBUFFER_COMPLETE_EXT:
                raise Exception('Error setting up frame buffer')
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
            
            self.draw_shadow_map() #create shadow map
        else:
            #set shadow dim to maximum
            self.shadowdim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
            print >> sys.stderr, 'Insufficient framebuffer'
    
    def init_shadow_textures(self):
        """Initialize textures used in shadow map."""
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE1)
        #allocate and bind shadow texture
        glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
        shadowtex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, shadowtex)
        
        #map single depth value to RGBA (this is called intensity)
        glTexParameteri(GL_TEXTURE_2D, GL_DEPTH_TEXTURE_MODE, GL_INTENSITY)
        
        #check if ambient shadows are supported
        try:
            glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_FAIL_VALUE_ARB, 0.5)
        except Exception:
            self.ambienceNotSupported = True
        self.ambienceNotSupported = True
        
        #texture modulate underlying objects
        glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE)
        
        #set texture mapping to clamp and linear interpolation
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        
        #set automatic texture generation mode to Eye Linear
        glTexGeni(GL_S, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGeni(GL_T, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGeni(GL_R, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        glTexGeni(GL_Q, GL_TEXTURE_GEN_MODE, GL_EYE_LINEAR)
        
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE0)
    
    def draw_shadow_map(self, bounds=1000.0):
        """Draw the shadow map.  This needs to be called whenever any object or
        light moves.
        
        @param bounds bounding radius of scene
        
        TODO: support multiple lights
        
        """
        #save transforms and modes
        glPushMatrix()
        glPushAttrib(GL_TRANSFORM_BIT | GL_ENABLE_BIT | GL_VIEWPORT_BIT)
        
        glShadeModel(GL_FLAT)   #no smoothing
        glColorMask(0, 0, 0, 0) #no writing to color buffer
        glEnable(GL_POLYGON_OFFSET_FILL) #overcome imprecision
        
        #turn off lighting
        self.enable_lighting(False)
        
        #distance of light from origin, ensuring it's out of bounds
        lightPos = self.lights['primary'].position
        lightDistance = max(coordinates.distance(*lightPos[0:3]), 1.1 * bounds)
        
        #set perspective view from light position
        self.set_perspective(float(self.Sdim), float(self.Tdim),
                lightDistance - bounds, lightDistance + bounds,
                60.0 * math.atan(bounds / lightDistance))
        gluLookAt(*(lightPos + self.center + self.up))
        
        #size viewport to desired dimensions
        glViewport(0, 0, int(self.Sdim), int(self.Tdim))
        
        #redirect traffic to the frame buffer
        if self.frameBufferID > 0:
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, self.frameBufferID)
        
        #clear the depth buffer
        glClear(GL_DEPTH_BUFFER_BIT)
        self.draw_objects() #draw all objects that can cast a shadow
        if self.shadowedParticles:
            self.particles.draw()
        self.spacecraft.draw()
        
        #copy depth values into depth texture
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE1)
        glCopyTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT, 0, 0,
            int(self.Sdim), int(self.Tdim), 0)
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE0)
        
        #retrieve light projection and modelview matrices
        lightProjectionMatrix = glGetDoublev(GL_PROJECTION_MATRIX)
        lightModelviewMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        
        #set up texture matrix for shadow map projection, which will be rolled
        #  into the eye linear texture coordinate generation plane equations
        glLoadIdentity()
        glTranslated(0.5, 0.5, 0.5)
        glScaled(0.5, 0.5, 0.5)
        glMultMatrixd(lightProjectionMatrix)
        glMultMatrixd(lightModelviewMatrix)
        
        #retrieve result and transpose to get the s, t, r, and q rows for
        #  plane equations
        #textureProjectionMatrix: | S1 T1 R1 Q1 |
        #                         | S2 T2 R2 Q2 |
        #                         | S3 T3 R3 Q3 |
        #                         | S4 T4 R4 Q4 |
        textureProjectionMatrix = glGetDoublev(GL_MODELVIEW_MATRIX)
        self.S = [row[0] for row in textureProjectionMatrix]
        self.T = [row[1] for row in textureProjectionMatrix]
        self.R = [row[2] for row in textureProjectionMatrix]
        self.Q = [row[3] for row in textureProjectionMatrix]
        
        #restore normal drawing state
        glShadeModel(GL_SMOOTH)
        glColorMask(1, 1, 1, 1)
        glDisable(GL_POLYGON_OFFSET_FILL)
        glPopAttrib()
        glPopMatrix()
        if self.frameBufferID > 0:
            glBindFramebufferEXT(GL_FRAMEBUFFER_EXT, 0)
    
    def enable_lighting(self, on=True):
        """Enable/disable lighting (and related)."""
        if on:
            self.lights['primary'].commit_properties()
            glEnable(GL_LIGHTING)
            glEnable(GL_NORMALIZE)
        else:
            glDisable(GL_LIGHTING)
            glDisable(GL_NORMALIZE)
    
    def init_lighting(self):
        """Initialize lighting."""
        glEnable(GL_LIGHTING)
        glLightModelfv(GL_LIGHT_MODEL_AMBIENT, [0.05] * 3) #space is dark
        
        for light in self.lights.keys():
            self.lights[light].init()
    
    def set_perspective(self, width, height, zNear, zFar, fieldOfView=40.0):
        """Set perspective."""
        aspectRatio = (float(width) / height) if (height > 0) else 1
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fieldOfView, aspectRatio, zNear, zFar)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
    
    def draw_shadow_pass(self):
        """Draw scene with dim lighting."""
        self.enable_lighting(True)
        self.lights['primary'].ambient =  [0.05, 0.05, 0.05]
        self.lights['primary'].diffuse =  [0.3,  0.3,  0.3]
        self.lights['primary'].specular = [0.05, 0.05, 0.05]
        self.lights['primary'].commit_properties()
        self.draw_objects()
        self.particles.draw()
        self.spacecraft.draw()
        # Enable alpha test so that shadowed fragments are discarded
        #glAlphaFunc(GL_GREATER, 0.9) #causes problems for some nvidia hardware
        glEnable(GL_ALPHA_TEST)
    
    def display(self):
        """Display scene."""
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        #glLoadIdentity()
        
        glDisable(GL_LIGHTING) #disable lighting for first pass
        
        self.set_perspective(self.width, self.height, self.zNear, self.zFar)
        
        #set viewer orientation
        gluLookAt(*(self.camera + self.center + self.up))
        
        #  Shadow pass - needed if ambient shadows are not supported
        if self.ambienceNotSupported:
            self.draw_shadow_pass()
        
        #set up shadow texture comparison
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE1)
        glEnable(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_COMPARE_MODE,
           GL_COMPARE_R_TO_TEXTURE)
        
        #set up the eye plane for projecting the shadow map on the scene
        glEnable(GL_TEXTURE_GEN_S); glTexGenfv(GL_S, GL_EYE_PLANE, self.S)
        glEnable(GL_TEXTURE_GEN_T); glTexGenfv(GL_T, GL_EYE_PLANE, self.T)
        glEnable(GL_TEXTURE_GEN_R); glTexGenfv(GL_R, GL_EYE_PLANE, self.R)
        glEnable(GL_TEXTURE_GEN_Q); glTexGenfv(GL_Q, GL_EYE_PLANE, self.Q)
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE0)
        
        #re-enable lighting
        if self.ambienceNotSupported:
            self.lights['primary'].ambient = self.lightingDefaults['ambient']
            self.lights['primary'].diffuse = self.lightingDefaults['diffuse']
            self.lights['primary'].specular = self.lightingDefaults['specular']
            self.lights['primary'].commit_properties()
        self.enable_lighting(True)
        
        #draw objects in scene
        self.particles.draw()
        self.draw_objects()
        for bolt in self.bolts:
            bolt.draw()
        self.spacecraft.draw()
        
        #disable textures and texture generation
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE1)
        glDisable(GL_TEXTURE_2D)
        glDisable(GL_TEXTURE_GEN_S)
        glDisable(GL_TEXTURE_GEN_T)
        glDisable(GL_TEXTURE_GEN_R)
        glDisable(GL_TEXTURE_GEN_Q)
        if self.MultiTex:
            glActiveTexture(GL_TEXTURE0)
        
        #disable alpha test if the shadow pass is done
        if self.ambienceNotSupported:
            glDisable(GL_ALPHA_TEST)
        
        if self.drawAxes:
            self.axes.draw()
            
        #draw background
        skybox.draw_skybox(self.center, self.zFar - self.maxCameraDistance)
        
        if self.debug:
            util.print_to_screen(
                'Camera: (%0.2f, %0.2f, %0.2f); Light: (%0.2f, %0.2f, %0.2f)' %
                tuple(self.camera + self.lights['primary'].position))
        
        glFlush()
        glutSwapBuffers()
    
    def toggle_ambience(self):
        """TODO: remove"""
        self.ambienceNotSupported = not self.ambienceNotSupported
    
    def keyboard(self, key, x, y):
        """Handle ASCII key."""
        try:
            {
              '\x1b': lambda : sys.exit(0),         #<escape>
              'a':    lambda : self.toggle_axes(),
              'd':    lambda : self.toggle_debug(),
              'm':    lambda : self.toggle_camera_mode(),
              'r':    lambda : self.toggle_ambience(),
              's':    lambda : self.toggle_particle_shadows(),
              ' ':    lambda : self.fire_blasters() #<space>
            }[key.lower()]()
        except KeyError as error:
            print >> sys.stderr, 'Unhandled key: %s' % error
    
    def motion(self, x, y):
        """Handle mouse movement."""
        if self.firstPersonMode:
            pass
        elif ('ROTATE' == self.moveMode):
            #rotate view based on mouse movement since last reference point
            self.rotate((self.mousePosition[0] - x) / 100.0,
                        (self.mousePosition[1] - y) / 100.0)
        elif ('ZOOM' == self.moveMode):
            self.zoom((y - self.mousePosition[1]) / 10.0)
        else:
            pass #invalid move mode
        
        #set new reference points
        self.mousePosition = [x, y]
    
    def mouse(self, button, state, x, y):
        """Handle mouse clicks."""
        #set new reference points
        self.mousePosition = [x, y]
        if self.firstPersonMode:
            pass
        elif GLUT_DOWN == state:
            if GLUT_LEFT_BUTTON == button:
                self.moveMode = 'ROTATE'
            elif GLUT_RIGHT_BUTTON == button:
                self.moveMode = 'ZOOM'
            else:
                self.moveMode = 'NONE'
            glutPostRedisplay() #refresh drawing
    
    def reshape(self, width, height):
        """Handle window resizing."""
        (self.width, self.height) = (width, height)
        glViewport(0, 0, width, height)
        if (self.frameBufferID == 0):
            self.Sdim = util.upper_power_of_two(
                    width  if (width  < self.shadowdim) else self.shadowdim)
            self.Tdim = util.upper_power_of_two(
                    height if (height < self.shadowdim) else self.shadowdim)
            self.draw_shadow_map()
    
    def rotate(self, azimuth, inclination):
        """Move the camera about self.center."""
        #calculate camera position as offset from where it's pointing
        #offset = map(self.difference, self.camera, self.center)
        offset = map(lambda x, y: x - y, self.camera, self.center)
        
        #convert to spherical coordinates
        (rho, theta, phi) = coordinates.spherical(*offset)
        
        #adjust phi (azimuth) and theta (inclination)
        phi = (phi + azimuth) % (math.pi * 2)
        theta = min(max(0.01, theta + inclination), math.pi)
        
        #convert back to cartesian coordinates
        (x, y, z) = coordinates.cartesian(rho, theta, phi)
        
        #update camera position (taking into account offset)
        self.camera = map(sum, zip((x, y, z), self.center))
        glutPostRedisplay() #refresh drawing
    
    def zoom(self, dist):
        """Move the camera closer to or farther from self.center."""
        #calculate camera position as offset from where it's pointing
        offset = map(lambda x, y: x - y, self.camera, self.center)
        
        #convert to spherical coordinates
        (rho, theta, phi) = coordinates.spherical(*offset)
        
        #adjust rho (distance from origin)
        rho = max(self.minCameraDistance, min(self.maxCameraDistance, rho + dist))
        
        #convert back to cartesian coordinates
        (x, y, z) = coordinates.cartesian(rho, theta, phi)
        
        #update camera position (taking into account offset)
        self.camera = map(sum, zip((x, y, z), self.center))
        glutPostRedisplay() #refresh drawing
    
    def special(self, key, x, y):
        """Handle 'special' keys (up, down, etc.)."""
        if key in (GLUT_KEY_UP, GLUT_KEY_DOWN, GLUT_KEY_LEFT, GLUT_KEY_RIGHT):
            self.spacecraft.turn(key, glutGetModifiers())
            self.adjust_camera([0, 0, 0])
        else:
            print >> sys.stderr, 'Unhandled special key:', key
        glutPostRedisplay()
    
    def main(self):
        """Set up and execute the main loop."""
        glutInit(sys.argv)
        glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutCreateWindow(self.title)
        
        #set up callbacks
        glutDisplayFunc(self.display)    #put things on screen
        glutReshapeFunc(self.reshape)    #window resize
        glutKeyboardFunc(self.keyboard)  #ASCII keys
        glutSpecialFunc(self.special)    #non-printing keys (e.g. arrows)
        glutMouseFunc(self.mouse)        #mouse clicks
        glutMotionFunc(self.motion)      #mouse movement
        glutTimerFunc(self.dt, self.timer, 0) #activate timer at most every 50 ms
                
        self.init_scene() #initialize lighting, perspective, etc.
        
        glutMainLoop()
        return


if __name__ == '__main__':
    version = platform.python_version()
    if version < '2.7.1':
        sys.exit('requires python 2.7.1 (found %s)' % version)
    SpaceFlight().main()
