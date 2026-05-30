#!/usr/bin/env python3
"""Main module for the A-Maze-ing project.

Handles configuration parsing, user interaction, and maze file exporting.
"""

import sys
from typing import Final

from mazegen_package.mazegen import MazeGenerator

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


def parse_config(file_path: str) -> ConfigDict | None:
    """Safely parses the configuration file.

    Lines starting with '#' are ignored. Validates that all mandatory
    keys are present. Handles all file and format exceptions gracefully.
    """
    config: ConfigDict = {}
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, 1):
                clean_line = line.strip()

                if not clean_line or clean_line.startswith("#"):
                    continue

                if "=" not in clean_line:
                    print(
                        f"Error: Invalid syntax on line {line_num}: '{line}'",
                        file=sys.stderr
                    )
                    return None

                key, val = clean_line.split("=", 1)
                config[key.strip()] = val.strip()

        for key in MANDATORY_KEYS:
            if key not in config:
                print(
                    f"Error: Missing mandatory configuration key: '{key}'",
                    file=sys.stderr
                )
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
    print(f"\n{COLOR_BOLD}A-Maze-ing======{COLOR_RESET}")
    print("1. Re-generate a new maze")
    print("2. Show/Hide path from entry to exit")
    print("3. Rotate maze wall colors")
    print("4. Rotate 42 background colors")
    print("5. Quit")


def convert_path_to_coords(entry: tuple[int, int],
                           path_steps: list[str]) -> set[tuple[int, int]]:
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
    path_coords: set[tuple[int, int]],
    pattern_42_coords: set[tuple[int, int]],
    show_path: bool,
    color_index: int,
    bg_42_index: int
) -> None:
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
            elif show_path and (x, y) in path_coords:
                mid_line += f"{COLOR_PATH} • {COLOR_RESET}"
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
    path_steps: list[str]
) -> None:
    show_path: bool = False
    color_index: int = 0
    bg_42_index: int = 0

    current_grid = grid
    current_path_steps = path_steps
    current_pattern_coords = pattern_42_coords
    path_coords = convert_path_to_coords(entry, current_path_steps)

    render_maze(
        current_grid, entry, exit_coords, path_coords,
        current_pattern_coords, show_path, color_index, bg_42_index
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
                current_path_steps = new_gen.solve(entry, exit_coords)
                current_pattern_coords = new_gen.get_pattern_42_coords()
                path_coords = convert_path_to_coords(entry, current_path_steps)

                export_maze(current_grid, entry, exit_coords,
                            current_path_steps, output_file)
                render_maze(
                    current_grid, entry, exit_coords, path_coords,
                    current_pattern_coords, show_path, color_index, bg_42_index
                )

            elif choice == "2":
                show_path = not show_path
                render_maze(
                    current_grid, entry, exit_coords, path_coords,
                    current_pattern_coords, show_path, color_index, bg_42_index
                )

            elif choice == "3":
                color_index = (color_index + 1) % len(WALL_COLORS)
                render_maze(
                    current_grid, entry, exit_coords, path_coords,
                    current_pattern_coords, show_path, color_index, bg_42_index
                )

            elif choice == "4":
                bg_42_index = (bg_42_index + 1) % len(BACKGROUND_42_COLORS)
                render_maze(
                    current_grid, entry, exit_coords, path_coords,
                    current_pattern_coords, show_path, color_index, bg_42_index
                )

            elif choice == "5":
                print(f"\n{COLOR_BOLD}Goodbye!{COLOR_RESET}")
                break

            else:
                print(
                    "\nError: Invalid choice. Please enter a number between 1 "
                    "and 5.",
                    file=sys.stderr
                )

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{COLOR_BOLD}Program interrupted. Exiting.{COLOR_RESET}"
                  )
            break
        except Exception as e:
            print(f"\nError: An unexpected error occurred: {e}",
                  file=sys.stderr)


def main() -> int:
    """Main execution flow of the application."""
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

        perfect = raw_config["PERFECT"].lower() == "true"
        output_file = raw_config["OUTPUT_FILE"]

        if width <= 0 or height <= 0:
            print("Error: Impossible maze parameters (WIDTH/HEIGHT must "
                  "be > 0).", file=sys.stderr)
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
        generator.generate(perfect=perfect)
    except ValueError as e:
        print(f"Error during generation: {e}", file=sys.stderr)
        return 1

    grid = generator.get_walls()
    path_steps = generator.solve(entry, exit_coords)
    pattern_coords = generator.get_pattern_42_coords()

    export_success = export_maze(grid, entry, exit_coords, path_steps,
                                 output_file)
    if not export_success:
        print("Warning: Initial maze export failed.", file=sys.stderr)

    interactive_loop(grid, entry, exit_coords, perfect, output_file,
                     pattern_coords, path_steps)

    return 0


if __name__ == "__main__":
    sys.exit(main())
