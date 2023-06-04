from dataclasses import dataclass, field
import functools
from typing import Callable, Optional, List, Self
from string import Template
import sys
from abc import ABC, abstractmethod


class ConfigFormatter(ABC):
    @abstractmethod
    def header(self, procedure):
        pass

    @abstractmethod
    def step_title(self, state, step):
        pass

    @abstractmethod
    def step_instructions_for_execution(self, state, step):
        pass

    @abstractmethod
    def automated_note_for_execution(self, state, step):
        pass

    @abstractmethod
    def automated_output(self, state, automated, result):
        pass


class ConfigIO(ABC):
    @abstractmethod
    def output(self, text):
        pass

    @abstractmethod
    def prompt_to_begin(self):
        pass

    @abstractmethod
    def prompt_step_completion(self):
        pass


@dataclass
class Config:
    io: ConfigIO
    formatter: ConfigFormatter


@dataclass
class Automation:
    execute: Callable
    output: Optional[str] = None
    inputs: List[str] = field(default_factory=list)


@dataclass
class Step:
    title: str
    instructions: Optional[str] = None
    automation: Optional[Automation] = None


def get_inputs(state, run):
    return map(lambda key: state[key], run.inputs)


class MarkdownFormatter(ConfigFormatter):
    def header(self, procedure):
        return """
# {}

{}

""".format(
            procedure.title, procedure.description
        )

    def step_title(self, state, step):
        return """## {}

""".format(
            step.title
        )

    def step_instructions_for_execution(self, state, step):
        return """{}

""".format(
            Template(step.instructions).substitute(state)
        )

    def automated_note_for_execution(self, state, step):
        return "Executing step automatically.\n\n"

    def automated_output(self, state, automated, result):
        return """**Outputs**:
  - `{}`: {}

""".format(
            automated.output, result
        )


class StdIO(ConfigIO):
    def output(self, text):
        sys.stdout.write(text)

    def prompt_to_begin(self):
        input("[Enter] to begin")
        print("")

    def prompt_step_completion(self):
        input("[Enter] to continue")
        print("")


def execute_manual(state, step, config):
    config.io.output(config.formatter.step_title(state, step))
    config.io.output(config.formatter.step_instructions_for_execution(state, step))
    config.io.prompt_step_completion()
    return state


def execute_automated(state, step, config):
    config.io.output(config.formatter.step_title(state, step))
    config.io.output(config.formatter.automated_note_for_execution(state, step))
    automation = step.automation
    inputs = get_inputs(state, automation)
    result = automation.execute(*inputs)
    if automation.output is not None:
        state[automation.output] = result
        config.io.output(config.formatter.automated_output(state, automation, result))
    return state


def execute_step(state, step, config):
    if step.automation is None:
        return execute_manual(state, step, config)
    else:
        return execute_automated(state, step, config)


@dataclass
class Procedure:
    title: str
    description: str
    steps: List[Step] = field(default_factory=list)

    def add_step(
        self,
        title: str,
        instructions: Optional[str] = None,
        automation: Optional[Automation] = None,
    ) -> Self:
        self.steps = self.steps + [
            Step(title=title, instructions=instructions, automation=automation)
        ]
        return self

    def execute(self, config=Config(formatter=MarkdownFormatter(), io=StdIO())):
        config.io.output(config.formatter.header(self))
        config.io.prompt_to_begin()

        state = dict()
        functools.reduce(
            lambda state, step: execute_step(state, step, config), self.steps, state
        )
        print("done!")


def my_function():
    return "world"

# kwargs = {"execute": my_function, "output": "add"}
# procedure = (
#     Procedure(title="procedure", description="description")
#     .add_step(title="my step", instructions="world")
#     .add_step(title="run step", automation=Automation(**kwargs))
#     .add_step(title="my step", instructions="interpolation works here: $add")
#     .execute()
# )
