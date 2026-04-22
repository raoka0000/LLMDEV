import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from flask import Flask, render_template, request, make_response, session
from original.graph import get_bot_response, get_messages_list, memory

app = Flask(__name__)
app.secret_key = 'your_secret_key'


@app.route('/', methods=['GET', 'POST'])
def index():
    # セッションからthread_idを取得、なければ新しく生成
    if 'thread_id' not in session:
        session['thread_id'] = str(uuid.uuid4())

    if request.method == 'GET':
        memory.storage.clear()
        session.pop('character', None)
        return make_response(render_template('index.html', messages=[], character=''))

    # キャラクター名とメッセージを取得
    character = request.form.get('character', '').strip()
    user_message = request.form.get('user_message', '').strip()

    # キャラクター名未入力ならメッセージを処理しない
    if not character or not user_message:
        messages = get_messages_list(memory, session['thread_id'])
        return make_response(render_template(
            'index.html',
            messages=messages,
            character=session.get('character', '')
        ))

    # キャラクターが変わった場合はメモリをリセット
    prev_character = session.get('character')
    if prev_character != character:
        memory.storage.clear()
        session['thread_id'] = str(uuid.uuid4())
        session['character'] = character

    get_bot_response(user_message, character, memory, session['thread_id'])
    messages = get_messages_list(memory, session['thread_id'])

    return make_response(render_template(
        'index.html',
        messages=messages,
        character=character
    ))


@app.route('/clear', methods=['POST'])
def clear():
    session.pop('thread_id', None)
    session.pop('character', None)
    memory.storage.clear()
    return make_response(render_template('index.html', messages=[], character=''))


if __name__ == '__main__':
    app.run(debug=True)
