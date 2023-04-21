"""
Responsable for handeling the user input and displaying the current GameState
"""

import pygame as p
import ChessEngine

p.init()
WIDTH = HEIGTH = 512 
DIMENSION = 8 #Dimension of the chess board of 8x8
SQ_SIZE = HEIGTH // DIMENSION
MAX_FSP = 15 #For animation later on
IMAGES = {}

"""
Initialize a global dictionary of images. This will be call one in the main    
"""
def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
        

"""
The main driver. This will handle user input and updating the graphics   
"""
def main():

    screen, clock, gs, validMoves, moveMade, running, sqSelected, playerClicks = init_ChessMain()
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() #(x, y) location of mouse
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): #the user clicked the same square twice (undo)
                    sqSelected = () #deselect
                    playerClicks = [] #clear player clicks
                else:
                    sqSelected = (row,col)
                    playerClicks.append(sqSelected)
                
                if len(playerClicks) == 2: #after second click
                    move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                    print(move.getChessNotation())
                    
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = () #reser user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
         
        if moveMade == True:
             validMoves = gs.getValidMoves()
             moveMade = False
                        
        drawGameState(screen, gs)        
        clock.tick(MAX_FSP)
        p.display.flip()

"""
Initialize the main driver
"""
def init_ChessMain():
    screen = p.display.set_mode((WIDTH,HEIGTH))
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState() #Game State (llama al estado del tablero) initialized in the standard starting position
    validMoves = gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    loadImages()
    running = True
    sqSelected = () #no square is selected, keep track of the last click of the user (tuple: row, col)
    playerClicks = [] #keeps track of player clicks (two tuples:[(),()])

    return screen, clock, gs, validMoves, moveMade, running, sqSelected, playerClicks


"""
Responsible for all the graphics within the current game state
"""
def drawGameState(screen,gs):
    drawBoard(screen) #Draw squares on the board
    drawPieces(screen, gs.board) #Draw pieces on top of the squares      

"""
Draw the squares on the board
"""
def drawBoard(screen):
    colors = [p.Color("white"), p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c)%2)]
            p.draw.rect(screen, color, p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))

"""
Draws the pieces in the board
"""
def drawPieces(screen, board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #Not empty space    
                screen.blit(IMAGES[piece], (c*SQ_SIZE, r*SQ_SIZE))
            

if __name__ == "__main__":
    main()
    
