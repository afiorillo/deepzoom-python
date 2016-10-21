from pathlib2 import Path

from image_interface import FlatDeepzoomImage as _FlatDeepzoomImage
from deepzoom_objects import DeepzoomInterface as _DeepzoomInterface
from deepzoom_objects import StaticCachingDeepzoomInterface as _CachedInterface

def Deepzoom(image_or_directory_path,create_static_cache=False,**kwargs):
    """
    Returns a Deepzoom interface corresponding to the given image. Can accept
    either a filepath (and will read tiles on the fly) or a directory path (that
    contains an image with the same name as the directory) that contains/will
    contain a static DeepZoom image directory.
    :param image_or_directory_path: String or Pathlib object
    :param create_static_cache: If True, creates a static DeepZoom image
     directory directory structure *around* the given image (or in the given
     directory). This is done lazily, saving each tile as it's requested.
    :param kwargs: Same as DeepzoomInterface
    :return: DeepZoom
    """
    p = Path(image_or_directory_path).resolve()
    img = None
    if p.is_file():
        img = _ImageFactory(p)
    elif p.is_dir():
        fList = list(p.glob('%s.*'%p.name))
        if len(fList)==0:
            raise IOError('Invalid Deepzoom directory (%s). '
                          'Must contain and image named (%s) to be valid.'
                          ''%(p,'%s.<EXT>'%p.name))
        for f in fList:
            try: img = _ImageFactory(f)
            except IOError: pass

    if img is None:
        raise IOError('Invalid Deepzoom target (%s). '
                      'Not a supported image format.'%(p))

    if create_static_cache:
        # do something to DeepZoomGenerator so that it saves on get_tile()
        dzGen = _CachedInterface(img,**kwargs)
    else:
        dzGen = _DeepzoomInterface(img,**kwargs)
    return dzGen

def _ImageFactory(image_path):
    """ Factory function to produce a DeepzoomImage around the given path. """
    p = Path(image_path).resolve()
    try:
        img = _FlatDeepzoomImage(p)
    except IOError:
        raise IOError('Unable to open image (%s).'%p)

    return img