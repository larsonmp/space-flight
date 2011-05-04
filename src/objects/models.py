"""Module for loading wavefront models (.obj/.mtl files)."""
__author__ = "Micah Larson"
__date__   = "$Apr 17, 2011 10:12:55 PM$"

from OpenGL.GL import *   #@UnusedWildImport
from OpenGL.GLU import *  #@UnusedWildImport
from OpenGL.GLUT import * #@UnusedWildImport

import coordinates

MODEL_PATH = os.path.join('..', 'etc', 'models') #assumes running from src

class ModelLibrary(object):
    """Dictionary of models."""
    def __init__(self):
        """Constructor"""
        super(ModelLibrary, self).__init__()
        self.files = [
            'bacchus.obj',
            'castalia.obj',
            'geographos.obj',
            'golevka.obj',
            'kleopatra.obj',
            'ky26.obj',
            'toutatis.obj'
        ]
        self.models = {}

    def init(self):
        """Loads display lists into this class' dictionary."""
        print '%s> loading models:' % self.__class__.__name__
        for file in self.files:
            name = file.rsplit('.', 1)[0]
            model = Model()
            print ' ', name
            model.init(os.path.join(MODEL_PATH, file))
            
            glPushAttrib(GL_LIGHTING_BIT)
            glPushMatrix()
            callList = glGenLists(1)
            glNewList(callList, GL_COMPILE)
            model.draw()
            glEndList()
            glPopMatrix()
            glPopAttrib()
            
            self.models[name] = callList

class Material(object):
    """Encapsulates OpenGL material properties."""
    def __init__(
                self,
                ambient=[ 0.0, 0.0, 0.0],
                diffuse=[ 0.0, 0.0, 0.0],
                specular=[0.0, 0.0, 0.0],
                emissive=[0.0, 0.0, 0.0],
                shininess=0.0):
        """Constructor"""
        super(Material, self).__init__()
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.emissive = emissive 
        self.shininess = shininess
    
    def activate(self):
        """Load this Material's properties into OpenGL."""
        glMaterialfv(GL_FRONT, GL_AMBIENT,  self.ambient)
        glMaterialfv(GL_FRONT, GL_DIFFUSE,  self.diffuse)
        glMaterialfv(GL_FRONT, GL_SPECULAR, self.specular)
        glMaterialfv(GL_FRONT, GL_EMISSION, self.emissive)
        glMaterialf(GL_FRONT, GL_SHININESS, self.shininess)
    
    def __str__(self):
        """Return a string representation of this Material."""
        return '''Material[%s]:
          ambient: %s
          diffuse: %s
          specular: %s
          emissive: %s
          shininess: %s
        ''' % (self.__hash__(), self.ambient, self.diffuse, self.specular,
                self.emissive, self.shininess)
        
class Mesh(object):
    """Collection of faces and associated materials."""
    def __init__(self):
        """Constructor"""
        super(Mesh, self).__init__()
        self.faces = []
        self.material = Material()
    
    def __str__(self):
        """Return a string representation of this Mesh."""
        return '''Mesh[%s]:
          faces (%d): %s
          material: %s
        ''' % (self.__hash__(), len(self.faces), str(self.faces), self.material)
        
    def __nonzero__(self):
        """Return True if this Mesh has at least one face."""
        return len(self.faces) > 0

class Face(object):
    """Polygon (vertices and normal) representing a facet of 3D shape."""
    def __init__(self):
        """Constructor"""
        super(Face, self).__init__()
        self.vertexIndices = []
        self.normalIndices = []
    
    def __str__(self):
        """Return a string representation of this Face."""
        return '''face[%s]:
          vInd: %s
          nInd: %s
        ''' % (self.__hash__(), self.vertexIndices, self.normalIndices)
  
