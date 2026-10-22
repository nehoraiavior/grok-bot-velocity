# Set up velocity on a Grok Bot

1. Unzip this archive on the Bot's computer.
2. Put the Python package at `/workspace/velocity`. The directory that contains `__init__.py` must be `/workspace/velocity`.
3. Put observations at `/workspace/faucet/observations.jsonl`. Create the file if it is missing.
4. Put the label log at `/workspace/labeler/labels.jsonl`. Create the file if it is missing.
5. Save `grok/SKILL.md` as a skill.
6. Create the hourly routine from `grok/routine.md` in the app. The routine is the clock.
7. Do not post, like, follow, or reply.
8. The Bot reads the home timeline and looks up one-snapshot posts by id. The package does not call X.
