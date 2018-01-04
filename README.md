# python-tetris
Tetris Python 3.6

Game written using pygame library. Class Board is game model, generates new tetris-blocks, contains modules for moving, rotating etc.
have level and score attributes and controls what is happening on board using array where ints representing tetris blocks are being kept.
Class Board_View displays rectangles and score on a screen. Tetris-blocks are called 'items' consist of 4 blocks and each object has own ingcolour,
blocks XYs and int. Main loop handles pygame events. Levels increases every 500 points gained. Each level decreases time interval by 0,9.
Clearing rows calculations: full row ^ 2 * 50. Game screen size, number of blocks in column and row can be adjusted.

Game controls:
Arrows  - move, rotate\n
Space   - boost speed
ESC     - restart
(P       - pause game)

12.2017.
