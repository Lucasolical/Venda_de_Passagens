from main import app 
from flask import render_template, request, redirect, url_for
                                                           
import os 
import json 
import pandas as pd 


import arvorePesquisaCPF as bt_cpf 
import arvorePesquisaNome as bt_nome 


base_dir = os.path.dirname(__file__)
json_path = os.path.join(base_dir, 'dicionarioVoo.json')
csv_path = os.path.join(base_dir, 'clientes.csv')
    

Ap_Raiz_CPF = None 
Ap_Raiz_Nome = None
Dataframe_clientes = None


def construir_arvore(dataframe, ordem, coluna, bt_modulo):

    Ap_Raiz = None

    if dataframe.empty:
        return None
    
    #índice da coluna que será usada como chave(0 para cpf, 1 para nome).
    indice_coluna = dataframe.columns.get_loc(coluna)
    
    for i in range(len(dataframe)):
        reg = bt_modulo.Registro()
        try:
            # Define o valor da CHAVE
            if coluna == 'cpf':
                # Converte o CPF para inteiro
                reg.Chave = int(dataframe.iloc[i, indice_coluna])
            elif coluna == 'nome':
                # Converte o Nome para string
                reg.Chave = str(dataframe.iloc[i, indice_coluna])
            else:
                continue
                
            reg.Elemento = i 
            
            # Insere o Registro na Árvore.
            Ap_Raiz = bt_modulo.Insere(reg, Ap_Raiz, ordem)
        except ValueError:
            continue
        except Exception:
            continue
            
    return Ap_Raiz


#Pegar os dados do csv e construir a arovre 
def inicializar_arvores():

    global Ap_Raiz_CPF, Ap_Raiz_Nome, Dataframe_clientes
    
    if os.path.exists(csv_path):
        Dataframe_clientes = pd.read_csv(csv_path, dtype=str)
        
        # Constrói a Árvore B de CPF  com ordem 4 
        Ap_Raiz_CPF = construir_arvore(Dataframe_clientes, 4, 'cpf', bt_cpf)
        print("Árvore de Clientes por CPF carregada!")

        Ap_Raiz_Nome = construir_arvore(Dataframe_clientes, 4, 'nome', bt_nome)
        print("Árvore de Clientes por Nome carregada!")

    else:
        # Cria um arquivo CSV vazio se ele não existir e seta as raízes como nulas.
        df_vazio = pd.DataFrame(columns=["cpf", "nome", "reserva", "data", "milhas"])
        df_vazio.to_csv(csv_path, index=False)
        Dataframe_clientes = df_vazio
        Ap_Raiz_CPF = None
        Ap_Raiz_Nome = None


inicializar_arvores()


