from .version import VERSION as __version__
from .detector import Detector
from .extractor import MetricExtractor
from .matcher import Matcher
from .matcher.faiss_index import FaissIndex

__all__ = ["Detector", "MetricExtractor"]
