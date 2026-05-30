#一个走棋的记录类，这个类应该能够被转化为pgn JSON等多种格式，只需要多一个转化器就能够做到
#所以，记载的东西应该尽量详细

class MoveRecord:
    """一步走棋的原始记录，不包含任何格式逻辑"""
    def __init__(self, piece, from_pos, to_pos, captured=False, 
                 promotion=None, castling=False, is_check=False, 
                 is_checkmate=False):
        self.piece = piece          # 棋子对象（不是字符串）
        self.from_pos = from_pos    # (from_y, from_x)
        self.to_pos = to_pos        # (to_y, to_x)
        self.captured = captured    # bool
        self.promotion = promotion  # "Q"/"R"/"B"/"N" 或 None
        self.castling = castling    # bool
        self.is_check = is_check    # bool
        self.is_checkmate = is_checkmate  # bool

    def __repr__(self):
        # 列名映射
        col = {0: "a", 1: "b", 2: "c", 3: "d", 4: "e", 5: "f", 6: "g", 7: "h"}
        row = {0: "8", 1: "7", 2: "6", 3: "5", 4: "4", 5: "3", 6: "2", 7: "1"}
        
        from_str = col[self.from_pos[1]] + row[self.from_pos[0]]
        to_str = col[self.to_pos[1]] + row[self.to_pos[0]]
        
        parts = [f"{self.piece.color}{self.piece.type_char}", f"{from_str}→{to_str}"]
        
        if self.captured:
            parts.append("x")
        if self.promotion:
            parts.append(f"={self.promotion}")
        if self.castling:
            parts.append("O-O" if self.to_pos[1] > self.from_pos[1] else "O-O-O")
        if self.is_check:
            parts.append("+")
        if self.is_checkmate:
            parts.append("#")
        
        return " ".join(parts)
