[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

# My puzzle-rush bot

This repo contains my OOP implementation of my ![puzzle rush bot](https://github.com/Clement-Lelievre/puzzle_rush_bot)

![](https://github.com/Clement-Lelievre/puzzle_rush_bot_OOP/blob/master/youtube-video-gif.gif)   

![](https://github.com/Clement-Lelievre/puzzle_rush_bot_OOP/blob/master/scores_screenshots/2021-06-01_10-05-06.png)   

## Description 

A bot coded in Python that plays puzzle rush on chess.com. 
Puzzle rush is a popular game where the player has to solve as many chess puzzles in exactly 5 minutes as possible. 
Currently the best humans on the planet perform at about 50 to 55 puzzles.


It performs the following actions:
- opens a browser (Firefox)
- visits chess.com, removes annoying banners then logs in (you need your own credentials*)
- visits the puzzle rush page and clicks "Play"
- cracks puzzles one after the other* (sometimes it might fail a problem)
- once the 5 minutes countdown elapsed or if game aborted due 3 failures, takes a screenshot of its score and saves it locally in the appropriate folder

Do not forget to include your own chess.com credentials else below method will fail:

```python
class PuzzleRushBot():
    '''The blueprint for the bot that plays puzzle rush'''
    # def __init__(self):
    #     pass # this bot has many methods but does not really require attributes

    def get_credentials(self):
        with open("credentials.txt") as f:
            content = f.readlines()
        creds = [line.strip() for line in content if not "#" in line]
        return creds[0], creds[1]
```

## * Here is how it proceeds to solve puzzles:
It loops over the following workflow:
- parses the HTML in order to get which pieces are on which squares (it disregards castling and en passant rights at this stage; I might add this later) => selenium & beautiful soup
- processes that information (make a FEN) to convert it to Stockfish lingo => ad hoc functions
- passes the position FEN description to the Stockfish neural network, which in turn provides its best move => python-chess and ad hoc functions
- this best move is defined as a start and end square, hence pyautogui is used to click on these in order to actually complete the move
- repeats till game is over

There were several challenges, including:
- removing the annoying banners
- find the relevant piece and square data in the HTML and convert that into Stockfish-digestible language
- finetune the waiting times so as to maximize speed while preventing any crashes

OS: Windows 10
Launched via Powershell.
There is still much room for improvement as this is only a first version. 
- for example, using WebDriverWait... in selenium would be better than time.sleep() as it i more robust
- I noticed that my program is faster at making the first move of each challenge than the remaining moves and cannot understand why yet
- -generally speaking, I'm sure the program can be made faster

## Files and directories

- The main file is obvisouly main.py => just run
``` bash
python main.py
```
- bot.py contains the class **PuzzleRushBot** that has all the tailored methods I created
- stockfish_13_win_x64_avx2.exe is the chess engine
- scores_screenshots is the directory where screenshots of scores are saved

## Steps required to install the project

- the firefox driver for Selenium (this requires to add Geckodriver to PATH)
- the stockfish engine executable (to be placed in the same directory as the main Python file)
 ``` bash
pip install -r requirements.txt
```

## Warnings: 
- you may have to disable manually the cookies-related banner at the bottom of the page else clicks due to happen on the first rank will fail; moreover disable the squares highlighting and legal moves highlighting (else, parsing the HTML may fail.). Leave the coordinates inside board and set animation type to FAST.

- The program does not account yet for underpromotions, castling or en passant rights but can still solve most puzzles. 

- some of the clicks are not robust: while clicking on "Log in" and "Play" buttons is done via selenium (so, it is robust in the sense that it uses the HTML), clicking on the squares while making a move is done via pyautogui, because playing the move by clicking via selenium was too inconvenient.
Hence, this program is calibrated for a specific screen size (1920,1080). If your screen size is different, you need to adapt the coordinates of the points that are clicked (the squares) in main.py

- you cannot try accelerating the program by reducing the time.sleep() as this will induce "engine process died unexpectedly (exit code: 3221225477)"

Please use this program responsibly and respect chess.com terms of use.

## Credits

I obviously did not code a chess engine myself... Kudos to the Stockfish team.
