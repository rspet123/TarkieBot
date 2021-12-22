from flask import Flask
from flask import render_template
from flask import Markup
from threading import Thread
from replit import db
app = Flask('')
@app.route('/')
def main():
    return render_template("webapp.html")
def keep_alive():
    server = Thread(target=run)
    server.start()
def run():
    app.run(host="0.0.0.0", port=8080)
