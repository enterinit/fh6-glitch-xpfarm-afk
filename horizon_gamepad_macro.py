"""Loop a simple Xbox controller macro through a virtual XInput gamepad."""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Iterator
from dataclasses import dataclass

try:
    import vgamepad as vg
except ImportError as exc:
    raise SystemExit(
        "Missing dependency: vgamepad. Run .\\run_macro.ps1 first, or install with "
        "`python -m pip install -r requirements.txt`."
    ) from exc


DEFAULT_PRESS_SECONDS = 0.12
DEFAULT_START_WAIT_SECONDS = 5.0
DEFAULT_FIRST_WAIT_SECONDS = 40.0
DEFAULT_AFTER_X_WAIT_SECONDS = 2.0
DEFAULT_LOOP_WAIT_SECONDS = 10.0
DEFAULT_RT_VALUE = 1.0


@dataclass(frozen=True)
class MacroConfig:
    start_wait_seconds: float
    first_wait_seconds: float
    after_x_wait_seconds: float
    loop_wait_seconds: float
    press_seconds: float
    rt_value: float
    initial_delay_seconds: float
    loops: int | None


@dataclass(frozen=True)
class ButtonPress:
    name: str
    button: vg.XUSB_BUTTON


def positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def non_negative_float(value: str) -> float:
    parsed = float(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be 0 or greater")
    return parsed


def trigger_float(value: str) -> float:
    parsed = float(value)
    if not 0 <= parsed <= 1:
        raise argparse.ArgumentTypeError("must be between 0 and 1")
    return parsed


def positive_int(value: str) -> int:
    parsed = int(value, 10)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than 0")
    return parsed


def parse_args(argv: list[str]) -> MacroConfig:
    parser = argparse.ArgumentParser(
        description=(
            "Wait, press Xbox A, hold RT, wait, press X, wait, press A, wait, then repeat. "
            "Stop with Ctrl+C."
        )
    )
    parser.add_argument(
        "--start-wait",
        type=positive_float,
        default=DEFAULT_START_WAIT_SECONDS,
        help=f"Seconds to wait at the beginning of every loop. Default: {DEFAULT_START_WAIT_SECONDS:g}.",
    )
    parser.add_argument(
        "--first-wait",
        type=positive_float,
        default=DEFAULT_FIRST_WAIT_SECONDS,
        help=f"Seconds after the first A press before pressing X. Default: {DEFAULT_FIRST_WAIT_SECONDS:g}.",
    )
    parser.add_argument(
        "--after-x-wait",
        type=positive_float,
        default=DEFAULT_AFTER_X_WAIT_SECONDS,
        help=f"Seconds after X before pressing A. Default: {DEFAULT_AFTER_X_WAIT_SECONDS:g}.",
    )
    parser.add_argument(
        "--loop-wait",
        type=positive_float,
        default=DEFAULT_LOOP_WAIT_SECONDS,
        help=f"Seconds after the second A press before the next loop. Default: {DEFAULT_LOOP_WAIT_SECONDS:g}.",
    )
    parser.add_argument(
        "--press",
        type=positive_float,
        default=DEFAULT_PRESS_SECONDS,
        help=f"How long to hold each button. Default: {DEFAULT_PRESS_SECONDS:g}.",
    )
    parser.add_argument(
        "--rt",
        type=trigger_float,
        default=DEFAULT_RT_VALUE,
        help=f"Right trigger value after the first A press. Default: {DEFAULT_RT_VALUE:g}.",
    )
    parser.add_argument(
        "--initial-delay",
        type=non_negative_float,
        default=3.0,
        help="Seconds to wait before the first button press so you can focus the game. Default: 3.",
    )
    parser.add_argument(
        "--loops",
        type=positive_int,
        default=None,
        help="Number of loops to run. Omit to loop until Ctrl+C.",
    )
    args = parser.parse_args(argv)
    return MacroConfig(
        start_wait_seconds=args.start_wait,
        first_wait_seconds=args.first_wait,
        after_x_wait_seconds=args.after_x_wait,
        loop_wait_seconds=args.loop_wait,
        press_seconds=args.press,
        rt_value=args.rt,
        initial_delay_seconds=args.initial_delay,
        loops=args.loops,
    )


def loop_numbers(limit: int | None) -> Iterator[int]:
    current = 1
    while limit is None or current <= limit:
        yield current
        current += 1


def interruptible_sleep(seconds: float) -> None:
    deadline = time.monotonic() + seconds
    while True:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            return
        time.sleep(min(remaining, 0.25))


def press_button(gamepad: vg.VX360Gamepad, press: ButtonPress, hold_seconds: float) -> None:
    print(f"Pressing {press.name}", flush=True)
    gamepad.press_button(button=press.button)
    gamepad.update()
    interruptible_sleep(hold_seconds)
    gamepad.release_button(button=press.button)
    gamepad.update()


def hold_right_trigger(gamepad: vg.VX360Gamepad, value: float) -> None:
    print(f"Holding RT at {value:g}", flush=True)
    gamepad.right_trigger_float(value_float=value)
    gamepad.update()


def run_macro(config: MacroConfig) -> None:
    gamepad = vg.VX360Gamepad()
    gamepad.reset()
    gamepad.update()

    button_a = ButtonPress("A", vg.XUSB_BUTTON.XUSB_GAMEPAD_A)
    button_x = ButtonPress("X", vg.XUSB_BUTTON.XUSB_GAMEPAD_X)

    if config.initial_delay_seconds:
        print(
            f"Virtual Xbox controller connected. Starting in {config.initial_delay_seconds:g}s.",
            flush=True,
        )
        interruptible_sleep(config.initial_delay_seconds)

    try:
        for loop in loop_numbers(config.loops):
            print(f"Loop {loop}", flush=True)
            print(f"Waiting {config.start_wait_seconds:g}s", flush=True)
            interruptible_sleep(config.start_wait_seconds)

            press_button(gamepad, button_a, config.press_seconds)
            hold_right_trigger(gamepad, config.rt_value)
            print(f"Waiting {config.first_wait_seconds:g}s", flush=True)
            interruptible_sleep(config.first_wait_seconds)

            press_button(gamepad, button_x, config.press_seconds)
            print(f"Waiting {config.after_x_wait_seconds:g}s", flush=True)
            interruptible_sleep(config.after_x_wait_seconds)

            press_button(gamepad, button_a, config.press_seconds)
            print(f"Waiting {config.loop_wait_seconds:g}s", flush=True)
            interruptible_sleep(config.loop_wait_seconds)
    finally:
        gamepad.reset()
        gamepad.update()


def main(argv: list[str] | None = None) -> int:
    config = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        run_macro(config)
    except KeyboardInterrupt:
        print("\nStopped.", flush=True)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
