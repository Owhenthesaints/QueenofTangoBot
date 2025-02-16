import time

from online_connector_queens import OnlineConnectorQueens
from queenssolver import QueensSolver
import dotenv
import os

if __name__ == "__main__":
    dotenv.load_dotenv()

    connector = OnlineConnectorQueens(os.getenv('PATH_TO_GECKODRIVER'))

    colors = connector.get_colors()
    queens = connector.get_queens()

    solver = QueensSolver(colors, queens)
    solver.solve()
    solved_queens = solver.get_queens()

    connector.solve_board(solved_queens)

    while True:
        time.sleep(1)
