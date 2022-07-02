from flask import Flask, render_template
from deta import Deta
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
deta = Deta()
users = deta.Base('users')

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
