#!/usr/bin/python3
from flask import Flask, render_template
import uuid
from os import getenv

app = Flask(__name__, template_folder='static')
inst = getenv('TYPE', None)

@app.route('/', strict_slashes=False)
def entry_point():
    """This is the entry point for the Frontend"""
    cache_id = str(uuid.uuid4())
    return render_template('login.html',
                            cache_id=cache_id,
                            TYPE=inst)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=True)
