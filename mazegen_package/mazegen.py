import random
from typing import List, Tuple, Optional


class MazeGenerator:
    """A generator that creates random mazes with an optional '42' pattern.

    Supports generating both perfect (single path) and imperfect mazes,
    and includes a BFS-based solver to find paths from entry to exit.
    """

    width: int
    height: int
    seed: Optional[int]
    grid: List[List[int]]

    N: int = 1
    E: int = 2
    S: int = 4
    W: int = 8

    def __init__(self, width: int, height: int,
                 seed: Optional[int] = None) -> None:
        """Initializes the maze generator with dimensions and an optional seed.

        Args:
            width: The number of cells in the horizontal direction.
            height: The number of cells in the vertical direction.
            seed: An optional integer to seed the random number generator.
        """
        self.width = width
        self.height = height
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        self.grid = [[15 for _ in range(width)] for _ in range(height)]
        self.perfect_grid: List[List[int]] = []

    def get_walls(self) -> List[List[int]]:
        """Returns the current structural state of the maze grid.

        Returns:
            A 2D list of integers representing encoded wall states.
        """
        return self.grid

    def generate(self, perfect: bool = True) -> None:
        """Generates a maze grid using a Depth-First Search (DFS) algorithm.

        Carves out paths while optionally protecting a central '42' pattern.
        If perfect is False, additional random internal walls are removed.

        Args:
            perfect: If True, creates a perfect maze with exactly one path.
        """
        visited: List[List[bool]] = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]

        protected_cells = self.get_pattern_42_coords()

        for tx, ty in protected_cells:
            visited[ty][tx] = True

        stack: List[Tuple[int, int]] = []

        found_start = False
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) not in protected_cells:
                    visited[y][x] = True
                    stack.append((x, y))
                    found_start = True
                    break
            if found_start:
                break

        while stack:
            cx, cy = stack[-1]
            neighbors: List[Tuple[str, int, int]] = []

            if cy > 0 and not visited[cy - 1][cx]:
                neighbors.append(("N", cx, cy - 1))
            if cx < self.width - 1 and not visited[cy][cx + 1]:
                neighbors.append(("E", cx + 1, cy))
            if cy < self.height - 1 and not visited[cy + 1][cx]:
                neighbors.append(("S", cx, cy + 1))
            if cx > 0 and not visited[cy][cx - 1]:
                neighbors.append(("W", cx - 1, cy))

            if neighbors:
                direction, nx, ny = random.choice(neighbors)

                if direction == "N":
                    self.grid[cy][cx] &= ~self.N
                    self.grid[ny][nx] &= ~self.S
                elif direction == "E":
                    self.grid[cy][cx] &= ~self.E
                    self.grid[ny][nx] &= ~self.W
                elif direction == "S":
                    self.grid[cy][cx] &= ~self.S
                    self.grid[ny][nx] &= ~self.N
                elif direction == "W":
                    self.grid[cy][cx] &= ~self.W
                    self.grid[ny][nx] &= ~self.E

                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

        self.perfect_grid = [row[:] for row in self.grid]

        if not perfect:
            walls_to_remove = (self.width * self.height) // 10
            attempts = 0
            removed = 0

            directions: List[Tuple[str, int, int, int, int]] = [
                ("N", 0, -1, self.N, self.S),
                ("E", 1, 0, self.E, self.W),
                ("S", 0, 1, self.S, self.N),
                ("W", -1, 0, self.W, self.E)
            ]

            while removed < walls_to_remove and attempts < 3000:
                attempts += 1

                cx = random.randint(0, self.width - 1)
                cy = random.randint(0, self.height - 1)

                if (cx, cy) in protected_cells:
                    continue

                res = random.choice(directions)
                d_name, dx, dy, current_wall_bit, neighbor_wall_bit = res
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (nx, ny) not in protected_cells:
                        if self.grid[cy][cx] & current_wall_bit:
                            self.grid[cy][cx] &= ~current_wall_bit
                            self.grid[ny][nx] &= ~neighbor_wall_bit
                            removed += 1

    def get_pattern_42_coords(self) -> set[Tuple[int, int]]:
        """Calculates coordinates of the '42' block based on current size.

        Returns:
            A set of (x, y) coordinates forming the protected '42' pattern.
            Returns an empty set if the dimensions are below 10x7.
        """
        if self.width < 10 or self.height < 7:
            return set()

        start_y = (self.height - 5) // 2
        start_x = (self.width - 8) // 2

        pattern_42 = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2), (2, 3),
            (2, 4), (5, 0), (6, 0), (7, 0), (7, 1), (7, 2), (6, 2), (5, 3),
            (5, 4), (6, 4), (7, 4)
        ]

        return {(start_x + px, start_y + py) for px, py in pattern_42}

    def solve(self, entry: Tuple[int, int],
              exit_coords: Tuple[int, int],
              use_perfect_grid: bool = False) -> List[str]:
        """Finds the shortest path from entry to exit using BFS.

        Args:
            entry: A tuple of (x, y) representing start coordinates.
            exit_coords: A tuple of (x, y) representing end coordinates.
            use_perfect_grid: If True, solves using the baseline perfect grid.

        Returns:
            A list of cardinal direction strings (N, E, S, W) tracking the
            path.
        """
        start_x, start_y = entry
        target_x, target_y = exit_coords

        queue: List[Tuple[int, int, List[str]]] = [(start_x, start_y, [])]
        visited = {(start_x, start_y)}

        check_grid = use_perfect_grid and self.perfect_grid
        active_grid = self.perfect_grid if check_grid else self.grid

        directions = [
            ("N", 0, -1, 1),
            ("E", 1, 0, 2),
            ("S", 0, 1, 4),
            ("W", -1, 0, 8)
        ]

        while queue:
            cx, cy, path = queue.pop(0)

            if cx == target_x and cy == target_y:
                return path

            current_walls = active_grid[cy][cx]

            for direction, dx, dy, wall_bit in directions:
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (current_walls & wall_bit) == 0:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny, path + [direction]))

        return []
