from pathlib2 import Path

from base import DeepzoomImageBase
from flat_image import FlatDeepzoomImage

TYPES = [
    FlatDeepzoomImage,
]

def ImageFactory(image_path):
    """ Factory function to produce a DeepzoomImage around the given path. """
    p = Path(image_path).resolve()

    img = None

    for TYPE in TYPES:
        try:
            img = TYPE(p)
        except IOError:
            pass

    if img is None:
        raise IOError('Unable to open image (%s). Unsupported filetype.'%p)

    return img

def register_type(imageCls):
    """
    Registers the given class as supported image type.
    MUST subclass DeepzoomImageBase.
    """
    ## TODO: look into what PIL does to register plugins
    if not isinstance(imageCls,DeepzoomImageBase):
        raise TypeError('The given image class MUST subclass DeepzoomImageBase.')

    TYPES.append(imageCls)

def supported_extensions():
    """ Returns a list of supported file extensions (with dot). """
    ext = []
    for t in TYPES:
        ext.extend(t.supported_types)
    return ext