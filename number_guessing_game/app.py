from flask import Flask, render_template, request, jsonify
import random
import json

app = Flask(__name__)

def new_game(difficulty):
    ranges = {'easy': (1, 50), 'medium': (1, 100), 'hard': (1, 200)}
    min_num, max_num = ranges[difficulty]
    return {
        'number': random.randint(min_num, max_num),
        'attempts': 0,
        'score': 1000,
        'hints_used': 0,
        'range': [min_num, max_num],
        'difficulty': difficulty,
        'guesses': []
    }

game_state = None

@app.route('/')
def home():
    global game_state
    game_state = new_game('medium')  # Default difficulty
    return render_template('game.html')

@app.route('/start', methods=['POST'])
def start_game():
    global game_state
    difficulty = request.form.get('difficulty', 'medium')
    game_state = new_game(difficulty)
    return jsonify({'message': f'New {difficulty} game started!', 'range': game_state['range']})

@app.route('/guess', methods=['POST'])
def guess():
    global game_state
    try:
        guess = int(request.form['guess'])
        game_state['attempts'] += 1
        game_state['guesses'].append(guess)
        game_state['score'] = max(0, game_state['score'] - 20)  # Decrease score per attempt
        
        if guess == game_state['number']:
            return jsonify({
                'result': 'win',
                'message': f'Congratulations! You won with {game_state["score"]} points in {game_state["attempts"]} attempts!',
                'score': game_state['score']
            })
        elif guess < game_state['number']:
            game_state['range'][0] = max(game_state['range'][0], guess)
            return jsonify({'result': 'low', 'message': 'Too low!', 'range': game_state['range']})
        else:
            game_state['range'][1] = min(game_state['range'][1], guess)
            return jsonify({'result': 'high', 'message': 'Too high!', 'range': game_state['range']})
    except ValueError:
        return jsonify({'result': 'error', 'message': 'Invalid number!'})

@app.route('/hint', methods=['POST'])
def hint():
    global game_state
    game_state['hints_used'] += 1
    game_state['score'] = max(0, game_state['score'] - 100)  # Hint penalty
    
    hints = [
        f"It's {'even' if game_state['number'] % 2 == 0 else 'odd'}",
        f"It's {'greater' if game_state['number'] > sum(game_state['range']) / 2 else 'less'} than {sum(game_state['range']) // 2}",
        f"The sum of its digits is {sum(int(d) for d in str(game_state['number']))}"
    ]
    available_hints = [h for i, h in enumerate(hints) if i >= game_state['hints_used'] - 1]
    return jsonify({'hint': available_hints[0] if available_hints else 'No more hints!'})

if __name__ == '__main__':
    app.run(debug=True)