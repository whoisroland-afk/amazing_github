import random
from typing import List, Tuple, Optional


class MazeGenerator:

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
        self.width = width
        self.height = height
        self.seed = seed
        if seed is not None:
            random.seed(seed)

        self.grid = [[15 for _ in range(width)] for _ in range(height)]

    def get_walls(self) -> List[List[int]]:
        return self.grid

    def generate(self, perfect: bool = True) -> None:
        if self.width < 9 or self.height < 6:
            raise ValueError("Maze size is too small to contain the '42' "
                             "pattern.")

        visited: List[List[bool]] = [
            [False for _ in range(self.width)] for _ in range(self.height)
        ]

        # "42"
        start_y = (self.height - 5) // 2
        start_x = (self.width - 8) // 2

        pattern_42 = [
            # 4
            (0, 0), (0, 1), (0, 2),
            (1, 2),
            (2, 0), (2, 1), (2, 2), (2, 3), (2, 4),
            # 2
            (5, 0), (6, 0), (7, 0),
            (7, 1), (7, 2),
            (6, 2), (5, 3), (5, 4),
            (6, 4), (7, 4)
        ]

        for px, py in pattern_42:
            target_x = start_x + px
            target_y = start_y + py
            visited[target_y][target_x] = True

        stack: List[Tuple[int, int]] = []

        found_start = False
        for y in range(self.height):
            for x in range(self.width):
                if not visited[y][x]:
                    visited[y][x] = True
                    stack.append((x, y))
                    found_start = True
                    break
            if found_start:
                break

        while stack:
            cx, cy = stack[-1]
            neighbors = []

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
                    self.grid[cy][cx] -= self.N
                    self.grid[ny][nx] -= self.S
                elif direction == "E":
                    self.grid[cy][cx] -= self.E
                    self.grid[ny][nx] -= self.W
                elif direction == "S":
                    self.grid[cy][cx] -= self.S
                    self.grid[ny][nx] -= self.N
                elif direction == "W":
                    self.grid[cy][cx] -= self.W
                    self.grid[ny][nx] -= self.E

                visited[ny][nx] = True
                stack.append((nx, ny))
            else:
                stack.pop()

    def get_pattern_42_coords(self) -> set[Tuple[int, int]]:
        start_y = (self.height - 5) // 2
        start_x = (self.width - 8) // 2

        pattern_42 = [
            (0, 0), (0, 1), (0, 2), (1, 2), (2, 0), (2, 1), (2, 2), (2, 3),
            (2, 4), (5, 0), (6, 0), (7, 0), (7, 1), (7, 2), (6, 2), (5, 3),
            (5, 4), (6, 4), (7, 4)
        ]

        return {(start_x + px, start_y + py) for px, py in pattern_42}

    def solve(self, entry: Tuple[int, int],
              exit_coords: Tuple[int, int]) -> List[str]:
        start_x, start_y = entry
        target_x, target_y = exit_coords

        queue: List[Tuple[int, int, List[str]]] = [(start_x, start_y, [])]
        visited = {(start_x, start_y)}

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

            current_walls = self.grid[cy][cx]

            for direction, dx, dy, wall_bit in directions:
                nx, ny = cx + dx, cy + dy

                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if (current_walls & wall_bit) == 0:
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append((nx, ny, path + [direction]))

        return []
