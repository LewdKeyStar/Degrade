# Copy-pasting this again...
# And again...and again...and again...
# We should make this a lib at this point, I'm sick of it!!

from dataclasses import dataclass
from typing import Union

from argparse import BooleanOptionalAction

from src.utils.string_utils import abbreviate, to_kebab

@dataclass
class ParserArgument:

    name: str
    special_shorthand: str = None

    @property
    def shorthand(self):
        return (
            self.special_shorthand
            if self.special_shorthand is not None
            else abbreviate(self.name)
        )

    @property
    def name_fields(self):
        return [
            f"--{to_kebab(self.name)}",
            f"-{self.shorthand}"
        ]

    type: any = int

    nargs: Union[int, str] = '?' # Do we allow for '*' in this project..? Let's see.

    @property
    def type_fields(self):
        return (
            {
                "type": self.type,
                "nargs": self.nargs
            }
            if self.type != bool
            else {
                "action": BooleanOptionalAction
            }
        )

    default: any = 0

    choices: list = None # probably won't use those here,
    # but we need a dict after a dict, not a positional, so here it comes anyway

    @property
    def value_fields(self):
        return {
            "default": self.default,
            "choices": self.choices
        }

    def add_to_parser(self, parser):

        parser.add_argument(
            *self.name_fields,
            **self.type_fields,
            **self.value_fields
        )

    # And now, this particular implem's ugly hack
    # A flag to know if the argument is also an argument of the degrade function.

    pass_to_compute: bool = True
