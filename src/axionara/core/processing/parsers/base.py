from abc import ABC, abstractmethod

from axionara.core.db.models import DatasetAsset
from axionara.core.processing.types import ParsedResult


class BaseParser(ABC):
    @abstractmethod
    def parse(self, dataset: DatasetAsset, content: bytes) -> ParsedResult:
        raise NotImplementedError
