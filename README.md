# do_nothing

A gradual automation scripting framework.

## Installation

```
pip install git+https://github.com/erikareads/do_nothing.py.git
```

## Usage

```python3
import do_nothing

(
    do_nothing.Procedure(title="my procedure", description="...")
    .add_step(title="hello step", instructions="...")
    .add_step(
        title="execute",
        automation=do_nothing.Automation(
            execute=lambda: "hello", output="hello_output"
        ),
    )
    .add_step(title="interpolate", instructions="interpolate this: $hello_output")
    .execute()
)
```

Which will output:

```
# my procedure

...

[Enter] to begin

## hello step

...

[Enter] to continue

## execute

Executing step automatically.

**Outputs**:
  - `hello_output`: hello

## interpolate

interpolate this: hello

[Enter] to continue

done!
```
