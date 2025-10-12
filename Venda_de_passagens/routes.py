from main import app
from flask import render_template,request, redirect, url_for
@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    # Aqui você poderia validar com seu dicionário, se quiser
    return redirect(url_for("usuarios", nome_usuario=usuario))

@app.route("/contatos")
def contatos():
    return render_template("contatos.html")

@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    
    return render_template("usuariopage.html", nome_usuario = nome_usuario)