# Module level variable to store source string, set by the parser
source = ""

# pos tracks the current position in the source string
pos = 0

# Map single character symbols to their token types
# Dictionary lookup is used over elif chain for efficiency & maintainability
SINGLE_CHAR_TOKENS = {
    '+': 'PLUS',
    '-': 'MINUS',
    '*': 'STAR',
    '=': 'ASSIGN',
    ';': 'SEMICOLON',
    '(': 'LPAREN',
    ')': 'RPAREN',
}

# Map keywords to their token types
# Checked after scanning an identifier to distinguish keywords from variable names
KEYWORDS = {
    'let': 'LET'
}

# Consume and return the next character in the source string
# Returns null terminator '\0' if end of input has been reached
def next_char():
    global pos
    c = '\0' if pos >= len(source) else source[pos]
    pos += 1
    return c

# Step back one character in the source string
# Called when you've read one character too far to confirm a token is complete
def retract():
    global pos
    pos -= 1   

# Scan the source string and return the next token as a (type, value) tuple
# Implements a transition-diagram-based lexical analyzer with the following states
#    0 - Start state: reads first character and branches to appropriate state
#    1 - Just read '0': checks for illegal leading zero (e.g 001)
#    2 - Reading a multi-digit literal (starts with 1-9)
#    3 - Reading an identifier (starts with letter or underscore)
# Returns None at end of input
# Token types returned: LITERAL, IDENTIFIER, LET, PLUS, MINUS, STAR, ASSIGN, SEMICOLON, LPAREN, RPAREN, ERROR
def get_next_token():
    state = 0
    while True:
        c = next_char()
        match state:
            case 0:
                if c == '0':
                    state = 1    # literal zero or error (e.g. 001)
                elif c.isdigit() and c != '0':
                    lexeme = c
                    state = 2    # start of multi-digit literal
                elif c.isalpha() or c == '_':
                    lexeme = c
                    state = 3    # start of identifier
                elif c in SINGLE_CHAR_TOKENS:
                    return (SINGLE_CHAR_TOKENS[c], c)    # single character token
                elif c.isspace():
                    continue    # skip whitespace
                elif c == '\0':
                    return None   # end of input
                else:
                    return ('ERROR', c)    # unexpected character
            case 1:
                # Just consumed '0' - peek at next char to detect leading zeros
                if c.isdigit():
                    return ('ERROR', 'leading zero')
                else:
                    retract()    # put back non-digit character
                    return ('LITERAL', '0')
            case 2:
                # Accumulate digits for a multi-digit literal (e.g. 123)
                if c.isdigit():
                    lexeme += c    # keep consuming digits
                else:
                    retract()    # put back non-digit character
                    return ('LITERAL', lexeme) 
            case 3:
                # Accumulate characters for an identifier (letters, digits, underscores)
                if c.isalpha() or c.isdigit() or c == '_':
                    lexeme += c    # keep consuming valid characters
                else:
                    retract()    # put back the non-identifier character
                    # check if lexeme is a keyword before returning IDENTIFIER
                    if lexeme in KEYWORDS:
                        return (KEYWORDS[lexeme], lexeme)
                    return ('IDENTIFIER', lexeme)     
