import time

from online_connector_queens import OnlineConnectorQueens
from queenssolver import QueensSolver
import dotenv
import os


if __name__ == "__main__":
    dotenv.load_dotenv()

    connector = OnlineConnectorQueens(os.getenv('PATH_TO_GECKODRIVER'))
    connector.save_queens('hard_queens')
    connector.save_colors('hard_colors')