class OBJLoader(object):
    """Loads properties from .obj/.mtl files to construct a Model."""
    def __init__(self):
        """Constructor"""
        super(OBJLoader, self).__init__()
        self.vertices = []
        self.normals = []
        self.meshes = []
        self.mtllib = {}
    
    def init(self, path):
        """Initialize this OBJLoader with the file at the specified path."""
        activeMesh = Mesh()
        with open(path) as file:
            content = file.readlines()
            for line in content:
                data = line.strip().split()
                if data is None or data[0].startswith('#'):
                    continue
                if data[0] == 'v':
                    self.vertices.append(self.parse_vertex(data[1:]))
                elif data[0] == 'vn':
                    self.normals.append(self.parse_normal(data[1:]))
                elif data[0] == 'vt':
                    pass
                elif data[0] == 'f':
                    activeMesh.faces.append(self.parse_face(data[1:]))
                elif data[0] == 'mtllib':
                    dir = os.path.dirname(path)
                    for mfn in data[1:]:
                        self.load_mtllib(os.path.join(dir, mfn))
                elif data[0] == 'usemtl':
                    if activeMesh:
                        self.meshes.append(activeMesh)
                    activeMesh = Mesh()
                    name = data[1]
                    if self.mtllib.has_key(name):
                        activeMesh.material = self.mtllib[name]
                elif data[0] == 's':
                    pass
                else:
                    print >> sys.stderr, 'init> unhandled key: %s' % data[0]
            self.meshes.append(activeMesh)

    def load_mtllib(self, path):
        """Load the specified .mtl file's properties into this OBJLoader."""
        mtlname = None
        material = None
        with open(path) as file:
            for line in file:
                m = line.strip().split()
                if not m or m[0].startswith('#'):
                    continue
                if m[0] == 'newmtl':
                    if material is not None:
                        self.mtllib[mtlname] = material
                    mtlname = m[1]
                    material = Material()
                elif m[0] == 'Ns':
                    material.shininess = float(m[-1])
                elif m[0] == 'Ka':
                    material.ambient = [float(n) for n in m[1:]]
                elif m[0] == 'Kd':
                    material.diffuse = [float(n) for n in m[1:]]
                elif m[0] == 'Ks':
                    material.specular = [float(n) for n in m[1:]]
                elif m[0] == 'Ke':
                    material.emissive = [float(n) for n in m[1:]]
                else:
                    print >> sys.stderr, 'load_mtllib> unhandled key: %s' % m[0]
            if material is not None:
                self.mtllib[mtlname] = material
        
    def parse_face(self, data):
        """Parse a facet of the shape from the specified data (line)."""
        face = Face()
        for packet in data:
            elements = packet.split('/')
            face.vertexIndices.append(int(elements[0]) - 1) #shift index
            if len(elements) > 1 and elements[1]:
                pass
            if len(elements) > 2 and elements[2]:
                face.normalIndices.append(int(elements[2]) - 1) #shift index
        return face
    
    def parse_normal(self, data):
        """Parse the normal of a face from the specified data (line)."""
        return coordinates.normalize([float(n) for n in data])
        
    def parse_vertex(self, data):
        """Parse a vertex of a face from the specified data (line)."""
        return [float(n) for n in data]

class Texture(object):
    """A model texture."""
    def __init__(self):
        """Constructor"""
        super(Texture, self).__init__()
        self.img = None
        
    def bind(self):
        """Bind this texture."""
        glBindTexture(self.img)
    
    def s(self, u):
        """Return the s dimension of this texture."""
        return u * self.img.width
    
    def t(self, v):
        """Return the t dimension of this texture."""
        return v * self.img.height

class Model(OBJLoader):
    """A renderable model, loaded from .obj/.mtl files."""
    def __init__(self):
        """Constructor"""
        super(Model, self).__init__()
        self.textures = {}

    def init(self, file):
        """Load properties from the specified file."""
        super(Model, self).init(file)
    
    def draw(self):
        """Draw this Model based on the properties loaded from file."""
        glPushAttrib(GL_LIGHTING_BIT)
        glPushMatrix()
        for mesh in self.meshes:
            if mesh.material is not None:
                mesh.material.activate()
            #draw each face as a bunch of triangles
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for j in xrange(2, len(face.vertexIndices)):
                    if len(face.normalIndices) > 0:
                        glNormal3fv(self.normals[face.normalIndices[0]])
                    glVertex3fv(self.vertices[face.vertexIndices[0]])
                    if len(face.normalIndices) > 0:
                        glNormal3fv(self.normals[face.normalIndices[j - 1]])
                    glVertex3fv(self.vertices[face.vertexIndices[j - 1]])
                    if len(face.normalIndices) > 0:
                        glNormal3fv(self.normals[face.normalIndices[j]])
                    glVertex3fv(self.vertices[face.vertexIndices[j]])
            glEnd()
        glPopMatrix()
        glPopAttrib()
