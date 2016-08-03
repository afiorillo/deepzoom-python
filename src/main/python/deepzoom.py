from __future__ import division
from math import ceil
from PIL import Image
from numpy import array

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

    def div(factor=2):
        """Returns a copy of LevelInfo downsampled by factor."""
        return LevelInfo(int(self.w/factor),int(self.h/factor),
                         float(self.xRes*factor),float(self.yRes*factor),
                         int(self.ds*factor))

class TileInfo(object):
    def __init__(self,x0,y0,width,height,imgLvl):
        self.x0 = x0
        self.y0 = y0
        self.width = width
        self.height = height
        self.imgLvl = imgLvl
    @property
    def w(self): return self.width
    @property
    def h(self): return self.height
    @property
    def x1(self): return self.x0+self.width
    @property
    def y1(self): return self.y0+self.height

class DeepzoomImage(object):

    def __init__(self,filename):
        self._imgPtr = Image.open(filename)
        self._imgArr = [array(self._imgPtr)] # cached copies of image levels

        self._levels = [LevelInfo(self._imgArr.shape[0],self._imgArr.shape[1],1,1,1)]

    @property
    def levels(self):
        # default is a plain, flat, image
        return self._levels

    def best_level_from_downsample(self,downsample):
        return 0

    def downsample(self,level):
        return self._levels[level].downsample

    def read_region(self,level,x0,y0,x1,y1):
        return self._imgArr[level][x0:x1,y0:y1,:]


class Deepzoom(object):

    # deepsoom constraints
    defaults = {
        'tileSize': (512,512),
        'tileFormat': 'jpeg', # 'jpeg' or 'png'
        'tileQuality': 80,
        # 'overlap': [0,0],
    }

    def __init__(self,image,**kwargs):
        self.image = image
        self.constraints = self.defaults.update(kwargs)

        # Array of image levels from level 0 (ds==1) to N
        self._imageLayout = [
            LevelInfo(lvl.width,lvl.height,lvl.xRes,lvl.yRes,lvl.ds)
            for lvl in image.levels]

        # Array of deepzoom levels from level 0 (ds== 1<<M) to M (ds==1)
        self._dzLayout = [self._imageLayout[0]]
        while self._dzLayout[-1].w>1 and self._dzLayout[-1].h>1:
            self._dzLayout.append(self._dzLayout[-1].div(2))
        self._dzLayout.reversed() # level 0 is w,h==(1,1)

        # Array of number of tiles from dz level 0 (ds==1<<M) to M (ds==1)
        self._tileLayout = [
            LevelInfo( width = ceil(dz.width / self.tileSize[0]),
                       height= ceil(dz.height / self.tileSize[1],
                       xRes  = dz.xRes, yRes = dz.yRes, downsample = dz.ds))
            for lvl in self._dzLayout]

    def _get_tileInfo(self,tileLevel,tileCol,tileRow):
        # check params
        # ...

        # "img..." is "image" coordinates
        imgLvl = self.image.best_level_from_downsample(tileLevel) # SLOW
        imgDs = self.image.downsample(imgLvl)
        # scales size from level image was read to deepzoom level
        imgToDzDs = self._tileLayout[tileLevel].ds / imgDs

        # "dz..." is "deepzoom" coordinates, the image in the level of the deepzoom pyramid
        dzSize = self._tileLayout[tileLevel].sz
        dzTL = (
            self.tile_size[0]*tileCol,
            self.tile_size[1]*tileRow,
        )
        imgTL = (
            dzTL[0] * imgToDzDs,
            dzTL[1] * imgToDzDs,
        )

        imgTL = (
            min(self.tile_size[0],(self.tile_size[0]*tileCol - lvlSize[0])),
            min(self.tile_size[1],(self.tile_size[1]*tileRow - lvlSize[1])),
        )

        return TileInfo(imgTL[0],imgTL[1],pSize[0],pSize[1],imgLvl)

    def get_tile(tileLevel,tileCol,tileRow):
        tInfo = self._get_tileInfo(tileLevel,tileCol,tileRow)
        return self.image.read_region(
            level=tInfo.imgLvl,x0=tInfo.x0,y0=tInfo.y0,width=tInfo.w,height=tInfo.h
        )

    @property
    def tileSize(self): return self.constraints['tileSize']
    @property
    def tileFormat(self): return self.constraints['jpeg']
    @property
    def tileQuality(self): return self.constraints['tileQuality']

    @property
    def imageLayout(self): return self._imageLayout
    @property
    def tileLayout(self): return self._tileLayout
