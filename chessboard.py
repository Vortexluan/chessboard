import pygame
import rules
import pieces

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

#highlighted_moves is the set of legal target squares for the currently selected piece
#我的天，原来还可以用冒号写注释的，以前一直不知道
#没有必要使用一整个board进行记录了，能够移动到的位置本身就只有几个，
#只用元组将要高亮显示的部分记录下来就好了
highlighted_moves: set[tuple[int,int]] = set()
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
def render_board(highlighted):
    for i in range(8):#876
        for j in range(8):#abc
            if (i,j) in highlighted:
                if (i+j)%2==1:
                    pygame.draw.rect(screen,(50,50,255),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))
                else:
                    pygame.draw.rect(screen,(200,200,255),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))
            else:
                if (i+j)%2==1:
                    pygame.draw.rect(screen,(50,50,50),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))
                else:
                    pygame.draw.rect(screen,(255,255,255),(SQUAREORIGIN[0]+j*SQUARESIZE,SQUAREORIGIN[1]+i*SQUARESIZE,SQUARESIZE,SQUARESIZE))

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



#note that we need use piece matrix to use as a parameter in Piece so we can use it in class method
PIECE_MAP={"P":pieces.Pawn,"R":pieces.Rook,"N":pieces.Knight,"B":pieces.Bishop,"Q":pieces.Queen,"K":pieces.King}
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
                            highlighted_moves = set(piece.get_legal_moves(piece_matrix))
                            selecting=True
                    elif (selecting==True and piece_matrix[mouse_coordinationy][mouse_coordinationx]!="space"and piece_matrix[mouse_coordinationy][mouse_coordinationx].color==turn):
                        highlighted_moves.clear()
                        piece=piece_matrix[mouse_coordinationy][mouse_coordinationx]
                        highlighted_moves = set(piece.get_legal_moves(piece_matrix))
                    elif selecting==True:
                        if (mouse_coordinationy, mouse_coordinationx) in highlighted_moves:
                            move_result, move_info = piece.try_move(mouse_coordinationx,mouse_coordinationy,piece_matrix)
                            if move_result=="PROMOTE":
                                promote_position = move_info
                                current_state=GameState.PROMOTING
                            else:
                                turn="w" if turn=="b" else "b"
                            if rules.is_checkmate(turn,piece_matrix):
                                current_state=GameState.CHECKMATE
                        selecting=False
                        highlighted_moves.clear()
            elif current_state==GameState.PROMOTING:#remember we need to change the color after promoting
                    PROMOTING_MAP1={0:"Q",1:"R",2:"B",3:"N"}
                    PROMOTING_MAP2={0:pieces.Queen,1:pieces.Rook,2:pieces.Bishop,3:pieces.Knight}
                    (coordinationy,coordinationx)=promote_position

                    direction=1 if turn=="w" else -1

                    for i in range(4):
                        if mouse_coordinationx==coordinationx+1 and mouse_coordinationy==coordinationy+i*direction:
                            piece_matrix[coordinationy][coordinationx]=PROMOTING_MAP2[i](coordinationx,coordinationy,turn,PROMOTING_MAP1[i])
                            current_state=GameState.NORMAL
                            turn="w" if turn=="b" else "b"

            elif current_state==GameState.CHECKMATE:#but we need another click to trigger this...?
                print("you win! actually you can always win")

    
    screen.fill("purple")

    #I need render my chessboard here
    render_board(highlighted_moves)
    if current_state==GameState.PROMOTING:
        (coordinationy,coordinationx)=promote_position
        render_pormotion_bar(coordinationy,coordinationx,turn) 
    #FLIP is used to display my render work on screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()