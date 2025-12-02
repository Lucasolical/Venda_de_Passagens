from main import app
from flask import render_template, request, redirect, url_for
import os
import json
import pandas as pd
import arvore as bt

base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, 'dicionarioVoo.json')
csv_path = os.path.join(base_dir, 'clientes.csv')

Ap_Raiz = None
DF_Clientes = None

def inicializar_arvore():
    global Ap_Raiz, DF_Clientes
    if os.path.exists(csv_path):
        DF_Clientes = pd.read_csv(csv_path, dtype=str)
        
        Ap_Raiz = None
        chave_inicial = 0
        Ap_Raiz, _ = bt._InserirElementos(Ap_Raiz, 4, DF_Clientes, chave_inicial)
        print("Árvore de Clientes carregada!")
    else:
        df_vazio = pd.DataFrame(columns=["cpf", "nome", "reserva", "data", "milhas"])
        df_vazio.to_csv(csv_path, index=False)
        DF_Clientes = df_vazio
        Ap_Raiz = None

inicializar_arvore()

def carregar_dados():
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def homepage():
    dados = carregar_dados()    
    voos = dados["voos"]
    return render_template("index.html", lista_de_voos=voos.items(), search_terms={})

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

@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    return render_template("adminpage.html", nome_usuario=nome_usuario)

@app.route("/usuario/<nome_usuario>/voos")
def listar_voos_para_admin(nome_usuario):
    dados = carregar_dados()
    voos = dados["voos"]
    return render_template("listar_voos_admin.html", lista_de_voos=voos, nome_usuario=nome_usuario)

@app.route("/buscar_voos")
def buscar_voos():
    dados = carregar_dados()
    voos = dados["voos"]
    origem_filtro = request.args.get('origem', '').lower()
    destino_filtro = request.args.get('destino', '').lower()
    voos_filtrados = {}
    for codigo, voo in voos.items():
        if (origem_filtro in voo['origem'].lower()) and (destino_filtro in voo['destino'].lower()):
            voos_filtrados[codigo] = voo
    return render_template("index.html", lista_de_voos=voos_filtrados.items(), search_terms={'origem': request.args.get('origem', ''), 'destino': request.args.get('destino', '')})

@app.route("/cadastrar_voo", methods=["GET", "POST"])
def cadastrar_voo():
    if request.method == "POST":
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
        if "voos" not in dados: dados["voos"] = {}
        dados["voos"][codigo] = novo_voo
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return redirect(url_for("listar_voos_para_admin", nome_usuario="admin"))
    return render_template("cadastrar_voo.html")

@app.route("/excluir_voo/<codigo>", methods=["GET", "POST"])
def excluir_voo(codigo):
    dados = carregar_dados()
    voos = dados["voos"]
    if codigo not in voos: return render_template("erro.html", mensagem=f"O voo {codigo} não existe.")
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
    if codigo not in voos: return render_template("erro.html", mensagem=f"O voo {codigo} não existe.")
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
    return render_template("edicao.html", codigo=codigo, voo=voos[codigo])

@app.route("/cadastro")
def cadastro():
    return render_template("cadastro.html")

@app.route("/voos")
def listar_voos():
    dados = carregar_dados()
    voos = dados["voos"]
    return render_template("listar_voos.html", lista_de_voos=voos)



@app.route("/clientes", methods=["GET", "POST"])
def gerenciar_clientes():
    global Ap_Raiz, DF_Clientes
    
    resultados = []
    mensagem = None

    if os.path.exists(csv_path):
        DF_Clientes = pd.read_csv(csv_path, dtype=str)

    if request.method == "POST":
        tipo_busca = request.form.get("tipo_busca")
        valor_busca = request.form.get("valor_busca", "").strip()

        if tipo_busca == "cpf":
            try:
                if not valor_busca: raise ValueError
                cpf_int = int(valor_busca)
                
                cliente_lista = bt.BuscarCliente(Ap_Raiz, cpf_int, DF_Clientes)
                
                if cliente_lista:
                    dict_cliente = {
                        "cpf": cliente_lista[0], 
                        "nome": cliente_lista[1], 
                        "reserva": cliente_lista[2], 
                        "data": cliente_lista[3], 
                        "milhas": cliente_lista[4]
                    }
                    resultados = [dict_cliente]
                else:
                    mensagem = "CPF não encontrado."
            except ValueError:
                mensagem = "CPF inválido. Digite apenas números."

        elif tipo_busca == "nome":

            filtro = DF_Clientes[DF_Clientes['nome'].str.contains(valor_busca, case=False, na=False)]
            resultados = filtro.to_dict('records')
            if not resultados:
                mensagem = "Nenhum cliente com esse nome."

        elif tipo_busca == "reserva":
            filtro = DF_Clientes[DF_Clientes['reserva'].str.contains(valor_busca, case=False, na=False)]
            resultados = filtro.to_dict('records')
            if not resultados:
                mensagem = "Nenhuma reserva encontrada com esse código."

    if not resultados and request.method == "GET":
        resultados = DF_Clientes.to_dict('records') if DF_Clientes is not None else []

    return render_template("gestaoclientes.html", clientes=resultados, mensagem=mensagem)

@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():
    global Ap_Raiz, DF_Clientes
    
    novo_cliente = {
        "cpf": request.form["cpf"],
        "nome": request.form["nome"],
        "reserva": request.form["reserva"],
        "data": request.form["data"],
        "milhas": request.form["milhas"]
    }
    
    novo_df = pd.DataFrame([novo_cliente])
    DF_Clientes = pd.concat([DF_Clientes, novo_df], ignore_index=True)
    DF_Clientes.to_csv(csv_path, index=False)
    
    inicializar_arvore()
    
    return redirect(url_for("gerenciar_clientes"))