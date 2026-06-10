#!/usr/bin/env python3

import sys
from typing import Final
from mazegen_package import MazeGenerator

ConfigDict = dict[str, str]

MANDATORY_KEYS: Final[list[str]] = [
    "WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"
]

COLOR_RESET: Final[str] = "\033[0m"
COLOR_BOLD: Final[str] = "\033[1m"

WALL_COLORS: Final[list[str]] = [
    "\033[33m",
    "\033[32m",
    "\033[34m",
    "\033[35m",
    "\033[36m",
]

BACKGROUND_42_COLORS: Final[list[str]] = [
    "\033[44m   \033[0m",
    "\033[45m   \033[0m",
    "\033[46m   \033[0m",
    "\033[43m   \033[0m",
    "\033[42m   \033[0m",
    "\033[41m   \033[0m",
]

COLOR_PATH: Final[str] = "\033[94m"
COLOR_PATH_ALT: Final[str] = "\033[95m"


def parse_config(file_path: str) -> ConfigDict | None:
    """Parses a key-value configuration file for maze generation.

    Comments starting with '#' and blank lines are safely skipped.

    Args:
        file_path: System string path to the target configuration file.

    Returns:
        A dictionary containing parsed configuration pairs, or None on failure.
    """
    config: ConfigDict = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                clean_line = line.strip()

                if not clean_line or clean_line.startswith("#"):
                    continue

                if "=" not in clean_line:
                    print(f"Error: Invalid syntax on line "
                          f"{line_num}: '{line}'", file=sys.stderr)
                    return None

                key, val = clean_line.split("=", 1)
                config[key.strip().upper()] = val.strip()

        for key in MANDATORY_KEYS:
            if key not in config:
                print(f"Error: Missing mandatory configuration key: '{key}'",
                      file=sys.stderr)
                return None

        return config

    except FileNotFoundError:
        print(f"Error: Configuration file '{file_path}' not found.",
              file=sys.stderr)
        return None
    except PermissionError:
        print(f"Error: Permission denied when accessing '{file_path}'.",
              file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error: Unexpected error while reading config: {e}",
              file=sys.stderr)
        return None


