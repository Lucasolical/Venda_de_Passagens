from main import app
from flask import render_template, request, redirect, url_for
import os
import json

base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, 'dicionarioVoo.json')

def carregar_dados():
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)
    
@app.route("/")
def homepage():
    dados = carregar_dados()
    voos = dados["voos"]
    return render_template("index.html", 
                           lista_de_voos=voos.items(), 
                           search_terms={})

@app.route("/admin_login")
def admin_login_page():
    return render_template("login.html")

@app.route("/login", methods=["POST"])
def login():
    dados = carregar_dados()
    logins = dados["logins"]
    usuario = request.form["usuario"]
    senha = request.form["senha"]
    for user in logins:
        if usuario == user["nome"] and senha == user["senha"]:
            return redirect(url_for("usuarios", nome_usuario=user["nome"]))
    return render_template("login.html", erro="Usuário ou senha incorretos!")

@app.route("/buscar_voos")
def buscar_voos():
    dados = carregar_dados()
    voos = dados["voos"]

    origem_filtro = request.args.get('origem', '').lower()
    destino_filtro = request.args.get('destino', '').lower()
    
    #FAZER 
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
    dados = carregar_dados()
    voos = dados["voos"]
    return render_template("listar_voos.html", lista_de_voos=voos)

@app.route("/usuario/<nome_usuario>/voos")
def listar_voos_para_admin(nome_usuario):
    dados = carregar_dados()
    voos = dados["voos"]
    return render_template("listar_voos_admin.html", 
                           lista_de_voos=voos, 
                           nome_usuario=nome_usuario)

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/cadastrar_voo", methods=["GET", "POST"])
def cadastrar_voo():
    if request.method == "POST":
        # Lê os dados do formulário
        novo_voo = {
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": int(request.form["milhas"]),
            "preco": float(request.form["preco"]),
            "aeronave": request.form["aeronave"],
            "assentos": int(request.form["assentos"])
        }

        codigo = request.form["codigo"]

        with open(json_path, "r", encoding="utf-8") as f:
            dados = json.load(f)

        if "voos" not in dados:
            dados["voos"] = {}
        dados["voos"][codigo] = novo_voo

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        return redirect(url_for("listar_voos_para_admin", nome_usuario="admin"))

    return render_template("cadastrar_voo.html")

@app.route("/excluir_voo/<codigo>", methods=["GET", "POST"])
def excluir_voo(codigo):
    dados = carregar_dados()
    voos = dados["voos"]

    if codigo not in voos:
        return render_template("erro.html", mensagem=f"O voo {codigo} não existe.")

    if request.method == "POST":
        del dados["voos"][codigo]

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)

        return redirect(url_for("listar_voos_para_admin", nome_usuario="admin"))

    return render_template("excluir_voo.html", codigo=codigo, voo=voos[codigo])

@app.route("/editar_voo/<codigo>", methods=["GET", "POST"])
def editar_voo(codigo):
    dados = carregar_dados()
    voos = dados["voos"]

    if codigo not in voos:
        return render_template("erro.html", mensagem=f"O voo {codigo} não existe.")

    if request.method == "POST":

        voo_atualizado = {
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": int(request.form["milhas"]),
            "preco": float(request.form["preco"]),
            "aeronave": request.form["aeronave"],
            "assentos": int(request.form["assentos"])
        }
  
        dados["voos"][codigo] = voo_atualizado
        

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            

        return redirect(url_for("listar_voos_para_admin", nome_usuario="admin"))

    voo_para_editar = voos[codigo]
  
    return render_template("edicao.html", 
                           codigo=codigo, 
                           voo=voo_para_editar)