#代码重构，这里的棋子逻辑应该单独提取出来作一个类，但是解耦的部分会非常麻烦

#matrix这个是一个8x8的棋子layout，是一个二维列表
import copy
import rules

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

    def clear_en_passant(self,matrix):#如果是一个兵走第一次走了两格，我们需要排除它自己
        for i in range(8):
            for j in range(8):
                if matrix[i][j] != "space" and matrix[i][j].type_char =="P" and matrix[i][j]!=self:
                    matrix[i][j].allow_en_passant=False
    
    def get_attack_squares(self,matrix):
        raise NotImplementedError("didn't write get_attack_squares function")
    
    def get_move_squares(self,matrix):
        raise NotImplementedError("didn't write get_move_squares function lol")
    #it does the same way as get_attack_squares does
    
    def get_legal_moves(self,matrix):#原本是show_move_squares，但是我们不能够使用全局
        #变量board,所以我们需要这个能够返回一个valid_moves列表[(y_0,x_0),(y_1,x_1)]这种
        #我们确保这里的legal moves是能够实行的，不会导致将军等问题

        #卧槽！卧槽！！卧槽！！！
        #看上去只找一次king坐标的貌似没有问题，但是如果被移动的是王呢？
        possible_moves=self.get_move_squares(matrix)
        valid_moves=[]


        for (my,mx) in possible_moves:
            for i in range(8):
                for j in range(8):
                    if (matrix[i][j]!="space" and matrix[i][j].type_char=="K" 
                        and matrix[i][j].color==self.color):
                        king_y=i
                        king_x=j
                

            temp_matrix=copy.deepcopy(matrix)
            #here we move, note that we move the piece in temp_matrix
            old_x=self.coordinationx
            old_y=self.coordinationy
            temp_matrix[old_y][old_x].coordinationx=mx
            temp_matrix[old_y][old_x].coordinationy=my
            temp_matrix[my][mx]=temp_matrix[old_y][old_x]
            temp_matrix[old_y][old_x]="space"
            #here we check

            if(rules.is_attacked(king_x,king_y,temp_matrix[king_y][king_x].color,temp_matrix)==False):
                valid_moves.append((my,mx))
        return(valid_moves)

    def try_move(self,mx,my,matrix):
            #x,y means the coordination mouse clicked and we also need to judge when we clicked somewhere illegal
            #and by the way we need to check there is no check after the move was made
            old_x=self.coordinationx
            old_y=self.coordinationy
            self.coordinationx=mx
            self.coordinationy=my
            matrix[my][mx]=matrix[old_y][old_x]
            matrix[old_y][old_x]="space"
            #here a move was made so we need to clean En Passant now
            self.clear_en_passant(matrix)
            self.is_firstmove=False
            return("SUCCESS",None)

class SlidingPiece(Piece):
    offset=[] # class attribute, to be overridden by subclasses
    def get_attack_squares(self,matrix):
        attack_squares=[]#(y,x)
        for (x,y) in self.offset:# BE AWARE THAT there is no need to if "w" elif "b",we just need to judge the color is diffrent or not
            to_x=self.coordinationx+x
            to_y=self.coordinationy+y
            while(0<=to_x<=7 and 0<=to_y<=7 ):
                target=matrix[to_y][to_x]
                if(target=="space"):
                    attack_squares.append((to_y,to_x))
                elif(target.color==self.color):
                    break
                elif(target.color!=self.color):
                    attack_squares.append((to_y,to_x))
                    break

                to_x+=x
                #(to_x,to_y)+=(x,y) seems won't work
                to_y+=y
        return(attack_squares)
    
    def get_move_squares(self, matrix):
        return self.get_attack_squares(matrix)
    
    
