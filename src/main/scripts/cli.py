from pathlib2 import Path

from deepzoom.factory_functions import Deepzoom


if __name__=='__main__':
    imageName = 'img_001_1268_1024.jpg'
    img = Path(__file__).parent.parent.parent.joinpath('unittest/python/%s'%imageName)
    img.resolve()
    #
    # dzImg = FlatDeepzoomImage(str(img))

    # dzGen = DeepzoomInterface(dzImg)

    dzGen = Deepzoom(img,create_static_cache=True,tileQuality=100)

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

    print 'JSON:'
    print dzGen.json

    print 'XML:'
    print dzGen.xml