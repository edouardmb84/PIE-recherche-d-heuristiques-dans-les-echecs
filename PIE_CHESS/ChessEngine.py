"""
Responsable for storing all the information of the chess game.
Responsable for determining a valid move in the current state.
"""

class GameState():
    def __init__(self):
        #8x8 2d list, each element has 2 characters.
        #The first character represents the color of the piece, 'b': black or 'w': white
        #The second character represents the type of the piece, 'K': king, 'Q': queen, 'B': bishop, 'N': knight, 'R': rook, 'P': pawn
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],]
        self.moveFunction = {'P':self.getPawnMoves, 'R':self.getRookMoves,
                             'N':self.getKnigthMoves, 'B':self.getBishopMoves,
                             'Q':self.getQueenMoves, 'K':self.getKingMoves}
        
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7,4)
        self.blackKingLocation = (0,4)
        self.inCheck = False
        self.pins = []
        self.checks = []
        
        
    '''
    Takes a Move as a parameter and executes it
    '''    
    def makeMove(self, move):
        #TODO: check that move is acceptable
        #->TODO: check that move is possible for that player
        #->TODO: check that move is legal
        #   ->TODO: if move is castling, castle
        
        #optional TODO: check that move.pieceMoved is the piece moved
        #optional TODO: check that move.pieceCaptured is the piece captured 
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        
        self.moveLog.append(move) #save the move so that we can change it
        self.whiteToMove = not self.whiteToMove #swap players
        #update king's location
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        #TODO: check and update self.inCheck, self.pins and self.checks? cf getValidMoves
        print("Do:", move)
        
    '''
    Undo the last move made
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:   #make sure that there is a move to undo
            move = self.moveLog.pop() #pop returns the last element of the list and removes it
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove #swap player to move
            #update king's location
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            print("Undo:", move.getChessNotation())
            #TODO: check and update self.inCheck, self.pins and self.checks? cf getValidMoves
        else:
            #no move to undo
            #optional TODO: check that you're at the starting position?
            #optional TODO: send message to inform of the reason for failure
            pass
            
            
    '''
    All the moves considering checks
    '''
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinAndChecks()
        
        if self.whiteToMove:
            kingRow = self.whiteKingLocation[0]
            kingCol = self.whiteKingLocation[1]
        else:
            kingRow = self.blackKingLocation[0]
            kingCol = self.blackKingLocation[1]
            
        if self.inCheck:
            if len(self.checks) == 1: 
                moves = self.getAllPossibleMoves()
                check = self.checks[0]
                checkRow = check[0]
                checkCol = check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == "N":
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1,8):
                        validSquare = (kingRow + check[2]*i, kingCol + check[3]*i)
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol:
                            break
                for i in range(len(moves) -1, -1, -1):
                    if moves[i].pieceMoved[1] != "K":
                        if not (moves[i].endRow, moves[i].endCol) in validSquares:
                            moves.remove(moves[i])     
            else:
                self.getKingMoves(kingRow, kingCol, moves)
        else:
            moves = self.getAllPossibleMoves()
                            
        
        return moves


    '''
    All the moves without considering checks
    '''
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)): #Number of rows
            for c in range(len(self.board[r])): #Number of columns given a row
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    self.moveFunction[piece](r, c, moves) #Calls the appropiate piece function
        return moves
    
    
    '''
    Get all the PAWN moves for a pawn in a given position
    '''                 
    def getPawnMoves(self, r, c, moves):
        
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break 
                
        if self.whiteToMove: #white pawn moves
            if self.board[r-1][c] == "--": #1 square pawn advance
                if not piecePinned or pinDirection == (-1,0):
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--": #2 square pawn advance
                        moves.append(Move((r, c), (r-2, c), self.board))
                    
            if c-1 > 0: 
                if self.board[r-1][c-1][0] == 'b' : #capture to the left
                    if not piecePinned or pinDirection == (-1, -1): 
                        moves.append(Move((r, c),(r-1, c-1),self.board))
            if c+1 < 8: 
                if self.board[r-1][c+1][0] == 'b' : #capture to the right
                    if not piecePinned or pinDirection == (-1, 1):
                        moves.append(Move((r, c),(r-1, c+1),self.board))
                    
        else: #black pawn moves
                if self.board[r+1][c] == "--": #1 square pawn advance
                    if not piecePinned or pinDirection == (1, 0):
                        moves.append(Move((r, c), (r+1, c), self.board))
                        if r == 1 and self.board[r+2][c] == "--": #2 square pawn advance
                            moves.append(Move((r, c), (r+2, c), self.board))
                        
                if c-1 > 0: #capture to the left
                    if self.board[r+1][c-1][0] == 'w' : #capture to the left 
                        if not piecePinned or pinDirection == (1, -1):
                            moves.append(Move((r, c),(r+1, c-1),self.board))
                if c+1 < 8:
                    if self.board[r+1][c+1][0] == 'w' : #capture to the right
                        if not piecePinned or pinDirection == (1, 1):
                            moves.append(Move((r, c),(r+1, c+1),self.board))
      
                  
    '''
    Get all the ROOK moves for a rook in a given postion
    '''
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != "Q":
                    self.pins.remove(self.pins[i])
                break
            
        directions = [(-1,0),(1,0),(0,-1),(0,1)]
        enemy = "b" if self.whiteToMove else "w" 
        for d in directions:
            for i in range(1,8):
                endRow = r + (d[0]*i)
                endCol = c + (d[1]*i)
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[endRow][endCol] == "--" :
                            moves.append(Move((r, c), (endRow, endCol), self.board))  
                        elif self.board[endRow][endCol][0] == enemy:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break 
                        else:
                            break
                else:
                    break                    
    
    
    '''
    Get all the BISHOP moves for a rook in a given postion
    '''
    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
            
        directions = [(-1,-1),(1,1),(1,-1),(-1,1)]
        enemy = "b" if self.whiteToMove else "w" 
        for d in directions:
            for i in range(1,8):
                endRow = r + (d[0]*i)
                endCol = c + (d[1]*i)
                if (0 <= endRow < 8) and (0 <= endCol < 8):
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        if self.board[endRow][endCol] == "--":
                            moves.append(Move((r, c), (endRow, endCol), self.board))  
                        elif self.board[endRow][endCol][0] == enemy:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else:
                            break
                else:
                    break             
    
    
    '''
    Get all the KNIGHT moves for a rook in a given postion
    '''
    def getKnigthMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins)-1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
            
        directions = [(-1,2),(-1,-2),(-2,-1),(-2,1),(1,-2),(2,-1),(2,1),(1,2)]
        enemy = "b" if self.whiteToMove else "w" 
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if (0 <= endRow < 8) and (0 <= endCol < 8):
                if not piecePinned:
                    if self.board[endRow][endCol] == "--" or self.board[endRow][endCol][0] == enemy:
                        moves.append(Move((r, c), (endRow, endCol), self.board))  
                
    
    '''
    Get all the QUEEN moves for a rook in a given postion
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r,c,moves)
        self.getBishopMoves(r,c,moves)
    
    
    '''
    Get all the KING moves for a rook in a given postion
    '''
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1,-1, -1, 0, 0 , 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = "w" if self.whiteToMove else "b"

        
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i] 
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    # pretend the king has moved for pins and checks
                    if allyColor == "w":
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                        
                    inCheck, pins, checks = self.checkForPinAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    
                    if allyColor == "w":
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)
        #TODO: Castling.
    
    
    """
    Return whether the player to move is in check, a list of pins and a list of checks
    """
    def checkForPinAndChecks(self):
        pins = [] #squares where the allied pinned piece is and direction pinned from                            
        checks = [] #squares from where enemy is applying a check
        inCheck= False
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1] 
        
        #check outward from king for pins and checks, keep track of pins
        directions = ((0,1),(0,-1),(1,0),(-1,0),(-1,-1),(-1,1),(1,-1),(1,1))
        for k in range(len(directions)):
            d = directions[k]
            possiblePin = () #reset possible pins
            for i in range(1,8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == (): #first allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else: #second allied piece so no pin in that direction
                             break
                    elif endPiece[0] == enemyColor:
                        typeName = endPiece[1]
                        if (0 <= k <= 3 and typeName == "R") or (4 <= k <= 7 and typeName == "B") or (i == 1 and typeName == "P" and ((enemyColor == "w" and 6 <= k <= 7) or (enemyColor == "b" and 4 <= k <= 5))) or (typeName == "Q") or (i == 1 and typeName == "K"):
                               if possiblePin == (): #No piece blocking, so check
                                   inCheck = True
                                   checks.append((endRow, endCol, d[0], d[1]))
                                   break
                               else: #Piece blocking, so pin
                                   pins.append(possiblePin)
                        else: #enemy piece not applying check
                            break
                else: #off board 
                    break       
        #check for knight checks
        knightMoves = ((-1,2),(-1,-2),(-2,-1),(-2,1),(1,-2),(2,-1),(2,1),(1,2))
        for j in knightMoves:
            endRow = startRow + j[0]
            endCol = startCol + j[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":
                    inCheck = True
                    checks.append((endRow, endCol, j[0], j[1]))
        
        return inCheck, pins, checks

    ### DEBUGGING ZONE ###
    # CRITICAL TODO: Write unitary tests for every function.
    #def testCheckForPinsAndChecks(self):


    ### END DEBUGGING ZONE
        
        
        
        
class Move():
    #Maps keys to values
    #key : value
    
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}
    
    def __init__(self, starSq, endSq, board):
        self.startRow = starSq[0]
        self.startCol = starSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False     
        
    def getChessNotation(self):
        #Not quite PGN format.
        if self.pieceCaptured != "--":
            EAT = True
        else:
            EAT = False
        if EAT:
            self.pieceMoved + self.getRankFile(self.startRow, self.startCol) + " x " + self.pieceCaptured + self.getRankFile(self.endRow, self.endCol)
        return self.pieceMoved + self.getRankFile(self.startRow, self.startCol) + " to " + self.getRankFile(self.endRow, self.endCol)

    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]
        