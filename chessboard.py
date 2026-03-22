import pygame

#this fucking file-fiding mechanic is so stupid it just try to find the file
#  in the current working directory(CWD) instead of the parent folder of .py file.
# so we need to reset it
import os 
import sys
script_path=os.path.dirname(os.path.abspath(__file__))
os.chdir(script_path)

import copy #goddamn it we need to deal with deep copy

pygame.init()
screen=pygame.display.set_mode((1280,720))
clock=pygame.time.Clock()
running=True
dt=0

promote_position=(-1,-1)# need to konw (y,x)

class GameState():
    NORMAL=0
    PROMOTING=1
    CHECKMATE=2
current_state=GameState.NORMAL

#here we need to set some constants
SQUARESIZE=80
#this is used to draw the lefttop point of the whole board
SQUAREORIGIN=[0,0]
#mind that sets are unordered so I can't just "for in" it.
SQUARE_DIC=["space","moveto","bP","wP","bR","wR","bN","wN","bB","wB","bQ","wQ","bK","wK"]
IMAGES={}
selecting=False
turn="w"

#seems it should be two layers...
board=[["space" for _ in range(8)] for _ in range(8)]
layout=[["bR","bN","bB","bQ","bK","bB","bN","bR"],
       ["bP","bP","bP","bP","bP","bP","bP","bP"],
       ["space","space","space","space","space","space","space","space"],
       ["space","space","space","space","space","space","space","space"],
       ["space","space","space","space","space","space","space","space"],
       ["space","space","space","space","space","space","space","space"],
       ["wP","wP","wP","wP","wP","wP","wP","wP"],
       ["wR","wN","wB","wQ","wK","wB","wN","wR"]]#we use this for piece_matrix
#load images and set sizes (maybe this could be simplified?we need classified png here)
for piece in SQUARE_DIC:
    if piece=="space" or piece=="moveto":
        pass
    else:
        file_path=f"{piece}.png"
        tempt_image=pygame.image.load(file_path).convert_alpha()
        IMAGES[piece]=pygame.transform.scale(tempt_image,(SQUARESIZE,SQUARESIZE))


#use coordination to draw different pieces. map(0,0)to a8,abc to y,876tox
# that's how pygame works.the board is divided into 100x100-pixel squares
#x,y is int, piece_name is string
def render_piece(x,y,piece_name):
    screen.blit(IMAGES[piece_name],(SQUAREORIGIN[0]+x*SQUARESIZE,SQUAREORIGIN[1]+y*SQUARESIZE))
#use this to draw the board accoring to the variable 'board'
def render_board():
    for i in range(8):#876
        for j in range(8):#abc
            if board[i][j]=="space":
                if (i+j)%2==1:
                    pygame.draw.rect(screen,(50,50,50),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))
                else:
                    pygame.draw.rect(screen,(255,255,255),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))
            elif board[i][j]=="moveto":#there is no else if in python...jesus
                if (i+j)%2==1:
                    pygame.draw.rect(screen,(50,50,255),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))
                else:
                    pygame.draw.rect(screen,(200,200,255),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))

            if piece_matrix[i][j]!="space":
                render_piece(j,i,f"{piece_matrix[i][j].color}{piece_matrix[i][j].type_char}")

def render_pormotion_bar(coordinationy,coordinationx,color):#this coordination is of the pawn
    if color=="w":
        pygame.draw.rect(screen,(255,215,0),(SQUAREORIGIN[0]+(coordinationx+1)*SQUARESIZE,SQUAREORIGIN[1]+coordinationy*SQUARESIZE,SQUARESIZE,SQUARESIZE*4))
        render_piece(coordinationx+1,coordinationy,f"{color}Q")
        render_piece(coordinationx+1,coordinationy+1,f"{color}R")
        render_piece(coordinationx+1,coordinationy+2,f"{color}B")
        render_piece(coordinationx+1,coordinationy+3,f"{color}N")
    elif color=="b":
        pygame.draw.rect(screen,(255,215,0),(SQUAREORIGIN[0]+(coordinationx+1)*SQUARESIZE,SQUAREORIGIN[1]+(coordinationy-3)*SQUARESIZE,SQUARESIZE,SQUARESIZE*4))
        render_piece(coordinationx+1,coordinationy,f"{color}Q")
        render_piece(coordinationx+1,coordinationy-1,f"{color}R")
        render_piece(coordinationx+1,coordinationy-2,f"{color}B")
        render_piece(coordinationx+1,coordinationy-3,f"{color}N")
