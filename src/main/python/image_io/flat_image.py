"""
image_io.flat_image

FlatDeepzoomImage supports all types that PIL supports. JPEG, PNG, BMP, etc.

"""
from PIL import Image
from numpy.core.numeric import array
from pathlib2 import Path

from image_io.base import DeepzoomImageBase, LevelInfo

class FlatDeepzoomImage(DeepzoomImageBase):
    """ A Deepzoom Image for the "flat" images, i.e. jpegs, pngs, etc. """

    def __init__(self,filepath):
        super(FlatDeepzoomImage,self).__init__(filepath)
        p = Path(filepath).resolve()
        self._filepath = p
        self._imgPtr = Image.open(str(p))
        self._imgArr = [array(self._imgPtr)] # cached copies of image levels

        self._levels = [LevelInfo(self._imgArr[0].shape[0],self._imgArr[0].shape[1],1,1,1)]

    @property
    def filepath(self): return self._filepath

    @property
    def levels(self):
        # default is a plain, flat, image
        return self._levels

    @property
    def supported_types(self):
        return ['.png','.jpeg','.jpg','.bmp'] ## TODO: get this list from PIL

    def read_region(self,level,x0,y0,x1,y1):
        return Image.fromarray(self._imgArr[level][x0:x1,y0:y1,:])