
# coding: utf-8

# In[1]:

import random
import matplotlib
import pandas as pd
import numpy as np
from sets import Set
import operator
from abc import abstractmethod


# In[2]:

class board:
    # during gameplay, the player that makes the first move will be assigned sym1 and second player sym2 
    def __init__ (self,sym1,sym2):
        self.board_array = [0]*9
        self.game_status = 0 #0 not in game | 1 in game
        self.sym1 = sym1
        self.sym2 = sym2
        self.move_num = 0
        self.board_scoring_array = []
    
    # getter for board
    def return_board(self):
        return self.board_array
    
    # accept player move
    def accept_move(self, pos):
        self.move_num += 1
        if self.move_num%2 != 0:
            player_id = self.sym1
        else:
            player_id = self.sym2
        self.board_array[pos] = player_id
        
    # return possible moves on board
    def possible_moves(self):
        winner = self.return_winner()
        if winner != 0:
            return None
        return [i for i,x in enumerate(self.board_array) if x==0] 

    def best_board(self, weights):
        """Return the best board out of all successor boards"""
        #get a list of successor boards
        successors_lst = self.successors(weights)
        #sort by score
        ss = sorted(successors_lst,key=lambda x: x[1],reverse=True)#setting this to True makes the player learn to lose
        # return the boards with the highest score
        to_sel = [i[1]==ss[0][1] for i in ss]
        sp = []
        for i in range(len(to_sel)):
            if to_sel[i]:
                sp.append(ss[i])
        #select, at random, one of the boards with the highest score
        best_board = sp[random.randrange(0,len(sp))][0]
        return best_board

    

    def successors(self,weights):
        """Returns an array of tuples (board_array, score)"""
        # here we check equality since we want the successors for the subsequent player
        # and we do not want to alter self.move
        if self.move_num%2 == 0:
            player_id = self.sym1
        else:
            player_id = self.sym2
        pm = self.possible_moves()
        successors_lst = []
        for i in pm:
            self.board_scoring_array = list(self.board_array)
            self.board_scoring_array[i] = player_id
            score = self.board_score(weights)
            successors_lst.append((list(self.board_scoring_array),self.board_score(weights)))
        return successors_lst

    def board_score(self,weights):
        scores = self.feature_extractor()
     #   score = np.dot(scores,self.weights)
        score = scores[0]*weights[0]+scores[1]*weights[1]+scores[2]*weights[2]+             scores[3]*weights[3]+scores[4]*weights[4]+scores[5]*weights[5]+scores[6]*weights[6]
        return score

    def feature_extractor(self):
        if self.move_num%2 == 0:
            self_symbol = self.sym1
            opp_symbol = self.sym2        
        else:
            self_symbol = self.sym2
            opp_symbol = self.sym1

        #features
        number_me = self.board_scoring_array.count(self_symbol)
        number_opp = self.board_scoring_array.count(self_symbol)
        number_tworow_me = len(around_me_two(self_symbol,self.board_scoring_array))
        number_tworow_opp = len(around_me_two(opp_symbol,self.board_scoring_array))
        number_threerow_me = len(around_me_three(self_symbol,self.board_scoring_array))
        number_threerow_opp = len(around_me_three(opp_symbol,self.board_scoring_array))
        scores = np.array([1,
                            number_me,
                            number_opp,
                            number_tworow_me,
                            number_tworow_opp,
                            number_threerow_me,
                            number_threerow_opp])
        return scores




    # return winner or 0 for game in progress
    def return_winner(self):
        if (self.board_array[0]==self.board_array[1]==self.board_array[2]!=0):
            winner = self.board_array[0]
            return winner#+' has won!'
        elif (self.board_array[3]==self.board_array[4]==self.board_array[5]!=0):
            winner = self.board_array[3]
            return winner#+' has won!'
        elif (self.board_array[6]==self.board_array[7]==self.board_array[8]!=0):
            winner = self.board_array[6]
            return winner#+' has won!'
        elif (self.board_array[0]==self.board_array[3]==self.board_array[6]!=0):
            winner = self.board_array[0]
            return winner#+' has won!'
        elif (self.board_array[1]==self.board_array[4]==self.board_array[7]!=0):
            winner = self.board_array[1]
            return winner#+' has won!'
        elif (self.board_array[2]==self.board_array[5]==self.board_array[8]!=0):
            winner = self.board_array[2]
            return winner#+' has won!'
        elif (self.board_array[0]==self.board_array[4]==self.board_array[8]!=0):
            winner = self.board_array[0]
            return winner#+' has won!'
        elif (self.board_array[2]==self.board_array[4]==self.board_array[6]!=0):
            winner = self.board_array[2]
            return winner#+' has won!'
        elif (len([i for i,x in enumerate(self.board_array) if x==0])!=0):
            return 0  
        else:
            return 'Draw'

class player:

    def __init__(self):
        self.games_played = 0
        self.game_status = 0 # 1-in game 0-in between games
    
    @abstractmethod
    def make_move(self,symbol):pass

class simple_player(player):
    
    def make_move(self,board):
        possible_moves = board.possible_moves()
        if(possible_moves == None):
            self.game_status = 0
            self.games_played +=1
            return board.return_winner()
        l = len(possible_moves)
        move = possible_moves[random.randrange(0,l)]
        board.accept_move(move)
        
class human_player:
        
    def make_move(self,board,pos):
        possible_moves = board.possible_moves()
        if(possible_moves == None):
            self.game_status = 0
            self.games_played +=1
            return board.return_winner()
        board.accept_move(pos)

        
