from PIL import Image
from numpy.core.numeric import array
from pathlib2 import Path

from deepzoom_objects import LevelInfo

class _DeepzoomImageBase(object):
    """ The basic Deepzoom Image.
    Needs to have a notion of levels, and a way to read_region."""

    @property
    def levels(self): raise NotImplementedError
    """ Returns a list of LevelInfo objects from 0 (ds==1) to N. """

    def best_level_from_downsample(self,downsample): raise NotImplementedError
    """ Returns the best level to read given the desired downsample. """

    def read_region(self,level,x0,y0,x1,y1): raise NotImplementedError
    """ Returns the region of the image specified. """

    def downsample(self,level): return self._levels[level].downsample
    def size(self,level): return self._levels[level].sz


class FlatDeepzoomImage(_DeepzoomImageBase):
    """ A Deepzoom Image for the "flat" images, i.e. jpegs, pngs, etc. """

    def __init__(self,filename):
        p = Path(filename).resolve()
        self._filename = p
        self._imgPtr = Image.open(str(p))
        self._imgArr = [array(self._imgPtr)] # cached copies of image levels

        self._levels = [LevelInfo(self._imgArr[0].shape[0],self._imgArr[0].shape[1],1,1,1)]

    @property
    def filename(self): return self._filename

    @property
    def levels(self):
        # default is a plain, flat, image
        return self._levels

    def best_level_from_downsample(self,downsample):
        return 0

    def read_region(self,level,x0,y0,x1,y1):
        return Image.fromarray(self._imgArr[level][x0:x1,y0:y1,:])