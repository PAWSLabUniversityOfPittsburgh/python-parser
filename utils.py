import ast, json, sys, re, os
from os import path
from tqdm import tqdm
import pandas as pd
from ply.lex import lex

# These nodes will be ignored and are not added to the node list.
#
# For example, the operators are skipped because the actual operator
# will be added to the list instead of the operator family.
nodesToSkip = {'Store', 'Load', 'Name', 'Expr', 'arguments', 'Subscript', 'BoolOp', 'BinOp', 'Compare', 'UnaryOp'}
tokensToSkip = {}
allowed_call_names = ['print','input','dict','set','list']

# *****************************************************************************
# Special handlers for some nodes

def handleNameConstant(node, line):
    """ Converts the NameConstant node to represent the type of the value (True, False, None). """
    return str(node.value)

def handleNum(node, line):
    """ Converts the Num node to represent the type of the value (Int, Float). """
    return node.n.__class__.__name__.capitalize()

handlers = {'Num' : handleNum, 'NameConstant' : handleNameConstant}
# *****************************************************************************

def simpleTraverse(node, line, nodes):

    name = node.__class__.__name__
    # if name == 'Constant': print(re.split(r'[<,\s,>,\']',str(type(node.__dict__['value']))))
    # if name == 'Call': print(node.__dict__['func'].__dict__['id'])
    
    if name == 'Constant':
        name = re.split(r'[<,\s,>,\']',str(type(node.__dict__['value'])))[3].capitalize()

    if name =='Call':  
        name = f"{node.__dict__['func'].__dict__['id']}" if 'id' in node.__dict__['func'].__dict__ else ''
        if not(name.lower() in allowed_call_names): name = ''

    # Only some nodes contain line number
    if hasattr(node, 'lineno'):
        line = node.lineno

    if name not in nodesToSkip:
        if line not in nodes['lines']:
            nodes['lines'][line] = set()
        if name not in handlers:
            
            nodes['lines'][line].add(name)
        else:
            nodes['lines'][line].add(handlers[name](node, line))

    for child in ast.iter_child_nodes(node):
        simpleTraverse(child, line, nodes)

def complexTraverse(node, line, nodes):

    name = node.__class__.__name__

    # Only some nodes contain line number
    if hasattr(node, 'lineno'):
        line = node.lineno

    endLine = line

    current = {'name': name, 'startLine': line}

    if name not in nodesToSkip:
        if line not in nodes['lines']:
            nodes['lines'][line] = []
        if name not in handlers:
            nodes['lines'][line].append(current)
        else:
            current['name'] = handlers[name](node, line)
            nodes['lines'][line].append(current)

    maxLine = endLine
    for child in ast.iter_child_nodes(node):
        maxLine = max(maxLine, complexTraverse(child, line, nodes))

    if maxLine != line:
        current['endLine'] = maxLine

    return maxLine

def hierarchicalTraverse(node, line, currentNode):

    name = node.__class__.__name__

    # Only some nodes contain line number
    if hasattr(node, 'lineno'):
        line = node.lineno

    endLine = line

    current = {'name': name, 'startLine': line, 'children': []}

    if name not in nodesToSkip:
        if name not in handlers:
            currentNode['children'].append(current)
        else:
            current['name'] = handlers[name](node, line)
            currentNode['children'].append(current)
    else:
        current = currentNode

    maxLine = endLine
    for child in ast.iter_child_nodes(node):
        maxLine = max(maxLine, hierarchicalTraverse(child, line, current))

    if maxLine != line:
        current['endLine'] = maxLine

    return maxLine


def read_input_files(local=True,filename='./py-files/chap2/sec_2_1.py',format="simple"):
    if not(local):
        data = input()
        parsed = json.loads(data)
        code = parsed['code']
        mode = parsed.get('mode', 'simple')
        return code,mode

    if local:
        with open(filename) as f:
            code = f.read()
            codelines = code.split('\n')
            return code,codelines, format

def merge_lines_nodes(nodes):
    conceptset = []
    for lineno,conceptlist in nodes['lines'].items():
        conceptset.extend(set(conceptlist))
    return set(conceptset)


def lexer_tokens(code):
    tokens = (
    'NAME','NUMBER',
    'PLUS','MINUS','TIMES','DIVIDE','EQUALS',
    'LPAREN','RPAREN',
    )

    # Tokens

    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_TIMES   = r'\*'
    t_DIVIDE  = r'/'
    t_EQUALS  = r'='
    t_LPAREN  = r'\('
    t_RPAREN  = r'\)'
    t_NAME    = r'[a-zA-Z_][a-zA-Z0-9_]*'

    lexer = lex()

    # Parsing rules

    precedence = (
        ('left','PLUS','MINUS'),
        ('left','TIMES','DIVIDE'),
        ('right','UMINUS'),
        )
    
    lexer.input(code)
    ret_tokens = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        
        if not(tok in tokensToSkip):
            ret_tokens.append(tok)
    
    return set(ret_tokens)

