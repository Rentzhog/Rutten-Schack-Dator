
from cmu_graphics import *
from enum import Enum
from Settings import *
from Board import *
import time

class Side(Enum):
    WHITE = 0
    BLACK = 1

class Type(Enum):
    PAWN = 0
    KNIGHT = 2
    BISHOP = 4
    ROOK = 6
    QUEEN = 8
    KING = 10

class Piece:
    def __init__(self, x, y, side, type, board):
        self.b = board

        self.x = x
        self.y = y

        self.side = side
        self.type = type

        self.firstMove = True

        self.pinningPiece = None

    def move(self, tile):
        self.x = tile.x
        self.y = tile.y

    def copy(self):
        copy = type(self)(self.x, self.y, self.side, self.b)
        copy.firstMove = self.firstMove
        copy.pinningPiece = self.pinningPiece
        return copy

    def print(self):
        print('      -------PIECE-------')
        print('      Position: ', (self.x, self.y))
        print('      Side: ', self.side)
        print('      Type: ', self.type)
        print('      PinningPiece: ', self.pinningPiece)
        print('      -------PIECE-------')

    def getLegalMoves(self):
        # print(self.type)
        # s = time.time()
        moves = []

        for m in self.getPseudoLegalMoves():
            if(self.b.isLegalMove(m)):
                moves.append(m)

        # e = time.time()
        # print(e-s)
        # print('--------------------')
        return moves

class Pawn(Piece):
    def __init__(self, x, y, side, board):
        super().__init__(x, y, side, Type.PAWN, board)
        self.value = 10

    def getPseudoLegalMoves(self):
        moves = []
        ### move[0] = startSquare ### move[1] == targetSquare ###

        if(self.side == Side.WHITE): 
            dir = -1
        if(self.side == Side.BLACK):
            dir = 1
        
        steps = 1
        if(self.firstMove):
            steps *= 2
        
        for i in range(steps):
            if(self.b.coordsAreInBounds((self.x, self.y + dir * (i + 1)))):
                move = ((self.x, self.y), (self.x, self.y + dir * (i + 1)))
                if(not self.b.hasPieceOnTile(self.b.tiles[move[1][0]][move[1][1]])):
                    moves.append(move)
                else:
                    break
        
        moves += self.getPseudoLegalMovesDiag()

        return moves

    def getPseudoLegalMovesDiag(self):
        moves = []
        if(self.side == Side.WHITE): 
            dir = -1
        if(self.side == Side.BLACK):
            dir = 1

        if(self.b.coordsAreInBounds((self.x - 1, self.y + dir))):
            move = ((self.x, self.y), (self.x - 1, self.y + dir))
            moves.append(move)

        if(self.b.coordsAreInBounds((self.x + 1, self.y + dir))):
            move = ((self.x, self.y), (self.x + 1, self.y + dir))
            moves.append(move)

        return moves

class Knight(Piece):
    def __init__(self, x, y, side, board):
        super().__init__(x, y, side, Type.KNIGHT, board)
        self.value = 30

    def getPseudoLegalMoves(self):
        moves = []
        ### move[0] = startSquare ### move[1] == targetSquare ###

        for i in range(2):
            for j in range(-1, 2, 2):
                if(i == 0):
                    k = 2 * j
                else:
                    k = -2 * j
                if(self.b.coordsAreInBounds((self.x + j, self.y + k))):
                    move = ((self.x, self.y), (self.x + j, self.y + k))
                    movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
                    if(not(movePiece and movePiece.side == self.side and movePiece.type == Type.KING)):
                        moves.append(move)
                if(self.b.coordsAreInBounds((self.x + k, self.y + j))):
                    move = ((self.x, self.y), (self.x + k, self.y + j))
                    movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
                    if(not(movePiece and movePiece.side == self.side and movePiece.type == Type.KING)):
                        moves.append(move)
        return moves

class Bishop(Piece):
    def __init__(self, x, y, side, board):
        super().__init__(x, y, side, Type.BISHOP, board)
        self.value = 30

    def getPseudoLegalMoves(self):
        moves = []
        ### move[0] = startSquare ### move[1] == targetSquare ###

        for i in range(stepsToEdge(self.x, self.y, -1, -1)):
            move = ((self.x, self.y), (self.x - (i + 1), self.y - (i + 1)))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                    moves.remove(move)
                break

        for i in range(stepsToEdge(self.x, self.y, 1, -1)):
            move = ((self.x, self.y), (self.x + (i + 1), self.y - (i + 1)))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                    moves.remove(move)
                break

        for i in range(stepsToEdge(self.x, self.y, 1, 1)):
            move = ((self.x, self.y), (self.x + (i + 1), self.y + (i + 1)))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                    moves.remove(move)
                break

        for i in range(stepsToEdge(self.x, self.y, -1, 1)):
            move = ((self.x, self.y), (self.x - (i + 1), self.y + (i + 1)))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                    moves.remove(move)
                break

        return moves

