#!/usr/bin/env python

import sys
from time import sleep
from random import choice

class Game(object):
    '''
    A game class for 'Rock', 'Paper', 'Scissors'.
    Will play a nominal amount of games, and then exit.
    
    To start playing create an instance, game = Game().
    Then simply start playing  with game.play().
    
    Keyword arguments
    :games: the amount of games to play, (default 1)

    '''
    def __init__(self, games=1):
        self.options = ['rock', 'paper', 'scissors']
        self.game_cycles = games
        self.wait = 1
        
    def play(self, chosen=None):
        '''
        Plays the game, expects input from user.
        To bypass user input, use chosen arg
        
        All inputs are validated against self.options
        
        Keyword arguments
        :chosen: the hand you wish to play eg 'rock', (default=None)
        
        '''
        if chosen:
            chosen = self.validate_input(chosen, self.options)
        while not chosen:
            msg = 'Please type Rock, Paper, or Scissors, then press enter: '
            chosen = raw_input(msg)
            chosen = self.validate_input(chosen, self.options)
        c = choice(self.options)
        print 'Player: %s vs Computer: %s' %(chosen, c)
        sleep(self.wait)
        plyr = self.options.index(chosen)
        comp = self.options.index(c)
        result = self.decide(plyr=plyr, comp=comp)
        sleep(self.wait)
        self.game_cycles -= 1
        self.play_again()       
        
    def validate_input(self, input_, options):
        '''
        Validate input, test if it matches any of the options
        White space and case do not affect validation
        
        '''
        i = input_.lower().strip()
        if i not in options:
            print 'Sorry, "%s" is not a valid choice.\n' %(input_)
            return None
        return i

    def decide(self, plyr, comp):
        if (plyr - 1) == comp or plyr == (comp - 2):
            print 'Congratulations you won!'
            return 1
        elif (comp -1) == plyr or comp == (plyr - 2):
            print "Bad luck, you lost"
            return 0
        else:
            print 'A draw!'
            return 2
            
    def play_again(self):
        options = ['y', 'n']        
        if self.game_cycles < 1:
            self.end()
        else:
            r = False
            while not r:
                msg = 'You have %s game(s) remaining, play again "Y" or "N"? '\
                %(self.game_cycles)
                r = raw_input(msg)
                
                r = self.validate_input(r, options)
            if r == 'y':
                self.play()
            else:
                self.end()
    
    def end(self):
        print 'Thanks for playing, good bye'        
        sys.exit()
            

if __name__ == '__main__':
    number_games = '1' and sys.argv[-1]
    game = Game(int(number_games))
    game.play()
    

     
        
    

        
        