"""Dictionary of textures and methods to populate it."""
__author__ = "Micah Larson"
__date__   = "$Mar 26, 2011 7:17:22 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport
from PIL import Image

#format of pixel data
formats = {
    'RGB':  GL_RGB,
    'RGBA': GL_RGBA
}

BORDER = 0                #BORDER width; 0 = no BORDER
INTERNAL_FORMAT = GL_RGB  #number of color components in the texture
LEVEL = 0                 #LEVEL-of-detail; 0 = base image

TEXTURE_PATH = os.path.join('..', 'etc', 'textures') #assumes running from src
textures = {}

def load_2D_texture(path):
    """Load a texture from an image and return the texture name."""
    ((width, height), format, pixel_data) = load_image(path)
    
    texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texture)
    
    #scale linearly when image size doesn't match
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    
    #copy image
    glTexImage2D(GL_TEXTURE_2D, LEVEL, INTERNAL_FORMAT, width, height, BORDER,
            format, GL_UNSIGNED_BYTE, pixel_data)
    if glGetError():
        raise Exception('Error loading %s, (%dx%d)' % (path, width, height))
    
    return texture #texture name


def load_cube_textures():
    """Load textures and assign them to the cube map."""
    data = {}
    for file in ['starfield.png', 'starfield_orange_sun.png']:
        name = file.rsplit('.', 1)[0]
        print ' ', name
        data[name] = load_image(os.path.join(TEXTURE_PATH, file))
    
    faces = {
        GL_TEXTURE_CUBE_MAP_POSITIVE_X_EXT: data['starfield'],
        GL_TEXTURE_CUBE_MAP_NEGATIVE_X_EXT: data['starfield'],
        GL_TEXTURE_CUBE_MAP_POSITIVE_Y_EXT: data['starfield_orange_sun'],
        GL_TEXTURE_CUBE_MAP_NEGATIVE_Y_EXT: data['starfield'],
        GL_TEXTURE_CUBE_MAP_POSITIVE_Z_EXT: data['starfield'],
        GL_TEXTURE_CUBE_MAP_NEGATIVE_Z_EXT: data['starfield']
    }
    
    glBindTexture(GL_TEXTURE_CUBE_MAP, glGenTextures(1))
    
    glTexEnvi(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexParameteri(GL_TEXTURE_CUBE_MAP, GL_TEXTURE_WRAP_R, GL_CLAMP)
    
    for face in faces.keys():
        ((width, height), format, pixel_data) = faces[face]
        glTexImage2D(face, LEVEL, INTERNAL_FORMAT, width, height, BORDER,
                format, GL_UNSIGNED_BYTE, pixel_data)
        if glGetError():
            raise Exception('Error loading %s, (%dx%d)' % (face, width, height))


def load_image(path):
    """Load image. Returns (width, height, format, pixel_data)."""
    image = Image.open(path)
    return image.size[0:2], formats[image.mode], image.tostring()


def init():
    """Load textures into the dictionary and cube map."""
    print '%s> loading 2D textures:' % __name__
    for file in ['asteroid_01.png', 'asteroid_02.png', 'command_pod.png',
                 'earth.png', 'wing.bmp']:
        name = file.rsplit('.', 1)[0]
        print ' ', name
        textures[name] = load_2D_texture(os.path.join(TEXTURE_PATH, file))
    
    print '%s> loading cube map textures:' % __name__
    load_cube_textures()