class Rook(Piece):
    def __init__(self, x, y, side, board):
        super().__init__(x, y, side, Type.ROOK, board)
        self.value = 50

    def getPseudoLegalMoves(self):
        moves = []
        ### move[0] = startSquare ### move[1] == targetSquare ###

        for i in range(stepsToEdge(self.x, self.y, -1, 0)):
            move = ((self.x, self.y), (self.x - (i + 1), self.y))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                        moves.remove(move)
                break

        for i in range(stepsToEdge(self.x, self.y, 0, -1)):
            move = ((self.x, self.y), (self.x, self.y - (i + 1)))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                        moves.remove(move)
                break

        for i in range(stepsToEdge(self.x, self.y, 1, 0)):
            move = ((self.x, self.y), (self.x + (i + 1), self.y))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                    moves.remove(move)
                break

        for i in range(stepsToEdge(self.x, self.y, 0, 1)):
            move = ((self.x, self.y), (self.x, self.y + (i + 1)))
            moves.append(move)
            movePiece = self.b.tiles[move[1][0]][move[1][1]].piece
            if(self.b.isPseudoLegalMove(move)):
                if(movePiece and movePiece.type == Type.KING and movePiece.side != self.side):
                    continue
                if(movePiece and movePiece.type != Type.KING):
                    break
            else:
                if(movePiece.type == Type.KING):
                        moves.remove(move)
                break

        return moves

class Queen(Piece):
    def __init__(self, x, y, side, board):
        super().__init__(x, y, side, Type.QUEEN, board)
        self.value = 90

    def getPseudoLegalMoves(self):
        moves = []
        # ### move[0] = startSquare ### move[1] == targetSquare ###

        # for i in range(stepsToEdge(self.x, self.y, -1, 0)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x - (i + 1)][self.y])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, 0, -1)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x][self.y - (i + 1)])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, 1, 0)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x + (i + 1)][self.y])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, 0, 1)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x][self.y + (i + 1)])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, -1, -1)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x - (i + 1)][self.y - (i + 1)])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, 1, -1)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x + (i + 1)][self.y - (i + 1)])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, 1, 1)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x + (i + 1)][self.y + (i + 1)])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break

        # for i in range(stepsToEdge(self.x, self.y, -1, 1)):
        #     move = (self.b.tiles[self.x][self.y], self.b.tiles[self.x - (i + 1)][self.y + (i + 1)])
        #     moves.append(move)
        #     if(self.b.isPseudoLegalMove(move)):
        #         if(move[1].piece and move[1].piece.type == Type.KING and move[1].piece.side != self.side):
        #             continue
        #         if(move[1].piece and move[1].piece.type != Type.KING):
        #             break
        #     else:
        #         if(move[1].piece.type == Type.KING):
        #                 moves.remove(move)
        #         break
        
        moves.extend(Bishop.getPseudoLegalMoves(self))
        moves.extend(Rook.getPseudoLegalMoves(self))

        return moves

class King(Piece):
    def __init__(self, x, y, side, board):
        super().__init__(x, y, side, Type.KING, board)
        self.value = 900

    def getPseudoLegalMoves(self):
        moves = []
        ### move[0] = startSquare ### move[1] == targetSquare ###

        for dirX in range(-1, 2, 2):
            for dirY in range(-1, 2, 2):
                targetTileStraightCoords = (self.x + dirX, self.y + dirY)
                if(self.b.coordsAreInBounds(targetTileStraightCoords)):
                    move = ((self.x, self.y), (self.x + dirX, self.y + dirY))
                    moves.append(move)

                targetTileDiagCoords1 = (self.x + dirY, self.y)
                targetTileDiagCoords2 = (self.x, self.y + dirY)
                if(dirX == -1 and self.b.coordsAreInBounds(targetTileDiagCoords1)):
                    move2 = ((self.x, self.y), (self.x + dirY, self.y))
                    moves.append(move2)
                elif(dirX == 1 and self.b.coordsAreInBounds(targetTileDiagCoords2)):
                    move2 = ((self.x, self.y), (self.x, self.y + dirY))
                    moves.append(move2)

        return moves



