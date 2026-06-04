# mazegen

Reusable maze generator module.

## Usage

```python
from mazegen_package.mazegen import MazeGenerator
```

## Instantiate with width, height and optional seed
```python
generator = MazeGenerator(width=20, height=15, seed=42)
```

## Generate the maze structure
```python
generator.generate()
```

## Access the generated grid (2D list of integers)
```python
grid = generator.get_walls()
```

## Solve the maze from entry to exit
```python
path = generator.solve(entry=(0, 0), exit_coords=(19, 14))
print(path) # Returns list of steps, e.g., ['S', 'E', 'S']
```