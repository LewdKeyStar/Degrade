from dataclasses import dataclass
from abc import ABC

from src.utils.string_utils import abbreviate

# Unlike ImageManipScripts (and like Fascinate), we need this here,
# Since the Filter type is shortenable too.

@dataclass(kw_only = True)
class Shortenable(ABC):

    special_shorthand: str = None

    @property
    def shorthand(self):
        return (
            self.special_shorthand
            if self.special_shorthand is not None
            else abbreviate(self.name)
        )
