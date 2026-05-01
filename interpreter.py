import sys
import lexer
import parser as p

# Accept either a filename or a raw string as a command line argument
# Sets lexer.source
arg = sys.argv[1]
try:
    with open(arg, 'r') as f:
        lexer.source = f.read()
except FileNotFoundError:
    lexer.source = arg

lexer.pos = 0

symbol_table = {} # name -> int value
let_vars = set()  # name declared with 'let'

def interpret(tree):
    for assignment in tree.children:
        eval_assignment(assignment)
    for name, val in symbol_table.items():
        print(f"{name} = {val}")

# node.children will be one of:
#    [LET, IDENTIFIER, ASSIGN, Exp, SEMICOLON]  <- let assignment
#    [IDENTIFIER, ASSIGN, Exp, SEMICOLON]       <- normal assignment
def eval_assignment(node):
    is_let = node.children[0].type == 'LET'

    # LET token occupies children[0] in let assignments
    # if is_let == TRUE, shift all subsequent indices by 1
    id_node = node.children[1] if is_let else node.children[0]
    exp_node = node.children[3] if is_let else node.children[2]

    name = id_node.value
    value = eval_exp(exp_node, in_let=is_let)

    symbol_table[name] = value
    if is_let:
        let_vars.add(name)

# node.type == 'Exp'
# children are [Term, Exp_Prime]
def eval_exp(node, in_let=False):
    term = node.children[0]
    exp_prime = node.children[1]

    value = eval_term(term, in_let)
    value = eval_exp_prime(exp_prime, value, in_let)
    return value

# node.type == 'Exp_Prime' or 'epsilon'
# left is the accumulated value from the left side
# children are [PLUS/MINUS, Term, Exp_Prime]
def eval_exp_prime(node, left, in_let=False):
    if node.type == 'epsilon':
        return left

    op = node.children[0] # PLUS or MINUS token
    term = node.children[1]
    exp_prime = node.children[2]

    right = eval_term(term, in_let)
    
    if op.value == '+':
        result = left + right
    else:
        result = left - right

    return eval_exp_prime(exp_prime, result, in_let)

# node.type == 'Term'
# children are [Fact, Term_Prime]
def eval_term(node, in_let=False):
    fact = node.children[0]
    term_prime = node.children[1]

    value = eval_fact(fact, in_let)
    value = eval_term_prime(term_prime, value, in_let)
    return value

# node.type == 'Term_Prime' or epsilon
# left is the accumulated value from teh left side
# children are [STAR, Fact, Term_Prime]
def eval_term_prime(node, left, in_let=False):
    if node.type == 'epsilon':
        return left
    
    op = node.children[0]
    fact = node.children[1]
    term_prime = node.children[2]
    
    right = eval_fact(fact, in_let)
    result = left * right

    return eval_term_prime(term_prime, result, in_let)

# node.type == 'Fact'
def eval_fact(node, in_let=False):
    # First child determines which Fact we're in
    # Options:
    #    [IDENTIFIER]
    #    [LITERAL]
    #    ( Exp )
    #    - Fact
    #    + Fact
    child = node.children[0]

    # [IDENTIFIER] case
    if child.type == 'IDENTIFIER':
        name = child.value
        # Variable has not been assigned
        if name not in symbol_table:
            print("error")
            sys.exit(1)
        # Normal variable is inside a 'LET' statement - not allowed
        if in_let and name not in let_vars:
            print("error, normal variables in let expression")
            sys.exit(1)
        # Passes both checks - returns integer value stored in variable
        return symbol_table[name]

    # [LITERAL] case
    elif child.type == 'LITERAL':
        return int(child.value)

    # ( EXP ) case
    elif child.type == 'LPAREN':
        return eval_exp(node.children[1], in_let)

    # - FACT or + FACT case (unaryy operators)
    elif child.type in ('MINUS','PLUS'):
        # Handle inner Fact
        val = eval_fact(node.children[1], in_let)
        # Negate of preserve the result
        return -val if child.type == 'MINUS' else val

if __name__ == "__main__":
    p.advance()
    tree = p.parse_program()
    interpret(tree)
