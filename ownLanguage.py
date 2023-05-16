###########################
# IMPORTS
###########################
from string_with_arrows import *

import string

###########################
# CONSTANTS
###########################

DIGITS = '0123456789'
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
        super().__init__(pos_start, pos_end,'Invalid Syntax',details)

class RuntimeError (Error):
    def __init__(self,pos_start, pos_end, details = ''):
        super().__init__(pos_start, pos_end,'Runtime Error',details)

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
    
    def advance(self, current_char = None):
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

TT_EOF = "EOF"
TT_INT = "INT"
TT_IDENTIFIER = "IDENTIFIER"
TT_KEYWORD = "KEYWORD"
TT_FLOAT = "FLOAT"
TT_PLUS = "PLUS"
TT_MINUS = "MINUS"
TT_MUL = "MUL"
TT_COLON = "COLON"
TT_DIV = "DIV"
TT_LPAREN = "LPAREN"
TT_RPAREN = "RPAREN"
KEYWORDS = ['Var','VAR','var']
TT_SEMICOLON = "SEMICOLON"

class Token:
    def __init__(self, type_, value = None, pos_start = None, pos_end = None):
        self.type = type_
        self.value = value

        if pos_start:
            self.pos_start = pos_start.copy()
            self.pos_end = pos_start.copy()
            self.pos_end.advance()
        if pos_end:
            self.pos_end = pos_end

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
            # elif self.current_char in LETTERS:
            #     tokens.append(self.make_identifier())
            #     self.advance()
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS,pos_start = self.pos))
                self.advance()
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS,pos_start = self.pos))
                self.advance()
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL,pos_start = self.pos))
                self.advance()
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV,pos_start = self.pos))
                self.advance()
            elif self.current_char == '(':
                tokens.append(Token(TT_LPAREN,pos_start = self.pos))
                self.advance()
            elif self.current_char == ')':
                tokens.append(Token(TT_RPAREN,pos_start = self.pos))
                self.advance()
            else:
                pos_start = self.pos.copy()
                char  = self.current_char
                self.advance()
                return [], IllegalCharError(pos_start, self.pos,"'" + char + "'")
        tokens.append(Token(TT_EOF,pos_start=self.pos))
        return tokens, None
    
    def make_numbers(self):
        num_str = ''
        dot_count = 0
        pos_start = self.pos.copy()        

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
            return Token(TT_INT, int(num_str), pos_start, self.pos)
        else:
            return Token(TT_FLOAT,float(num_str),pos_start, self.pos)

    # def make_identifier(self):
    #     id_str = ''

    #     while self.current_char != None and self.current_char in LETTERS_DIGITS + '_':
    #         id_str += self.current_char
    #         self.advance()

    #     if id_str in KEYWORDS:
    #         tok_type = TT_KEYWORD
    #     elif id_str in DATA_TYPES:
    #         tok_type =  TT_DATATYPE
    #     else:
    #         tok_type = TT_IDENTIFIER
    #     return Token(tok_type,id_str)

###########################
# NODES
###########################

class NumberNode:
    def __init__(self,tok):
        self.tok = tok
        self.pos_start = tok.pos_start
        self.pos_end = tok.pos_end
    
    def __repr__(self):
        return f'{self.tok}'
    
class UnaryNode:
    def __init__(self,op_tok,node):
        self.op_tok = op_tok
        self.node = node
        self.pos_start = self.op_tok.pos_start
        self.pos_end = node.pos_end
    
    def __repr__(self):
        return f'({self.op_tok}, {self.node})'

class BinOpNode:
    def __init__ (self, left_node, op_tok, right_node):
        self.left_node = left_node
        self.op_tok = op_tok
        self.right_node = right_node
        self.pos_start = self.left_node.pos_start
        self.pos_end = self.right_node.pos_end
    
    def __repr__(self):
        return f'({self.left_node},{self.op_tok},{self.right_node})'

###########################
# PARSER RESULT
###########################

