import ast, json, sys, re, os
from ast import Call, Name, Attribute, Load,Store
from os import path
from tqdm import tqdm
import pandas as pd
from ply.lex import lex
from version import __developer__

# These nodes will be ignored and are not added to the node list.
#
# For example, the operators are skipped because the actual operator
# will be added to the list instead of the operator family.
nodesToSkip = {'Store', 'Load', 'Name', 'Expr', 'arg', 'arguments','Subscript', 'BoolOp', 'BinOp', 'Compare', 'UnaryOp'} ## we skip these because this data can be parsed with other nodes
tokensToSkip = {}
associated_py_concepts = json.load(open(path.join(path.dirname(__file__), './static/py_keyword_functions.json'))) ## function keywords associated concepts
op_py_concepts = json.load(open(path.join(path.dirname(__file__), './static/py_ops.json')))


# *****************************************************************************
# Special handlers for some nodes

def handleNameConstant(node, line):
    """ Converts the NameConstant node to represent the type of the value (True, False, None). """
    return str(node.value)

def handleNum(node, line):
    """ Converts the Num node to represent the type of the value (Int, Float). """
    return node.n.__class__.__name__.capitalize()

handlers = {'Num' : handleNum, 'NameConstant' : handleNameConstant}

def get_name_from_ast_object(node,type):
    if type == 'Name':
        # print(node.__dict__,node.__dict__['id'])
        name = node.__dict__['id']
        if name.endswith('Error'): return 'Exception-Types'
        
        if name in associated_py_concepts: return associated_py_concepts[name].capitalize()
        if node.__dict__['ctx'] == Store: return 'Variable-decl-or-assign'
        if node.__dict__['ctx'] == Load: return "Variable-usage"
    
    if type == 'Attribute':
        # pass
        name = node.__dict__['attr']
        if name.endswith('Try') or name.endswith('ExceptHandler'): return 'Exception-Handler'
        if name in associated_py_concepts: return associated_py_concepts[name].capitalize()
        return name

    if type == 'Call':
        
        CallObjectDict = node.__dict__['func'].__dict__
        CallObjectNode = node.__dict__['func']

        lineno = CallObjectDict['lineno']
        
        if False: print(CallObjectNode.__class__.name,
            CallObjectDict,
            CallObjectDict['id'] if 'id' in CallObjectDict['id'] else CallObjectDict['value'],
            CallObjectDict['ctx']
        )

        if 'id' in CallObjectDict:
            return f"{associated_py_concepts[CallObjectDict['id']].capitalize()}" if CallObjectDict['id'] in associated_py_concepts else 'Class-Obj-Instantiate', lineno

        elif 'attr' in CallObjectDict:
            return f"{associated_py_concepts[CallObjectDict['attr']].capitalize()}" if CallObjectDict['attr'] in associated_py_concepts else 'ClassMethod-or-Function-Call', lineno
        
        else: f"Parsed Concept {type}: this should not happen -- email {__developer__}"

    else:
        
        if type in op_py_concepts:
            print(type)
            return op_py_concepts[type].capitalize()
    
    return type.capitalize()


# *****************************************************************************

def simpleTraverse(node, line, nodes,prev_node = None):

    name = node.__class__.__name__
    lineno = node.__dict__['lineno'] if 'lineno' in node.__dict__ else 0#node.__dict__[''].__dict__['lineno']
    # if name == 'Constant': print(re.split(r'[<,\s,>,\']',str(type(node.__dict__['value']))))
    # if name == 'Call': print(node.__dict__['func'].__dict__['id'])
    # print(prev_node)
    name = 'if-elif' if name.lower() == 'if' and not(prev_node == None) and type(prev_node) == ast.If else name

    prev_node = node.__dict__['orelse'][0] if name.lower() == 'if' and \
                len(node.__dict__['orelse']) > 0 and\
                 type(node.__dict__['orelse'][0]) == ast.If \
                else node if prev_node == None else prev_node
    
    if name.lower() == 'if' and len(node.__dict__['orelse']) > 0: name = name
    
    if name.lower() == 'if'  and \
        len(node.__dict__['orelse']) > 0 and \
        not(type(node.__dict__['orelse'][0])) == ast.If: name = f'{name}-else'
    if name.lower() == 'elif': name = f'{name}-else'

    if name == 'Name':
        # print(name,node.__dict__)
        # print(name, prev_node.__dict__)
        
        name = get_name_from_ast_object(node,'Name')
            

    if name == 'Attribute':
        # print(name, node.__dict__['attr'].capitalize(), node.__dict__['value'].__dict__['id'],prev_node.__dict__)
        
        name = get_name_from_ast_object(node,'Attribute')


    if name == 'Constant':
        # print(name, node.__dict__)
        name = re.split(r'[<,\s,>,\']',str(type(node.__dict__['value'])))[3].capitalize()
        

    if name == 'Call':  

        name,lineno = get_name_from_ast_object(node,'Call')

    else:
        if name not in nodesToSkip:
            
            name = get_name_from_ast_object(node,name)
        

    if name not in nodesToSkip:
        if line not in nodes['lines']:
            nodes['lines'][line] = set()
        if name not in handlers:
            
            nodes['lines'][line].add(name)
        else:
            nodes['lines'][line].add(handlers[name](node, line))

    for child in ast.iter_child_nodes(node):
        simpleTraverse(child, line, nodes, prev_node)

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

