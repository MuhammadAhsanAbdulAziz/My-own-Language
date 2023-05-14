###########################
# IMPORTS
###########################
from string_with_arrows import *

import string

###########################
# CONSTANTS
###########################

DIGITS = '012345689'
LETTERS = string.ascii_letters
LETTERS_DIGITS = LETTERS + DIGITS

###########################
# ERRORS
###########################

class Error:
    def __init__ (self, pos_start, pos_end, error_name, details):
        self.pos_start = pos_start
        self.pos_end = pos_end
        self.error_name = error_name
        self.details = details
    
    def as_string(self):
        result =  f'{self.error_name} : {self.details}\n'
        result += f'File {self.pos_start.fn}, Line {self.pos_start.ln + 1}'
        result += '\n\n' + string_with_arrows(self.pos_start.ftxt, self.pos_start,self.pos_end)
        return result

class IllegalCharError (Error):
    def __init__(self,pos_start, pos_end, details):
        super().__init__(pos_start, pos_end,'Illegal Character',details)

class InvalidSyntaxError (Error):
    def __init__(self,pos_start, pos_end, details = ''):
        super().__init__(pos_start, pos_end,'Illegal Syntax',details)

###########################
# POSITION
###########################

class Position:
    def __init__(self,idx,ln,col,fn,ftxt):
        self.idx = idx
        self.ln = ln
        self.col = col
        self.fn = fn
        self.ftxt = ftxt
    
    def advance(self, current_char):
        self.idx +=1
        self.col +=1

        if current_char == '\n':
            self.ln +=1
            self.col = 0
        return self

    def copy(self):
        return Position(self.idx,self.ln,self.col,self.fn,self.ftxt)

###########################
# TOKENS
###########################

TT_INT = "INT"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_DATATYPE = "DATA TYPE"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_COLON = "COLON"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
KEYWORDS = ['Var','VAR','var']
DATA_TYPES = ['Number','Word','Boolean']
TT_SEMICOLON = "SEMICOLON"

class Token:
    def __init__(self, type_, value = None):
        self.type = type_
        self.value = value

    def __repr__(self):
        if self.value: return f'{self.type}:{self.value}'
        return f'{self.type}'

###########################
# LEXER
###########################

class Lexer:
    def __init__(self, text,fn):
        self.fn = fn
        self.text = text
        self.pos = Position(-1,0,-1,fn,text)
        self.current_char = None
        self.advance()
    
    def advance(self):
        self.pos.advance(self.current_char)
        self.current_char = self.text[self.pos.idx] if self.pos.idx < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())
                self.advance()
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
                self.advance()
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN))
                self.advance()
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON))
                self.advance()
            elif self.current_char == ';':
                tokens.append(Token(TT_SEMICOLON))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char  = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,"'" + char + "'")
        return tokens, None
    
    def make_numbers(self):
        num_str = ''
        dot_count = 0
        
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: break
                dot_count += 1
                num_str += '.'
                self.advance()
            else:
                num_str += self.current_char
                self.advance()
        
        if dot_count == 0:
            return Token(TT_INT, int(num_str))
        else:
            return Token(TT_FLOAT,float(num_str))
    
    def make_identifier(self):
        id_str = ''

        while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
            id_str += self.current_char
            self.advance()

        if id_str in KEYWORDS:
            tok_type = TT_KEYWORD
        elif id_str in DATA_TYPES:
            tok_type =  TT_DATATYPE
        else:
            tok_type = TT_IDENTIFIER
        return Token(tok_type,id_str)

###########################
# NODES
###########################

class NumberNode:
    def __init__(self,tok):
        self.tok = tok
    
    def __repr__(self):
        return f'{self.tok}'

class BinOpNode:
    def __init__ (self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
    
    def __repr__(self):
        return f'({self.left_node},{self.op_tok},{self.right_node})'

###########################
# PARSER
###########################

class Parser:
    def __init__(self,tokens):
        self.tokens = tokens
        self.tok_idx = -1
        self.advance()

    def advance(self, ):
        self.tok_idx +=1
        if self.tok_idx < len(self.tokens):
            self.currrent_tok = self.tokens[self.tok_idx]
            return self.currrent_tok

    def parse(self):
        res = self.expr()
        return res

    def factor(self):
        tok = self.currrent_tok

        if tok.type in (TT_INT,TT_FLOAT):
            self.advance()
            return NumberNode(tok)

    def expr(self):
        return self.BinOp(self.term,(TT_PLUS,TT_MINUS))

    def term(self):
        return self.BinOp(self.factor,(TT_MUL,TT_DIV))

    def BinOp (self,func,ops):
        left = func()

        while self.currrent_tok.type in ops:
            op_tok = self.currrent_tok
            self.advance()
            right = func()
            left = BinOpNode(left,op_tok,right)
        return left
        
###########################
# RUN
###########################

def run(fn,text):

    # Generate Tokens

    lexer = Lexer(text,fn)
    tokens, error = lexer.make_tokens()
    if error: return None, error

    # Generate AST

    parser = Parser(tokens)
    ast = parser.parse()

    return ast, None