class SteppingPiece(Piece):
    offset=[] # class attribute, to be overridden by subclasses
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
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx+1<=7
            and matrix[self.coordinationy+forwardone][self.coordinationx+1]!="space" 
            and matrix[self.coordinationy+forwardone][self.coordinationx+1].color!=self.color):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx+1))
        #En Passant
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx-1<=7 
            and matrix[self.coordinationy][self.coordinationx-1]!="space"
            and matrix[self.coordinationy][self.coordinationx-1].type_char=="P"
            and matrix[self.coordinationy][self.coordinationx-1].color!=self.color
            and matrix[self.coordinationy][self.coordinationx-1].allow_en_passant==True):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx-1))
        if (0<=self.coordinationy+forwardone<=7 and 0<=self.coordinationx+1<=7 
            and matrix[self.coordinationy][self.coordinationx+1]!="space"
            and matrix[self.coordinationy][self.coordinationx+1].type_char=="P"
            and matrix[self.coordinationy][self.coordinationx+1].color!=self.color
            and matrix[self.coordinationy][self.coordinationx+1].allow_en_passant==True):
            move_squares.append((self.coordinationy+forwardone,self.coordinationx+1))
        return(move_squares)


    def get_legal_moves(self,matrix):
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
                temp_matrix[self.coordinationy][x]="space"
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
                        and temp_matrix[i][j].color==self.color and rules.is_attacked(j,i,temp_matrix[i][j].color,temp_matrix)==False):
                        valid_moves.append((y,x))
        return(valid_moves)


    def try_move(self,x,y,matrix):#我们将检查是否这步对应的是move的地方的代码写在了pygame的判断里面
            forwardone=-1 if self.color=="w" else 1
            if (matrix[y][x]=="space" and  y==self.coordinationy+forwardone and 
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
                self.clear_en_passant(matrix)
            else:
                if y==self.coordinationy+forwardone*2 and x==self.coordinationx:
                    self.allow_en_passant=True
                old_x=self.coordinationx
                old_y=self.coordinationy
                self.coordinationx=x
                self.coordinationy=y
                matrix[y][x]=matrix[old_y][old_x]
                matrix[old_y][old_x]="space"
                #here a move was made so we need to clean En Passant now (don't clean itself)
                self.clear_en_passant(matrix)

            self.is_firstmove=False
            #here we need to deal with promotion
            if self.coordinationy==(0 if self.color=="w" else 7):
                return("PROMOTE",(self.coordinationy,self.coordinationx))
            return("SUCCESS",None)


class Knight(SteppingPiece):
    #注意一下，实例属性是会遮蔽类属性的，所以如果在piece的__init__里面写了个
    #self.offset=[]继承下来的实例属性会把所有类属性给屏蔽掉
    offset=[(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(-1,2),(1,-2),(-1,-2)]
        
class Rook(SlidingPiece):#castling part we set it for King
    offset=[(0,1),(0,-1),(-1,0),(1,0)]

class Bishop(SlidingPiece):
    offset=[(1,1),(1,-1),(-1,1),(-1,-1)]

class Queen(SlidingPiece):
    offset=[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]

class King(SteppingPiece):
    offset=[(1,1),(1,-1),(-1,1),(-1,-1),(1,0),(-1,0),(0,1),(0,-1)]
    def get_legal_moves(self,matrix):
        #注意！不能够直接用is_attacked来判断，给出的matrix不是走棋后的matrix，这样的判断是不可行的



        valid_moves=[]
        for (x,y) in self.offset:
            to_x=self.coordinationx+x
            to_y=self.coordinationy+y

            temp_matrix=copy.deepcopy(matrix)
            #here we move, note that we move the piece in temp_matrix
            if (0<=to_x<=7 and 0<=to_y<=7 
                and (temp_matrix[to_y][to_x]=="space" or self.color!=temp_matrix[to_y][to_x].color)):
                old_x=self.coordinationx
                old_y=self.coordinationy
                temp_matrix[old_y][old_x].coordinationx=to_x
                temp_matrix[old_y][old_x].coordinationy=to_y
                temp_matrix[to_y][to_x]=temp_matrix[old_y][old_x]
                temp_matrix[old_y][old_x]="space"
                #here we check


                if(rules.is_attacked(to_x,to_y,self.color,temp_matrix)==False):
                    valid_moves.append((to_y,to_x))
        
        #here we deal with Castle part
        #short Castle
        if (self.is_firstmove==True
            and 0<=self.coordinationx+3<=7
            and matrix[self.coordinationy][self.coordinationx+3]!="space"
            and matrix[self.coordinationy][self.coordinationx+3].is_firstmove==True
            and matrix[self.coordinationy][self.coordinationx+1]=="space"
            and matrix[self.coordinationy][self.coordinationx+2]=="space"
            and rules.is_attacked(self.coordinationx+2,self.coordinationy,self.color,matrix)==False
            and rules.is_attacked(self.coordinationx+1,self.coordinationy,self.color,matrix)==False
            and rules.is_attacked(self.coordinationx,self.coordinationy,self.color,matrix)==False
            ):
            valid_moves.append((self.coordinationy,self.coordinationx+2))
        #long Castle
        if (self.is_firstmove==True
            and 0<=self.coordinationx-4<=7
            and matrix[self.coordinationy][self.coordinationx-4]!="space"
            and matrix[self.coordinationy][self.coordinationx-4].is_firstmove==True
            and matrix[self.coordinationy][self.coordinationx-1]=="space"
            and matrix[self.coordinationy][self.coordinationx-2]=="space"
            and matrix[self.coordinationy][self.coordinationx-3]=="space"
            and rules.is_attacked(self.coordinationx-2,self.coordinationy,self.color,matrix)==False
            and rules.is_attacked(self.coordinationx-1,self.coordinationy,self.color,matrix)==False
            and rules.is_attacked(self.coordinationx,self.coordinationy,self.color,matrix)==False
            ):
            valid_moves.append((self.coordinationy,self.coordinationx-2))
        return(valid_moves)
    
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
                self.clear_en_passant(matrix)
                self.is_firstmove=False
                return("SUCCESS",None)
            elif (x==self.coordinationx-2 and y==self.coordinationy):
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
                self.clear_en_passant(matrix)
                self.is_firstmove=False
                return("SUCCESS",None)
            else:
                old_x=self.coordinationx
                old_y=self.coordinationy
                self.coordinationx=x
                self.coordinationy=y
                matrix[y][x]=matrix[old_y][old_x]
                matrix[old_y][old_x]="space"
                #here a move was made so we need to clean En Passant now
                self.clear_en_passant(matrix)
                self.is_firstmove=False
                return("SUCCESS",None)