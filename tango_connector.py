import os
import re

import dotenv
from enum import Enum

import numpy as np
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from selenium.webdriver.remote.webelement import WebElement

from linkedin_connector import LinkedinGameConnector


class EqualityStates(Enum):
    Free = 0
    Equal = 1
    NotEqual = -1


class TangoBoardStates(Enum):
    Empty = 0
    Sun = 1
    Moon = -1


class TangoConnector(LinkedinGameConnector):
    BOARD_SHAPE = (6, 6)
    RELATIONS_SHAPE_HORIZONTAL = (6, 5)
    RELATIONS_SHAPE_VERTICAL = (5, 6)

    def __init__(self, path_to_driver, full_screen=True, save_file='tango_test_files'):
        super().__init__(path_to_driver, "https://linkedin.com/games/tango", full_screen=full_screen)
        self.tango_board = np.zeros(self.BOARD_SHAPE, dtype=np.uint8)
        self.clickable_squares = []
        self.horizontal_equals = np.zeros(self.RELATIONS_SHAPE_HORIZONTAL).astype(np.int8)
        self.vertical_equals = np.zeros(self.RELATIONS_SHAPE_VERTICAL).astype(np.int8)
        self.extract_board()
        self.boards_folder = save_file

    def change_board_folder(self, new_folder: str):
        self.boards_folder = new_folder

    def extract_board(self):
        # extract the shape
        board_elements = self.driver.find_element(By.CLASS_NAME, "lotka-grid")
        # fully empty board means full 0s
        board_elements_soupified = BeautifulSoup(board_elements.get_attribute("innerHTML"), 'html.parser')
        self.populate_moons_sun(board_elements_soupified)
        self.populate_relations(board_elements_soupified)
        self.populate_clickers(board_elements)

    def populate_moons_sun(self, board_elements_soupified: BeautifulSoup):
        # iterate through grid cells
        for index, cell in enumerate(board_elements_soupified.find_all(recursive=False)):
            # append sun or Moon
            content = cell.find(class_="lotka-cell-content-img")
            if content is not None:
                if content.get("aria-label") == "Sun":
                    self.tango_board[int(np.floor(index / self.BOARD_SHAPE[1]))][
                        index % self.BOARD_SHAPE[0]] = TangoBoardStates.Sun.value
                elif content.get("aria-label") == "Moon":
                    self.tango_board[int(np.floor(index / self.BOARD_SHAPE[1]))][
                        index % self.BOARD_SHAPE[0]] = TangoBoardStates.Moon.value

    def populate_relations(self, board_elements_soupified: BeautifulSoup):
        for index, cell in enumerate(board_elements_soupified.find_all(recursive=False)):
            # create categories
            # iterate through all the edges found
            edge_relations = cell.find_all(class_="lotka-cell-edge")

            for edge_relation in edge_relations:
                # get the class
                classes = edge_relation.get("class")
                # extract right or left
                match = re.search(r'\b(right|down)\b', classes[1])
                if match is not None:
                    if match.group() == "right":
                        relation_table = self.horizontal_equals
                    else:
                        relation_table = self.vertical_equals

                    edge_relation_type = edge_relation.find('svg').get('aria-label')
                    if edge_relation_type == "Cross" or edge_relation_type == "Equal":
                        relation_table[int(np.floor(index / self.BOARD_SHAPE[1]))][index % self.BOARD_SHAPE[
                            0]] = EqualityStates.Equal.value if edge_relation_type == "Equal" else EqualityStates.NotEqual.value

    def populate_clickers(self, board_elements: WebElement):
        for index, cell in enumerate(board_elements.find_elements(By.XPATH, './*')):
            self.clickable_squares.append(cell)

    def save_boards(self, tango_name="tango_board", vertical_name="vertical_board", horizontal_name="horizontal_board",
                    use_folder=True):
        if not os.path.exists(self.boards_folder):
            os.makedirs(self.boards_folder)

        if use_folder:
            tango_name = os.path.join(self.boards_folder, tango_name)
            vertical_name = os.path.join(self.boards_folder, vertical_name)
            horizontal_name = os.path.join(self.boards_folder, horizontal_name)
        else:
            tango_name = tango_name
            vertical_name = vertical_name
            horizontal_name = horizontal_name

        self._save_board(tango_name + '.npy')
        self._save_horizontal_relations(horizontal_name + '.npy')
        self._save_vertical_relations(vertical_name + '.npy')

    def _save_board(self, file_name: str):
        np.save(file_name, self.tango_board)

    def _save_horizontal_relations(self, file_name: str):
        np.save(file_name, self.horizontal_equals)

    def _save_vertical_relations(self, file_name: str):
        np.save(file_name, self.vertical_equals)

    def get_horizontal_relations(self):
        return self.horizontal_equals

    def get_vertical_relations(self):
        return self.vertical_equals

    def __del__(self):
        self.quit()

    def __str__(self):
        return str(self.tango_board)

    def quit(self):
        self.driver.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    tango_connector = TangoConnector(os.getenv('PATH_TO_GECKODRIVER'), full_screen=True)
    print(tango_connector)
    print(tango_connector.get_horizontal_relations())
    print(tango_connector.get_vertical_relations())
    tango_connector.save_boards("hard_tango_board", "hard_vertical_board", "hard_horizontal_board")
