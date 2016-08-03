from __future__ import division
from math import ceil
from PIL import Image
from shutil import copy


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


class DeepzoomInterface(object):

    # deepsoom constraints
    defaults = {
        'tileSize': (512,512),
        'tileFormat': 'jpeg', # 'jpeg' or 'png'
        'tileQuality': 80,
        # 'overlap': [0,0],
    }

    def __init__(self,image,**kwargs):
        # super(DeepzoomInterface,self).__init__(**kwargs) ## TODO: Should be a mix-in?
        self.image = image
        self.constraints = dict(kwargs.items() + self.defaults.items())

        # Array of image levels from level 0 (ds==1) to N
        self._imageLayout = [
            LevelInfo(lvl.width,lvl.height,lvl.xRes,lvl.yRes,lvl.ds)
            for lvl in image.levels]

        # Array of deepzoom levels from level 0 (ds== 1<<M) to M (ds==1)
        self._dzLayout = [self._imageLayout[0]]
        while self._dzLayout[-1].w>1 and self._dzLayout[-1].h>1:
            self._dzLayout.append(self._dzLayout[-1].div(2))
        self._dzLayout.reverse() # level 0 is w,h==(1,1)

        # Array of number of tiles from dz level 0 (ds==1<<M) to M (ds==1)
        self._tileLayout = [
            LevelInfo( width = ceil(layout.width/self.tileSize[0]),
                       height= ceil(layout.height/self.tileSize[1]),
                       xRes  = layout.xRes, yRes = layout.yRes, downsample = layout.ds)
            for layout in self._dzLayout]

    def _get_tileInfo(self,tileLevel,tileCol,tileRow):
        # check params
        # ...

        # "img..." is "image" coordinates
        imgLvl = self.image.best_level_from_downsample(tileLevel) # SLOW
        imgDs = self.image.downsample(imgLvl)
        # scales size from level image was read to deepzoom level
        imgToDzDs = self._tileLayout[tileLevel].ds / imgDs

        # "dz..." is "deepzoom" coordinates, the image in the level of the deepzoom pyramid
        dzSize = self._dzLayout[tileLevel].sz
        dzTL = (
            self.tileSize[0]*tileCol,
            self.tileSize[1]*tileRow,
        )
        imgTL = (
            dzTL[0] * imgToDzDs,
            dzTL[1] * imgToDzDs,
        )

        imgSz = (
            min(self.tileSize[0],(dzSize[0] - self.tileSize[0]*tileCol)),
            min(self.tileSize[1],(dzSize[1] - self.tileSize[1]*tileRow)),
        )

        return TileInfo(imgTL[0],imgTL[1],imgSz[0],imgSz[1],imgLvl)

    def get_tile(self,tileLevel,tileCol,tileRow):
        tInfo = self._get_tileInfo(tileLevel,tileCol,tileRow)
        return self.image.read_region(
            level=tInfo.imgLvl,x0=tInfo.x0,y0=tInfo.y0,x1=tInfo.x1,y1=tInfo.y1
        )

    @property
    def tileSize(self): return self.constraints['tileSize']
    @property
    def tileFormat(self): return self.constraints['tileFormat']
    @property
    def tileQuality(self): return self.constraints['tileQuality']

    @property
    def imageLayout(self): return self._imageLayout
    @property
    def tileLayout(self): return self._tileLayout

class StaticCachingDeepzoomInterface(DeepzoomInterface):

    def __init__(self,image,**kwargs):
        super(StaticCachingDeepzoomInterface,self).__init__(image,**kwargs)
        if image.filepath.stem.lower()!=image.filepath.parent.name.lower():
            newParent = image.filepath.parent.joinpath(image.filepath.stem)
            newParent.mkdir(parents=True,exist_ok=True)
            newFilepath = newParent.joinpath(image.filepath.name)
            copy(str(image.filepath),str(newFilepath))
            self._filepath = newFilepath
            self._parentDir = newParent
        else:
            self._filepath = image.filepath
            self._parentDir = image.filepath.parent

    @property
    def filepath(self): return self._filepath

    @property
    def parentDir(self): return self._parentDir

    def get_tile(self,tileLevel,tileCol,tileRow):
        target = self.parentDir.joinpath('%02d/%d_%d.%s'%(
            tileLevel,tileCol,tileRow,self.tileFormat))
        try:
            target.resolve()
            tile = Image.open(str(target))
        except OSError:
            tile = super(StaticCachingDeepzoomInterface,self).get_tile(
                tileLevel,tileCol,tileRow
            )
            target.parent.mkdir(parents=True,exist_ok=True)
            tile.save(str(target))
        return tile