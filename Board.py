from tabnanny import check
from Settings import *
from cmu_graphics import *
from Piece import *
from math import inf
import time

class Tile:
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.piece = None

        self.glowColor = None

        self.checkedBy = []

    def print(self) -> str:
        print('   -------TILE---------')
        print('   X: ', self.x)
        print('   Y: ', self.y)
        print('   Checked by: ', )
        for p in self.checkedBy:
            p.print()
        if(self.piece):
            print('   Piece On Tile: ')
            self.piece.print()
        else:
            print('   Piece On Tile: ', self.piece)
        print('   -------TILE---------')

    def copy(self):
        piece = None
        if(self.piece):
            piece = self.piece.copy()
        copy = Tile(self.x, self.y)
        copy.piece = piece
        copy.checkedBy = self.checkedBy
        copy.glowColor = self.glowColor
        return copy

class Board:
    def __init__(self, playerSide):
        self.tiles = [[None for _ in range(BOARD_COLS)] for _ in range(BOARD_ROWS)]

        self.initializeTiles()

        self.playerSide = playerSide

        self.pieceSprites = []
        self.tileSprites = []

        self.previousMoves = []

        self.inCheck = None

        self.pieces = []

        self.blackScore = 0
        self.whiteScore = 0

        self.blackKingTile = None
        self.whiteKingTile = None

        self.selected = None
        self.turn = Side.WHITE

    def print(self):
        print('-------BOARD-------')
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                print('-----')
                self.tiles[x][y].print()
        print('-----')
        print('In Check: ', self.inCheck)
        if(self.selected):
            print('Current Selected Square:')
            self.selected.print()
        else:
            print('Current Selected Square: ', self.selected)
        print('Current Turn: ', self.turn)
        print('TileSprites: ', len(self.tileSprites))
        print('PieceSprites: ', len(self.pieceSprites))
        print('Pieces On Board: ', len(self.pieces))

        if(self.blackKingTile):
            print('Black King Tile:')
            self.blackKingTile.print()
        else:
            print('Black King Tile: ', self.blackKingTile)
        
        if(self.whiteKingTile):
            print('White King Tile:')
            self.whiteKingTile.print()
        else:
            print('White King Tile: ', self.whiteKingTile)

        print('All Pieces On Board: ')
        for p in self.pieces:
            p.print()

        print('-------BOARD-------')


    def drawBoard(self):
        
        for sprite in self.tileSprites:
            sprite.visible = False

        self.tileSprites = []

        for sprite in self.pieceSprites:
            sprite.visible = False

        self.pieceSprites = []

        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                if(self.selected == self.tiles[x][y]):
                    color = HIGHLIGHTED_TILE_COLOR
                # For debugging
                # elif(len(self.tiles[x][y].checkedBy) != 0):
                #     if((x + y) % 2 == 0):
                #         color = LIGHT_ALLOWEDMOVE_TILE_COLOR
                #     else:
                #         color = DARK_ALLOWEDMOVE_TILE_COLOR
                elif(self.selected and self.selected.piece and (x, y) in [i[1] for i in self.selected.piece.getLegalMoves()]):
                    if((x + y) % 2 == 0):
                        color = LIGHT_ALLOWEDMOVE_TILE_COLOR
                    else:
                        color = DARK_ALLOWEDMOVE_TILE_COLOR
                else:
                    if((x + y) % 2 == 0):
                        color = LIGHT_TILE_COLOR
                    else:
                        color = DARK_TILE_COLOR
                self.tileSprites.append(Rect(x * TILE_WIDTH, y * TILE_HEIGHT, TILE_WIDTH, TILE_HEIGHT, fill=color))

                piece = self.tiles[x][y].piece
                coords = convertToCoords(x, y)
                if(piece):
                    if(piece.side is Side.WHITE):
                        piece.b.pieceSprites.append(Image(PieceSprites[piece.type.value], coords[0] - TILE_WIDTH/2, coords[1] - TILE_HEIGHT/2, width=TILE_WIDTH, height=TILE_HEIGHT))
                    else:
                        piece.b.pieceSprites.append(Image(PieceSprites[piece.type.value + 1], coords[0] - TILE_WIDTH/2, coords[1] - TILE_HEIGHT/2, width=TILE_WIDTH, height=TILE_HEIGHT))

    def initializeTiles(self):
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                self.tiles[x][y] = Tile(x, y)

    def initializeBoard(self):
        self.calculateAllCheckedTiles()

    def createPiece(self, x, y, type, side):
        if(type == Type.PAWN):
            self.tiles[x][y].piece = Pawn(x, y, side, self)
            if(side == Side.WHITE):
                self.whiteScore += 10
            elif(side == Side.BLACK):
                self.blackScore += 10
        elif(type == Type.KNIGHT):
            self.tiles[x][y].piece = Knight(x, y, side, self)
            if(side == Side.WHITE):
                self.whiteScore += 30
            elif(side == Side.BLACK):
                self.blackScore += 30
        elif(type == Type.BISHOP):
            self.tiles[x][y].piece = Bishop(x, y, side, self)
            if(side == Side.WHITE):
                self.whiteScore += 30
            elif(side == Side.BLACK):
                self.blackScore += 30
        elif(type == Type.ROOK):
            self.tiles[x][y].piece = Rook(x, y, side, self)
            if(side == Side.WHITE):
                self.whiteScore += 50
            elif(side == Side.BLACK):
                self.blackScore += 50
        elif(type == Type.QUEEN):
            self.tiles[x][y].piece = Queen(x, y, side, self)
            if(side == Side.WHITE):
                self.whiteScore += 90
            elif(side == Side.BLACK):
                self.blackScore += 90
        elif(type == Type.KING):
            self.tiles[x][y].piece = King(x, y, side, self)
            if(side == Side.BLACK):
                self.blackScore += 900
                self.blackKingTile = self.tiles[x][y]
            elif(side == Side.WHITE):
                self.whiteScore += 900
                self.whiteKingTile = self.tiles[x][y]

        self.pieces.append(self.tiles[x][y])

    def selectTile(self, mx, my, cc):

        if(self.playerSide != self.turn):
            return

        mouseX = mx // TILE_WIDTH
        mouseY = my // TILE_HEIGHT

        x = int(mouseX)
        y = int(mouseY)

        mouseTile = self.tiles[x][y]

        # Check if piece is selected. If so, make move if legal
        if self.selected:
            tryMove = ((self.selected.x, self.selected.y), (mouseTile.x, mouseTile.y))
            if(tryMove in self.selected.piece.getLegalMoves()):
                self.makeMove(tryMove)
                self.selected = None
                bM = cc.minimax(cc.depth, -inf, inf, True, Side.BLACK)[0]
                if(bM == None):
                    print('checkmate')
                else:
                    self.makeMove(bM)
                return

        # If we click outside any legal moves, deselect the current selected tile
        if self.selected:
            self.selected = None

        # If we click on a tile which has a piece of our color, select it
        if(self.hasPieceOnTile(mouseTile) and mouseTile.piece.side == self.turn):
            self.selected = mouseTile

    def nextTurn(self):
        if(self.turn == Side.WHITE):
            self.turn = Side.BLACK
        else:
            self.turn = Side.WHITE

        # If no AI:
        # if(self.playerSide == Side.WHITE):
        #     self.playerSide = Side.BLACK
        # else:
        #     self.playerSide = Side.WHITE
        
    def hasPieceOnTile(self, tile):
        if(tile.piece):
            return True
        return False

    def coordsAreInBounds(self, coords):
        x = coords[0]
        y = coords[1]
        if(x >= 0 and x <= BOARD_COLS-1 and y >= 0 and y <= BOARD_ROWS-1):
            return True
        return False

    def hasEnemyOnTile(self, tile, side):
        if(self.hasPieceOnTile(tile) and tile.piece.side != side):
            return True
        return False

    def getMovesInLine(self, startTile, endTile):
        dirX = endTile.x - startTile.x
        dirY = endTile.y - startTile.y

        piece = self.tiles[startTile.x][startTile.y].piece

        if(piece.type == Type.BISHOP and (dirX == 0 or dirY == 0 or dirY/dirX != 1 or dirY/dirX != -1)):
            return False, [], []
        if(piece.type == Type.ROOK and (dirX != 0 and dirY != 0)):
            return False, [], []
        if(piece.type == Type.QUEEN and (dirX == 0 or dirY == 0 or dirY/dirX != 1 or dirY/dirX != -1) and (dirX != 0 and dirY != 0)):
            return False, [], []

        if(dirX == 0):
            steps = abs(dirY)
        elif(dirY == 0):
            steps = abs(dirX)
        else:
            steps = abs(dirX)

        dirX = sign(dirX)
        dirY = sign(dirY)

        moves = []
        piecesInLine = []
        for i in range(steps - 1):
            if(self.coordsAreInBounds((startTile.x + dirX * (i + 1), startTile.y + dirY * (i + 1)))):
                move = self.tiles[startTile.x + dirX * (i + 1)][startTile.y + dirY * (i + 1)]
                if(move.piece):
                    piecesInLine.append(move.piece)
                moves.append(move)

        return True, moves, piecesInLine

    def isLegalMove(self, move):
        startTile = self.tiles[move[0][0]][move[0][1]]
        targetTile = self.tiles[move[1][0]][move[1][1]]
        movingPiece = startTile.piece

        if(targetTile.piece and targetTile.piece.side == movingPiece.side):
            return False

        if(movingPiece.side == Side.BLACK):
            king = self.blackKingTile
        elif(movingPiece.side == Side.WHITE):
            king = self.whiteKingTile

        checkingPieces = []

        for p in king.checkedBy:
            if(p.side != movingPiece.side):
                checkingPieces.append(p)
        
        if(movingPiece.type == Type.PAWN):
            if(not self.hasPieceOnTile(targetTile) and targetTile.x != startTile.x):
                return False
        if(not king):
            return True

        if(len(checkingPieces) == 0 and movingPiece.type != Type.KING and not movingPiece.pinningPiece):
            return True
        
        if(movingPiece.type == Type.KING):
            for piece in targetTile.checkedBy:
                if(piece.side != movingPiece.side):
                    return False
            return True
        else:

            if(len(checkingPieces) > 1):
                return False

            if(movingPiece.pinningPiece):
                if(movingPiece.type == Type.KNIGHT or movingPiece.type == Type.PAWN):
                    return False

                dirX = sign(movingPiece.pinningPiece.x - movingPiece.x)
                dirY = sign(movingPiece.pinningPiece.y - movingPiece.y)

                moveDirX = sign(targetTile.x - startTile.x)
                moveDirY = sign(targetTile.y - startTile.y)

                if((moveDirX == dirX and moveDirY == dirY) or (moveDirX * -1 == dirX and moveDirY * -1 == dirY)):
                    if(len(checkingPieces) == 0):
                        return True
                    else:
                        return False
                else:
                    return False

            checkingPiece = checkingPieces[0]
            if(checkingPiece.type == Type.KNIGHT or checkingPiece.type == Type.PAWN):
                if(targetTile == self.tiles[checkingPiece.x][checkingPiece.y]):
                    return True
                else:
                    return False

            dirToKingFromCp = (king.x - checkingPiece.x, king.y - checkingPiece.y)
            dirToKingFromTt = (king.x - targetTile.x, king.y - targetTile.y)

            if(dirToKingFromCp[0] == 0):
                ratioCp = 0
            else:
                ratioCp = dirToKingFromCp[1]/dirToKingFromCp[0]
            
            if(dirToKingFromTt[0] == 0):
                ratioTt = 0
            else:
                ratioTt = dirToKingFromTt[1]/dirToKingFromTt[0]

            relX1 = king.x - checkingPiece.x
            relY1 = king.y - checkingPiece.y

            relX2 = king.x - targetTile.x
            relY2 = king.y - targetTile.y

            if(ratioCp == ratioTt and abs(relX2) <= abs(relX1) and abs(relY2) <= abs(relY1) and sign(relX1) == sign(relX2) and sign(relY1) == sign(relY2)):
                return True
            else:
                return False

    def isPseudoLegalMove(self, move):
        startTile = self.tiles[move[0][0]][move[0][1]]
        targetTile = self.tiles[move[1][0]][move[1][1]]

        if(not self.hasPieceOnTile(targetTile) or self.hasEnemyOnTile(targetTile, startTile.piece.side)):
            return True
        return False

    def calculateAllCheckedTiles(self):
        self.inCheck = None
        for x in range(BOARD_COLS):
            for y in range(BOARD_ROWS):
                self.tiles[x][y].checkedBy = []
                if(self.tiles[x][y].piece):
                    self.tiles[x][y].piece.pinningPiece = None

        for tile in self.pieces:     
            piece = tile.piece
            if(piece.type == Type.PAWN):
                for move in piece.getPseudoLegalMovesDiag():
                    self.tiles[move[1][0]][move[1][1]].checkedBy.append(piece)
                    # if(move[1].piece and move[1].piece.type == Type.KING):
                    #     self.inCheck = move[1].piece
            else:
                if(piece.type == Type.BISHOP or piece.type == Type.ROOK or piece.type == Type.QUEEN):
                    if(piece.side == Side.BLACK):
                        king = self.whiteKingTile
                    elif(piece.side == Side.WHITE):
                        king = self.blackKingTile
                    hasLine, moves, piecesInLine = self.getMovesInLine(tile, king)
                    if(hasLine and len(piecesInLine) == 1):
                        pieceInLine = piecesInLine[0]
                        pieceInLine.pinningPiece = piece

                for move in piece.getPseudoLegalMoves():
                    self.tiles[move[1][0]][move[1][1]].checkedBy.append(piece)
                    # if(move[1].piece and move[1].piece.type == Type.KING):
                    #     self.inCheck = move[1].piece


    def calculateCheckedTilesNew(self):
        pass

    def getMoves(self, side):
        moves = []
        for tile in self.pieces:
            if(tile.piece.side == side):
                moves.extend(tile.piece.getLegalMoves())

        return list(set(moves))

    def makeMove(self, move):
        # app.num += 1
        # print(app.num)

        startTile = self.tiles[move[0][0]][move[0][1]]
        targetTile = self.tiles[move[1][0]][move[1][1]]

        previousState = {
            "startTile": (startTile, startTile.copy()),
            "targetTile": (targetTile, targetTile.copy()),
            "blackScore": self.blackScore,
            "whiteScore": self.whiteScore
            }

        self.previousMoves.append(previousState)

        movingPiece = startTile.piece

        startTile.piece = None
        if(startTile in self.pieces):
            self.pieces.remove(startTile)
            self.pieces.append(targetTile)
        startTile.selected = False

        movingPiece.move(targetTile)
        movingPiece.firstMove = False

        if(movingPiece.type == Type.KING):
            if(movingPiece.side == Side.BLACK):
                self.blackKingTile = targetTile
            elif(movingPiece.side == Side.WHITE):
                self.whiteKingTile = targetTile
                
        if(targetTile.piece):
            self.pieces.remove(targetTile)

        targetTile.piece = movingPiece
        
        ### CHECK FOR PAWN PROMOTION ###

        ### CHECK FOR CHECKMATE ###
        ### CHECH FOR STALEMATE ###
        self.calculateAllCheckedTiles()
        # print(e - s)
        self.nextTurn()

    def unMakePrevMove(self):
        if(len(self.previousMoves) != 0):
            self.selected = None
            prevState = self.previousMoves.pop()

            startTileX = prevState["startTile"][0].x
            startTileY = prevState["startTile"][0].y
            self.tiles[startTileX][startTileY] = prevState["startTile"][1]
            self.pieces.append(self.tiles[startTileX][startTileY])
            if(self.tiles[startTileX][startTileY].piece.type == Type.KING):
                if(self.tiles[startTileX][startTileY].piece.side == Side.BLACK):
                    self.blackKingTile = self.tiles[startTileX][startTileY]
                elif(self.tiles[startTileX][startTileY].piece.side == Side.WHITE):
                    self.whiteKingTile = self.tiles[startTileX][startTileY]

            targetTileX = prevState["targetTile"][0].x
            targetTileY = prevState["targetTile"][0].y
            self.pieces.remove(self.tiles[targetTileX][targetTileY])
            self.tiles[targetTileX][targetTileY] = prevState["targetTile"][1]
            if(self.tiles[targetTileX][targetTileY].piece):
                self.pieces.append(self.tiles[targetTileX][targetTileY])

            self.blackScore = prevState["blackScore"]
            self.whiteScore = prevState["whiteScore"]

            self.calculateAllCheckedTiles()

            self.nextTurn()
        else:
            print('No Previous Moves Availabe')

    def evaluate(self):
        totEval = 0
        for tile in self.pieces:
            if(tile.piece.side == Side.WHITE):
                totEval -= tile.piece.value
            else:
                totEval += tile.piece.value
        return totEval



        
