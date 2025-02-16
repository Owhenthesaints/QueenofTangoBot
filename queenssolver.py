import numpy as np
from scipy.ndimage import binary_dilation
from enum import Enum

class SquareState(Enum):
    Free = 0
    Queen = 1
    Occupied = 2

class QueensSolver:
    def __init__(self, colors: np.ndarray, queens: np.ndarray):
        self.colors = colors
        self.queens = queens
        self.eliminated_colors = []

    def append_queen(self, row, col):
        mask = self.__create_queen_mask(np.array([row, col]))
        self.queens[mask] = SquareState.Occupied.value
        self.queens[row][col] = SquareState.Queen.value
        # eliminate the color
        self.eliminated_colors.append(self.colors[row, col])

    def solve(self):
        # first pass to eliminate around queens
        queen_positions_rows, queen_positions_col = np.where(self.queens == SquareState.Queen.value)
        for queen_position in zip(queen_positions_rows, queen_positions_col):
            self.append_queen(queen_position[0], queen_position[1])


        # iterate until all queens are found
        for i in range(20):
            temp_board = self.queens.copy()
            self.simple_possibilities_eliminator()
            continue

            if np.array_equal(temp_board, self.queens):
                self.semi_greedy_eliminator()

            if np.sum(self.queens == SquareState.Queen.value) == len(self.queens):
                break

    def semi_greedy_eliminator(self):
        unique_colors = np.unique(self.colors)
        uncovered_unique_colors = np.setdiff1d(unique_colors, self.eliminated_colors)
        for color in uncovered_unique_colors:
            self.eliminate_border_blockers(color)

    def eliminate_border_blockers(self, color):
        # get all the border squares
        free_color_spots = (self.colors == color) & (self.queens == SquareState.Free.value)
        structure = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
        next_points_to_test = binary_dilation(free_color_spots, structure=structure) & ~free_color_spots
        indices = np.column_stack(np.where(next_points_to_test))
        for index in indices:
            mask = self.__create_queen_mask(index)
            if not np.any((~mask & free_color_spots)):
                self.queens[index] = SquareState.Occupied.value

    def __create_queen_mask(self, index):
        mask = np.zeros(self.queens.shape, dtype=bool)
        mask[:, index[1]] = True
        mask[index[0],:] = True
        mask[max(index[0] - 1, 0):min(index[0] + 2, self.queens.shape[0] - 1),
        max(index[1] - 1, 0): min(index[1] + 2, self.queens.shape[1] -1)] = True
        mask[index[0], index[1]] = False
        return mask

    def simple_possibilities_eliminator(self):
        unique_colors = np.unique(self.colors)
        uncovered_unique_colors = np.setdiff1d(unique_colors, self.eliminated_colors)
        # first pass try to find easy queens
        for color in uncovered_unique_colors:
            free_color_spots = (self.colors == color) & (self.queens == SquareState.Free.value)
            # if one spot is left for the color
            if np.sum(free_color_spots) == 1:
                row, col = np.where(free_color_spots)
                self.append_queen(row[0], col[0])


        # second pass
        uncovered_unique_colors = np.setdiff1d(unique_colors, self.eliminated_colors)
        for color in uncovered_unique_colors:
            self.handle_color_in_depth(color)

    def handle_color_in_depth(self, color):
        if color not in self.colors:
            return

        free_color_spots = (self.colors == color) & (self.queens == SquareState.Free.value)

        # if all the free spots are on the same row or column
        if np.sum(free_color_spots) == 0:
            return
        indices = np.column_stack(np.where(free_color_spots))
        if np.all(indices[:, 0] == indices[0, 0]):
            self.queens[indices[0, 0], :] = SquareState.Occupied.value

        if np.all(indices[:, 1] == indices[0, 1]):
            self.queens[:, indices[0, 1]] = SquareState.Occupied.value
        # reset the free spots
        self.queens[indices[:, 0], indices[:, 1]] = SquareState.Free.value

        # if a color is the only one remaining in a row or column eliminate the rest
        possibility_and_color = (self.colors == color) | (self.queens == SquareState.Occupied.value)
        full_col_care = np.all(possibility_and_color, axis=0)
        col = np.where(full_col_care)
        if col[0].size == 1:
            mask = np.ones(self.queens.shape, dtype=bool)
            mask[:, col] = False
            self.queens[(self.colors == color) & mask] = SquareState.Occupied.value

        full_row_care = np.all(possibility_and_color, axis=1)
        row = np.where(full_row_care)
        if row[0].size == 1:
            mask = np.ones(self.queens.shape, dtype=bool)
            mask[row, :] = False
            self.queens[(self.colors == color) & mask] = SquareState.Occupied.value

    def get_queens(self):
        return self.queens

    def __str__(self):
        return str(self.queens)

if __name__ == '__main__':
    colors = np.load('hard_colors.npy')
    queens = np.load('hard_queens.npy')

    solver = QueensSolver(colors, queens)
    solver.solve()
    print(solver)
