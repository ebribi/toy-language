# Toy Language Interpreter - Class Project

A from-scratch lexer, parser, and interpreter for a small expression langauge, built as part of a programming language and compilers course project at Brooklyn College.

## Language Features

Programs consist of integer assignment statements. Variables decalred with `let` are single-assignment and may only reference other `let` variables on the right-hand side.

## Error Handling

- Syntax errors (e.g. leading zeros, missing semicolons)
- Use of uninitialized variables
- Normal variables referenced inside `let` expressions

## Usage

```bash
python interpreter.py <file>
python interpreter.py "let x=1; y= 2; z = ---(x+y)*(x+-y);"
```

## Files

- `lexer.py` - tokenizer
- `parser.py` - recursive descent parser, produces a parse tree
- `interpreter.py` - tree-walk interpreter
- `tests/` - test cases from the project spec
