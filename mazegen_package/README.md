# mazegen

Reusable maze generator module.

## Installation

You can install this module directly from the built wheel file located at the root of the repository:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

## Quick Start Example

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

## Features & Parameters

- MazeGenerator(width, height, seed=None): Initializes the maze. The seed parameter ensures reproducibility.

- generate(perfect=True): Executes the generation algorithm.

- get_walls(): Grants direct programmatic access to the underlying cell structural data.

- solve(entry, exit_coords): Returns a list of cardinal direction strings ('N', 'E', 'S', 'W') tracking the shortest path.
