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
    def __init__(self, path_to_driver, game_url):
        options = FirefoxOptions()
        self.driver = webdriver.Firefox(service=FirefoxService(executable_path=path_to_driver),
                                        options=options)
        self.driver.get(game_url)
        iframe = self.driver.find_element(By.CLASS_NAME, "game-launch-page__iframe")
        self.driver.switch_to.frame(iframe)
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(ec.element_to_be_clickable((By.ID, "ember19")))
        button.click()

        # click to close popup
        wait = WebDriverWait(self.driver, 10)
        button = wait.until(ec.element_to_be_clickable((By.CLASS_NAME, "artdeco-modal__dismiss")))
        button.click()