#we use this to check if a square can be attacked by any piece in one color
#for convinience sake, color means the side which will be attacked, as "w" we will check if there is a "b" piece is attacking
def is_attacked(x,y,color,matrix):
    #1.first we detect Pawn
    forwardone=-1 if color=="w" else 1
    #take diagnally
    if (0<=y+forwardone<=7 and 0<=x-1<=7
        and matrix[y+forwardone][x-1]!="space" 
        and matrix[y+forwardone][x-1].color!=color
        and matrix[y+forwardone][x-1].type_char=="P"):
        return True
    if (0<=y+forwardone<=7 and 0<=x+1<=7
        and matrix[y+forwardone][x+1]!="space" 
        and matrix[y+forwardone][x+1].color!=color
        and matrix[y+forwardone][x+1].type_char=="P"):
        return True
    #2. second we check sliding pieces. Here we can simultaniously check Queen
    offset=[(0,1),(0,-1),(-1,0),(1,0)]
    for (x0,y0) in offset:# BE AWARE THAT there is no need to if "w" elif "b",we just need to judge the color is diffrent or not
        to_x=x+x0
        to_y=y+y0
        while(0<=to_x<=7 and 0<=to_y<=7 and (matrix[to_y][to_x]=="space" or matrix[to_y][to_x].color!=color)):
            if( matrix[to_y][to_x]!="space" and matrix[to_y][to_x].color!=color 
            and (matrix[to_y][to_x].type_char=="R" or matrix[to_y][to_x].type_char=="Q" )):
                return True
            to_x+=x0
            #(to_x,to_y)+=(x,y) seens won't work
            to_y+=y0
    #3. then bishop
    offset=[(1,1),(1,-1),(-1,1),(-1,-1)]    
    for (x0,y0) in offset:
        to_x=x+x0
        to_y=y+y0
        while(0<=to_x<=7 and 0<=to_y<=7 and (matrix[to_y][to_x]=="space" or matrix[to_y][to_x].color!=color)):
            if( matrix[to_y][to_x]!="space" and matrix[to_y][to_x].color!=color 
            and (matrix[to_y][to_x].type_char=="B" or matrix[to_y][to_x].type_char=="Q" )):
                return True
            to_x+=x0
            #(to_x,to_y)+=(x,y) seens won't work
            to_y+=y0
    #4. Knight
    offset=[(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
    for (x0,y0) in offset:
        if color=="w":
            if (0<=y+y0<=7 and 0<=x+x0<=7 
                and matrix[y+y0][x+x0]!="space"
                and matrix[y+y0][x+x0].color=="b"
                and matrix[y+y0][x+x0].type_char=="N"):
                return True
        elif color=="b":
            if (0<=y+y0<=7 and 0<=x+x0<=7 
                and matrix[y+y0][x+x0]!="space" 
                and matrix[y+y0][x+x0].color=="w"
                and matrix[y+y0][x+x0].type_char=="N"):
                return True
    #5. King
    offset=[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
    for (x0,y0) in offset:
        to_x=x+x0
        to_y=y+y0
        if (0<=to_x<=7 and 0<=to_y<=7 
            and matrix[to_y][to_x]!="space" 
            and color!=matrix[to_y][to_x].color
            and matrix[to_y][to_x].type_char=="K"):
            return True
    return False
                
def is_checkmate(color,matrix):
    valid_moves=[]
    for i in range(8):
        for j in range(8):
            if matrix[i][j]!="space" and matrix[i][j].color==color:
                piece=matrix[i][j]
                possible_moves=piece.get_move_squares(matrix)
                
                for (my,mx) in possible_moves:
                    temp_matrix=copy.deepcopy(matrix)
                    #here we move, note that we move the piece in temp_matrix
                    old_x=piece.coordinationx
                    old_y=piece.coordinationy
                    temp_matrix[old_y][old_x].coordinationx=mx
                    temp_matrix[old_y][old_x].coordinationy=my
                    temp_matrix[my][mx]=temp_matrix[old_y][old_x]
                    temp_matrix[old_y][old_x]="space"
                    #here we check
                    for i in range(8):
                        for j in range(8):
                            if (temp_matrix[i][j]!="space" and temp_matrix[i][j].type_char=="K" 
                                and temp_matrix[i][j].color==piece.color and is_attacked(j,i,temp_matrix[i][j].color,temp_matrix)==False):
                                valid_moves.append((my,mx))
    if len(valid_moves)==0:
        return True
    return False

#in order to allow pieces to move naturally, we need class-based programming

#there is one big problem that I have to deal with, check the king. the solution is here:
#we split try_move into get_attack_squares and get_attack_squares, then at show_move, we first build a new layout(matrix, that is, in class part)
#to see is there is a king being attacked.
class Piece():
    def __init__(self,x,y,color,type_char):
        #by the way, we will set offset as a class attribute

        self.coordinationx=x
        self.coordinationy=y
        self.color=color
        self.type_char=type_char#this attribution is like "P" "R" "K", capital by the way
        self.is_firstmove=True
        self.attack_sqaures=[]#but the problem is that moveable squares do not mean been attacked
        self.move_squares=[]
    
    def get_attack_squares(self,matrix):
        raise NotImplementedError("didn't write get_attack_squares function")
    
    def get_move_squares(self,matrix):
        raise NotImplementedError("didn't write get_move_squares function lol")
    #it does the same way as get_attack_squares does
    
    def show_move_squares(self,matrix):
        possible_moves=self.get_move_squares(matrix)
        valid_moves=[]
        for (my,mx) in possible_moves:
            temp_matrix=copy.deepcopy(matrix)
            #here we move, note that we move the piece in temp_matrix
            old_x=self.coordinationx
            old_y=self.coordinationy
            temp_matrix[old_y][old_x].coordinationx=mx
            temp_matrix[old_y][old_x].coordinationy=my
            temp_matrix[my][mx]=temp_matrix[old_y][old_x]
            temp_matrix[old_y][old_x]="space"
            #here we check
            for i in range(8):
                for j in range(8):
                    if (temp_matrix[i][j]!="space" and temp_matrix[i][j].type_char=="K" 
                        and temp_matrix[i][j].color==self.color and is_attacked(j,i,temp_matrix[i][j].color,temp_matrix)==False):
                        valid_moves.append((my,mx))
        for (y,x) in valid_moves:
            board[y][x]="moveto"

    def try_move(self,mx,my,matrix):#x,y means the coordination mouse clicked and we also need to judge when we clicked somewhere illegal
    #and by the way we need to check there is no check after the move was made
        if board[my][mx]=="moveto":
            old_x=self.coordinationx
            old_y=self.coordinationy
            self.coordinationx=mx
            self.coordinationy=my
            matrix[my][mx]=matrix[old_y][old_x]
            matrix[old_y][old_x]="space"
            #here a move was made so we need to clean En Passant now
            for i in range(8):
                for j in range(8):
                    if (matrix[i][j]!="space" and matrix[i][j].type_char=="P" and matrix[i][j].is_firstmove==False):
                        matrix[i][j].allow_en_passant=False
            self.is_firstmove=False

class SlidingPiece(Piece):
    def get_attack_squares(self,matrix):
        attack_squares=[]
        for (x,y) in self.offset:# BE AWARE THAT there is no need to if "w" elif "b",we just need to judge the color is diffrent or not
            to_x=self.coordinationx+x
            to_y=self.coordinationy+y
            while(0<=to_x<=7 and 0<=to_y<=7 and (matrix[to_y][to_x]=="space" or matrix[to_y][to_x].color!=self.color)):
                attack_squares.append((to_y,to_x))
                if matrix[to_y][to_x]!="space" and matrix[to_y][to_x].color!=self.color:
                    break
                to_x+=x
                #(to_x,to_y)+=(x,y) seems won't work
                to_y+=y
        return(attack_squares)
    
    def get_move_squares(self, matrix):
        return self.get_attack_squares(matrix)
    
    
class SteppingPiece(Piece):
    def get_attack_squares(self,matrix):
        attack_squares=[]
        for (x,y) in self.offset:
            if (0<=self.coordinationy+y<=7 and 0<=self.coordinationx+x<=7 
                and (matrix[self.coordinationy+y][self.coordinationx+x]=="space" or matrix[self.coordinationy+y][self.coordinationx+x].color!=self.color)):
                attack_squares.append((self.coordinationy+y,self.coordinationx+x))
        return(attack_squares)
    def get_move_squares(self, matrix):
        return self.get_attack_squares(matrix)
    

class Pawn(Piece):
    def __init__(self,x,y,color,type_char):
        super().__init__(x,y,color,type_char)
        self.allow_en_passant=False

    def get_move_squares(self,matrix):
        move_squares=[]#(y,x)
        #forward
        forwardone=-1 if self.color=="w" else 1
        forwardtwo=-2 if self.color=="w" else 2
        if (0<=self.coordinationy+forwardone<=7 and matrix[self.coordinationy+forwardone][self.coordinationx]=="space"):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx))

        if (0<=self.coordinationy+forwardtwo<=7 and matrix[self.coordinationy+forwardtwo][self.coordinationx]=="space" 
            and self.is_firstmove==True and matrix[self.coordinationy+forwardone][self.coordinationx]=="space"):
            move_squares.append((self.coordinationy+forwardtwo,self.coordinationx))
        #take diagnally
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx-1<=7
            and matrix[self.coordinationy+forwardone][self.coordinationx-1]!="space" 
            and matrix[self.coordinationy+forwardone][self.coordinationx-1].color!=self.color):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx-1))
            print("B")
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx+1<=7
            and matrix[self.coordinationy+forwardone][self.coordinationx+1]!="space" 
            and matrix[self.coordinationy+forwardone][self.coordinationx+1].color!=self.color):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx+1))
            print("A")
        #En Passant
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx-1<=7 
            and matrix[self.coordinationy][self.coordinationx-1]!="space"
            and matrix[self.coordinationy][self.coordinationx-1].type_char=="P"
            and matrix[self.coordinationy][self.coordinationx-1].color!=self.color
            and matrix[self.coordinationy][self.coordinationx-1].allow_en_passant==True):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx-1))
            print("9")
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx+1<=7 
            and matrix[self.coordinationy][self.coordinationx+1]!="space"
            and matrix[self.coordinationy][self.coordinationx+1].type_char=="P"
            and matrix[self.coordinationy][self.coordinationx+1].color!=self.color
            and matrix[self.coordinationy][self.coordinationx+1].allow_en_passant==True):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx+1))
            print("8")
        return(move_squares)


    def show_move_squares(self,matrix):
        forwardone=-1 if self.color=="w" else 1
        forwardtwo=-2 if self.color=="w" else 2

        possible_moves=self.get_move_squares(matrix)
        valid_moves=[]
        for (y,x) in possible_moves:
            temp_matrix=copy.deepcopy(matrix)
            #here we need to judge which move did pawn want to take
            #note that all moves in possible_moves is already on the board
            #forward

            #I think we just need to check En Passant
            if (y==self.coordinationy+forwardone and (x==self.coordinationx+1 or x==self.coordinationx-1)
                and temp_matrix[y][x]=="space"):
                temp_matrix[self.coordinationy][x]=="space"
                #we just need to clear the square En passant takes, then every thing goes to normal
            #here we move, note that we move the piece in temp_matrix
            old_x=self.coordinationx
            old_y=self.coordinationy
            temp_matrix[old_y][old_x].coordinationx=x
            temp_matrix[old_y][old_x].coordinationy=y
            temp_matrix[y][x]=temp_matrix[old_y][old_x]
            temp_matrix[old_y][old_x]="space"
            #here we check
            for i in range(8):
                for j in range(8):
                    if (temp_matrix[i][j]!="space" and temp_matrix[i][j].type_char=="K" 
                        and temp_matrix[i][j].color==self.color and is_attacked(j,i,temp_matrix[i][j].color,temp_matrix)==False):
                        valid_moves.append((y,x))
        for (y,x) in valid_moves:
            board[y][x]="moveto"


    def try_move(self,x,y,matrix):
        global promote_position
        forwardone=-1 if self.color=="w" else 1
        if ( board[y][x]=="moveto" and matrix[y][x]=="space" and  y==self.coordinationy+forwardone and 
            ((0<=self.coordinationx+1<=7 and x==self.coordinationx+1)or(0<=self.coordinationx-1<=7 and x==self.coordinationx-1))
            ):
            matrix[y-forwardone][x]="space"
            old_x=self.coordinationx
            old_y=self.coordinationy
            self.coordinationx=x
            self.coordinationy=y
            matrix[y][x]=matrix[old_y][old_x]
            matrix[old_y][old_x]="space"
            #here a move was made so we need to clean En Passant now
            for i in range(8):
                for j in range(8):
                    if (matrix[i][j]!="space" and matrix[i][j].type_char=="P" and matrix[i][j].is_firstmove==False):
                        matrix[i][j].allow_en_passant=False
        elif board[y][x]=="moveto":
            if y==self.coordinationy+forwardone*2 and x==self.coordinationx:
                self.allow_en_passant=True
            old_x=self.coordinationx
            old_y=self.coordinationy
            self.coordinationx=x
            self.coordinationy=y
            matrix[y][x]=matrix[old_y][old_x]
            matrix[old_y][old_x]="space"
            #here a move was made so we need to clean En Passant now (don't clean itself)
            for i in range(8):
                for j in range(8):
                    if (matrix[i][j]!="space" and matrix[i][j].type_char=="P" and (i,j)!=(self.coordinationy,self.coordinationx)):
                        matrix[i][j].allow_en_passant=False
        self.is_firstmove=False
        #here we need to deal with promotion
        if self.coordinationy==(0 if self.color=="w" else 7):
            promote_position=(self.coordinationy,self.coordinationx)
            return("PROMOTE")
        return("SUCCESS")


