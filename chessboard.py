'''
UI 层：只负责渲染和事件捕获
调用 game.py 的 Game 类来处理所有游戏逻辑
'''

import pygame

#this fucking file-fiding mechanic is so stupid it just try to find the file
#  in the current working directory(CWD) instead of the parent folder of .py file.
# so we need to reset it
import os 
import sys
script_path=os.path.dirname(os.path.abspath(__file__))
os.chdir(script_path)

import game

pygame.init()
screen=pygame.display.set_mode((1280,720))
clock=pygame.time.Clock()
running=True

#here we need to set some constants
SQUARESIZE=80
#this is used to draw the lefttop point of the whole board
SQUAREORIGIN=[0,0]
#mind that sets are unordered so I can't just "for in" it.
SQUARE_DIC=["space","moveto","bP","wP","bR","wR","bN","wN","bB","wB","bQ","wQ","bK","wK"]
IMAGES={}

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
def render_board(highlighted,piece_matrix):
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
#创建游戏实例
game_instance = game.Game()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running=False
        if event.type ==pygame.MOUSEBUTTONDOWN:#detect where the mouse actually clicked
            (mouse_posx,mouse_posy)=event.pos
            mouse_coordinationx=(mouse_posx-SQUAREORIGIN[0])//SQUARESIZE
            mouse_coordinationy=(mouse_posy-SQUAREORIGIN[1])//SQUARESIZE

            action, info = game_instance.handle_click(mouse_coordinationx, mouse_coordinationy)

            if action == "CHECKMATE":
                print("you win! actually you can always win")

    
    screen.fill("purple")

    #I need render my chessboard here
    render_board(game_instance.get_highlighted_moves(), game_instance.get_piece_matrix())
    if game_instance.get_state() == game.GameState.PROMOTING:
        (coordinationy,coordinationx) = game_instance.get_promote_position()
        render_pormotion_bar(coordinationy, coordinationx, game_instance.get_turn()) 
    #FLIP is used to display my render work on screen
    pygame.display.flip()

    clock.tick(60)

pygame.quit()
