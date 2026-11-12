"""H3GIF - split storyboard contact sheets and export looping GIFs."""

from .nodes.animation import StoryboardAnimation
from .nodes.gif_export import StoryboardGIFExport
from .nodes.grid_split import StoryboardGridSplit
from .nodes.loop_optimizer import StoryboardLoopOptimizer
from .nodes.storyboard_director import H3GIFStoryboardDirector

__version__ = "0.3.1-beta"

NODE_CLASS_MAPPINGS = {
    "StoryboardGridSplit": StoryboardGridSplit,
    "StoryboardAnimation": StoryboardAnimation,
    "StoryboardGIFExport": StoryboardGIFExport,
    "StoryboardLoopOptimizer": StoryboardLoopOptimizer,
    "H3GIFStoryboardDirector": H3GIFStoryboardDirector,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "StoryboardGridSplit": "H3GIF Grid Split",
    "StoryboardAnimation": "H3GIF Animation",
    "StoryboardGIFExport": "H3GIF GIF Export",
    "StoryboardLoopOptimizer": "H3GIF Loop Optimizer",
    "H3GIFStoryboardDirector": "H3GIF Storyboard Director",
}

__all__ = [
    "NODE_CLASS_MAPPINGS",
    "NODE_DISPLAY_NAME_MAPPINGS",
    "__version__",
]
