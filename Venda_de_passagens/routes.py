from main import app
from flask import render_template, request, redirect, url_for
from dicionarioVoo import voos, logins

@app.route("/")
def homepage():
    return render_template("index.html", 
                           lista_de_voos=voos.items(), 
                           search_terms={})

@app.route("/admin_login")
def admin_login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    for user in logins:
        if usuario == user["nome"] and senha == user["senha"]:
            return redirect(url_for("usuarios", nome_usuario=user["nome"]))
    return render_template("login_admin.html", erro="Usuário ou senha incorretos!")

@app.route("/buscar_voos")
def buscar_voos():

    origem_filtro = request.args.get('origem', '').lower()
    destino_filtro = request.args.get('destino', '').lower()
    
    # (adicionar data_ida e data_volta aqui depois)

    voos_filtrados = {}
    
    for codigo, voo in voos.items():
        origem_match = origem_filtro in voo['origem'].lower()
        destino_match = destino_filtro in voo['destino'].lower()
        
        if origem_match and destino_match:
            voos_filtrados[codigo] = voo
            
    return render_template("index.html", 
                           lista_de_voos=voos_filtrados.items(),
                           search_terms={'origem': request.args.get('origem', ''), 
                                         'destino': request.args.get('destino', '')})


@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    return render_template("adminpage.html", nome_usuario=nome_usuario)

@app.route("/voos")
def listar_voos():
    return render_template("listar_voos.html", lista_de_voos=voos)

@app.route("/usuario/<nome_usuario>/voos")
def listar_voos_para_admin(nome_usuario):
    return render_template("listar_voos_admin.html", 
                           lista_de_voos=voos, 
                           nome_usuario=nome_usuario)

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")