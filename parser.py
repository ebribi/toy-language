import sys
import lexer

# handle input
arg = sys.argv[1]
try:
    with open(arg, 'r') as f:
        lexer.source = f.read()
except FileNotFoundError:
    lexer.source = arg

class Node:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value
        self.children = []

    def add_child(self, node):
        self.children.append(node)

current_token = None

def advance():
    global current_token
    current_token = lexer.getNextToken()

def error(message="syntax error"):
    print(f"error: {message}")
    sys.exit(1)

def match(token_type):
    if current_token is not None and current_token[0] == token_type:
        token = current_token
        advance()
        return token
    else:
        error(f"expected {token_type}, got {current_token}")

def parse_program():
    node = Node('Program')
    while current_token is not None:
        node.add_child(parse_assignment())
    return node

def parse_assignment():
    node = Node('Assignment')
    if current_token[0] == 'LET':
        node.add_child(Node(*match('LET')))
    node.add_child(Node(*match('IDENTIFIER')))
    node.add_child(Node(*match('ASSIGN'))) 
    node.add_child(parse_exp())
    node.add_child(Node(*match('SEMICOLON')))
    return node

def parse_exp():
    node = Node('Exp')
    node.add_child(parse_term())
    node.add_child(parse_exp_prime())
    return node

def parse_exp_prime():
    if current_token is not None and current_token[0] in ('PLUS','MINUS'):
        node = Node('Exp_Prime')
        node.add_child(Node(*match(current_token[0])))
        node.add_child(parse_term())
        node.add_child(parse_exp_prime())
        return node
    else:
        return Node('epsilon')

def parse_term():
    node = Node('Term')
    node.add_child(parse_fact())
    node.add_child(parse_term_prime())
    return node

def parse_term_prime():
    if current_token is not None and current_token[0] in ('STAR'):
        node = Node('Term_Prime')
        node.add_child(Node(*match('STAR')))
        node.add_child(parse_fact())
        node.add_child(parse_term_prime())
        return node
    else:
        return Node('epsilon')

def parse_fact():
    node = Node('Fact')
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

def print_tree(node, prefix="", is_last=True):
    connector = "└── " if is_last else "├── "
    label = f"{node.type}: {node.value}" if node.value is not None else node.type
    print(prefix + connector + label)
    prefix += "    " if is_last else "│   "
    for i, child in enumerate(node.children):
        print_tree(child, prefix, i == len(node.children) - 1)

advance()
tree = parse_program()
print_tree(tree)
