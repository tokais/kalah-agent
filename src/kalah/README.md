# Kalah implementation for Alpha Zero General

An implementation of a simple game provided to check extendability of the framework. Main difference of this game comparing to Othello is that it allows draws, i.e. the cases when nobody won after the game ended. To support such outcomes ```Arena.py``` and ```Coach.py``` classes were modified. Also the players are able to make mulkiple moves.


and the first line of ```__main__``` to
```python
g = KalahGame()
```
 Make similar changes to ```pit.py```.

To start training a model for TicTacToe:
```bash
python main.py
```
To start a tournament of 100 episodes with the model-based player against a random player:
```bash
python pit.py
```
You can play againt the model by switching to HumanPlayer in ```pit.py```

### Experiments
ToDO

### Contributors and Credits
* [Vincent](https://github.com/Firevince)

The implementation is based on the game of Othello (https://github.com/suragnair/alpha-zero-general/tree/master/othello).
