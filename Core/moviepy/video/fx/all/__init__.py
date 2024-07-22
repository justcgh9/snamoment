"""
Loads all the fx !
Usage:
import moviepy.video.fx.all as vfx
clip = vfx.resize(some_clip, width=400)
clip = vfx.mirror_x(some_clip)
"""

import pkgutil
from Core.moviepy.video import fx

__all__ = [name for _, name, _ in pkgutil.iter_modules(fx.__path__) if name != "all"]

for name in __all__:
    exec(f"from ..{name} import {name}")
