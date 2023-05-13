###########################
# IMPORTS
###########################

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
    def __init__ (self,error_name,details,CharTrackCount):
        self.error_name = error_name
        self.details = details
        self.CharTrackCount = CharTrackCount
    
    def as_string(self):
        result =  f'{self.error_name} : {self.details}  at character ' f'{self.CharTrackCount} '
        return result

class IllegalCharError (Error):
    def __init__(self,details,CharTrackCount):
        super().__init__('Illegal Character',details,CharTrackCount)

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
    def __init__(self, text):
        self.text = text
        self.pos = -1
        self.current_char = None
        self.CharTrackCount = 0
        self.advance()
    
    def advance(self):
        self.pos +=1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def make_tokens(self):
        tokens = []

        while self.current_char != None:
            if self.current_char in ' \t':
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char in DIGITS:
                tokens.append(self.make_numbers())
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char in LETTERS:
                tokens.append(self.make_identifier())
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char == '+':
                tokens.append(Token(TT_PLUS))
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char == '-':
                tokens.append(Token(TT_MINUS))
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char == '*':
                tokens.append(Token(TT_MUL))
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char == '/':
                tokens.append(Token(TT_DIV))
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char == ':':
                tokens.append(Token(TT_COLON))
                self.advance()
                self.CharTrackCount +=1
            elif self.current_char == ';':
                tokens.append(Token(TT_SEMICOLON))
                self.advance()
                self.CharTrackCount +=1
            else:
                char  = self.current_char
                self.advance()
                return [], IllegalCharError("'" + char + "'",self.CharTrackCount)
        return tokens, None
    
    def make_numbers(self):
        num_str = ''
        dot_count = 0
        
        while self.current_char != None and self.current_char in DIGITS + '.':
            if self.current_char == '.':
                if dot_count == 1: 
                    break
                dot_count += 1
                num_str += '.'
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
# RUN
###########################

def run(text):
    lexer = Lexer(text)
    tokens, error = lexer.make_tokens()

    return tokens, error
