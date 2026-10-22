# ADM
The repository is an agentic AI software that uses value iteration and other RL Algorithms to win paceman using an agent, coded in python. 

## Installation
Install all required libraries before running:

```bash
pip install simpleai && sudo apt install -y python3-tk
```

`simpleai` is only needed for `eightpuzzle.py`; `tkinter` (`python3-tk`) is needed for the graphical display. Everything else uses the Python standard library. On macOS/Windows, `tkinter` ships with the official Python installer, so only the `pip` command is needed.

## Running
```bash
cd source
python pacman.py -p MDPAgent -l mediumClassic
```
