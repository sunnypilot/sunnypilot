# LAICa: Lesmo's AI Car

This is a project forked from SunnyPilot, an open source driver assistance system for comma.ai's comma 3X.

Unless told otherwise, assume the vehicle is a Volkswagen GLI 2021.

## Python Scripts

Always activate the .venv/bin/activate script before running any python scripts, including `scons`.

## Code Generation

### Hooks and Interventions

You must attempt to avoid making major code changes to the original codebase outside of the laica/ directory. Instead, you should try to keep new code inside of the laica/ directory.

To achieve this, we may use decorators to add code before and after the original function.