class ParserResult:
    def __init__(self):
        self.error = None
        self.node = None
    
    def register(self,res):
        if isinstance(res, ParserResult):
            if res.error:
                self.error = res.error
            return res.node
        return res

    def success(self,node):
        self.node = node
        return self

    def failure(self,error):
        self.error = error
        return self

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
        if not res.error and self.currrent_tok.type != TT_EOF:
            return res.failure(InvalidSyntaxError(
                self.currrent_tok.pos_start,self.currrent_tok.pos_end,
                "Expected '+', '-', '*', '/' "
            ))
        return res

    def factor(self):
        res = ParserResult()
        tok = self.currrent_tok

        if tok.type in (TT_PLUS,TT_MINUS):
            res.register(self.advance())
            factor = res.register(self.factor())
            if res.error : return res
            return res.success(UnaryNode(tok, factor))

        elif tok.type in (TT_INT,TT_FLOAT):
            res.register(self.advance())
            return res.success(NumberNode(tok))
        
        elif tok.type == TT_LPAREN :
            res.register(self.advance())
            expr = res.register(self.expr())
            if res.error: return res
            if self.currrent_tok.type == TT_RPAREN:
                res.register(self.advance())
                return res.success(expr)
            else:
                return res.failure(InvalidSyntaxError(
                    self.currrent_tok.pos_start, self.currrent_tok.pos_end ,
                    "Expected ')'"
                ))
        
        return res.failure(InvalidSyntaxError(
			tok.pos_start, tok.pos_end,
			"Expected int or float"
		))

    def expr(self):
        return self.BinOp(self.term,(TT_PLUS,TT_MINUS))

    def term(self):
        return self.BinOp(self.factor,(TT_MUL,TT_DIV))

    def BinOp (self,func,ops):
        res = ParserResult()
        left = res.register(func())
        if res.error : return res

        while self.currrent_tok.type in ops:
            op_tok = self.currrent_tok
            res.register(self.advance())
            right = res.register(func())
            if res.error : return res
            left = BinOpNode(left,op_tok,right)

        return res.success(left)

###########################
# RUNTIME RESULT
###########################

class RTResult:
    def __init__(self):
        self.value = None
        self.error = None
    
    def register(self, res):
        if res.error : self.error = res.error
        return res.value
    
    def success(self, value):
        self.value = value
        return self
    
    def failure(self, error):
        self.error = error
        return self

###########################
# VALUES
###########################

class Number:
    def __init__(self,value):
        self.value = value
        self.set_pos()
    
    def set_pos(self, pos_start = None, pos_end  = None):
        self.pos_start = pos_start
        self.pos_end = pos_end
        return self
    
    def added_to(self,other):
        if isinstance(other, Number):
            return Number(self.value + other.value), None
    
    def subbed_to(self,other):
        if isinstance(other, Number):
            return Number(self.value - other.value), None
        
    def multed_to(self,other):
        if isinstance(other, Number):
            return Number(self.value * other.value), None
        
    def divided_to(self,other):
        if isinstance(other, Number):
            if other.value == 0:
                return None,RuntimeError(other.pos_start,other.pos_end,'Division by zero')
            return Number(self.value / other.value),
        
    def __repr__(self):
        return str(self.value)


###########################
# COMPILER
###########################

class Compiler:
    def visit(self,node):
        method_name = f'visit_{type(node).__name__}'
        method = getattr(self,method_name,self.no_visit_name)
        return method(node)
    
    def no_visit_name(self,node):
        raise Exception(f'No visit_{type(node).__name__} method defined')
    
    ##########################

    def visit_NumberNode(self,node):
        return RTResult().success( 
        Number(node.tok.value).set_pos(node.pos_start,node.pos_end)
        )
    
    def visit_BinOpNode(self,node):
        res = RTResult()
        left = res.register(self.visit(node.left_node))
        if res.error : return res
        right = res.register(self.visit(node.right_node))
        if res.error : return res

        if node.op_tok.type == TT_PLUS:
            result , error = left.added_to(right)
        elif node.op_tok.type == TT_MINUS:
            result, error = left.subbed_to(right)
        elif node.op_tok.type == TT_MUL:
            result, error = left.multed_to(right)
        elif node.op_tok.type == TT_DIV:
            result, error = left.divided_to(right)
        
        if error: return res.failure(error)
        else:
            return res.success(result.set_pos(node.pos_start,node.pos_end))
    
    def visit_UnaryNode(self,node):
        res = RTResult()
        number = res.register(self.visit(node.node))
        if res.error : return res

        error = None
        if node.op_tok.type == TT_MINUS:
            number, error = number.multed_to(number(-1))
        
        if error: return res.failure(error)
        else:
            return res.success(number.set_pos(node.pos_start,node.pos_end))

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
    if ast.error : return None, ast.error

    # Run Program
    compiler = Compiler()
    result = compiler.visit(ast.node)

    return result.value,result.error
