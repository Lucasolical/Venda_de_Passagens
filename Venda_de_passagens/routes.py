from main import app # Importa a instância principal do Flask ('app') do arquivo main.py.
from flask import render_template, request, redirect, url_for # Importa funções essenciais do Flask:
                                                             # - render_template: carrega arquivos HTML.
                                                             # - request: acessa dados de formulários (POST/GET).
                                                             # - redirect, url_for: redireciona o usuário entre as páginas.
import os # Biblioteca para interagir com o sistema operacional (caminhos de arquivo).
import json # Biblioteca para trabalhar com arquivos JSON (onde estão voos e logins).
import pandas as pd # Biblioteca poderosa para manipulação de dados em tabela (DataFrame), usada para clientes.
import datetime # NOVO: Necessário para registrar a data da compra/reserva.

from groq import Groq # Importar o groq para utilizar o chatbot

# Importa as implementações customizadas da Árvore B para otimizar diferentes buscas:
import arvorePesquisaCPF as bt_cpf # Árvore B indexada por CPF (chave numérica).
import arvorePesquisaNome as bt_nome # Árvore B indexada por Nome (chave de string/alfabética).

# --- Configurações de Caminhos de Arquivo ---
base_dir = os.path.dirname(__file__) # Pega o diretório atual do arquivo routes.py.
json_path = os.path.join(base_dir, 'dicionarioVoo.json') # Caminho para o arquivo JSON (dicionários de voos e logins).
csv_path = os.path.join(base_dir, 'clientes.csv') # Caminho para o arquivo CSV (dados persistentes dos clientes).
    
# --- Variáveis Globais (Armazenamento de Estado) ---
# Essas variáveis precisam ser globais para que todas as rotas e funções possam acessá-las.
Ap_Raiz_CPF = None # Armazena a Raiz da Árvore B de CPF. É o ponto de entrada para todas as buscas por CPF.
Ap_Raiz_Nome = None # Armazena a Raiz da Árvore B de Nome. Ponto de entrada para buscas por Nome/Inicial.
DF_Clientes = None # Armazena os dados dos clientes em um DataFrame Pandas (cópia dos dados do clientes.csv).


# Variaveis para utilizar os grafos
Grafo_Voos = None
Mapa_Cidades = None

from utils_grafo import construir_grafo_voos, buscar_melhor_conexao, gerar_diagrama_grafo