class learning_player(player):

    def __init__(self, learning_rate=0.001, weights=[random.random() for _ in range(0, 7)]):
        self.games_played = 0
        self.game_status = 0 # 1-in game 0-in between games
        self.weights = weights
        self.learning_rate = learning_rate
    
    def make_move(self,board):
        possible_moves = board.possible_moves()
        if(possible_moves == None):
            self.game_status = 0
            self.games_played +=1
            return board.return_winner()
        move = self.best_move(board,self.weights)
        board.accept_move(move)

    def best_move(self,board,weights):
        """" Return the playable move on the best board"""
        board_array = board.return_board()
        bb = board.best_board(weights) 
        for i in range(len(bb)):
            if bb[i] != board_array[i]:
                return i
            
    def Vest(self,board):
        return board.board_score(self.weights)
    
    def Vtrain(self,board,self_symbol,opp_symbol):        
        outcome = board.return_winner()
        if outcome == self_symbol:
            return 100
        elif outcome == opp_symbol:
            return -100
        elif outcome == 'Draw':
            return 0
        else:
            #board.board_scoring_array = list(board.board_array)
            board.board_scoring_array = list(board.best_board(self.weights))
            return board.board_score(self.weights)
    
    # whoever goes first will automatically be assigned sym1, second player will be assigned sym2
    def update_weights (self,board,self_symbol,opp_symbol):               
        self.weights = self.weights + self.learning_rate*(self.Vtrain(board,self_symbol,opp_symbol)-self.Vest(board))*board.feature_extractor()
        #self.weights = -1*self.weights




# In[3]:

def create_matrix(board_array):
    o =[]
    for i in range (3):
        o.append(board_array[i*3:i*3+3])
    return np.matrix(o)

def around_me_two (symbol,board_array):
    board_mat = create_matrix(board_array)
    two_row = []
    for i in range(3):
        for j in range(3):
            if (board_mat[i,j] == symbol):
                if(board_mat[i,j] == board_mat[i,(j+1) % 3]):
                    two_row.append([(i,j),(i,(j+1) % 3)])
                if(board_mat[i,j] == board_mat[i,(j-1)%3]):
                    two_row.append([(i,j),(i,(j-1)%3)])
                if(board_mat[i,j] == board_mat[(i+1) % 3,j]):
                    two_row.append([(i,j),((i+1) % 3,j)])
                if(board_mat[i,j] == board_mat[(i-1)%3,j]):
                    two_row.append([(i,j),((i-1)%3,j)])
    for i in two_row:
        i[0] = i[0][0]*3+i[0][1]
        i[1] = i[1][0]*3+i[1][1]
    two_row=map(lambda x: list(sort(x)),two_row)    
    return list(eval(x) for x in set([str(x) for x in two_row]))
    

def around_me_three(symbol,board_array):
    three_row_possible = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]
    three_row = []
    for i in three_row_possible:
        if (board_array[i[0]]==board_array[i[1]]==board_array[i[2]]==symbol):
            three_row.append(i)
    return three_row        
    

    
#Learned vs Random
#learning and testing 
n=10000
sym1 = 'x'
sym2 = 'y'

winners =[]
final_results=[]
lr  = (0,0.01,0.001,0.0001,0.00001,0.000001,0.0000001,0.00000001,0.000000001)

for l in lr:

    train_winner = {'player1' : 0,
                   'player2' : 0,
                   'Draw'    : 0}
    
    player1 = learning_player(learning_rate = l)
    player2 = simple_player()

   
    for i in range(n):
        my_board = board(sym1,sym2)
        win = ''
        while win == '':
            if i%2==0:
               # player2.update_weights(my_board)
                if my_board.return_winner()==0:
                    player1.make_move(my_board)
                    player1.update_weights(my_board,sym1,sym2)
                    player2.make_move(my_board)
                else:
                    if my_board.return_winner() == sym1:
                        win = 'player1'
                    elif my_board.return_winner() == sym2:
                        win = 'player2'
                    else:
                        win = 'Draw'
                    train_winner[win]+=1
            else:
                if my_board.return_winner()==0:
                    player2.make_move(my_board)
                    player1.make_move(my_board)
                    player1.update_weights(my_board,sym2,sym1)
                else:
                    if my_board.return_winner() == sym1:
                        win = 'player2'
                    elif my_board.return_winner() == sym2:
                        win = 'player1'
                    else:
                        win = 'Draw'
                    train_winner[win]+=1

    winners.append(train_winner)
    
    N=100
    m=50
    test_winner_df= pd.DataFrame(columns = ('player3','player4','Draw'))

    
    for k in range(N):
        test_winner = {'player3' : 0,
                       'player4' : 0,
                       'Draw'    : 0}
        player3 = learning_player(weights = player1.weights)
        player4 = simple_player()
        for i in range(m):
            my_board = board(sym1,sym2)
            win = ''
            while win == '':
                if i%2==0:
                   # player2.update_weights(my_board)
                    if my_board.return_winner()==0:
                        player3.make_move(my_board)
                        player4.make_move(my_board)
                    else:
                        if my_board.return_winner() == sym1:
                            win = 'player3'
                        elif my_board.return_winner() == sym2:
                            win = 'player4'
                        else:
                            win = 'Draw'
                        test_winner[win]+=1
                else:
                    if my_board.return_winner()==0:
                        player4.make_move(my_board)
                        player3.make_move(my_board)
                    else:
                        if my_board.return_winner() == sym1:
                            win = 'player4'
                        elif my_board.return_winner() == sym2:
                            win = 'player3'
                        else:
                            win = 'Draw'
                        test_winner[win]+=1
        test_winner_df.loc[k] = [test_winner['player3'],test_winner['player4'],test_winner['Draw']]
    final_results.append(test_winner_df.mean())


