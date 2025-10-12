from main import app
from flask import render_template
@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/contatos")
def contatos():
    return render_template("contatos.html")

@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    return render_template("usuariopage.html", nome_usuario = nome_usuario)