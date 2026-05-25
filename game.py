'''
Game 类：封装棋盘游戏的所有逻辑
从 chessboard.py 中分离出来的纯逻辑层
'''

import pieces
import rules

PIECE_MAP = {"P": pieces.Pawn, "R": pieces.Rook, "N": pieces.Knight,
             "B": pieces.Bishop, "Q": pieces.Queen, "K": pieces.King}

INITIAL_LAYOUT = [
    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["space", "space", "space", "space", "space", "space", "space", "space"],
    ["space", "space", "space", "space", "space", "space", "space", "space"],
    ["space", "space", "space", "space", "space", "space", "space", "space"],
    ["space", "space", "space", "space", "space", "space", "space", "space"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
]


class GameState:
    NORMAL = 0
    PROMOTING = 1
    CHECKMATE = 2


class Game:
    #注意，chessboard里面大概率是需要用到game的实例的
    def __init__(self):
        self.reset()

    def reset(self):
        """重置游戏到初始状态"""
        self.piece_matrix = self._load_board(INITIAL_LAYOUT)
        self.turn = "w"
        self.state = GameState.NORMAL
        self.selected_piece = None
        self.highlighted_moves: set[tuple[int, int]] = set()
        self.promote_position = (-1, -1)

    def _load_board(self, layout):
        """从字符串布局加载棋子实例"""
        matrix = [["space" for _ in range(8)] for _ in range(8)]
        for i in range(8):
            for j in range(8):
                if layout[i][j] != "space":
                    color = layout[i][j][0]
                    type_char = layout[i][j][1]
                    type_name = PIECE_MAP[type_char]
                    matrix[i][j] = type_name(j, i, color, type_char)
        return matrix

    # 查询，便于有什么东西来申请访问

    def get_piece_matrix(self):
        return self.piece_matrix

    def get_turn(self):
        return self.turn

    def get_state(self):
        return self.state

    def get_highlighted_moves(self):
        return self.highlighted_moves

    def get_promote_position(self):
        return self.promote_position

    def is_selecting(self):
        return self.selected_piece is not None

    #点击，这个部分将会和pygame的点击处理分离开来，
    #我们通过pygame来捕捉到点击信号，然后转交给game来处理

    def handle_click(self, grid_x: int, grid_y: int):
        """
        处理鼠标点击（网格坐标）
        返回: (action, info)
            action: "SELECT" / "MOVE" / "PROMOTE" / "CHECKMATE" / "NONE"
        """
        if not (0 <= grid_x <= 7 and 0 <= grid_y <= 7):
            return ("NONE", None)

        if self.state == GameState.NORMAL:
            return self._handle_normal_click(grid_x, grid_y)
        elif self.state == GameState.PROMOTING:
            return self._handle_promotion_click(grid_x, grid_y)
        else:
            return ("NONE", None)

    def _handle_normal_click(self, grid_x: int, grid_y: int):
        """处理正常状态下的点击"""
        clicked = self.piece_matrix[grid_y][grid_x]

        # 没有选中任何棋子，点击了一个己方棋子 → 选中它
        if self.selected_piece is None:
            if clicked != "space" and clicked.color == self.turn:
                self.selected_piece = clicked
                self.highlighted_moves = set(clicked.get_legal_moves(self.piece_matrix))
                return ("SELECT", (grid_y, grid_x))
            return ("NONE", None)

        # 已经选中了棋子，点击了另一个己方棋子 → 切换选中
        if clicked != "space" and clicked.color == self.turn:
            self.selected_piece = clicked
            self.highlighted_moves = set(clicked.get_legal_moves(self.piece_matrix))
            return ("SELECT", (grid_y, grid_x))

        # 已经选中了棋子，点击了高亮位置 → 走棋
        if (grid_y, grid_x) in self.highlighted_moves:
            return self._execute_move(grid_x, grid_y)

        # 点击了无效位置 → 取消选中
        self.selected_piece = None
        self.highlighted_moves.clear()
        return ("NONE", None)

    def _execute_move(self, to_x: int, to_y: int):
        """执行走棋"""
        piece = self.selected_piece

        move_result, move_info = piece.try_move(to_x, to_y, self.piece_matrix)

        self.selected_piece = None
        self.highlighted_moves.clear()

        if move_result == "PROMOTE":
            self.promote_position = move_info
            self.state = GameState.PROMOTING
            return ("PROMOTE", move_info)

        # 切换回合
        self.turn = "w" if self.turn == "b" else "b"

        # 检测将杀
        if rules.is_checkmate(self.turn, self.piece_matrix):
            self.state = GameState.CHECKMATE
            return ("CHECKMATE", None)

        return ("MOVE", None)

    def _handle_promotion_click(self, grid_x: int, grid_y: int):
        """处理升变选择点击"""
        py, px = self.promote_position
        direction = 1 if self.turn == "w" else -1

        PROMOTING_MAP1 = {0: "Q", 1: "R", 2: "B", 3: "N"}
        PROMOTING_MAP2 = {0: pieces.Queen, 1: pieces.Rook,
                          2: pieces.Bishop, 3: pieces.Knight}

        for i in range(4):
            if grid_x == px + 1 and grid_y == py + i * direction:
                self.piece_matrix[py][px] = PROMOTING_MAP2[i](px, py, self.turn, PROMOTING_MAP1[i])
                self.state = GameState.NORMAL
                self.turn = "w" if self.turn == "b" else "b"

                if rules.is_checkmate(self.turn, self.piece_matrix):
                    self.state = GameState.CHECKMATE
                    return ("CHECKMATE", None)

                return ("PROMOTED", None)

        return ("NONE", None)