def carregar_dados():
    """Função auxiliar para carregar dados do JSON (voos e logins)."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)



@app.route("/")
def homepage():
    """Rota da página inicial (Módulo do Passageiro)."""
    dados = carregar_dados()    
    voos = dados["voos"] 
    return render_template("index.html", lista_de_voos=voos.items(), search_terms={})




@app.route("/admin_login")
def admin_login_page():
    """Rota para a página de login de Administradores/Clientes."""
    return render_template("login.html")



@app.route("/login", methods=["POST"])
def login():
    """Lógica de Autenticação (Dicionários)."""
    dados = carregar_dados()
    logins_passengers = dados.get("loginsusuarios", [])
    
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    if usuario == "Lucas" and senha == "matoseco":
        return redirect(url_for("usuarios", nome_usuario=usuario))

    for user in logins_passengers:
        if usuario == user["nome"] and senha == user["senha"]:
            return redirect(url_for("homepage")) 

    return render_template("login.html", erro="Usuário ou senha incorretos!")



@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    """Rota para o Painel Administrativo (Módulo Administrativo)."""
    if nome_usuario != "Lucas":
        return redirect(url_for("admin_login_page"))
    return render_template("adminpage.html", nome_usuario=nome_usuario)



@app.route("/usuario/<nome_usuario>/voos")
def listar_voos_para_admin(nome_usuario):
    """Lista todos os voos para o Administrador."""
    if nome_usuario != "Lucas":
        return redirect(url_for("admin_login_page"))
        
    dados = carregar_dados()
    voos = dados["voos"] 
    return render_template("listar_voos_admin.html", lista_de_voos=voos, nome_usuario=nome_usuario)



@app.route("/buscar_voos")
def buscar_voos():
    """Filtra voos disponíveis na homepage (Módulo Passageiro)."""
    dados = carregar_dados()
    voos = dados["voos"]
    origem_filtro = request.args.get('origem', '').lower()
    destino_filtro = request.args.get('destino', '').lower()
    voos_filtrados = {}
    

    for codigo, voo in voos.items():
        if (origem_filtro in voo['origem'].lower()) and (destino_filtro in voo['destino'].lower()):
            voos_filtrados[codigo] = voo
            
    return render_template("index.html", search_terms={'origem': request.args.get('origem', ''), 'destino': request.args.get('destino', '')}, lista_de_voos=voos_filtrados.items())


@app.route("/cadastrar_voo", methods=["GET", "POST"])
def cadastrar_voo():
    """Adiciona um novo voo ao dicionário (JSON)."""
    
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
        return redirect(url_for("listar_voos_para_admin", nome_usuario="Lucas"))
    return render_template("cadastrar_voo.html")


@app.route("/excluir_voo/<codigo>", methods=["GET", "POST"])
def excluir_voo(codigo):
    """Remove um voo específico do dicionário (JSON)."""
    dados = carregar_dados()
    voos = dados["voos"]
    if codigo not in voos: return render_template("erro.html", mensagem=f"O voo {codigo} não existe.")
    
    if request.method == "POST":
        del dados["voos"][codigo] 
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return redirect(url_for("listar_voos_para_admin", nome_usuario="Lucas"))
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
        return redirect(url_for("listar_voos_para_admin", nome_usuario="Lucas"))
    return render_template("edicao.html", codigo=codigo, voo=voos[codigo])



@app.route("/cadastro")
def cadastro():
    """Página de Cadastro de Clientes."""
    return render_template("cadastro.html")


# TODO  VERIFICAR PORQUE ESTA DANDO ERRO
# @app.route("/realizar_cadastro", methods=["POST"])
# def realizar_cadastro():
#     """Lógica de cadastro de um novo cliente."""
#     global Dataframe_clientes
    
#     nome = request.form["nome"]
#     cpf = request.form["cpf"]
#     senha = request.form["senha"]

#     with open(json_path, "r", encoding="utf-8") as f:
#         dados = json.load(f)

#     # Verifica se o CPF já existe.
#     if Dataframe_clientes is not None and cpf in Dataframe_clientes['cpf'].values:
#         return render_template("cadastro.html", erro="CPF já cadastrado.")

#     # Atualiza o JSON de logins
#     novo_usuario_login = {"nome": nome, "senha": senha, "cpf": cpf}
#     if "loginsusuarios" not in dados:
#         dados["loginsusuarios"] = []
#     dados["loginsusuarios"].append(novo_usuario_login)
#     with open(json_path, "w", encoding="utf-8") as f:
#         json.dump(dados, f, indent=4, ensure_ascii=False)
    
#     # Atualiza o CSV de clientes
#     novo_cliente_csv = {"cpf": cpf, "nome": nome, "reserva": "", "data": "", "milhas": "0"}
#     novo_df = pd.DataFrame([novo_cliente_csv])
#     Dataframe_clientes = pd.concat([Dataframe_clientes, novo_df], ignore_index=True)
#     Dataframe_clientes.to_csv(csv_path, index=False)
    
#     inicializar_arvores()
    
#     return redirect(url_for("admin_login_page"))


@app.route("/voos")
def listar_voos():
    """Rota para listar voos em uma página simples (Módulo Passageiro)."""
    dados = carregar_dados()
    voos = dados["voos"]
    return render_template("listar_voos.html", lista_de_voos=voos)


@app.route("/clientes", methods=["GET", "POST"])
def gerenciar_clientes():
    """
    Rota principal de Gestão de Clientes. 
    Lida com a listagem inicial e todas as consultas otimizadas por Árvore B.
    """
    global Ap_Raiz_CPF, Ap_Raiz_Nome, Dataframe_clientes 
        
    resultados = []
    mensagem = None

    if os.path.exists(csv_path):
        Dataframe_clientes = pd.read_csv(csv_path, dtype=str)
        if Ap_Raiz_CPF is None or Ap_Raiz_Nome is None:
             inicializar_arvores()


    if request.method == "POST":
        tipo_busca = request.form.get("tipo_busca")
        valor_busca = request.form.get("valor_busca", "").strip()

        if tipo_busca == "cpf":
            try:
                if not valor_busca: raise ValueError
                cpf_int = int(valor_busca)
                
                cliente_dict = bt_cpf.BuscarCPF(Ap_Raiz_CPF, cpf_int, Dataframe_clientes)
                
                if cliente_dict:
                    resultados = [cliente_dict] 
                else:
                    mensagem = "CPF não encontrado."
            except ValueError:
                mensagem = "CPF inválido. Digite apenas números."

        elif tipo_busca == "nome":

            cliente_dict = bt_nome.BuscarNome(Ap_Raiz_Nome, valor_busca, Dataframe_clientes)
            
            if cliente_dict:
                resultados = [cliente_dict]
            else:
                # Caso a busca exata falhe, faz uma busca parcial usando Pandas
                filtro = Dataframe_clientes[Dataframe_clientes['nome'].str.contains(valor_busca, case=False, na=False)]
                resultados = filtro.to_dict('records')
                if not resultados:
                    mensagem = "Nenhum cliente com esse nome."

    # Exibir na ordem
    if not resultados:
        if Ap_Raiz_CPF is not None and request.method == "GET":
            # Usa a Árvore B para garantir que a lista inicial esteja em ordem crescente de CPF.
            resultados = bt_cpf.ListarEmOrdem(Ap_Raiz_CPF, Dataframe_clientes)
        elif Dataframe_clientes is not None:
            resultados = Dataframe_clientes.to_dict('records')
        else:
             resultados = []

    return render_template("gestaoclientes.html", clientes=resultados, mensagem=mensagem)




@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():
    """Cadastra um novo cliente diretamente pelo painel administrativo."""
    global Dataframe_clientes 
    
    novo_cliente = { 
        "cpf": request.form["cpf"],
        "nome": request.form["nome"],
        "reserva": request.form["reserva"],
        "data": request.form["data"],
        "milhas": request.form["milhas"]
    }
    
    # Adiciona o cliente ao DataFrame e salva no CSV.
    novo_df = pd.DataFrame([novo_cliente])
    Dataframe_clientes = pd.concat([Dataframe_clientes, novo_df], ignore_index=True)
    Dataframe_clientes.to_csv(csv_path, index=False)

    # Reconstrói as Árvores B para incluir o novo cliente.
    inicializar_arvores()
    
    return redirect(url_for("gerenciar_clientes"))