from deepzoom import Deepzoom,DeepzoomImage

from pathlib2 import Path


if __name__=='__main__':
    imageName = 'img_001_1268_1024.jpg'
    img = Path(__file__).parent.parent.parent.joinpath('unittest/python/%s'%imageName)
    img.resolve()

    dzImg = DeepzoomImage(str(img))

    dzGen = Deepzoom(dzImg)

    print 'Image Size: (%d,%d)'%(dzGen.imageLayout[0].w,dzGen.imageLayout[0].h)
    print 'N DeepZoom Levels: %s'%(len(dzGen.tileLayout))
    for lvl,layout in enumerate(dzGen.tileLayout):
        print 'DeepZoom Level %d: (%d,%d) tiles'%(lvl,layout.w,layout.h)

    print 'Showing Base Level Image Tiles:'

    lvl = len(dzGen.tileLayout)-1
    for col in range(int(dzGen.tileLayout[lvl].w)):
       for row in range(int(dzGen.tileLayout[lvl].h)):
           t = dzGen.get_tile(lvl,col,row)
           t.show()