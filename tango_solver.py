import os

import dotenv
import numpy as np

from tango_connector import TangoConnector, TangoBoardStates, EqualityStates

MAX_TYPE_PLINE = 3
VERTICAL_SHAPE = (6, 5)
HORIZONTAL_SHAPE = (5, 6)
TANGO_BOARD_SHAPE = (6, 6)


class TangoSolver:
    def __init__(self, tango_board: np.ndarray, vertical_relations: np.ndarray, horizontal_relations: np.ndarray):
        # boards and vertical relations
        self.tango_board = np.array(tango_board, dtype=np.int8)
        self.vertical_relations = np.array(vertical_relations, dtype=np.int8)
        self.horizontal_relations = np.array(horizontal_relations, dtype=np.int8)

        # working boards
        self._working_horizontal_relations = self.horizontal_relations.copy()
        self._working_vertical_relations = self.vertical_relations.copy()
        self._working_tango_board = self.tango_board.copy()

        # apply relations vars
        self.__apply_relations_following_board = self.tango_board.copy()
        # when the content of tango changes
        self.__apply_relations_discarding_rels = False

    def solve(self):
        self.solve_row_col(False)
        self.solve_row_col(True)

    def solve_row_col(self, row: bool):
        working_board = self.tango_board.copy()
        working_relations = self.horizontal_relations.copy() if not row else self.vertical_relations.copy()
        if row:
            working_board = working_board.T

        self.easy_row_completion(working_board, working_relations)

    @staticmethod
    def easy_row_completion(working_board, working_relations):

        for row_index, row in enumerate(working_board):
            num_moons = np.sum(row == TangoBoardStates.Moon.value)
            num_suns = np.sum(row == TangoBoardStates.Sun.value)

            if num_moons >= MAX_TYPE_PLINE or num_suns >= MAX_TYPE_PLINE:
                raise ValueError("Too many moons or suns in a row")

            # if there are three moons
            if num_moons == MAX_TYPE_PLINE and num_suns == MAX_TYPE_PLINE:
                continue
            elif num_suns == MAX_TYPE_PLINE or num_moons == MAX_TYPE_PLINE:
                row[row != TangoBoardStates.Moon.value] = TangoBoardStates.Sun.value

    def _apply_relations(self, vertical: bool):
        """
        Apply the relations of equality to the working board
        :param vertical: do vertical or horizontal strafing
        :return:
        """

        def manual_transpose(list_of_xs_ys):
            return tuple(zip(*list_of_xs_ys))

        # set it up as vertical
        if vertical:
            working_board = self._working_vertical_relations
        else:
            working_board = self._working_horizontal_relations

        interesting_indices_to_apply = np.where(working_board != EqualityStates.Free.value)

        # loop that takes care of the equality states
        for index in manual_transpose(interesting_indices_to_apply):
            equal = working_board[index] == EqualityStates.Equal.value

            if vertical:
                zone_of_interest = (index[0], slice(index[1], index[1] + 2))
            else:
                zone_of_interest = (slice(index[0], index[0] + 2), index[1])

            temp_zone_arr = self._working_tango_board[zone_of_interest]
            # if the zone of interest is not empty or not full
            if not (np.all(temp_zone_arr == TangoBoardStates.Empty.value) or np.all(
                    (temp_zone_arr == TangoBoardStates.Moon.value) |
                    (temp_zone_arr == TangoBoardStates.Sun.value))):

                # temporary zone to fill the spot with the equal slice

                # replace the empty spot with the other value or with the opposite of value
                if equal:
                    temp_zone_arr[temp_zone_arr == TangoBoardStates.Empty.value] = temp_zone_arr[
                        temp_zone_arr != TangoBoardStates.Empty.value][0]
                else:
                    temp_zone_arr[temp_zone_arr == TangoBoardStates.Empty.value] = - temp_zone_arr[
                        temp_zone_arr != TangoBoardStates.Empty.value][0]

                self._working_tango_board[zone_of_interest] = temp_zone_arr

        def _tango_changed(self, working_board:bool):
            if working_board:
                return not np.array_equal(self._working_tango_board, self.__apply_relations_following_board)
            else:
                return not np.array_equal(self._working_tango_board.T, self.__apply_relations_following_board.T)


if __name__ == "__main__":
    tango_board = np.zeros(TANGO_BOARD_SHAPE)
    tango_board[0] = TangoBoardStates.Moon.value

    equality_states_vertical = np.ones(VERTICAL_SHAPE)
    equality_states_horizontal = np.ones(HORIZONTAL_SHAPE)
    tango_solver = TangoSolver(tango_board, equality_states_vertical, equality_states_horizontal)
    tango_solver._apply_relations(False)
    print(tango_solver._working_tango_board)
