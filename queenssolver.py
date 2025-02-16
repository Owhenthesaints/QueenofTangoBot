import numpy as np
from scipy.ndimage import binary_dilation


class QueensSolver:
    def __init__(self, colors: np.ndarray, queens: np.ndarray):
        self.colors = colors
        self.queens = queens
        self.eliminated_colors = []

    def append_queen(self, row, col):
        self.queens[max(row - 1, 0):min(row + 2, self.queens.shape[0] - 1),
        max(col - 1, 0): min(col + 2, self.queens.shape[1] - 1)] = 2
        # eliminate the row and column
        self.queens[row, :] = 2
        self.queens[:, col] = 2

        # eliminate same color squares
        self.queens[self.colors == self.colors[row, col]] = 2

        self.queens[row, col] = 1
        # eliminate the color
        self.eliminated_colors.append(self.colors[row, col])

    def solve(self):

        # first pass to eliminate around queens
        queen_positions_rows, queen_positions_col = np.where(self.queens == 1)
        for queen_position in zip(queen_positions_rows, queen_positions_col):
            self.append_queen(queen_position[0], queen_position[1])

        temp_board = self.queens.copy()

        # iterate until all queens are found
        while True:
            temp_board = self.queens.copy()
            self.simple_possibilities_eliminator()

            if np.array_equal(temp_board, self.queens):
                self.semi_greedy_eliminator()

            if np.sum(self.queens == 1) == len(self.queens):
                break



    def semi_greedy_eliminator(self):
        unique_colors = np.unique(self.colors)
        uncovered_unique_colors = np.setdiff1d(unique_colors, self.eliminated_colors)
        for color in uncovered_unique_colors:
            self.eliminate_border_blockers(color)



    def eliminate_border_blockers(self, color):
        # get all the border squares
        free_color_spots = (self.colors == color) & (self.queens == 0)
        structure = np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
        to_test = binary_dilation(free_color_spots, structure=structure) & ~free_color_spots


    def __create_equiv_mask(self, index):
        mask = np.zeros(self.queens.shape, dtype=bool)
        mask[:, index[1]] = True
        mask[index[0],:] = True


    def simple_possibilities_eliminator(self):

        unique_colors = np.unique(self.colors)
        uncovered_unique_colors = np.setdiff1d(unique_colors, self.eliminated_colors)
        # first pass try to find easy queens
        for color in uncovered_unique_colors:
            free_color_spots = (self.colors == color) & (self.queens == 0)
            # if one spot is left for the color
            if np.sum(free_color_spots) == 1:
                row, col = np.where(free_color_spots)
                self.append_queen(row[0], col[0])

        uncovered_unique_colors = np.setdiff1d(unique_colors, self.eliminated_colors)

        # second pass try to find queens with column elimination
        for color in uncovered_unique_colors:
            self.handle_color_in_depth(color)

    def handle_color_in_depth(self, color):
        if color not in self.colors:
            return

        free_color_spots = (self.colors == color) & (self.queens == 0)

        # if all the free spots are on the same row or column
        if np.sum(free_color_spots) == 0:
            return
        indices = np.column_stack(np.where(free_color_spots))
        if np.all(indices[:, 0] == indices[0, 0]):
            self.queens[indices[0, 0], :] = 2

        if np.all(indices[:, 1] == indices[0, 1]):
            self.queens[:, indices[0, 1]] = 2
        # reset the free spots
        self.queens[indices[:, 0], indices[:, 1]] = 0

        # if a color is the only one remaining in a row or column eliminate the rest
        possibility_and_color = (self.colors == color) | (self.queens == 2)
        full_col_care = np.all(possibility_and_color, axis=0)
        col = np.where(full_col_care)
        if col[0].size == 1:
            mask = np.ones(self.queens.shape, dtype=bool)
            mask[:, col] = False
            self.queens[(self.colors == color) & mask] = 2

        full_row_care = np.all(possibility_and_color, axis=1)
        row = np.where(full_row_care)
        if row[0].size == 1:
            mask = np.ones(self.queens.shape, dtype=bool)
            mask[row, :] = False
            self.queens[(self.colors == color) & mask] = 2


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
