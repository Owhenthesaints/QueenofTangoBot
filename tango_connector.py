import os
import re

import dotenv
from enum import Enum

import numpy as np
from selenium.webdriver.common.by import By

from linkedin_connector import LinkedinGameConnector

class EqualityStates(Enum):
    EqualUp = 0
    EqualLeft = 1
    EqualDown = 2
    EqualRight = 3
    NeqUp = 4
    NeqLeft = 5
    NeqDown = 6
    NeqRight = 7

class TangoBoardStates(Enum):
    Empty = 0
    Sun = 1
    Moon = 2


class TangoConnector(LinkedinGameConnector):

    def __init__(self, path_to_driver):
        super().__init__(path_to_driver, "https://linkedin.com/games/tango")
        self.tango_board = None

    def extract_board(self):
        # extract the shape
        board_elements = self.driver.find_element(By.CLASS_NAME, "lotka-grid")
        style_attribute = board_elements.get_attribute("style")
        str_row_col = re.findall(r'\d+', style_attribute)
        shape = tuple(map(int, str_row_col))
        self.tango_board = np.zeros(shape, dtype=int)

        # iterate through children
        for child in board_elements.find_elements(By.XPATH, './*'):
            if isinstance(child, str):
                continue
            # get the equals and moons fillings
            for child_2 in child.find_elements(By.XPATH, './*'):
                if isinstance(child_2, str):
                    continue
                pass


if __name__ == "__main__":
    dotenv.load_dotenv()
    tango_connector = TangoConnector(os.getenv('PATH_TO_GECKODRIVER'))
