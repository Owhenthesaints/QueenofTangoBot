import os
import re

import dotenv
from enum import Enum

import numpy as np
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

from linkedin_connector import LinkedinGameConnector


class EqualityStates(Enum):
    Free = 0
    Equal = 1
    NotEqual = -1


class TangoBoardStates(Enum):
    Empty = 0
    Sun = 1
    Moon = 2


class TangoConnector(LinkedinGameConnector):
    BOARD_SHAPE = (6, 6)
    RELATIONS_SHAPE = (5, 5)

    def __init__(self, path_to_driver, full_screen=True):
        super().__init__(path_to_driver, "https://linkedin.com/games/tango", full_screen=full_screen)
        self.tango_board = None
        self.clickable_squares = []
        self.horizontal_equals = np.zeros(self.RELATIONS_SHAPE).astype(np.int8)
        self.vertical_equals = np.zeros(self.RELATIONS_SHAPE).astype(np.int8)
        self.extract_board()

    def extract_board(self):
        # extract the shape
        board_elements = self.driver.find_element(By.CLASS_NAME, "lotka-grid")
        # fully empty board means full 0s
        board_elements_soupified = BeautifulSoup(board_elements.get_attribute("outerHTML"), 'html.parser')
        self.tango_board = np.zeros(self.BOARD_SHAPE, dtype=int)
        self.populate_moons_sun(board_elements_soupified)
        self.populate_relations(board_elements_soupified)

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
                match = re.search(r'\b(right|down)\b', classes[1])
                if match is not None:
                    if match == "right":
                        relation_table = self.horizontal_equals
                    else:
                        relation_table = self.vertical_equals

                    if edge_relation.get("aria-label") == "Cross":
                        # assign a new category if it is in a free category
                        relation_table[int(np.floor(index / self.RELATIONS_SHAPE[1])) + 1][
                            index % self.RELATIONS_SHAPE[0] + 1] = EqualityStates.NotEqual.value

                    elif edge_relation.get("aria-label") == "Equal":
                        relation_table[int(np.floor(index / self.RELATIONS_SHAPE[1])) + 1][
                            index % self.RELATIONS_SHAPE[0] + 1] = EqualityStates.Equal.value

    def __del__(self):
        self.driver.quit()


if __name__ == "__main__":
    dotenv.load_dotenv()
    tango_connector = TangoConnector(os.getenv('PATH_TO_GECKODRIVER'), full_screen=True)
