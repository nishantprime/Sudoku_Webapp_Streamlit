# @title Sudoku Solver
import requests
import json


def fetch_puzzle(difficulty):
    body = {
        "difficulty": difficulty, # "easy", "medium", or "hard" (defaults to "easy")
        "solution": False, # True or False (defaults to True)
        "array": True # True or False (defaults to False)
    }
    headers =  {"Content-Type":"application/json"}

    response = requests.post("https://you-do-sudoku-api.vercel.app/api", json=body, headers=headers)
    data = json.loads(response.text)
    puzzle = data['puzzle']
    for i in range(9):
        for j in range(9):
            puzzle[i][j] = int(puzzle[i][j])
    for i in range(9):
        print(' '.join(str(puzzle[i])))

    return puzzle


def column(n):
    array = []
    for i in range(9):
        array.append(puzzle[i][n-1])
    return array
def row(n):
    return puzzle[n-1]
def block(n):
    array = []
    row_sets = [[0,1,2],[3,4,5],[6,7,8]]

    row_set = row_sets[(n-1)//3]
    column_set = row_sets[(n-1)%3]

    for rows in row_set:
        for col in column_set:
            array.append(puzzle[rows][col])
    return array


def missing(n):
    rows = []
    columns = []
    blocks = []
    for i in range(1,10):
        if n not in row(i):
            rows.append(i)
        if n not in column(i):
            columns.append(i)
        if n not in block(i):
            blocks.append(i)
    return rows,columns,blocks


# finding possible places

def possible_place_in_row(n,r):

    current_row = row(r)
    if n in current_row:
        return []
    possibilities = [(i+1) for i in range(9) if current_row[i] == 0]
    rows,columns,blocks = missing(n)
    possibilities = [i for i in possibilities if i in columns]

    block_set = (r-1)//3

    block_sets = [[1,2,3],[4,5,6],[7,8,9]]
    affected_blocks = block_sets[block_set]

    possible_blocks = [i for i in affected_blocks if i in blocks]
    possibles = []

    for i in  possibilities:
        if (((i-1)//3)+1 + 3*block_set) in possible_blocks:
            possibles.append(i)
    return possibles

def possible_place_in_column(n,c):
    current_column = column(c)
    if n in current_column:
        return []
    possibilities = [(i+1) for i in range(9) if current_column[i] == 0]
    rows,columns,blocks = missing(n)
    possibilities = [i for i in possibilities if i in rows]

    block_set = (c-1)//3

    block_sets = [[1,4,7], [2,5,8], [3,6,9]]
    affected_blocks = block_sets[block_set]

    possible_blocks = [i for i in affected_blocks if i in blocks]
    possibles = []

    for i in  possibilities:
        if (((i-1)//3)*3 + 1 + block_set) in possible_blocks:
            possibles.append(i)
    return possibles

def possible_place_in_block(n,b):
    current_block = block(b)
    if n in current_block:
        return []
    possibilities = [(i+1) for i in range(9) if current_block[i] == 0]
    blank_positions = [[(i-1)//3 + 1 + 3*((b-1)//3),(i-1)%3 + 1 + 3*((b-1)%3)] for i in possibilities]
    rows,columns,blocks = missing(n)

    possible_positions = [i for i in blank_positions if i[0] in rows and i[1] in columns]

    return possible_positions


def solve(puzzle):
    progress = True
    while progress:
        progress = False
        for s in range(1,10):
            for i in range(9):
                r = possible_place_in_row(s,i+1)
                if len(r) == 1:
                    progress = True
                    puzzle[i][r[0]-1] = s
                    print('filled a block -',s,'(',i+1, r[0],')')
                c = possible_place_in_column(s,i+1)
                if len(c) == 1:
                    progress = True
                    puzzle[c[0]-1][i] = s
                    print('filled a block -',s,'(',c[0],i+1,')')
    
        print('-'*20)
    
        for s in range(1,10):
            for i in range(9):
                b = possible_place_in_block(s,i+1)
                if len(b) == 1:
                    progress = True
                    puzzle[b[0][0] -1][b[0][1] -1] = s
                    print('filled a block -',s,'(',b[0][0],b[0][1],')')
    return puzzle
