# chess engine - related imports
import chess
import chess.engine

# browser related imports
from selenium import webdriver
from bs4 import BeautifulSoup
import pyautogui  # for mouse clicking when it is inconvenient to do so with Selenium
from time import *
import datetime

# defining a few variables that'll be needed thereafter
color_dict = {"w": True, "b": False}
type_dict = {"p": 1, "n": 2, "b": 3, "r": 4, "q": 5, "k": 6}


def get_squares_dict():
        """Creates a dictionary where the conversion is made between Stockfish square notation and chessdotcom HTML square notation"""
        squares_dict = {}
        columns = ["a", "b", "c", "d", "e", "f", "g", "h"]
        for row in range(1, 9):
            for letter in columns:
                squares_dict[letter + str(row)] = (
                    "square-" + str(columns.index(letter) + 1) + str(row)
                )
        return squares_dict, list(squares_dict.values())
squares_dict, l = get_squares_dict()

class PuzzleRushBot():
    '''The blueprint for the bot that plays puzzle rush'''
    # def __init__(self):
    #     pass # this bot has many methods but does not really require attributes

    def get_credentials(self):
        with open("credentials.txt") as f:
            content = f.readlines()
        creds = [line.strip() for line in content if not "#" in line]
        return creds[0], creds[1]


    def login(self, email, password, driver):
        driver.get("https://www.chess.com/login")
        driver.maximize_window()
        driver.fullscreen_window()  # this is like pressing the shortcut key F11
        username = driver.find_element_by_id("username")
        username.click()
        username.send_keys(email)
        pwd = driver.find_element_by_id("password")
        pwd.click()
        pwd.send_keys(password)
        log = driver.find_element_by_id("login")
        log.click()
        sleep(1)
        banner = driver.find_elements_by_class_name("icon-font-chess x")
        for cross in banner:
            cross.click()
        driver.get("https://www.chess.com/puzzles/rush")
        sleep(1)
        # now a few precautions to remove potentially annoying banners or pop-ups:
        annoying_banner = driver.find_elements_by_class_name("icon-font-chess x")
        for item in annoying_banner:
            try:
                item.click()
            except:
                pass
        try:
            bg = driver.find_elements_by_class_name("core-modal-background")
            for item in bg:
                try:
                    item.click()
                except:
                    continue
        except:
            pass
        try:
            a = driver.find_element_by_partial_link_text("Sauter l'essai")
            a.click()
        except:
            pass
        try:
            a = driver.find_elements_by_class_name(
                "icon-font-chess x ui_outside-close-icon"
            )
            for item in a:
                try:
                    item.click()
                except:
                    continue
        except:
            pass
        try:
            a = driver.find_elements_by_class_name("icon-font-chess x")
            for item in a:
                try:
                    item.click()
                except:
                    continue
        except:
            pass
        try:
            a = driver.find_elements_by_class_name("core-modal-background")
            for item in a:
                try:
                    a.click()
                except:
                    continue
        except:
            pass
        sleep(5)  # this leaves time for a human to click potential additional banners
        
    def click_play(self, driver):
        play_button = driver.find_element_by_class_name(
            "ui_v5-button-component.ui_v5-button-primary.ui_v5-button-large.ui_v5-button-full")
        play_button.click()
        try:
            a = driver.find_element_by_class_name("wrapper svelte-362hqn")
            a.click()
            print("removed the cookies banner successfully")
        except:
            pass
        
    def get_html(self, driver):
        return BeautifulSoup(driver.page_source, "html.parser")

    def fill_pieces(self, stuff):
        '''needed to get the pieces info'''
        return stuff["class"][1:]

    def get_chessdotcom_board_desc(self, soup):
        """Scrapes the HTML content of the puzzle rush current page, and returns the board position (which pieces on which squares)"""
        chesscom_board_desc = list(map(self.fill_pieces,
                [
                    stuff
                    for item in soup.find_all(id="board-board")
                    for stuff in item.find_all("div")
                ],
            )
        )
        chesscom_board_desc = [
            item for item in chesscom_board_desc if len(item) == 2
        ]  # for some reason it won't let me do a one-liner list comprehension
        # the len() thing is because the highlighted squares from the last move appear even without pieces on it, so I need to remove them

        # chesscom_board_desc = []
        # for item in soup.find_all(id='board-board'):
        #     for stuff in item.find_all('div'):
        #         chesscom_board_desc.append(stuff['class'][1:])
        for item in chesscom_board_desc:
            try:
                if "square" in item[1]:
                    item.reverse()  # this is performed in place (even on copies)
            except:
                continue
        return chesscom_board_desc

    def is_black_turn(self, soup):
        '''Returns whether it is white (False) or black (True) to move in the position that is in the HTML (soup) given as argument.'''
        try:
            return not not list(soup.find(class_="board flipped"))
        except: # I don't care about the error message
            return False

    def chessdotcom_board_to_fen(self, board_desc, soup):
        """Receives a chess board description as is currently (May 2021) used by chess.com in the puzzle rush page HTML,
        and processes it to setup the position on Stockfish"""
        board = chess.Board(fen=None)  # creating an empty board
        for item in board_desc: # setting up each piece one after another
            piece = chess.Piece(type_dict[item[1][1]], color_dict[item[1][0]])
            board.set_piece_at(l.index(item[0]), piece)
        if PuzzleRushBot.is_black_turn(self,soup):  # determines the side to move by looking at presence or not of "flipped board" in chess.com HTML
            board.turn = False
        else:
            board.turn = True
        return board.fen()

    def engine_best_move(self, engine, fen, time=0.1):
        """input: a FEN / output: the best move in the position according to Stockfish 13's neural network under the given time constraint (in ms)"""
        board = chess.Board(fen)
        info = engine.analyse(board, chess.engine.Limit(time=time))
        return str(info["pv"][0])

    def make_move(self, best_move, soup):
        best_move_start_square = squares_dict[best_move[:4][:2]][-2:]
        best_move_destination_square = squares_dict[best_move[:4][2:]][-2:]
        if PuzzleRushBot.is_black_turn(self, soup):  # board is flipped, so I need to adapt the coordinates that I pass to pyautogui.click()
                best_move_start_square = str(9 - int(best_move_start_square[0])) + str(9 - int(best_move_start_square[1]))
                best_move_destination_square = str(9 - int(best_move_destination_square[0])) + str(9 - int(best_move_destination_square[1]))
        pyautogui.click(
                262 + 130 * (int(best_move_start_square[0]) - 1),
                87 + 130 * 8 - 130 * (int(best_move_start_square[1])),
            )
        pyautogui.click(
            262 + 130 * (int(best_move_destination_square[0]) - 1),
            87 + 130 * 8 - 130 * (int(best_move_destination_square[1])),
        )
        if (
            len(best_move) > 4
        ):  # meaning the move is a promotion and thus ends with a piece symbol (ex: "d7d8q"). Thus I need to click on queen (I don't consider underpromotion yet)
            pyautogui.click(
                262 + 130 * (int(best_move_destination_square[0]) - 1),
                87 + 130 * 8 - 130 * (int(best_move_destination_square[1])),
            )
        sleep(
            1
        )  # this one is crucial to avoid the error "engine process died unexpectedly (exit code: 3221225477)"
    
    def make_screenshot(self, driver):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        screenshot_name = f"scores_screenshots/{now}.png"
        driver.save_screenshot(screenshot_name)

    def closedriver(self, driver):
        driver.quit()