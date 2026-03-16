import sys
import lexer

# Accept either a filename or a raw string as a command line argument
# Sets lexer.source so the lexer module can access the input
arg = sys.argv[1]
try:
    with open(arg, 'r') as f:
        lexer.source = f.read()
except FileNotFoundError:
    lexer.source = arg

# Reset lexer position for new input
lexer.pos = 0

# Node represents a single node in the parse tree
# type - the grammar symbol or token type (e.g. 'Program', 'Assignment', 'IDENTIFIER')
# value - the token value for terminal nodes (e.g. 'x', '1', '+'), None for nonterminals
# children - ordered list of child nodes
class Node:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

# Tracks the current token being examined by the parser
current_token = None

# Advance to the next token by calling the lexer
def advance():
    global current_token
    current_token = lexer.get_next_token()

# Print error message and exit
# Called on syntax errors during parsing
def error(message="syntax error"):
    print(f"error: {message}")
    sys.exit(1)

# Consume the current token if it matches the expected type
# Returns the consumed token so it can be added to the parse tree
# Calls error() if the current token does not match
def match(token_type):
    if current_token is not None and current_token[0] == token_type:
        token = current_token
        advance()
        return token
    else:
        error(f"expected {token_type}, got {current_token}")

# Program -> Assignment*
# Entry point for the parser - parses all assignments until end of input
def parse_program():
    node = Node('Program')
    while current_token is not None:
        node.add_child(parse_assignment())
    return node

# Assignment -> Identifier = Exp ; | let Identifier = Exp ;
# Handles both regular and single-assignment (let) variable assignments
def parse_assignment():
    node = Node('Assignment')
    if current_token is None:
        error("unexpected end of input")
    if current_token[0] == 'LET':
        node.add_child(Node(*match('LET')))
    node.add_child(Node(*match('IDENTIFIER')))
    node.add_child(Node(*match('ASSIGN'))) 
    node.add_child(parse_exp())
    node.add_child(Node(*match('SEMICOLON')))
    return node

# Exp -> Term Exp'
def parse_exp():
    node = Node('Exp')
    node.add_child(parse_term())
    node.add_child(parse_exp_prime())
    return node

# Exp' -> + Term Exp' | - Term Exp' | epsilon
# Handles left-recursive addition and subtraction
def parse_exp_prime():
    if current_token is not None and current_token[0] in ('PLUS','MINUS'):
        node = Node('Exp_Prime')
        node.add_child(Node(*match(current_token[0])))
        node.add_child(parse_term())
        node.add_child(parse_exp_prime())
        return node
    else:
        return Node('epsilon')

# Term -> Fact Term'
def parse_term():
    node = Node('Term')
    node.add_child(parse_fact())
    node.add_child(parse_term_prime())
    return node

# Term' -> * Fact Term' | epsilon
# Handles left-recursive multiplication
def parse_term_prime():
    if current_token is not None and current_token[0] == 'STAR':
        node = Node('Term_Prime')
        node.add_child(Node(*match('STAR')))
        node.add_child(parse_fact())
        node.add_child(parse_term_prime())
        return node
    else:
        return Node('epsilon')

# Fact -> ( Exp ) | - Fact | + Fact | Literal | Identifier
# Base case of expression parsing - handles grouping, unary operators, and values
def parse_fact():
    node = Node('Fact')
    if current_token is None:
        error("unexpected end of input")
    if current_token[0] == 'LPAREN': 
        node.add_child(Node(*match('LPAREN')))
        node.add_child(parse_exp())
        node.add_child(Node(*match('RPAREN')))
    elif current_token[0] in ('MINUS','PLUS'):
        node.add_child(Node(*match(current_token[0])))
        node.add_child(parse_fact())
    elif current_token[0] == 'LITERAL':
        node.add_child(Node(*match('LITERAL')))
    elif current_token[0] == 'IDENTIFIER':
        node.add_child(Node(*match('IDENTIFIER')))
    else:
        error(f"unexpected token {current_token}")
    return node

# Recursively print the parse tree with visual connectors
# Indent is managed via prefix string passed down through recursive calls
def print_tree(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    label = f"{node.type}: {node.value}" if node.value is not None else node.type
    print(prefix + connector + label)
    prefix += "    " if is_last else "│   "
    for i, child in enumerate(node.children):
        print_tree(child, prefix, i == len(node.children) - 1)

# Loads the first token and parse the program
if __name__ == "__main__":
    advance()
    tree = parse_program()
    print_tree(tree)
