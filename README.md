*This project has been created as part of the 42 curriculum by \<shavryle\>, \<jkudrnac\>.*

# A-Maze-ing

An interactive CLI application designed to generate, visualize, and solve random mazes using custom algorithms and parameters. This project features colorized terminal rendering, interactive maze switching, and a standalone reusable generator module.

---

## Team Management & Development Timeline

### Project Roles & Collaboration
As a team of two, we divided our responsibilities to balance core logic optimization with robustness and interface design:
- **Svitlana (shavryle):** Focused on the structural pipeline, core algorithmic design of the maze generator, implementation of the Depth-First Search (DFS) mechanics, and handling packaging systems.
- **Jiří (jkudrnac):** Responsible for input parsing validation layers, strict compliance with project constraints (including handling small-maze edge cases), the interactive terminal ANSI game loop, and type-hint coverage.

### Development Timeline
- **Milestone 1:** Architecture design, Makefile automation blueprinting, and rigid configuration file parser deployment.
- **Milestone 2:** Development of the `MazeGenerator` engine with integrated "42" pattern masking using randomized DFS.
- **Milestone 3:** Implementation of the Breadth-First Search (BFS) shortest path solver and multi-state rendering.
- **Milestone 4:** Strict type annotation refactoring, Google-style docstring integration, and production deployment testing.

### Project Retrospective
#### What Worked Well
- **Modular Decoupling:** Separating the CLI application logic from the core `mazegen` package allowed both team members to work concurrently without merge conflicts.
- **Strict Linting Early:** Integrating `mypy` and `flake8` from day one prevented technical debt and made the final refactoring phase much smoother.
- **AI Peer-Review:** Utilizing Gemini as a code opponent helped us catch edge cases regarding boundary conditions and invalid configuration shapes before integration testing.

#### What Could Be Improved
- **Dependency Scope:** We should have defined the precise Python minor versions within `pyproject.toml` earlier to avoid package installation discrepancies across different local environments.
- **Test Automation:** Developing automated unit tests for the CLI loop alongside the core engine would have reduced manual verification time during late-stage updates.

### Engineering Tools Used
To achieve high software quality and robust automation, we utilized the following toolstack:
- **Automation & Environment:** GNU `make` for infrastructure scripting, `virtualenv` (`pip`) for isolated dependency handling.
- **Static Analysis & Testing:** `flake8` (style guide enforcement), `mypy` (strict static type checking), `pytest` (validation testing), and `pdb` (runtime debugging).
- **Version Control:** `git` for collaborative branch management.
- **AI Collaboration:** `Gemini` (Google) for edge-case auditing and code review support.

---

## Algorithms & Technical Architecture

### Maze Generation: Depth-First Search (DFS)
The structural blueprint of the grid is carved out using a randomized **Depth-First Search (DFS)** algorithm driven by an explicit backtracking stack.
- **The '42' Protection Layer:** When the maze meets the minimum recommended layout ($10 \times 7$), a designated central area representing the characters "42" is flagged as a protected mask. The generation algorithm treats these static coordinates as pre-visited, forcing the carver to map valid, contiguous paths dynamically around the text without corrupting its visual shape.
- **Perfect vs. Imperfect States:** A *Perfect* configuration restricts paths to a single deterministic connection between any two cells. For *Imperfect* setups, the grid is post-processed by randomly extracting roughly $10\%$ of standing interior walls to introduce valid loops, open chambers, and alternative intersections.

### Pathfinding Solver: Breadth-First Search (BFS)
To compute the directional escape path from the designated `ENTRY` point to the `EXIT` coordinates, the solver employs a **Breadth-First Search (BFS)** pathfinding algorithm utilizing an active traversal queue. BFS guarantees locating the **absolute shortest path** through the matrix, providing essential benchmarking data when distinguishing short routes from baseline paths in imperfect networks.

---

## Description

The **A-Maze-ing** project generates random rectangular mazes based on custom configuration files. It supports creating both *Perfect* mazes (single unique path between any two cells, no loops) and *Imperfect* mazes (multiple paths, containing loops). Additionally, it features a protected, unalterable "42" pattern built directly into the generation layer, fully colorized visual modes in the terminal, and an interactive cycle loop.

The maze structural generation engine is decoupled into a separate, production-ready Python package suitable for redistribution via `pip`.

---

## Instructions

The project uses a dedicated python virtual environment (`virtualenv`) handled seamlessly via a custom `Makefile`.

