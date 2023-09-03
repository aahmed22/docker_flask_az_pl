from flask import Flask, render_template

app = Flask(__name__, template_folder='templates')
app.static_folder = 'static'

@app.route("/")
def welcome():
    return render_template('main.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0')