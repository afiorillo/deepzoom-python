from shutil import rmtree
from unittest import TestCase
from pathlib2 import Path

from deepzoom import FlatDeepzoomImage
from deepzoom import DeepzoomInterface,StaticCachingDeepzoomInterface
from deepzoom.deepzoom_objects import LevelInfo
from deepzoom.factory_functions import Deepzoom,_ImageFactory

FDIR = Path(__file__).parent

class TestDeepzoom(TestCase):
    INTERFACE = DeepzoomInterface
    IMAGE_PATH = FDIR.joinpath('img_001_1268_1024.jpg')

    def setUp(self):
        self.dzImg = FlatDeepzoomImage(self.IMAGE_PATH)
        self.dzGen = self.INTERFACE(self.dzImg)

    def test_properties(self):
        assert(isinstance(self.dzGen.tileSize,tuple) and
               len(self.dzGen.tileSize)==2)

        assert(isinstance(self.dzGen.tileFormat,basestring) and
               self.dzGen.tileFormat.lower() in ['jpeg','jpg','png'])

        assert(isinstance(self.dzGen.tileQuality,int) and
               self.dzGen.tileQuality>=0 and self.dzGen.tileQuality<=100)

    def test_layouts(self):
        assert(isinstance(self.dzGen.imageLayout,list) and
               len(self.dzGen.imageLayout)>0 and
               isinstance(self.dzGen.imageLayout[0],LevelInfo))

        assert(isinstance(self.dzGen.tileLayout,list) and
               len(self.dzGen.tileFormat)>0 and
               isinstance(self.dzGen.tileLayout[0],LevelInfo))

    def test_pull_tiles(self):
        for lvl in range(len(self.dzGen.tileLayout)):
            for col in range(int(self.dzGen.tileLayout[lvl].w)):
               for row in range(int(self.dzGen.tileLayout[lvl].h)):
                   t = self.dzGen.get_tile(lvl,col,row)

    def test_meta(self):
        assert(isinstance(self.dzGen.dzi,dict))
        assert(isinstance(self.dzGen.json,basestring))
        assert(isinstance(self.dzGen.xml,basestring))

class TestCachedDeepzoom(TestDeepzoom):
    INTERFACE = StaticCachingDeepzoomInterface
    IMAGE_PATH = FDIR.joinpath('img_002_1280_960.jpg')

    def tearDown(self):
        rmtree(str(FDIR.joinpath(self.IMAGE_PATH.stem)))

    def test_properties(self):
        super(TestCachedDeepzoom,self).test_properties()
        assert(isinstance(self.dzGen.filepath,Path))
        assert(isinstance(self.dzGen.parentDir,Path))

    def test_second_construction(self):
        newImg = FlatDeepzoomImage(self.dzGen.filepath)
        newGen = self.INTERFACE(newImg)

    def test_factory_construction(self):
        newGen = Deepzoom(FDIR.joinpath(self.IMAGE_PATH.stem),
                          create_static_cache=True)

class TestDeepzoomFactory(TestDeepzoom):
    IMAGE_PATH = FDIR.joinpath('img_001_1268_1024.jpg')

    def setUp(self):
        self.dzImg = _ImageFactory(self.IMAGE_PATH)
        self.dzGen = Deepzoom(self.IMAGE_PATH)