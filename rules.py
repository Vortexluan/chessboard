#we have is_attacked, is_checkmated as our rules

def is_attacked(x,y,color,matrix):
    '''
    我们必须要详细地解释这个函数的功能，
    检测在matrix下，对于color方来说，
    (x,y)这个地方有没有被地方棋子攻击到
    '''
    #1.first we detect Pawn
    forwardone=-1 if color=="w" else 1
    #take diagnally
    if (0<=y+forwardone<=7 and 0<=x-1<=7
        and matrix[y+forwardone][x-1] is not None
        and matrix[y+forwardone][x-1].color!=color
        and matrix[y+forwardone][x-1].type_char=="P"):
        return True
    if (0<=y+forwardone<=7 and 0<=x+1<=7
        and matrix[y+forwardone][x+1] is not None
        and matrix[y+forwardone][x+1].color!=color
        and matrix[y+forwardone][x+1].type_char=="P"):
        return True
    #2. second we check sliding pieces.
    #Here we check Rook
    offset=[(0,1),(0,-1),(-1,0),(1,0)]
    for (x0,y0) in offset:# BE AWARE THAT there is no need to if "w" elif "b",we just need to judge the color is diffrent or not
        to_x=x+x0
        to_y=y+y0
        while(0<=to_x<=7 and 0<=to_y<=7 
              and (matrix[to_y][to_x] is None or matrix[to_y][to_x].color!=color)
              ):
            if( matrix[to_y][to_x] is not None and matrix[to_y][to_x].color!=color 
            and matrix[to_y][to_x].type_char=="R" ):
                return True
            to_x+=x0
            #(to_x,to_y)+=(x,y) seens won't work
            to_y+=y0
    #3. Queen
    offset=[(0,1),(0,-1),(-1,0),(1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
    for (x0,y0) in offset:# BE AWARE THAT there is no need to if "w" elif "b",we just need to judge the color is diffrent or not
        to_x=x+x0
        to_y=y+y0
        while(0<=to_x<=7 and 0<=to_y<=7 
              and (matrix[to_y][to_x] is None or matrix[to_y][to_x].color!=color)
              ):
            if( matrix[to_y][to_x] is not None and matrix[to_y][to_x].color!=color 
            and matrix[to_y][to_x].type_char=="Q" ):
                return True
            to_x+=x0
            #(to_x,to_y)+=(x,y) seens won't work
            to_y+=y0
    #4. then bishop
    offset=[(1,1),(1,-1),(-1,1),(-1,-1)]    
    for (x0,y0) in offset:
        to_x=x+x0
        to_y=y+y0
        while(0<=to_x<=7 and 0<=to_y<=7 and (matrix[to_y][to_x] is None or matrix[to_y][to_x].color!=color)):
            if( matrix[to_y][to_x] is not None and matrix[to_y][to_x].color!=color 
            and (matrix[to_y][to_x].type_char=="B" or matrix[to_y][to_x].type_char=="Q" )):
                return True
            to_x+=x0
            #(to_x,to_y)+=(x,y) seens won't work
            to_y+=y0
    #5. Knight
    offset=[(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
    for (x0,y0) in offset:
        if (0<=y+y0<=7 and 0<=x+x0<=7 
            and matrix[y+y0][x+x0] is not None
            and matrix[y+y0][x+x0].color!=color
            and matrix[y+y0][x+x0].type_char=="N"):
            return True

    #6. King
    offset=[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
    for (x0,y0) in offset:
        to_x=x+x0
        to_y=y+y0
        if (0<=to_x<=7 and 0<=to_y<=7 
            and matrix[to_y][to_x] is not None
            and color!=matrix[to_y][to_x].color
            and matrix[to_y][to_x].type_char=="K"):
            return True
    return False


def is_checkmate(color, matrix):
    #卧槽，可以直接检查己方的棋子有没有可以走的棋(legal_move的时候就考虑了将军)
    for i in range(8):
        for j in range(8):
            piece = matrix[i][j]
            if piece is not None and piece.color == color:
                if piece.get_legal_moves(matrix):
                    return False
    return True

def is_check(color,matrix):#判断color方是否被将军了
    for i in range(8):
        for j in range(8):
            if (matrix[i][j] is not None and matrix[i][j].type_char=="K" 
                and matrix[i][j].color==color):
                king_y=i
                king_x=j
    
    if(is_attacked(king_x,king_y,color,matrix)==True):
        return True
    else:
        return False

def is_stalmate(color,matrix):
    for i in range(8):
        for j in range(8):
            if (matrix[i][j] is not None and matrix[i][j].type_char=="K" 
                and matrix[i][j].color==color):
                king_y=i
                king_x=j
    
    valid_moves=[]#这个是直接通过棋子的get_legal_moves来的,已经检查了保证一个move不会导致将军
    for i in range(8):
        for j in range(8):
            if matrix[i][j] is not None:
                for (my,mx) in matrix[i][j].get_legal_moves(matrix):
                    valid_moves.append((my,mx))
    if((is_attacked(king_x,king_y,matrix[king_y][king_x].color,matrix)==False)
       and len(valid_moves)==0):
        return True
    else:
        return False