To initialize the project, clone the repository and run:

```bash
make all
```

This command will automatically create a .venv directory, upgrade pip, and install all the mandatory quality tools and packaging libraries (flake8, mypy, build, wheel).

### Usage
The program requires exactly one argument pointing to a valid configuration file:

```bash
make run
```

Or execute it directly via the virtual environment python binary:

```bash
.venv/bin/python a_maze_ing.py config.txt
```

Formatting the config.txt
The input configuration file is case-insensitive regarding its keys and strictly validated. Example:

```bash
WIDTH=15
HEIGHT=10

ENTRY=0,0
EXIT=8,9

OUTPUT_FILE=maze.txt

PERFECT=True
SEED=42
ALGORITHM=dfs
```

###  Visual Representation (Interactive Loop)
Once launched, the maze will render in your terminal with colored text and background sequences (ANSI escape codes).

Protected Pattern: The "42" shape will bypass random carving and display using one of the configured background colors.

Interactive Controls: Pressing Enter cycles through 6 distinct visual states of the maze (e.g., showing the layout, showcasing different "42" pattern styles, highlighting the shortest path solution for imperfect structures, etc.).

---

##  Reusable Module: mazegen
The maze generation and solution layer is implemented as a standalone, isolated class called MazeGenerator. It can be packaged into standard distribution files (.whl and .tar.gz) for future projects.

How to Build the Package
To build the reusable component locally, run:

```bash
make build
```
This generates the installation files (e.g., mazegen-1.0.0-py3-none-any.whl) at the root of your repository.

### Developer API & Usage Documentation
To install and use this package independently in another system:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Code Integration Example

Here is a complete example of how to instantiate, configure, generate, access, and solve a maze:

```python
from mazegen_package.mazegen import MazeGenerator

# 1. Instantiate and pass custom parameters (size and seed)
width = 20
height = 15
custom_seed = 42

generator = MazeGenerator(width=width, height=height, seed=custom_seed)

# 2. Generate the maze structure (Perfect or Imperfect)
# Set perfect=True for a single-path maze, perfect=False for loops/multiple paths
generator.generate(perfect=True)

# 3. Access the generated structure (2D list of bit-encoded integers)
# Individual cell walls are represented by bitmasks (N=1, E=2, S=4, W=8)
grid = generator.get_walls()
print(f"Generated a {len(grid[0])}x{len(grid)} maze grid.")

# 4. Access the solution
# Finds the coordinates path or directional steps from entry to exit
entry_point = (0, 0)
exit_point = (width - 1, height - 1)

path = generator.solve(entry=entry_point, exit_coords=exit_point)
print("Solution path directions:", path)
# Example output: ['E', 'S', 'E', 'E', 'N', ...]
```

### Features & Parameters

- MazeGenerator(width, height, seed=None): Initializes the maze. The seed parameter ensures reproducibility.

- generate(perfect=True): Executes the generation algorithm.

- get_walls(): Grants direct programmatic access to the underlying cell structural data.

- solve(entry, exit_coords): Returns a list of cardinal direction strings ('N', 'E', 'S', 'W') tracking the shortest path.

---

## Development & Quality Assurance

The repository includes explicit tasks for static analysis and strict linting compliance to meet high software standards:

- **Linting Checks:** Run `make lint` to audit the code under `flake8` guidelines and enforce type safety using strict `mypy` configurations.
- **Strict Linting Enforcement:** Run `make lint-strict` to test absolute type enforcement policy variables inside the engine packages.
- **Debugging Framework:** Run `make debug` to launch the application runtime stack trapped directly inside an interactive Python Debugger (`pdb`) checkpoint.
- **Repository Purging:** Run `make fclean` to wipe all compiled bytecode caches, packaging tracks (`build/`, `dist/`), environment structures, and exported maze assets.

---

## Resources & AI Disclosures

Artificial Intelligence tools were integrated responsibly throughout development to replicate modern, production-grade programming workflows:
- **AI Tool Utilized:** Gemini (Google)
- **Application Context:** Employed as an automated peer-reviewer and static analysis auditor to verify edge cases (such as out-of-bounds start/exit safety checking), clarify complex strict-typing behaviors for type linting configurations, and sanity-check the implementation requirements.
- **Human Verification:** Every line of logic, verification block, data-structure assignment, and ANSI coloring scheme was manually reviewed, integrated, and validated within the local workspace environment by the team developers to ensure operational stability and absolute compliance with code standards.
