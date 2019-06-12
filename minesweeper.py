from random import randint
from typing import Iterator, Tuple, Set, List


class Zone:

    def __init__(self, x, y, has_mine=False):
        self._x = x
        self._y = y
        self._has_mine = has_mine
        self._revealed = False
        self._flagged = False
        self._adjacent_mine_count = 0

    def __str__(self):
        if not self._revealed:
            return "?" if not self._flagged else "F"
        elif self._has_mine:
            return "X"
        elif self._adjacent_mine_count:
            return str(self._adjacent_mine_count)
        else:
            return "_"

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def has_mine(self):
        return self._has_mine

    @property
    def flagged(self):
        return self._flagged

    @property
    def adjacent_mine_count(self):
        return self._adjacent_mine_count

    @adjacent_mine_count.setter
    def adjacent_mine_count(self, value):
        if isinstance(value, int) and (0 <= value <= 8):
            # print("update:", self._adjacent_mine_count, end=" ")
            self._adjacent_mine_count = value
            # print(self._adjacent_mine_count)

    @property
    def revealed(self):
        return self._revealed

    def toggle_flag(self):
        self._flagged = not self._flagged

    def reveal(self):
        self._revealed = True


class Field:

    def __init__(self, col_count, row_count, mine_count):
        self._lost_game = False
        self._flag_count = 0
        self._correctly_flagged = 0
        self._col_count = col_count
        self._row_count = row_count
        self._mine_count = mine_count
        mine_coordinates = self._generate_mine_placements(row_count, col_count, mine_count)
        self._grid = self._generate_grid(mine_coordinates, col_count, row_count)
        self._set_counts(mine_coordinates)

    def __str__(self):
        return "\n".join(
            " ".join(str(item) for item in row)
            for row in self._grid
        )

    def __iter__(self) -> Iterator[Zone]:
        for row in self._grid:
            for zone in row:
                yield zone

    def __getitem__(self, item):
        if isinstance(item, tuple) and len(item) == 2:
            x, y = item
            if 0 <= x < self._col_count and 0 <= y < self._row_count:
                return self._grid[y][x]
        raise ValueError("Item must be accessed with a tuple describing a coordinate in range")

    def _get_zone(self, x, y):
        return self._grid[y][x]

    @property
    def mine_count(self):
        return self._mine_count

    @property
    def col_count(self):
        return self._col_count

    @property
    def row_count(self):
        return self._row_count

    @property
    def lost(self):
        return self._lost_game

    @property
    def won(self):
        return self._correctly_flagged == self._mine_count

    @staticmethod
    def _generate_mine_placements(n_rows: int, n_cols: int, n_mines: int) -> Set[Tuple[int, int]]:
        coordinates = set()
        while len(coordinates) < n_mines:
            x = randint(0, n_cols - 1)
            y = randint(0, n_rows - 1)
            coordinates.add((x, y))
        # print(coordinates)
        return coordinates

    @staticmethod
    def _generate_grid(mine_coordinates: Set[Tuple[int, int]], col_count: int, row_count: int) -> List[List[Zone]]:
        grid = []
        for y in range(row_count):
            row = []
            for x in range(col_count):
                row.append(Zone(x, y, (x, y) in mine_coordinates))
            grid.append(row)
        return grid

    def _set_counts(self, mine_coordinates: Set[Tuple[int, int]]):
        for x, y in mine_coordinates:
            for zone in self.adjacent_zones(x, y, True):
                zone.adjacent_mine_count += 1

    def adjacent_zones(self, x: int, y: int, include_diagonals: bool) -> Iterator[Zone]:
        if include_diagonals:
            x_range = range(max(0, x - 1), min(self._col_count, x + 2))
            y_range = range(max(0, y - 1), min(self._row_count, y + 2))
            for this_y in y_range:
                for this_x in x_range:
                    if not (this_x == x or this_y == y):
                        yield self[this_x, this_y]
        else:
            if y - 1 >= 0:
                yield self[x, y - 1]
            if x - 1 >= 0:
                yield self[x - 1, y]
            if x + 1 < self._col_count:
                yield self[x + 1, y]
            if y + 1 < self._row_count:
                yield self[x, y + 1]

    def _reveal_zone(self, zone):
        zone.reveal()
        if zone.has_mine:
            self._lost_game = True
        elif zone.adjacent_mine_count == 0:
            for adjacent_zone in self.adjacent_zones(zone.x, zone.y, False):
                if not (adjacent_zone.has_mine or adjacent_zone.adjacent_mine_count or adjacent_zone.revealed):
                    self._reveal_zone(adjacent_zone)

    def reveal(self, x, y):
        self._reveal_zone(self[x, y])

    def toggle_flag(self, x, y):
        zone = self[x, y]
        zone.toggle_flag()
        self._flag_count += 1 if zone.flagged else -1
        if zone.has_mine:
            self._correctly_flagged += 1 if zone.flagged else -1


if __name__ == "__main__":
    game = Field(10, 10, 4)
    game.toggle_flag(2, 3)
    print(game, end="\n\n")
    for z in game:
        z.reveal()
    print(game)
    for z in game:
        z._revealed = False
    game.reveal(int(input("x: ")), int(input("y: ")))
    print(game)