class Knight(SteppingPiece):
    offset=[(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
        
class Rook(SlidingPiece):#castling part we set it for King
    offset=[(0,1),(0,-1),(-1,0),(1,0)]

class Bishop(SlidingPiece):
    offset=[(1,1),(1,-1),(-1,1),(-1,-1)]

class Queen(SlidingPiece):
    offset=[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]

class King(SteppingPiece):
    offset=[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
    def show_move_squares(self,matrix):
        for (x,y) in self.offset:
            to_x=self.coordinationx+x
            to_y=self.coordinationy+y
            if (0<=to_x<=7 and 0<=to_y<=7 
                and (matrix[to_y][to_x]=="space" or self.color!=matrix[to_y][to_x].color)
                and is_attacked(to_x,to_y,self.color,matrix)==False):
                board[to_y][to_x]="moveto"
        
        #here we deal with Castle part
        #short Castle
        if (self.is_firstmove==True
            and 0<=self.coordinationx+3<=7
            and matrix[self.coordinationy][self.coordinationx+3]!="space"
            and matrix[self.coordinationy][self.coordinationx+3].is_firstmove==True
            and matrix[self.coordinationy][self.coordinationx+1]=="space"
            and matrix[self.coordinationy][self.coordinationx+2]=="space"
            and is_attacked(self.coordinationx+2,self.coordinationy,self.color,matrix)==False
            and is_attacked(self.coordinationx+1,self.coordinationy,self.color,matrix)==False
            and is_attacked(self.coordinationx,self.coordinationy,self.color,matrix)==False
            ):
            board[self.coordinationy][self.coordinationx+2]="moveto"
        #long Castle
        if (self.is_firstmove==True
            and 0<=self.coordinationx-4<=7
            and matrix[self.coordinationy][self.coordinationx-4]!="space"
            and matrix[self.coordinationy][self.coordinationx-4].is_firstmove==True
            and matrix[self.coordinationy][self.coordinationx-1]=="space"
            and matrix[self.coordinationy][self.coordinationx-2]=="space"
            and matrix[self.coordinationy][self.coordinationx-3]=="space"
            and is_attacked(self.coordinationx-2,self.coordinationy,self.color,matrix)==False
            and is_attacked(self.coordinationx-1,self.coordinationy,self.color,matrix)==False
            and is_attacked(self.coordinationx,self.coordinationy,self.color,matrix)==False
            ):
            board[self.coordinationy][self.coordinationx-2]="moveto"
    def try_move(self, x, y, matrix):
        if (x==self.coordinationx+2 and y==self.coordinationy):
            #here we deal with the rook first
            matrix[self.coordinationy][self.coordinationx+1]=matrix[self.coordinationy][self.coordinationx+3]
            matrix[self.coordinationy][self.coordinationx+3]="space"
            matrix[self.coordinationy][self.coordinationx+1].coordinationx=self.coordinationx+1
            #then we deal with the king
            old_x=self.coordinationx
            old_y=self.coordinationy
            self.coordinationx=x
            self.coordinationy=y
            matrix[y][x]=matrix[old_y][old_x]
            matrix[old_y][old_x]="space"
            
            #here a move was made so we need to clean En Passant now
            
            for i in range(8):
                for j in range(8):
                    if (matrix[i][j]!="space" and matrix[i][j].type_char=="P" and matrix[i][j].is_firstmove==False):
                        matrix[i][j].allow_en_passant=False
            self.is_firstmove=False
        elif (x==self.coordinationx-2 and y==self.coordinationy and board[y][x]=="moveto"):
            #here we deal with the rook first
            matrix[self.coordinationy][self.coordinationx-1]=matrix[self.coordinationy][self.coordinationx-4]
            matrix[self.coordinationy][self.coordinationx-4]="space"
            matrix[self.coordinationy][self.coordinationx-1].coordinationx=self.coordinationx-1
            #then we deal with the king
            old_x=self.coordinationx
            old_y=self.coordinationy
            self.coordinationx=x
            self.coordinationy=y
            matrix[y][x]=matrix[old_y][old_x]
            matrix[old_y][old_x]="space"
            
            #here a move was made so we need to clean En Passant now
            for i in range(8):
                for j in range(8):
                    if (matrix[i][j]!="space" and matrix[i][j].type_char=="P"):
                        matrix[i][j].allow_en_passant=False
            self.is_firstmove=False
        else:
            if board[y][x]=="moveto":
                old_x=self.coordinationx
                old_y=self.coordinationy
                self.coordinationx=x
                self.coordinationy=y
                matrix[y][x]=matrix[old_y][old_x]
                matrix[old_y][old_x]="space"
                #here a move was made so we need to clean En Passant now
                for i in range(8):
                    for j in range(8):
                        if (matrix[i][j]!="space" and matrix[i][j].type_char=="P"):
                            matrix[i][j].allow_en_passant=False
                self.is_firstmove=False

#note that we need use piece matrix to use as a parameter in Piece so we can use it in class method
PIECE_MAP={"P":Pawn,"R":Rook,"N":Knight,"B":Bishop,"Q":Queen,"K":King}
def load_board(layout):
    pieces=[["space" for _ in range(8)]for _ in range(8)]#piece_matrix is the second layer
    for i in range(8):
        for j in range(8):
            if layout[i][j]!="space":
                color=layout[i][j][0]
                type_char=layout[i][j][1]
                type_name=PIECE_MAP[type_char]
                new_piece=type_name(j,i,color,type_char)
                pieces[i][j]=new_piece
    return pieces
piece_matrix=load_board(layout)#all the instances is here

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type ==pygame.MOUSEBUTTONDOWN:#detect where the mouse actually clicked
            (mouse_posx,mouse_posy)=event.pos
            mouse_coordinationx=(mouse_posx-SQUAREORIGIN[0])//SQUARESIZE
            mouse_coordinationy=(mouse_posy-SQUAREORIGIN[1])//SQUARESIZE
            #we need to know if we are play normally or trying to upgrade a pawn
            if current_state==GameState.NORMAL:
                if 0<=mouse_coordinationx<=7 and 0<=mouse_coordinationy<=7:
                    if selecting==False:
                        piece=piece_matrix[mouse_coordinationy][mouse_coordinationx]
                        if piece!="space" and piece.color==turn:
                            piece.show_move_squares(piece_matrix)
                            selecting=True
                    elif (selecting==True and piece_matrix[mouse_coordinationy][mouse_coordinationx]!="space"
                          and piece_matrix[mouse_coordinationy][mouse_coordinationx].color==turn):
                        for i in range(8):
                            for j in range(8):
                                if board[i][j]=="moveto":board[i][j]="space"
                        piece=piece_matrix[mouse_coordinationy][mouse_coordinationx]
                        piece.show_move_squares(piece_matrix)
                    elif selecting==True:
                        if board[mouse_coordinationy][mouse_coordinationx]=="moveto":
                            #try_move can disable show_selected_squares part, and we need to receive its signals
                            #if a piece type doesn't have return ,signal will receive None
                            move_signal=piece.try_move(mouse_coordinationx,mouse_coordinationy,piece_matrix)
                            if move_signal=="PROMOTE":#here don't change the color yet
                                current_state=GameState.PROMOTING
                            else:turn="w" if turn=="b" else "b"
                            print(is_checkmate(turn,piece_matrix))
                            if is_checkmate(turn,piece_matrix):
                                current_state=GameState.CHECKMATE
                        selecting=False
                        #no matter how we need to clean the board
                        for i in range(8):
                            for j in range(8):
                                if board[i][j]=="moveto":board[i][j]="space"
            elif current_state==GameState.PROMOTING:#remember we need to change the color after promoting
                    PROMOTING_MAP1={0:"Q",1:"R",2:"B",3:"N"}
                    PROMOTING_MAP2={0:Queen,1:Rook,2:Bishop,3:Knight}
                    (coordinationy,coordinationx)=promote_position

                    direction=1 if turn=="w" else -1

                    for i in range(4):
                        if mouse_coordinationx==coordinationx+1 and mouse_coordinationy==coordinationy+i*direction:
                            piece_matrix[coordinationy][coordinationx]=PROMOTING_MAP2[i](coordinationx,coordinationy,turn,PROMOTING_MAP1[i])
                            current_state=GameState.NORMAL
                            turn="w" if turn=="b" else "b"

            elif current_state==GameState.CHECKMATE:
                print("you win! actually you can always win")

    
    screen.fill("purple")

    #I need render my chessboard here
    render_board()
    if current_state==GameState.PROMOTING:
        (coordinationy,coordinationx)=promote_position
        render_pormotion_bar(coordinationy,coordinationx,turn) 
        print("222222")
    #FLIP is used to display my render work on screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()