def carregar_dados():
    """Função auxiliar para carregar dados do JSON (voos e logins)."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- FUNÇÕES DE CONSTRUÇÃO DE ÍNDICE (ÁRVORE B) ---

def inicializar_grafo():
    """Função que constrói o Grafo de Voos."""
    global Grafo_Voos, Mapa_Cidades
    dados = carregar_dados()
    # Constrói o grafo se houver voos
    if "voos" in dados:
        Grafo_Voos, Mapa_Cidades = construir_grafo_voos(dados["voos"])
    print("Grafo de Voos carregado!")



def _construir_arvore(df, ordem, key_col_name, bt_module):
    """Função auxiliar para construir uma Árvore B a partir de um DataFrame (DF_Clientes)."""
    Ap_Raiz = None
    if df.empty:
        return None
    
    # Descobre o índice da coluna que será usada como CHAVE (Ex: 0 para 'cpf', 1 para 'nome').
    key_col_index = df.columns.get_loc(key_col_name)
    
    # Itera sobre cada linha (registro) do DataFrame de clientes.
    for i in range(len(df)):
        reg = bt_module.Registro()
        try:
            # 1. Define o valor da CHAVE (CPF ou Nome)
            if key_col_name == 'cpf':
                # Converte o CPF para inteiro, que é o tipo de chave esperado pela Árvore B de CPF.
                reg.Chave = int(df.iloc[i, key_col_index])
            elif key_col_name == 'nome':
                # Converte o Nome para string, chave esperada pela Árvore B de Nome.
                reg.Chave = str(df.iloc[i, key_col_index])
            else:
                continue
                
            # 2. Define o PONTEIRO (Elemento)
            # O Elemento armazena o índice da linha 'i' do DataFrame.
            # Este é o link que a Árvore B usará para localizar o registro completo no CSV.
            reg.Elemento = i 
            
            # 3. Insere o Registro (Chave + Ponteiro) na Árvore B.
            Ap_Raiz = bt_module.Insere(reg, Ap_Raiz, ordem)
        except ValueError:
            # Captura erro se, por exemplo, o CPF não puder ser convertido para número.
            continue
        except Exception:
            # Captura erro se, por exemplo, o CPF (chave) for duplicado.
            continue
            
    return Ap_Raiz # Retorna a raiz da Árvore B construída.


def inicializar_arvores():
    """Função principal que carrega os dados do CSV e constrói ambas as Árvores B."""
    global Ap_Raiz_CPF, Ap_Raiz_Nome, DF_Clientes # Permite modificar as variáveis globais.
    
    if os.path.exists(csv_path):
        # Carrega os dados dos clientes do arquivo CSV para o DataFrame Pandas.
        DF_Clientes = pd.read_csv(csv_path, dtype=str)
        
        # 1. Constrói a Árvore B de CPF (Ordem 4)
        Ap_Raiz_CPF = _construir_arvore(DF_Clientes, 4, 'cpf', bt_cpf)
        print("Árvore de Clientes por CPF carregada!")

        # 2. Constrói a Árvore B de Nome (Ordem 4)
        Ap_Raiz_Nome = _construir_arvore(DF_Clientes, 4, 'nome', bt_nome)
        print("Árvore de Clientes por Nome carregada!")

    else:
        # Cria um arquivo CSV vazio se ele não existir e seta as raízes como nulas.
        df_vazio = pd.DataFrame(columns=["cpf", "nome", "reserva", "data", "milhas"])
        df_vazio.to_csv(csv_path, index=False)
        DF_Clientes = df_vazio
        Ap_Raiz_CPF = None
        Ap_Raiz_Nome = None

inicializar_arvores() # A Árvore B é carregada logo na inicialização do sistema.

    
inicializar_grafo() # Grafo carregado na inicializacao do sistema
# --------------------------------------------------------------------------------------------------
# --- ROTAS (ENDPOINTS) DO FLASK ---
# --------------------------------------------------------------------------------------------------

@app.route("/")
def homepage():
    dados = carregar_dados()    
    voos = dados["voos"]
    return render_template("index.html", lista_de_voos=voos.items(), search_terms={})

@app.route("/admin_login")
def admin_login_page():
    return render_template("login.html")

@app.route("/logout")
def logout():
    return redirect(url_for("admin_login_page"))


@app.route("/login", methods=["POST"])
def login():
    """Lógica de Autenticação (MODIFICADA para passar CPF)."""
    dados = carregar_dados()
    logins_passengers = dados.get("loginsusuarios", [])
    
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    if usuario == "Lucas" and senha == "matoseco":
        return redirect(url_for("usuarios", nome_usuario=usuario))

    for user in logins_passengers:
        if usuario == user["nome"] and senha == user["senha"]:
            # REDIRECIONA PASSANDO O CPF DO CLIENTE
            return redirect(url_for("user_page", cpf=user["cpf"])) 

    return render_template("login.html", erro="Usuário ou senha incorretos!")

@app.route("/userpage/<cpf>") # MODIFICADA para receber o CPF
def user_page(cpf):
    """Rota da página inicial (Módulo do Passageiro Logado)."""
    dados = carregar_dados()    
    voos = dados["voos"]
    # Passa o CPF para o template
    return render_template("userpage.html", lista_de_voos=voos.items(), search_terms={}, cpf=cpf)

@app.route("/comprar/<codigo>")
def comprar_voo(codigo):
    """MODIFICADA: Carrega dados do cliente (Nome, Milhas) para simplificar o formulário."""
    global DF_Clientes
    dados = carregar_dados()    
    
    cpf = request.args.get('cpf') # Pega o CPF do cliente da query string
    
    if not cpf:
        return redirect(url_for('admin_login_page'))
    
    if codigo not in dados["voos"]:
        return render_template("erro.html", mensagem=f"Voo {codigo} não encontrado.", cpf=cpf)
        
    voo = dados["voos"][codigo]
    
    cliente_info = DF_Clientes[DF_Clientes['cpf'] == cpf]

    if cliente_info.empty:
        return redirect(url_for('logout'))

    nome_cliente = cliente_info['nome'].iloc[0]
    milhas_cliente = int(cliente_info['milhas'].iloc[0]) # Milhas atuais do cliente
    
    # Renderiza o template, passando as informações do cliente
    return render_template( "compra.html", 
                            codigo=codigo, 
                            voo=voo, 
                            nome_cliente=nome_cliente, 
                            milhas_cliente=milhas_cliente,
                            cpf=cpf)


@app.route("/finalizar_compra/<codigo>", methods=["POST"])
def finalizar_compra(codigo):
    """Lógica de compra completa: registra a reserva no histórico, atualiza milhas e assentos."""
    global DF_Clientes
    
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    pagamento = request.form["pagamento"]
    
    dados = carregar_dados()
    voos = dados["voos"]
    
    # ... (Validações iniciais, inalteradas) ...
    
    if codigo not in voos:
        return render_template("erro.html", mensagem=f"O voo {codigo} não foi encontrado.", cpf=cpf)
    
    voo = voos[codigo]
    
    if int(voo["assentos"]) <= 0:
        return render_template("erro.html", mensagem=f"O voo {codigo} não tem assentos disponíveis.", cpf=cpf)

    # 2. ATUALIZAÇÃO DO CLIENTE (DF_Clientes)
    if DF_Clientes is not None and cpf in DF_Clientes['cpf'].values:
        
        # --- NOVO BLOCO DE CORREÇÃO DE ERRO ---
        # Garante que a coluna 'historico_reservas' exista antes de ser acessada.
        if 'historico_reservas' not in DF_Clientes.columns:
            DF_Clientes['historico_reservas'] = None
        # -------------------------------------
        
        indice_cliente = DF_Clientes[DF_Clientes['cpf'] == cpf].index[0]
        data_reserva = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        milhas_cliente_atuais = int(DF_Clientes.loc[indice_cliente, 'milhas'])
        milhas_custo_voo = int(voo['milhas'])
        milhas_transacao = 0

        # --- LÓGICA DE PAGAMENTO E MILHAS (Inalterada) ---
        if pagamento == "milhas":
            if milhas_cliente_atuais < milhas_custo_voo:
                return render_template("erro.html", mensagem="Milhas insuficientes para esta compra.", cpf=cpf)
            
            milhas_restantes = milhas_cliente_atuais - milhas_custo_voo
            milhas_transacao = -milhas_custo_voo
            mensagem_pagamento = f"Pagamento realizado com sucesso via Milhas ({milhas_custo_voo} deduzidas)."

        elif pagamento == "dinheiro":
            milhas_a_ganhar = milhas_custo_voo 
            milhas_restantes = milhas_cliente_atuais + milhas_a_ganhar
            milhas_transacao = milhas_a_ganhar
            mensagem_pagamento = f"Pagamento realizado via Dinheiro. Milhas ({milhas_a_ganhar}) adicionadas para futura utilização."
        
        # 3. ATUALIZAÇÃO DO SALDO DE MILHAS
        DF_Clientes.loc[indice_cliente, 'milhas'] = str(milhas_restantes)

        # 4. CRIAÇÃO DA RESERVA E ATUALIZAÇÃO DO HISTÓRICO 
        nova_reserva = {
            "codigo": codigo,
            "data_compra": data_reserva,
            "origem": voo["origem"],
            "destino": voo["destino"],
            "aeronave": voo["aeronave"],
            "preco_pago": float(voo["preco"]),
            "milhas_transacao": milhas_transacao
        }

        # Tenta acessar a coluna (agora que sabemos que ela existe)
        historico_json = DF_Clientes.loc[indice_cliente, 'historico_reservas']
        
        if pd.isna(historico_json) or historico_json is None: # Trata tanto NaN quanto None
            historico_reservas = []
        else:
            historico_reservas = json.loads(historico_json)

        historico_reservas.append(nova_reserva)
        
        # Converte a lista atualizada de volta para JSON e salva no DataFrame
        DF_Clientes.loc[indice_cliente, 'historico_reservas'] = json.dumps(historico_reservas, ensure_ascii=False)
        
        # Mantemos 'reserva' e 'data' por retrocompatibilidade (se necessário)
        DF_Clientes.loc[indice_cliente, 'reserva'] = codigo
        DF_Clientes.loc[indice_cliente, 'data'] = data_reserva
        
        # Salva o DataFrame no CSV
        DF_Clientes.to_csv(csv_path, index=False)
        
        # 5. ATUALIZAÇÃO DO VOO (JSON)
        voo["assentos"] = int(voo["assentos"]) - 1 
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            
        # 6. RECONSTRUÇÃO DOS ÍNDICES
        inicializar_arvores()
        
        mensagem_final = f" Compra confirmada para {nome} no voo {codigo} para {voo['destino']}! {mensagem_pagamento}"
                
                # GARANTIR que o CPF está sendo passado para o template:
        return render_template("confirmacao.html", mensagem=mensagem_final, cpf=cpf)
                
    else:
                # GARANTIR que o CPF está sendo passado para o template de erro também:
        return render_template("erro.html", mensagem=f"Cliente com CPF {cpf} não encontrado no sistema.", cpf=cpf)

@app.route("/usuario/<nome_usuario>")
def usuarios(nome_usuario):
    """Rota para o Painel Administrativo (Módulo Administrativo)."""
    # Verifica a permissão: apenas 'Lucas' deve acessar.
    if nome_usuario != "Lucas":
        return redirect(url_for("admin_login_page"))
    return render_template("adminpage.html", nome_usuario=nome_usuario)


# --- ROTAS DE GESTÃO DE VOOS (DICIONÁRIOS) ---

@app.route("/usuario/<nome_usuario>/voos")
def listar_voos_para_admin(nome_usuario):
    """Lista todos os voos para o Administrador."""
    if nome_usuario != "Lucas":
        return redirect(url_for("admin_login_page"))
        
    dados = carregar_dados()
    voos = dados["voos"] # Pega o dicionário de voos.
    return render_template("listar_voos_admin.html", lista_de_voos=voos, nome_usuario=nome_usuario)


@app.route("/buscar_vooscliente")
def buscar_vooscliente():
    """Filtra voos disponíveis na userpage (Módulo Passageiro)."""
    dados = carregar_dados()
    voos = dados["voos"]
    origem_filtro = request.args.get('origem', '').lower()
    destino_filtro = request.args.get('destino', '').lower()
    voos_filtrados = {}
    
    # Percorre o dicionário de voos para aplicar os filtros.
    for codigo, voo in voos.items():
        if (origem_filtro in voo['origem'].lower()) and (destino_filtro in voo['destino'].lower()):
            voos_filtrados[codigo] = voo
            
    # Retorna a lista filtrada.
    return render_template("userpage.html", search_terms={'origem': request.args.get('origem', ''), 'destino': request.args.get('destino', '')}, lista_de_voos=voos_filtrados.items())

@app.route("/buscar_voos")
def buscar_voos():
    """Filtra voos disponíveis na homepage (Módulo Passageiro - Não Logado)."""
    dados = carregar_dados()
    voos = dados["voos"]
    origem_filtro = request.args.get('origem', '').lower()
    destino_filtro = request.args.get('destino', '').lower()
    voos_filtrados = {}
    
    # Percorre o dicionário de voos para aplicar os filtros.
    for codigo, voo in voos.items():
        if (origem_filtro in voo['origem'].lower()) and (destino_filtro in voo['destino'].lower()):
            voos_filtrados[codigo] = voo
            
    # Retorna a lista filtrada.
    return render_template("index.html", search_terms={'origem': request.args.get('origem', ''), 'destino': request.args.get('destino', '')}, lista_de_voos=voos_filtrados.items())


@app.route("/cadastrar_voo", methods=["GET", "POST"])
def cadastrar_voo():
    """Adiciona um novo voo ao dicionário (JSON)."""
    
    if request.method == "POST":
        # Pega os dados do formulário e cria o novo voo no formato de dicionário.
        novo_voo = {
            "origem": request.form["origem"],
            "destino": request.form["destino"],
            "milhas": int(request.form["milhas"]),
            "preco": float(request.form["preco"]),
            "aeronave": request.form["aeronave"],
            "assentos": int(request.form["assentos"])
        }
        codigo = request.form["codigo"]
        # Carrega o JSON, adiciona o novo voo usando o código como chave, e salva.
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
        # Usa 'del' para remover o voo do dicionário e salva o JSON atualizado.
        del dados["voos"][codigo] 
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
        return redirect(url_for("listar_voos_para_admin", nome_usuario="Lucas"))
    return render_template("excluir_voo.html", codigo=codigo, voo=voos[codigo])


@app.route("/editar_voo/<codigo>", methods=["GET", "POST"])
def editar_voo(codigo):
    """Atualiza os dados de um voo existente no dicionário (JSON)."""
    dados = carregar_dados()
    voos = dados["voos"]
    if codigo not in voos: return render_template("erro.html", mensagem=f"O voo {codigo} não existe.")
    
    if request.method == "POST":
        # Pega os dados do formulário e sobrescreve o dicionário existente do voo.
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


# --- ROTAS DE CLIENTES (ÁRVORE B E CSV) ---

@app.route("/cadastro")
def cadastro():
    """Página de Cadastro de Clientes."""
    return render_template("cadastro.html")


@app.route("/realizar_cadastro", methods=["POST"])
def realizar_cadastro():
    """Lógica de cadastro de um novo cliente."""
    global DF_Clientes # Permite modificar o DataFrame global.
    
    nome = request.form["nome"]
    cpf = request.form["cpf"]
    senha = request.form["senha"]

    # Carrega dados para adicionar o login (separado dos dados de gestão do cliente).
    with open(json_path, "r", encoding="utf-8") as f:
        dados = json.load(f)

    # 1. Validação: Verifica se o CPF (chave da Árvore B) já existe.
    if DF_Clientes is not None and cpf in DF_Clientes['cpf'].values:
        return render_template("cadastro.html", erro="CPF já cadastrado.")

    # 2. Atualiza o JSON de logins (para que o cliente possa logar).
    novo_usuario_login = {"nome": nome, "senha": senha, "cpf": cpf}
    if "loginsusuarios" not in dados:
        dados["loginsusuarios"] = []
    dados["loginsusuarios"].append(novo_usuario_login)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=4, ensure_ascii=False)
    
    # 3. Atualiza o CSV de clientes (os dados de gestão).
    novo_cliente_csv = {"cpf": cpf, "nome": nome, "reserva": "", "data": "", "milhas": "0"}
    novo_df = pd.DataFrame([novo_cliente_csv])
    # Concatena o novo DataFrame no DF global e salva no CSV.
    DF_Clientes = pd.concat([DF_Clientes, novo_df], ignore_index=True)
    DF_Clientes.to_csv(csv_path, index=False)
    
    # 4. Reconstrói as Árvores B para incluir o novo cliente no índice.
    inicializar_arvores()
    
    # Redireciona para a página de login para que o novo cliente acesse o sistema.
    return redirect(url_for("admin_login_page"))


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
    global Ap_Raiz_CPF, Ap_Raiz_Nome, DF_Clientes # Acesso às estruturas de dados globais.
        
    resultados = []
    mensagem = None

    if os.path.exists(csv_path):
        DF_Clientes = pd.read_csv(csv_path, dtype=str)
        # Garante que as árvores sejam reconstruídas se estiverem vazias.
        if Ap_Raiz_CPF is None or Ap_Raiz_Nome is None:
             inicializar_arvores()


    if request.method == "POST":
        tipo_busca = request.form.get("tipo_busca")
        valor_busca = request.form.get("valor_busca", "").strip()

        if tipo_busca == "cpf":
            try:
                if not valor_busca: raise ValueError
                cpf_int = int(valor_busca)
                
                # --- Busca Otimizada (Árvore B de CPF) ---
                # A função BuscarCPF usa a Ap_Raiz_CPF para busca rápida O(log N).
                cliente_dict = bt_cpf.BuscarCPF(Ap_Raiz_CPF, cpf_int, DF_Clientes)
                
                if cliente_dict:
                    resultados = [cliente_dict] 
                else:
                    mensagem = "CPF não encontrado."
            except ValueError:
                mensagem = "CPF inválido. Digite apenas números."

        elif tipo_busca == "nome":
            # --- Busca Otimizada (Árvore B de Nome) ---
            # A função BuscarNome usa a Ap_Raiz_Nome para busca rápida O(log N).
            cliente_dict = bt_nome.BuscarNome(Ap_Raiz_Nome, valor_busca, DF_Clientes)
            
            if cliente_dict:
                resultados = [cliente_dict]
            else:
                # Caso a busca exata falhe, faz uma busca parcial usando Pandas (menos eficiente, mas útil).
                filtro = DF_Clientes[DF_Clientes['nome'].str.contains(valor_busca, case=False, na=False)]
                resultados = filtro.to_dict('records')
                if not resultados:
                    mensagem = "Nenhum cliente com esse nome."

    # Lógica de Listagem (Executada no carregamento inicial ou após falha na busca)
    if not resultados:
        if Ap_Raiz_CPF is not None and request.method == "GET":
            # --- Listagem Otimizada (Árvore B de CPF) ---
            # Usa a Árvore B para garantir que a lista inicial esteja em ordem crescente de CPF.
            resultados = bt_cpf.ListarEmOrdem(Ap_Raiz_CPF, DF_Clientes)
        elif DF_Clientes is not None:
            # Caso a árvore não exista, retorna o DF completo (sem ordem garantida pela B-Tree).
            resultados = DF_Clientes.to_dict('records')
        else:
             resultados = []

    return render_template("gestaoclientes.html", clientes=resultados, mensagem=mensagem)


@app.route("/cadastrar_cliente", methods=["POST"])
def cadastrar_cliente():
    """Cadastra um novo cliente diretamente pelo painel administrativo."""
    global DF_Clientes # Permite modificar o DataFrame global.
    
    novo_cliente = { # Pega os dados do formulário
        "cpf": request.form["cpf"],
        "nome": request.form["nome"],
        "reserva": request.form["reserva"],
        "data": request.form["data"],
        "milhas": request.form["milhas"]
    }
    
    # Adiciona o cliente ao DataFrame e salva no CSV.
    novo_df = pd.DataFrame([novo_cliente])
    DF_Clientes = pd.concat([DF_Clientes, novo_df], ignore_index=True)
    DF_Clientes.to_csv(csv_path, index=False)

    # Reconstrói as Árvores B (índices) para incluir o novo cliente.
    inicializar_arvores()
    
    return redirect(url_for("gerenciar_clientes"))

#LJ

@app.route("/meus_voos/<cpf>")
def meus_voos(cpf):
    """MODIFICADA: Busca e lista todas as reservas do cliente no DF_Clientes."""
    global DF_Clientes 
    
    cliente_df = DF_Clientes[DF_Clientes['cpf'] == cpf]
    if cliente_df.empty:
        return redirect(url_for('logout'))

    lista_de_reservas = []
    
    # Tenta acessar a coluna de histórico
    if 'historico_reservas' in cliente_df.columns:
        historico_json = cliente_df['historico_reservas'].iloc[0]
        
        if not pd.isna(historico_json):
            # Carrega a lista de dicionários de reservas
            reservas_do_cliente = json.loads(historico_json)
            
            # Ordena as reservas da mais recente para a mais antiga
            reservas_do_cliente.sort(key=lambda r: r['data_compra'], reverse=True)
            
            # Itera sobre cada reserva (o dicionário completo já tem todas as informações)
            for reserva in reservas_do_cliente:
                 lista_de_reservas.append({
                    "codigo": reserva["codigo"],
                    "origem": reserva["origem"],
                    "destino": reserva["destino"],
                    "aeronave": reserva["aeronave"],
                    "preco_pago": reserva["preco_pago"],
                    "milhas_transacao": reserva["milhas_transacao"],
                    "data_compra": reserva["data_compra"]
                 })
            
    # Passa a lista completa de reservas para o template
    return render_template("meus_voos.html", lista_de_reservas=lista_de_reservas, cpf=cpf)


#LJ

@app.route("/milhas/<cpf>")
def ver_milhas(cpf):
    """Busca o saldo de milhas do cliente no DataFrame."""
    global DF_Clientes
    
    cliente_df = DF_Clientes[DF_Clientes['cpf'] == cpf]
    
    if cliente_df.empty:
        return redirect(url_for('logout'))
        
    # Pega o saldo de milhas do cliente
    milhas_saldo = int(cliente_df['milhas'].iloc[0])
    
    return render_template("milhas.html", milhas_saldo=milhas_saldo, cpf=cpf)

@app.route("/simular_conexoes", methods=["GET", "POST"])
def simular_conexoes():
    global Grafo_Voos, Mapa_Cidades
    
    cpf = request.args.get('cpf')
    dados = carregar_dados()
    voos_json = dados["voos"]
    
    if Grafo_Voos is None:
         inicializar_grafo()

    resultado = None
    mensagem = None
    origem = ""
    destino = ""
    diagrama_html = None
    
    if request.method == "POST" and Grafo_Voos is not None:
        origem = request.form.get("origem", "").strip()
        destino = request.form.get("destino", "").strip()
        
        if origem and destino:
            resultado, mensagem = buscar_melhor_conexao(Grafo_Voos, Mapa_Cidades, voos_json, origem, destino)
    
    # Gera o diagrama (SEMPRE): destaca a rota se houver resultado, senão mostra o grafo completo
    trajeto = resultado['trajeto'] if (resultado and 'trajeto' in resultado) else None
    
    # IMPORTANTE: A função gerar_diagrama_grafo agora aceita (dados_voos, trajeto)
    diagrama_html = gerar_diagrama_grafo(voos_json, trajeto)
    
    return render_template("conexoes.html", 
                            resultado=resultado, 
                            mensagem=mensagem, 
                            origem=origem, 
                            destino=destino,
                            cpf=cpf,
                            diagrama_html=diagrama_html)


# ------------------------------------------------------------------
# --- ROTA DO CHATBOT (IA - VERSÃO GEMINI) ---
# ------------------------------------------------------------------
# Não esqueça de ter o import no topo do arquivo:
# from groq import Groq

@app.route("/recomendacao_ia", methods=["GET", "POST"])
def recomendacao_ia():
    # 1. CAPTURA O CPF DA URL (Essencial para a Navbar funcionar)
    cpf = request.args.get('cpf')

    dados = carregar_dados()
    voos = dados["voos"]
    
    # 2. Extrair lista única de destinos disponíveis
    destinos_disponiveis = set()
    for voo in voos.values():
        destinos_disponiveis.add(voo['destino'])
    lista_destinos_str = ", ".join(destinos_disponiveis)

    recomendacao = None
    destino_sugerido = None
    
    if request.method == "POST":
        perfil_usuario = request.form["perfil"]
        
        # --- TENTATIVA 1: IA REAL (GROQ) ---
        try:
            # Substitua pela sua chave da Groq
            client = Groq(api_key="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")

            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {
                        "role": "system",
                        "content": f"Você é um guia de viagens. Destinos possíveis: {lista_destinos_str}. Responda estritamente no formato:\nDESTINO: [Nome]\nMOTIVO: [Texto curto]"
                    },
                    {
                        "role": "user",
                        "content": perfil_usuario
                    }
                ]
            )
            
            # Pega o texto da resposta
            resposta_texto = completion.choices[0].message.content
            
            # Processa a resposta para separar Destino e Motivo
            linhas = resposta_texto.split('\n')
            for linha in linhas:
                if "DESTINO:" in linha:
                    # Limpa formatação extra (como negrito **)
                    destino_sugerido = linha.replace("DESTINO:", "").replace("*", "").strip()
                if "MOTIVO:" in linha:
                    recomendacao = linha.replace("MOTIVO:", "").replace("*", "").strip()
            
            # Se a IA não responder no formato certo, força erro para cair na simulação
            if not destino_sugerido:
                raise Exception("Formato inválido recebido da IA")

        except Exception as e:
            # --- TENTATIVA 2: MODO DE SEGURANÇA (SIMULAÇÃO) ---
            # Se a Groq falhar (sem internet, chave errada, limite), cai aqui.
            print(f"IA falhou ({e}), ativando modo simulação.") 
            
            p = perfil_usuario.lower()
            
            # Lógica de fallback baseada em palavras-chave
            if "frio" in p or "neve" in p or "esquiar" in p or "inverno" in p:
                destino_sugerido = "Canada"
                recomendacao = "Baseado no seu gosto pelo frio, o Canadá oferece as melhores paisagens de inverno e montanhas."
            elif "praia" in p or "sol" in p or "mar" in p or "calor" in p:
                destino_sugerido = "Bahamas"
                recomendacao = "Para quem busca sol e mar, as Bahamas são o destino paradisíaco ideal com águas cristalinas."
            elif "compras" in p or "cidade" in p or "moderno" in p or "eua" in p:
                destino_sugerido = "EUA"
                recomendacao = "Os EUA são a escolha perfeita para quem busca modernidade, compras e grandes metrópoles."
            elif "historia" in p or "cultura" in p or "antigo" in p:
                destino_sugerido = "Mexico"
                recomendacao = "Rico em cultura e história, o México proporcionará uma viagem inesquecível pelas suas raízes."
            else:
                # Padrão genérico se nada for detectado
                destino_sugerido = "Sao Paulo"
                recomendacao = "São Paulo é a metrópole completa que oferece gastronomia, cultura e agito urbano."

    # Retorna o template passando o CPF para manter a sessão visual
    return render_template("chat.html", 
                           recomendacao=recomendacao, 
                           destino_sugerido=destino_sugerido,
                           cpf=cpf)