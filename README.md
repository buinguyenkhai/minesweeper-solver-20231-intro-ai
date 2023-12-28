# Minesweeper Solver

The primary codebase contains a replica version of the Microsoft Minesweeper for Windows XP, enhanced with four AI algorithms for solving the Minesweeper board.

#### Installation
You need to have Python installed on your machine. The project uses Pygame modules to create the Minesweeper game. To install the module, you can use a package manager like `pip`:
```
pip install pygame
```
#### Running the Game

The main script of the project is run_game.py. It can be run from the command line using the following command:
```
python main.py
```

Expected result
![Alt text](https://i.imgur.com/9M3WFUa.png)

Play -> Choose difficulty -> Choose solver to use

Left click: Open a tile

Right click: Flag/Unflag a tile

ESC: Return to main menu

### Analysis
If you wish to run the AI solver automatically for analysis, you can add these parameters as integers:
```
python main.py agent_type iter guess_method
```
guess_method is optional and only applicable for agent_type = 3

Example:
```
python main.py 3 100000 2
```
or
```
python main.py 2 100000
```
**The screen and fps has been disabled for maximum performance**

### Authors

Nguyen Trong Phuong Bach 20225473

Vu Minh Hieu 20225494

Bui Nguyen Khai 20225501

Tran Ngoc Quang 20225523

Nguyen Viet Tien 20225533

### Acknowledgments
[baraltech](https://youtu.be/GMBqjxcKogA?si=mwCa5cu7y11idoZ_) and [Tech & Gaming](https://youtu.be/n0jZRlhLtt0?si=Jp6tDBW5rqgg5vIl) for their pygame tutorials.

[Harvard's CS50](https://cs50.harvard.edu/ai/2020/projects/1/minesweeper/) and [enterpolation](https://github.com/enterpolation/Minesweeper-Solver) for the ideas of the solvers' logic.
