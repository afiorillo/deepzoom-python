"""
test_simple_img.py

Given an image, ensures it can open it and read metadata. Caches all tiles
and then wipes the cache. Also writes out the metadata files.
"""
from shutil import rmtree

from pathlib2 import Path

from deepzoom.factory import Deepzoom

IMG = Path(__file__).parent.parent.parent.joinpath('unittest/python/'
                                                   'img_001_1268_1024.jpg')

if __name__=='__main__':
    IMG.resolve()

    dzGen = Deepzoom(IMG, create_static_cache=True, tileQuality=100)

    print 'Image Size: (%d,%d)'%(dzGen.imageLayout[0].w,dzGen.imageLayout[0].h)
    print 'N DeepZoom Levels: %s'%(len(dzGen.tileLayout))
    for lvl,layout in enumerate(dzGen.tileLayout):
        print 'DeepZoom Level %d: (%d,%d) tiles'%(lvl,layout.w,layout.h)

    print 'Saving out all tiles...'

    for lvl in range(len(dzGen.tileLayout)):
        for col in range(int(dzGen.tileLayout[lvl].w)):
           for row in range(int(dzGen.tileLayout[lvl].h)):
               t = dzGen.get_tile(lvl,col,row)
    print 'Saved!'
    print 'Cache occupies %d kb'%(dzGen.cache_size/1024.0)

    print 'Popping some tiles.'
    while True:
        try: dzGen.del_oldest_tile()
        except IOError: break
    print 'Cache occupies %d kb'%(dzGen.cache_size/1024.0)

    rmtree(str(dzGen.parentDir))

    print 'JSON:'
    print dzGen.json

    print 'XML:'
    print dzGen.xml