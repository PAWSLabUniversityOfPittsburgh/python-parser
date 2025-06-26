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
from datetime import datetime


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

def post_process_parser(response,fname='tmp1.py'):
    section_concepts = {}
    section_concepts['content_id'] = []
    section_concepts ['section_id']= []    
    section_concepts['content_id'].append(section_concepts['content_id'][-1]+1 if len(section_concepts['content_id']) >0 else 143)
    section_concepts['section_id'].append(path.splitext(fname)[0])
    section_concepts['concept'] = '_'.join(list(response))
    smart_concepts_sections = pd.DataFrame.from_dict(section_concepts)
    timestamp = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    f_timestamp = datetime.today().strftime('%Y%m%d%H%M%S')
    smart_concepts_sections.loc[:,'resource_id'] = 'pfe'
    smart_concepts_sections.loc[:,'is_active'] = 1
    smart_concepts_sections.loc[:,'date_added'] = timestamp # '2024-06-23 19:40:02'
    return smart_concepts_sections#.to_csv(f'./smart_learning_content_section_{f_timestamp}.csv',index=False)
    

if __name__ == '__main__':
    local = True
    ## TODO handle case for non local (such as server api setup)
    if local: 
        PYTHON_TEXTBOOK_EXAMPLE_LIST = ['parsons','quizpet']#['pcex','py-files','pcex','pcex-python-code','quizpet','parsons']
        SMART_CONTENT_LIST = ['pcex','quizpet','pcex-python-code','parsons']
        
        for PYTHON_TEXTBOOK_EXAMPLES in PYTHON_TEXTBOOK_EXAMPLE_LIST:
            print("processing",PYTHON_TEXTBOOK_EXAMPLES)
            section_concepts = {}
            if PYTHON_TEXTBOOK_EXAMPLES in SMART_CONTENT_LIST:
                section_concepts ['content_name']= []
            if PYTHON_TEXTBOOK_EXAMPLES == 'py-files':
                section_concepts['content_id'] = []
                section_concepts ['section_id']= []

            section_concepts['concept'] = []
            
            for root,curr_dir,files in os.walk(f'./{PYTHON_TEXTBOOK_EXAMPLES}/'):
                for fname in tqdm(files):
                    if path.splitext(fname)[1] == '.py':
                        try:
                            codelines,response =  main(local,path.join(root,fname))
                            # print(response)
                            if PYTHON_TEXTBOOK_EXAMPLES == 'py-files':
                                section_concepts['content_id'].append(section_concepts['content_id'][-1]+1 if len(section_concepts['content_id']) >0 else 143)
                                section_concepts['section_id'].append(path.splitext(fname)[0])
                            if PYTHON_TEXTBOOK_EXAMPLES in SMART_CONTENT_LIST:
                                section_concepts['content_name'].append(path.splitext(fname)[0])
                            section_concepts['concept'].append('_'.join(list(response)))
                            # print(section_concepts)

                        except Exception:
                            print(root,fname)
                # print(response['lines'])
            # print(codelines)
            
            smart_concepts_sections = pd.DataFrame.from_dict(section_concepts)#.sort_values(by='section_id')
            # smart_concepts_sections.loc[:,'date_updated'] = pd.to_datetime('today')
            # smart_concepts_sections = smart_concepts_sections.explode('concept')

            # if PYTHON_TEXTBOOK_EXAMPLES == 'py-files': 
            #     db = pd.read_csv('./readingmirror-data-files/smart_learning_content_section.csv')

            # if PYTHON_TEXTBOOK_EXAMPLES in SMART_CONTENT_LIST:
            #     db = pd.read_csv(f'./readingmirror-data-files/smart_learning_content_concepts.csv')
            timestamp = pd.to_datetime('today').strftime('%Y%m%d%H%M%S')

            if PYTHON_TEXTBOOK_EXAMPLES == 'py-files':
                smart_concepts_sections.loc[:,'resource_id'] = 'pfe'
                smart_concepts_sections.loc[:,'is_active'] = 1
                smart_concepts_sections.loc[:,'date_added'] = '2024-06-23 19:40:02'
                smart_concepts_sections.to_csv('./smart_learning_content_section.csv',index=False)

            if PYTHON_TEXTBOOK_EXAMPLES in SMART_CONTENT_LIST:
                smart_concepts_sections.loc[:,'domain']='py'
                smart_concepts_sections.loc[:,'weight']=1
                smart_concepts_sections.loc[:,'active']=1
                smart_concepts_sections.loc[:,'source_method']='parser'
                smart_concepts_sections.loc[:,'importance']=1
                smart_concepts_sections.loc[:,'contributesK']=1
                smart_concepts_sections.loc[:,'component_name'] = smart_concepts_sections.loc[:,'concept']
                smart_concepts_sections.loc[:,'context_name'] = smart_concepts_sections.loc[:,'concept']
                smart_concepts_sections[[x for x in smart_concepts_sections.columns if not(x == 'concept')]].to_csv(f'./smart_learning_content_concepts_{PYTHON_TEXTBOOK_EXAMPLES}_{timestamp}.csv',index=False)
                
            

 # type: ignore


## TODO something from outcomes nothing beyong
## TODO why is it being allocated this way -- indexing mistake ?
## TODO all the worksexamples  -- get the py 





### Parser gives all the concepts -- new section / new concepts
### update the database for chatper sections 
### update the smartcontent database  
### filter in a separate -- no from future (before or present)
### filter smart contne database -- no from future (before or present)




