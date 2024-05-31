# *****************************************************************************
# Python AST parser for the ADL project
# Version 0.1.0, Teemu Sirkia

# Reads a given Python program and creates a JSON object
# describing line-by-line which language elements exist
# in the code.
#
# For the list of the available nodes, see:
# https://docs.python.org/3/library/ast.html#abstract-grammar
# *****************************************************************************

import os
from os import path
from tqdm import tqdm
import pandas as pd
from utils import *


def main(local=True,filename='./py-files/chap2/sec_2_7.py',mode='simple'):
    #TODO 5 -- create table of concepts -- matching tags -- present example integration from concept to textbook
    #TODO 1 -- expressions with parentheses -- simple / complex expression -- section 2.7
    #TODO 2 -- operator overload -- section 2.9 -- instead of Add -- Consider StrAdd
    #TODO 3 -- input function -- section 2.10
    #TODO 4 -- comments

    code,codelines,mode  = read_input_files(local,filename,mode)
    
    nodes = {'lines' : {}}

    try:

        tree = ast.parse(code)
        # tokens = lexer_tokens(code)
        
        startNode = {'name': 'root', 'children': []}

        # Traverse all the nodes in the AST

        if mode == 'complex':
            for node in ast.iter_child_nodes(tree):
                complexTraverse(node, 0, nodes)
        elif mode == 'hierarchical':
            for node in ast.iter_child_nodes(tree):
                hierarchicalTraverse(node, 0, startNode)
        elif mode in ('simple', 'concepts','ast_walk'):
            for node in ast.iter_child_nodes(tree):
                simpleTraverse(node, 0, nodes)
        else:
            print('Parsing failed!\n\nError occurred: Unknown parsing mode', file=sys.stderr)
            sys.exit(1)

        # Convert sets to lists before JSON transformation
        if mode == 'simple' or mode == 'complex':
            for line in nodes['lines']:
                nodes['lines'][line] = list(nodes['lines'][line])
        elif mode == 'hierarchical':
                nodes = startNode
        elif mode == 'concepts':
            concepts = set()
            for line in nodes['lines']:
                for concept in list(nodes['lines'][line]):
                    concepts.add(concept)
            nodes = list(concepts)
        elif mode == 'ast_walk':

            concepts = set()

            for node in ast.walk(tree):
                print(node.__dict__)

        if not(local):
            print(json.dumps(nodes))
        
        if local:
            return codelines ,merge_lines_nodes(nodes)#.union(tokens)

    except Exception as e:
        print('Parsing failed!\n\nError occurred: ' + str(e), file=sys.stderr)
        # print(re.split(r'[<,\s,>,\']',str(type(e)))[3], f'line no {e.args[1][1]}')
        if not(local): sys.exit(1)


if __name__ == '__main__':
    local = True
    PYTHON_TEXTBOOK_EXAMPLES = './py-files/'
    ## TODO handle case for non local (such as server api setup)
    if local: 
        section_concepts = {}
        section_concepts ['sec_name']= []
        section_concepts['concepts'] = []
        
        for root,curr_dir,files in os.walk(PYTHON_TEXTBOOK_EXAMPLES):
            for fname in tqdm(files):
                if path.splitext(fname)[1] == '.py':
                    try:
                        codelines,response =  main(local,path.join(root,fname))
                        # print(response)
                        section_concepts['sec_name'].append(path.splitext(fname)[0])
                        section_concepts['concepts'].append('_'.join(list(response)).lower())
                        # print(section_concepts)
                    except Exception:
                        print(root,fname)
            # print(response['lines'])
        # print(codelines)
        
        smart_concepts_sections = pd.DataFrame.from_dict(section_concepts).sort_values(by='sec_name')
        smart_concepts_sections['prev_concepts'] = smart_concepts_sections['concepts'].shift(1)
        smart_concepts_sections.to_csv('./smart_content_section_concepts.csv',index=False)
 # type: ignore


## TODO something from outcomes nothing beyong
## TODO why is it being allocated this way -- indexing mistake ?
## TODO all the worksexamples  -- get the py 