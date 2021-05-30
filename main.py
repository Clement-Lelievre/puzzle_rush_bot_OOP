# chess bot related imports
from bot import *
import chess
import chess.engine
from time import *

###########################################################################################################################
"This Python file opens a browser (Firefox) page to chess.com's puzzle rush page, logs in and solves puzzles"

with chess.engine.SimpleEngine.popen_uci("stockfish_13_win_x64_avx2") as engine:  # initiating a chess engine (Stockfish 13)
    bot = PuzzleRushBot() # instanciating a chess bot
    try:
        email, password = bot.get_credentials()
        bot.login(email, password)
        bot.click_play()
        time_start = time()
        sleep(4)  # wait for the 3 countdown seconds + time for the first move being played
        time_elapsed = time() - time_start
        # MAIN LOOP 
        while (time_elapsed < 305):  # puzzle rush lasts 5 min so I took just beyond 5min*60sec. A cleaner, more robust way to loop would be to parse the HTML and detect the end of the rush
            soup = bot.get_html()
            board_desc = bot.get_chessdotcom_board_desc(soup)
            fen = bot.chessdotcom_board_to_fen(board_desc, soup)
            best_move = bot.engine_best_move(engine, fen)
            bot.make_move(best_move, soup)
            time_elapsed = time() - time_start

    except Exception as e:
        print(f"Error encountered: {e}")
        bot.closedriver()

bot.make_screenshot()
sleep(5)
bot.closedriver()
