from dataclasses import dataclass, field
from typing import Union, Callable

from src.decl.types.ParserArgument import ParserArgument
from src.decl.types.abstract.Shortenable import Shortenable

from src.state.store import is_enabled_at_runtime

@dataclass(kw_only = True)
class Filter(Shortenable):

    name: str

    # Yup, that's how the type semantics work this time around.

    parameters: list[ParserArgument] = field(default_factory = list)

    # Address Fascinate's cardinal sin :
    # We won't have to enable every feature, just inputting its params will work!

    requires_explicit_enabling: bool = False

    @property
    def enable_flag(self):
        return ParserArgument(
            name = self.name,
            special_shorthand = self.special_shorthand,
            type = bool,
            default = False
        )

    # The active_condition callable will never take any arguments,
    # Since we have the runtime state primitives!
    # It's only a callable so that it's a dynamically evaluated expression.

    active_condition: Union[bool, Callable] = True

    # Same here, btw. This will be crucial to randomizing later.

    filter_string: Callable

    def __post_init__(self):

        if self.requires_explicit_enabling:

            other_active_conditions = self.active_condition

            self.active_condition = lambda: (
                is_enabled_at_runtime(self.name)
                and other_active_conditions()
            )

    def add_to_parser(self, parser):

        if self.requires_explicit_enabling:

            self.enable_flag.add_to_parser(parser)

        for param in self.parameters:

            param.name = f"{self.name}_{param.name}"
            param.add_to_parser(parser)


    def __call__(self):

        return (
            self.filter_string() if self.active_condition()
            else ""
        )
