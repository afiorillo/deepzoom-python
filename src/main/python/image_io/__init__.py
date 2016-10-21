"""
image_io

This package contains classes for compatible images, as well as a registerable
factory function for additional types.
"""

from flat_image import FlatDeepzoomImage
from factory import ImageFactory,register_type,supported_extensions