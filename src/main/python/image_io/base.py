"""
image_io.base

Defines the base class for images supported by deepzoom-python
"""
from abc import ABCMeta,abstractmethod,abstractproperty

class DeepzoomImageBase(object):
    """ The basic Deepzoom Image.
    Needs to have a notion of levels, and a way to read_region."""

    @abstractmethod
    def __init__(self, filepath, **kwargs):
        pass

    @abstractproperty
    def supported_types(self):
        """ Returns a list of extensions (with dot) this class supports. """
        pass

    @abstractproperty
    def filepath(self):
        """ Returns a Pathlib object to the file for this image. """
        pass

    @abstractproperty
    def levels(self):
        """ Returns a list of LevelInfo objects from 0 (ds==1) to N. """
        pass

    @abstractmethod
    def read_region(self,level,x0,y0,x1,y1):
        """ Returns the region of the image specified. """
        pass

    def best_level_from_downsample(self,downsample):
        """ Returns the "best" level to read the image given the desired downsample. """
        return 0 # Assumes a flat image. NOT always true.

    def downsample(self,level):
        """ Returns the downsample for the specified level. """
        try:
            return self.levels[level].downsample
        except IndexError:
            raise IndexError('Level (%d) out of range.'%level)

    def size(self,level):
        """ Returns the size tuple (width,height) for the specified level. """
        try:
            return self.levels[level].sz
        except IndexError:
            raise IndexError('Level (%d) out of range.'%level)


class LevelInfo(object):
    def __init__(self,width,height,xRes,yRes,downsample):
        self.width = width
        self.height = height
        self.xRes = xRes
        self.yRes = yRes
        self.downsample = downsample
    @property
    def w(self): return self.width
    @property
    def h(self): return self.height
    @property
    def sz(self): return (self.w,self.h)
    @property
    def ds(self): return self.downsample

    def div(self,factor=2):
        """Returns a copy of this level, downsampled by a factor."""
        return LevelInfo(int(self.w/factor),int(self.h/factor),
                         float(self.xRes*factor),float(self.yRes*factor),
                         int(self.ds*factor))