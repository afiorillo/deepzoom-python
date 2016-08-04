from __future__ import division
from math import ceil
from numpy import Inf,mean
from PIL import Image
from shutil import copy
from pathlib2 import Path
from json import dumps
from string import Template


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

    tileOverlap = 0 # TODO: bother with overlap?
    # deepsoom constraints
    defaults = {
        'tileSize': 512,
        'tileFormat': 'jpeg', # 'jpeg' or 'png'
        'tileQuality': 80,
        # 'overlap': [0,0],
    }


    def __init__(self,image,**kwargs):
        # super(DeepzoomInterface,self).__init__(**kwargs) ## TODO: Should be a mix-in?

        self.image = image
        self._dzi = None
        self.constraints = dict(kwargs.items() + self.defaults.items())
        if isinstance(self.constraints.get('tileSize'),int):
            self.constraints['tileSize'] = tuple([self.constraints['tileSize']
                                                  for i in range(2)])

        if (self.tileSize[0] != self.tileSize[1]):
            raise Exception('TileSize must be square.')

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

    @property
    def dzi(self):
        if self._dzi is None:
            self._dzi = {"Image": {
                "xmlns":    "http://schemas.microsoft.com/deepzoom/2008",
                "Format":   self.tileFormat, "Overlap":  self.tileOverlap,
                "TileSize": self.tileSize[0], "Size": {
                    "Height":self._dzLayout[-1].w,"Width":self._dzLayout[-1].h
                    }
                }
                  }
        return self._dzi

    @property
    def json(self): return dumps(self.dzi,indent=4)

    @property
    def xml(self):
        t = Template('''\
<?xml version="1.0" encoding="UTF-8"?>
<Image xmlns="http://schemas.microsoft.com/deepzoom/2008
    Format="$tileFormat" Overlap="$tileOverlap" TileSize="$tileSize >
        <Size Height="$height" Width="$width" />
</Image>''')
        return t.substitute(
            tileFormat=self.tileFormat,tileOverlap=self.tileOverlap,
            tileSize=self.tileSize[0],height=self._dzLayout[-1].h,
            width=self._dzLayout[-1].w)


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
            if self.tileFormat.lower() in ['jpeg','jpg']:
                tile.save(str(target),quality=self.tileQuality)
            else:
                tile.save(str(target))
        return tile

    ## Methods for handling the files in the cache

    def _get_cache_arr(self):
        fList = self.parentDir.rglob('*.%s'%self.tileFormat)
        cacheArr = {}
        for f in fList:
            if f == self.filepath: continue
            stat = f.stat()
            lvl = f.parent.name
            loc = f.stem.split('_')
            address = '%d_%d_%d'%(int(lvl),int(loc[0]),int(loc[1]))
            cacheArr[address] = {'sz':stat.st_size,
                                 'ts':stat.st_mtime,
                                 'path': f}
        return cacheArr

    @property
    def cache_size(self):
        """ Returns the current cache size in bytes, NOT including the source image. """
        sz = 0
        for k,v in self._get_cache_arr().iteritems(): sz += v.get('sz',0)
        return sz

    def del_oldest_tile(self):
        """ Deletes the oldest tile from the cache. """
        arr = self._get_cache_arr()
        oldestAddr = None
        oldestTs = Inf
        for k,v in arr.iteritems():
            if v.get('ts',Inf) < oldestTs:
                oldestTs = v.get('tx',Inf)
                oldestAddr = k

        if oldestAddr is not None:
            p = Path(arr[oldestAddr].get('path',None))
            if p is None: raise IOError('Invalid Path!')
            p.unlink()
        else:
            raise IOError('No tiles to delete!')