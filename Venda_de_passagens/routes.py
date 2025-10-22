from main import app
from flask import render_template,request, redirect, url_for
from dicionarioVoo import*

@app.route("/")
def homepage():
    return render_template("homepage.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    for user in logins:
        if usuario == user["nome"] and senha == user["senha"]:
            return redirect(url_for("usuarios", nome_usuario=user["nome"]))
    return render_template("homepage.html", erro="Usuário ou senha incorretos!")

@app.route("/contatos")
def contatos():
    return render_template("contatos.html")

@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    return render_template("usuariopage.html", nome_usuario = nome_usuario)

@app.route("/voos")
def listar_voos():
    return render_template("listar_voos.html", lista_de_voos=voos)
