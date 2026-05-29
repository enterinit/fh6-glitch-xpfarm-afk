# FH6 Glitch XP Farm AFK Macro

Subscribe to my channel:

https://www.youtube.com/@krevetti (UA)

https://www.youtube.com/@justplayxp

Windows macro runner that creates a virtual Xbox 360 controller and loops a timed gamepad sequence.

## Loop

Default loop:

1. Wait `5` seconds
2. Press `A`
3. Hold `RT` at full pressure
4. Wait `40` seconds
5. Press `X`
6. Wait `2` seconds
7. Press `A`
8. Wait `10` seconds
9. Repeat

Stop the macro with `Ctrl+C`.

## Requirements

- Windows 11
- Python 3.11 or newer
- ViGEmBus driver
- A game that accepts XInput/Xbox controller input

This project uses [`vgamepad`](https://pypi.org/project/vgamepad/) to create a virtual Xbox 360 controller. `vgamepad` connects that controller through the ViGEmBus driver. Install ViGEmBus from the official [Nefarius ViGEmBus releases](https://github.com/ViGEm/ViGEmBus/releases/) if the script cannot connect the virtual controller.

## Setup

Clone the repo:

```powershell
git clone https://github.com/enterinit/fh6-glitch-xpfarm-afk.git
cd fh6-glitch-xpfarm-afk
```

Run the batch launcher:

```powershell
.\run_macro.bat
```

The launcher creates a local `.venv`, installs dependencies from `requirements.txt`, and starts the macro.

If you prefer PowerShell directly:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run_macro.ps1
```

## Usage

Run forever with default timings:

```powershell
.\run_macro.bat
```

Run a fixed number of loops:

```powershell
.\run_macro.bat --loops 10
```

Change timings:

```powershell
.\run_macro.bat --start-wait 5 --first-wait 40 --after-x-wait 2 --loop-wait 10
```

Tune button/trigger behavior:

```powershell
.\run_macro.bat --press 0.12 --rt 1
```

Options:

| Option | Default | Meaning |
| --- | ---: | --- |
| `--start-wait` | `5` | Seconds to wait at the beginning of every loop |
| `--first-wait` | `40` | Seconds after the first `A` press before pressing `X` |
| `--after-x-wait` | `2` | Seconds after `X` before pressing `A` |
| `--loop-wait` | `10` | Seconds after the second `A` press before the next loop |
| `--press` | `0.12` | Seconds to hold each digital button |
| `--rt` | `1` | Right trigger pressure from `0` to `1` |
| `--initial-delay` | `3` | Seconds before the first loop starts |
| `--loops` | none | Number of loops to run; omit to run until stopped |

## Physical Controller Notes

If a physical gamepad is connected, Windows/the game may see two controllers:

- your real controller
- the virtual Xbox 360 controller created by this macro

The macro does not press buttons on the physical controller. If the game listens only to the physical controller, unplug it temporarily, disable it, or select the virtual Xbox 360 controller in the game/device settings if available.

## Troubleshooting

- `running scripts is disabled on this system`: use `.\run_macro.bat`, or run PowerShell with `-ExecutionPolicy Bypass` as shown above.
- `Missing dependency: vgamepad`: run `.\run_macro.bat` so dependencies install into `.venv`.
- `Could not connect to ViGEmBus`: install or repair ViGEmBus, then restart the macro.
- Game ignores the macro: focus the game window and check whether the game is using the virtual controller instead of the physical one.

## Files

- `horizon_gamepad_macro.py` - macro logic
- `run_macro.bat` - easiest Windows launcher
- `run_macro.ps1` - PowerShell launcher
- `requirements.txt` - Python dependency pin
