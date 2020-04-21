How to get a four-digit score on Flappy Bird?
Introduction to Reinforcement Learning

Ariel Modai - Niels Nicolas 

#Explanation of the code  

This project was developed on python and is divided into four python scripts:

##bot.py : The class of our algorithm
This file contains the Bot class that applies the Q-Learning logic to the game.
    
##flappy.py : the actual visual gameplay 
Running this code will open a game map and start Flappy Bird games. The Bird is moving according to the Q Values of the Q-table that is inside the `qvalues.json` file.

##learn.py} : faster learning/training 
This script is similar to flappy.py, except it runs without any pygame visualization, so it's much faster. We can also track the score obtained after each game, as well as keeping track with the learning rate value (by using the `--verbose` command). 
    
##initialize_qvalues.py} - This file resets the q-values : 
Running this code will clear the qvalues.json file and set the Q-table clear. 


#How to run the code 

The project requires `pygame` 1.9.6.

- 1) place yourself inside your src directory with your terminal. 
- 2) run `python initialize_qvalues.py` to reset the q-values
- 3) run `python flappy.py` and observe multiple flappy bird games without training the algorithm first. The bird will usely crash down before even reaching the first pipes. 
- 4) run `python learn.py --iter XXX --verbose` with XXX being the number of iterations you want to do. We usually did 20000 iterations for our tests. This code will help you train your algorithm way faster, as it doesn't require game visualizations. 
- 5) run `python flappy.py` one last time, to visualize the bird actually reaching higher scores in the game map ! 

Thank you for playing ! 
________________________
