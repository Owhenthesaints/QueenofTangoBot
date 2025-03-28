import re
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from bs4 import BeautifulSoup
import numpy as np

from linkedin_connector import LinkedinGameConnector
from queenssolver import QueensSolver


class OnlineConnectorQueens(LinkedinGameConnector):

    def __init__(self, path_to_driver):
        # open up driver
        super().__init__(path_to_driver, "https://linkedin.com/games/queens")

        self.queens : None | np.ndarray = None
        self.colors : None | np.ndarray = None

        self.extract_board()

        board_element_selenium = self.driver.find_element(By.ID, "queens-grid")


        self.list_of_squares = []
        # get a list of squares
        for child in board_element_selenium.find_elements(By.XPATH, './*'):
            self.list_of_squares.append(child)

    def extract_board(self):
        # take the dom
        dom = self.driver.page_source
        soup = BeautifulSoup(dom, 'html.parser')

        # get all the elements we need
        board_element = soup.find(id="queens-grid")
        style = board_element.get('style')
        str_row_col = re.findall(r'\d+', style)

        shape = tuple(map(int, str_row_col))
        self.colors = np.zeros(shape, dtype=int)
        # the queen is 1, impossible is 2
        self.queens = np.zeros(shape, dtype=int)

        # iterate through all the squares and get the color
        index = 0
        for square in board_element.children:
            # if string node ignore or if hidden cell
            if isinstance(square, str) or square.get('class')[0] == 'visually-hidden':
                    continue
            # look for color
            color_string = square.get('class')[1]
            self.colors[int(np.floor(index / shape[1]))][index % shape[0]] = int(
                re.search(r'\d+', color_string).group())

            # look for queen
            self.queens[int(np.floor(index / shape[1]))][index % shape[0]] = square.get('aria-label')[0:5] == 'Queen'
            index += 1

    def save_queens(self, str_name: str = 'queens'):
        np.save(str_name + '.npy', self.queens)

    def save_colors(self, str_name: str = 'colors'):
        np.save(str_name + '.npy', self.colors)

    def get_queens(self):
        return self.queens

    def solve_board(self, solved_queens, fill_crosses: bool = False):
        queen_indices = np.column_stack(np.where(solved_queens == 1))
        if fill_crosses:
            cross_indices = np.column_stack(np.where(solved_queens == 2))
            for index in cross_indices:
                self.click_square(index[0], index[1])

        for index in queen_indices:
            self.click_square(index[0], index[1])
            self.click_square(index[0], index[1])

    def get_colors(self):
        return self.colors

    def click_square(self, row, col):
        self.list_of_squares[row * self.colors.shape[1] + col].click()

    def left_click(self, row, col):
        self.list_of_squares[row * self.colors.shape[1] + col].click()



