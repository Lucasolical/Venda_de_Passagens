from main import app # Importa a instância principal do Flask ('app') do arquivo main.py.
from flask import render_template, request, redirect, url_for # Importa funções essenciais do Flask:
                                                             # - render_template: carrega arquivos HTML.
                                                             # - request: acessa dados de formulários (POST/GET).
                                                             # - redirect, url_for: redireciona o usuário entre as páginas.
import os # Biblioteca para interagir com o sistema operacional (caminhos de arquivo).
import json # Biblioteca para trabalhar com arquivos JSON (onde estão voos e logins).
import pandas as pd # Biblioteca poderosa para manipulação de dados em tabela (DataFrame), usada para clientes.

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


# --- FUNÇÕES DE CONSTRUÇÃO DE ÍNDICE (ÁRVORE B) ---

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


def carregar_dados():
    """Função auxiliar para carregar dados do JSON (voos e logins)."""
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --------------------------------------------------------------------------------------------------
# --- ROTAS (ENDPOINTS) DO FLASK ---
# --------------------------------------------------------------------------------------------------

@app.route("/")
def homepage():
    """Rota da página inicial (Módulo do Passageiro)."""
    dados = carregar_dados()    
    voos = dados["voos"] # Pega os voos do dicionário (JSON).
    # Renderiza o HTML principal, passando a lista de voos.
    return render_template("index.html", lista_de_voos=voos.items(), search_terms={})



@app.route("/admin_login")
def admin_login_page():
    """Rota para a página de login de Administradores/Clientes."""
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    """Lógica de Autenticação (Dicionários)."""
    dados = carregar_dados()
    logins_passengers = dados.get("loginsusuarios", []) # Logins de clientes.
    
    usuario = request.form["usuario"]
    senha = request.form["senha"]

    # 1. Verifica se é o Administrador único (Lucas/matoseco)
    if usuario == "Lucas" and senha == "matoseco":
        # Redireciona para o painel de administração.
        return redirect(url_for("usuarios", nome_usuario=usuario))

    # 2. Verifica se é um Cliente
    for user in logins_passengers:
        if usuario == user["nome"] and senha == user["senha"]:
            # Cliente logado, redireciona para a página principal de voos.
            return redirect(url_for("homepage")) 

    # Se a autenticação falhar
    return render_template("login.html", erro="Usuário ou senha incorretos!")


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


@app.route("/buscar_voos")
def buscar_voos():
    """Filtra voos disponíveis na homepage (Módulo Passageiro)."""
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

        elif tipo_busca == "reserva":
            # Busca por Reserva não é indexada com Árvore B (usa filtro Pandas).
            filtro = DF_Clientes[DF_Clientes['reserva'].str.contains(valor_busca, case=False, na=False)]
            resultados = filtro.to_dict('records')
            if not resultados:
                mensagem = "Nenhuma reserva encontrada com esse código."

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