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
from queenssolver import QueensSolver
from abc import ABC, abstractmethod

class LinkedinGameConnector(ABC):
    def __init__(self, path_to_driver, game_url, full_screen = True):
        # setup the page go to linkedin
        options = FirefoxOptions()

        if full_screen:
            options.add_argument("--start-fullscreen")
        else:
            options.add_argument("--width=800")
            options.add_argument("--height=600")

        self.driver = webdriver.Firefox(service=FirefoxService(executable_path=path_to_driver),
                                        options=options)
        self.driver.get(game_url)

        # switch to the right iframe
        iframe = self.driver.find_element(By.CLASS_NAME, "game-launch-page__iframe")
        self.driver.switch_to.frame(iframe)

        # click the start game button
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "artdeco-button--primary")))
        button.click()

        # click to close popup
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "artdeco-modal__dismiss")))
        button.click()

    @abstractmethod
    def extract_board(self):
        """
        Extract the board from the game
        :return:
        """
        pass

    def __del__(self):
        self.driver.quit()
