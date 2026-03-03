import sys

# Accept either a filename (.txt) or a raw string as a command line argument
arg = sys.argv[1]

if arg.endswith('.txt'):
    with open(arg, 'r') as f:
        source = f.read()
else:
    source = arg

print(f"source: '{source}', length: {len(source)}")

# pos tracks the current position in the source string
pos = 0


# Consume and return the next character in the source string
# Returns null terminator '\0' if end of input has been reached
def nextChar():
    global pos
    c = '\0' if pos >= len(source) else source[pos]
    pos += 1
    return c

# Step back one character in the source string
# Called when you've read one character too far to confirm a token is complete
def retract():
    global pos
    pos -= 1   

# Scan the source string and return the next token type as a (type, value) tuple
# Implements a transition-diagram-based lexical analyzer with the following states
#    0 - Start state: reads first character and branches to appropriate state
#    1 - Just read '0': checks for illegal leading zero (e.g 001)
#    2 - Reading a multi-digit literal (starts with 1-9)
#    3 - Reading an identifier (starts with letter or underscore)
# Token types returned: LITERAL, IDENTIFIER, PLUS, MINUS, STAR, ASSIGN, SEMICOLON, LPAREN, RPAREN, EOF, ERROR
def getNextToken():
    state = 0
    while True:
        match state:
            case 0:
                c = nextChar()
                if c == '0':
                    state = 1    # literal zero or error
                elif c in '123456789':
                    lexeme = c
                    state = 2    # start of multi-digit literal
                elif c.isalpha() or c == '_':
                    lexeme = c
                    state = 3    # start of identifier
                elif c == '+':
                    return ('PLUS', '+')
                elif c == '-':
                    return ('MINUS', '-')
                elif c == '*': 
                    return ('STAR', '*')
                elif c == '=':
                    return ('ASSIGN', '=')
                elif c == ';':
                    return ('SEMICOLON', ';')
                elif c == '(':
                    return ('LPAREN', '(')
                elif c == ')':
                    return ('RPAREN', ')')
                elif c == ' ' or c == '\n' or c == '\t':
                    continue    # skip whitespace
                elif c == '\0':
                    return ('EOF', None)
                else:
                    return ('ERROR', c)    # unexpected character
            case 1:
                # Just consumed '0' - peek at next char to detect leading zeros
                c = nextChar()
                if c.isdigit():
                    return ('ERROR', 'leading zero')
                else:
                    retract()    # put back non-digit character
                    return ('LITERAL', '0')
            case 2:
                # Accumulate digits for a multi-digit literal (e.g. 123)
                c = nextChar()
                if c.isdigit():
                    lexeme += c    # keep consuming digits
                else:
                    retract();    # put back non-digit character
                    return ('LITERAL', lexeme)   
            case 3:
                # Accumulate characters for an identifier (letters, digits, underscores)
                c = nextChar()
                if c.isalpha() or c.isdigit() or c == '_':
                    lexeme += c    # keep consuming valid characters
                else:
                    retract()    # put back the non-identifier character
                    return ('IDENTIFIER', lexeme)     

# For demo/testing:
# Drive the lexer - repeatedly call getNextToken() until EOF or ERROR
tokens = []
while True:
    token = getNextToken()
    tokens.append(token)
    if token[0] == 'EOF' or token[0] == 'ERROR':
        break

print(tokens)            