def export_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_coords: tuple[int, int],
    path: list[str],
    output_path: str
) -> bool:
    """Writes the generated maze matrix and calculated solution path to a file.

    Format details match standard hexadecimal wall constraints and tokens.

    Args:
        grid: 2D integer list mapping out existing cell structures.
        entry: X and Y absolute start indices.
        exit_coords: X and Y target destination indices.
        path: Ordered text steps resolving the maze layout.
        output_path: Target save destination file path string.

    Returns:
        True if the write operation completes cleanly, False otherwise.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as file:
            for row in grid:
                hex_row = "".join(f"{cell:X}" for cell in row)
                file.write(f"{hex_row}\n")

            file.write("\n")
            file.write(f"{entry[0]},{entry[1]}\n")
            file.write(f"{exit_coords[0]},{exit_coords[1]}\n")
            file.write(f"{''.join(path)}\n")

        print(f"Success: Maze successfully exported to '{output_path}'.")
        return True

    except IOError as e:
        print(f"Error: Failed to write to output file '{output_path}': {e}",
              file=sys.stderr)
        return False
    except Exception as e:
        print(f"Error: Unexpected error during export: {e}", file=sys.stderr)
        return False


def display_menu() -> None:
    """Prints available options within the terminal interactive loop."""
    print(f"\n{COLOR_BOLD}A-Maze-ing======{COLOR_RESET}")
    print("1. Re-generate a new maze")
    print("2. Cycle path display (None -> Shortest -> All)")
    print("3. Rotate maze wall colors")
    print("4. Rotate 42 background colors")
    print("5. Quit")


def convert_path_to_coords(entry: tuple[int, int],
                           path_steps: list[str]) -> set[tuple[int, int]]:
    """Unpacks directional instructions into concrete coordinate hashes.

    Args:
        entry: The absolute origin tuple.
        path_steps: Continuous single-character instructions.

    Returns:
        A unique set tracking every coordinate touched by the solution track.
    """
    coords: set[tuple[int, int]] = set()
    curr_x, curr_y = entry
    coords.add((curr_x, curr_y))

    for step in path_steps:
        if step == "N":
            curr_y -= 1
        elif step == "S":
            curr_y += 1
        elif step == "E":
            curr_x += 1
        elif step == "W":
            curr_x -= 1
        coords.add((curr_x, curr_y))

    return coords


def render_maze(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_coords: tuple[int, int],
    path_coords_short: set[tuple[int, int]],
    path_coords_long: set[tuple[int, int]],
    pattern_42_coords: set[tuple[int, int]],
    path_mode: int,
    color_index: int,
    bg_42_index: int
) -> None:
    """Renders the maze board structural walls and assets into stdout.

    Handles contextual color modes and toggle statuses.

    Args:
        grid: Active map array representation.
        entry: Origin cell bounds.
        exit_coords: Stop cell bounds.
        path_coords_short: Short path coordinate lookups.
        path_coords_long: Perfect/alternative grid solution lookups.
        pattern_42_coords: Coords flagged to highlight the core pattern.
        path_mode: Display visibility flag tracking active states.
        color_index: Matrix wall sequence palette picker value.
        bg_42_index: Active theme block background selector token.
    """
    if not grid or not grid[0]:
        return

    height = len(grid)
    width = len(grid[0])
    wall_color = WALL_COLORS[color_index]
    bg_42_color = BACKGROUND_42_COLORS[bg_42_index]

    for y in range(height):
        top_line = ""
        for x in range(width):
            cell = grid[y][x]
            if cell & 1:
                top_line += f"{wall_color}+---{COLOR_RESET}"
            else:
                top_line += "+   "
        print(top_line + "+")

        mid_line = ""
        for x in range(width):
            cell = grid[y][x]

            if cell & 8:
                mid_line += f"{wall_color}|{COLOR_RESET}"
            else:
                mid_line += " "

            if (x, y) == entry:
                mid_line += f" {COLOR_BOLD}E{COLOR_RESET} "
            elif (x, y) == exit_coords:
                mid_line += f" {COLOR_BOLD}X{COLOR_RESET} "
            elif (x, y) in pattern_42_coords:
                mid_line += bg_42_color
            elif path_mode == 1 and (x, y) in path_coords_short:
                mid_line += f"{COLOR_PATH} • {COLOR_RESET}"
            elif path_mode == 2 and (x, y) in path_coords_short:
                mid_line += f"{COLOR_PATH} • {COLOR_RESET}"
            elif path_mode == 2 and (x, y) in path_coords_long:
                mid_line += f"{COLOR_PATH_ALT} • {COLOR_RESET}"
            else:
                mid_line += "   "

        last_cell = grid[y][width - 1]
        if last_cell & 2:
            mid_line += f"{wall_color}|{COLOR_RESET}"
        else:
            mid_line += " "
        print(mid_line)

    bottom_line = ""
    for x in range(width):
        last_row_cell = grid[height - 1][x]
        if last_row_cell & 4:
            bottom_line += f"{wall_color}+---{COLOR_RESET}"
        else:
            bottom_line += "+   "
    print(bottom_line + "+")


def interactive_loop(
    grid: list[list[int]],
    entry: tuple[int, int],
    exit_coords: tuple[int, int],
    perfect: bool,
    output_file: str,
    pattern_42_coords: set[tuple[int, int]],
    path_steps_short: list[str],
    path_steps_long: list[str]
) -> None:
    """Manages runtime terminal commands and controls maze variable properties.

    Runs indefinitely until closed by users via specific option selections.

    Args:
        grid: Original map blueprint array.
        entry: Start point specifications.
        exit_coords: End target specifications.
        perfect: Standard type verification flag.
        output_file: Target text log destination path.
        pattern_42_coords: Set containing static safe zones coordinates.
        path_steps_short: Active shorthand track array.
        path_steps_long: Full perfect configuration array paths.
    """
    path_mode: int = 0
    color_index: int = 0
    bg_42_index: int = 0

    current_grid = grid
    current_pattern_coords = pattern_42_coords

    current_steps_short = path_steps_short
    current_steps_long = path_steps_long
    path_coords_short = convert_path_to_coords(entry, current_steps_short)
    path_coords_long = convert_path_to_coords(entry, current_steps_long)

    render_maze(
        current_grid, entry, exit_coords, path_coords_short, path_coords_long,
        current_pattern_coords, path_mode, color_index, bg_42_index
    )

    while True:
        display_menu()
        try:
            choice = input(f"{COLOR_BOLD}Choice? (1-5): {COLOR_RESET}").strip()

            if choice == "1":
                print("\nGenerating new random maze...")
                new_gen = MazeGenerator(len(current_grid[0]),
                                        len(current_grid), seed=None)
                new_gen.generate(perfect=perfect)
                current_grid = new_gen.get_walls()

                current_steps_short = new_gen.solve(entry, exit_coords,
                                                    use_perfect_grid=False)
                current_steps_long = new_gen.solve(entry, exit_coords,
                                                   use_perfect_grid=True)

                path_coords_short = convert_path_to_coords(entry,
                                                           current_steps_short)
                path_coords_long = convert_path_to_coords(entry,
                                                          current_steps_long)
                current_pattern_coords = new_gen.get_pattern_42_coords()

                export_maze(current_grid, entry, exit_coords,
                            current_steps_short, output_file)
                render_maze(
                    current_grid, entry, exit_coords, path_coords_short,
                    path_coords_long, current_pattern_coords, path_mode,
                    color_index, bg_42_index
                )

            elif choice == "2":
                if not perfect:
                    path_mode = (path_mode + 1) % 3
                else:
                    path_mode = (path_mode + 1) % 2

                render_maze(
                    current_grid, entry, exit_coords, path_coords_short,
                    path_coords_long, current_pattern_coords, path_mode,
                    color_index, bg_42_index
                )

            elif choice == "3":
                color_index = (color_index + 1) % len(WALL_COLORS)
                render_maze(
                    current_grid, entry, exit_coords, path_coords_short,
                    path_coords_long, current_pattern_coords, path_mode,
                    color_index, bg_42_index
                )

            elif choice == "4":
                bg_42_index = (bg_42_index + 1) % len(BACKGROUND_42_COLORS)
                render_maze(
                    current_grid, entry, exit_coords, path_coords_short,
                    path_coords_long, current_pattern_coords, path_mode,
                    color_index, bg_42_index
                )

            elif choice == "5":
                print(f"\n{COLOR_BOLD}Goodbye!{COLOR_RESET}")
                break

            else:
                print("\nError: Invalid choice. Please enter a number"
                      " between 1 and 5.", file=sys.stderr)

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{COLOR_BOLD}Program interrupted. "
                  f"Exiting.{COLOR_RESET}")
            break
        except Exception as e:
            print(f"\nError: An unexpected error occurred: {e}",
                  file=sys.stderr)


def main() -> int:
    """Performs validation, sets parameters and launches main execution tasks.

    Returns:
        Exit code (0 for successful run, 1 for parsing or initialization logs).
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    config_path = sys.argv[1]
    raw_config = parse_config(config_path)

    if raw_config is None:
        print("Error: Configuration loading failed. Exiting.", file=sys.stderr)
        return 1

    try:
        width = int(raw_config["WIDTH"])
        height = int(raw_config["HEIGHT"])

        entry_str = raw_config["ENTRY"].split(",")
        exit_str = raw_config["EXIT"].split(",")
        entry = (int(entry_str[0]), int(entry_str[1]))
        exit_coords = (int(exit_str[0]), int(exit_str[1]))

        perfect_val = raw_config["PERFECT"].lower()
        if perfect_val not in ("true", "false"):
            print(
                f"Error: Invalid boolean value '{raw_config['PERFECT']}' "
                f"for key 'PERFECT'. Must be 'True' or 'False'.",
                file=sys.stderr
            )
            return 1
        perfect = perfect_val == "true"
        output_file = raw_config["OUTPUT_FILE"]

        if width < 10 or height < 7:
            print(
                "Notice: Maze size is too small to contain the '42' pattern. "
                "Generating without it.",
                file=sys.stderr
            )

        if not (0 <= entry[0] < width and 0 <= entry[1] < height):
            print(
                f"Error: ENTRY coordinates {entry} are outside "
                f"the maze bounds (0-{width-1}, 0-{height-1}).",
                file=sys.stderr
            )
            return 1

        if not (0 <= exit_coords[0] < width and 0 <= exit_coords[1] < height):
            print(
                f"Error: EXIT coordinates {exit_coords} are outside "
                f"the maze bounds (0-{width-1}, 0-{height-1}).",
                file=sys.stderr
            )
            return 1

        if entry == exit_coords:
            print(
                "Error: ENTRY and EXIT coordinates must be different.",
                file=sys.stderr
            )
            return 1

    except (ValueError, IndexError):
        print("Error: Invalid value format in configuration file.",
              file=sys.stderr)
        return 1

    print("Configuration loaded and validated successfully:")
    print(f"  Dimensions: {width}x{height}")
    print(f"  Entry: {entry} | Exit: {exit_coords}")
    print(f"  Perfect: {perfect} | Output: {output_file}\n")

    seed_val = int(raw_config["SEED"]) if "SEED" in raw_config else None

    print("Generating maze...")
    try:
        generator = MazeGenerator(width, height, seed=seed_val)
        pattern_coords = generator.get_pattern_42_coords()
        check_p = entry in pattern_coords or exit_coords in pattern_coords
        if pattern_coords and check_p:
            print(
                "Error: ENTRY or EXIT cannot be placed inside "
                "the protected '42' pattern.",
                file=sys.stderr
            )
            return 1

        generator.generate(perfect=perfect)
    except ValueError as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        return 1

    grid = generator.get_walls()

    path_steps_short = generator.solve(entry, exit_coords,
                                       use_perfect_grid=False)
    path_steps_long = generator.solve(entry, exit_coords,
                                      use_perfect_grid=True)

    pattern_coords = generator.get_pattern_42_coords()

    export_success = export_maze(grid, entry, exit_coords,
                                 path_steps_short, output_file)
    if not export_success:
        print("Warning: Initial maze export failed.", file=sys.stderr)

    interactive_loop(
        grid, entry, exit_coords, perfect, output_file,
        pattern_coords, path_steps_short, path_steps_long
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
