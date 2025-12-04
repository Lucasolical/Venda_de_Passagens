import pandas as pd # Importa a biblioteca Pandas, usada para carregar e manipular os dados do arquivo clientes.csv (a "memória secundária").

# --- CLASSES FUNDAMENTAIS DA ÁRVORE B ---

class Registro:
  def __init__(self):
    # 'Registro' é a "dupla de dados" que será armazenada dentro de cada nó (Página) da Árvore B.
    
    self.Chave = None    # O valor que será usado para ordenar e buscar (a CHAVE).
                         # Neste arquivo (arvorePesquisaCPF), é o CPF do cliente (Inteiro).
                         # Se fosse a arvorePesquisaNome, seria o Nome (String).
                         
    self.Elemento = None # O 'ponteiro' para o dado completo. 
                         # Neste projeto, guarda o ÍNDICE da linha no DataFrame (clientes.csv) 
                         # onde os dados completos do cliente estão armazenados.
                         # A Árvore B apenas aponta, não armazena todos os dados.

class Pagina:
  def __init__(self, ordem):
    # 'Pagina' é o nó da Árvore B. É o bloco de dados que a Árvore tenta manter na memória
    # o máximo possível para acelerar as buscas.
    
    self.n = 0 # Contador que indica quantas chaves (Registros) estão atualmente armazenadas nesta Página.
               # O valor máximo de n é (ordem - 1).
               
    self.r = [None for i in range(ordem)] # Lista de Registros (Chave + Elemento). Armazena as chaves de busca.
                                          # O tamanho é 'ordem', mas só são usados os índices de 0 a (ordem - 2).
                                          
    self.p = [None for i in range(ordem+1)] # Lista de Ponteiros para as Páginas Filhas.
                                            # Um nó com N chaves tem N+1 ponteiros.
                                            # O tamanho máximo é 'ordem + 1'.

# --------------------------------------------------------------------------------------------------
# --- OPERAÇÕES DA ÁRVORE B ---
# --------------------------------------------------------------------------------------------------

# --- PESQUISA (Busca Binária e Recursiva) ---
def Pesquisa(x, Ap):
  # Busca um Registro (x) dentro da subárvore cuja raiz é Ap.
  i = 1
  if (Ap == None):
    # Se a página for nula (chegou a um ponteiro folha vazio), o elemento não existe.
    return None
    
  # 1. Busca binária dentro da Página Ap: encontra a primeira chave maior ou igual a x.Chave.
  while (i < Ap.n and x.Chave > Ap.r[i - 1].Chave):
    i += 1
    
  # 2. Verifica se a chave foi encontrada (Busca Exata)
  if (x.Chave == Ap.r[i - 1].Chave):
    # Se a chave for igual, o Registro é encontrado e retornado.
    return Ap.r[i - 1]
    
  # 3. Desce para o próximo nível (Busca Recursiva)
  if (x.Chave < Ap.r[i - 1].Chave):
    # Se a chave procurada é menor, desce para o ponteiro filho à esquerda (Ap.p[i - 1]).
    return Pesquisa(x, Ap.p[i - 1])
  else:
    # Se a chave procurada é maior que todas as chaves testadas, desce pelo último ponteiro (Ap.p[i]).
    return Pesquisa(x, Ap.p[i])

# --------------------------------------------------------------------------------------------------
# --- INSERÇÃO ---

def _InsereNaPagina(Ap, Reg, ApDir):
  # Função auxiliar para inserir um novo Registro (Reg) e seu ponteiro filho (ApDir)
  # de forma ordenada DENTRO de uma Página que ainda tem espaço.
  k = Ap.n # Começa do final do vetor de chaves (posição atual n)
  NaoAchouPosicao = (k > 0)
  
  # Desloca as chaves existentes para a direita até encontrar a posição correta de inserção
  while (NaoAchouPosicao):
    if ( Reg.Chave >= Ap.r[k - 1].Chave ):
      # Posição encontrada: a nova chave é maior ou igual à chave anterior.
      NaoAchouPosicao = False
      break
    # Deslocamento
    Ap.r[k] = Ap.r[k - 1]
    Ap.p[k + 1] = Ap.p[k]
    k-= 1
    if (k < 1): # Chegou na primeira posição
      NaoAchouPosicao = False
      
  # Insere o novo Registro e o novo ponteiro na posição encontrada
  Ap.r[k] = Reg
  Ap.p[k + 1] = ApDir
  Ap.n += 1 # Incrementa o número de chaves na Página

def _Ins( Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem ):
  # Função principal de inserção, que trata a recursão e a divisão de páginas (split).
  i = 1
  if (Ap == None):
    # Caso Base: Chegou a um ponteiro nulo (folha). A inserção deve ocorrer aqui.
    # Sinaliza que a árvore "cresceu" (o elemento será inserido e voltará na recursão).
    return True, Reg, None 
    
  # 1. Encontra o local para descer na recursão
  while ( i < Ap.n and Reg.Chave > Ap.r[i - 1].Chave ):
    i+= 1
    
  # 2. Tratamento de Chave Duplicada (Regra da Árvore B: não aceita chaves iguais)
  if(Reg.Chave == Ap.r[i - 1].Chave):
    # Retorna False, indicando que não houve inserção e a árvore não cresceu.
    return False, RegRetorno, ApRetorno
    
  if(Reg.Chave < Ap.r[i - 1].Chave ):
    i-= 1
    
  # 3. Chamada Recursiva: Desce para o nó filho
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap.p[i], Cresceu, RegRetorno, ApRetorno, Ordem)
  
  if(not Cresceu):
    # Se o filho não cresceu (ou seja, a inserção parou nos níveis inferiores), a função retorna.
    return False, RegRetorno, ApRetorno
    
  # 4. Caso de Inserção Simples (Sem Overflow)
  if (Ap.n < Ordem): 
    # A página atual tem espaço: insere o Registro que veio do nível inferior.
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
    return False, RegRetorno, ApRetorno
    
  # 5. Caso de Overflow (Divisão da Página - SPLIT)
  # A página está cheia (n == Ordem). É necessário dividir.
  ApTemp = Pagina(Ordem) # Cria uma nova Página temporária.
  ApTemp.n = 0
  ApTemp.p[0] = None
  
  # Move a chave mediana e as chaves maiores para a nova página (ApTemp).
  # A chave que deve subir é determinada (RegRetorno).
  if (i < (Ordem//2) + 1):
    # O novo Registro será inserido na página original (Ap).
    # Move a última chave de Ap para ApTemp.
    _InsereNaPagina(ApTemp, Ap.r[Ordem - 1], Ap.p[Ordem])
    Ap.n-= 1
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
  else:
    # O novo Registro será inserido na nova página (ApTemp).
    _InsereNaPagina(ApTemp, RegRetorno, ApRetorno)
    
  # Termina de mover o restante das chaves grandes para ApTemp.
  for J in range((Ordem//2) + 2, Ordem + 1):
    _InsereNaPagina(ApTemp, Ap.r[J - 1], Ap.p[J])
    
  # Atualiza o estado da página original (Ap) após o split.
  Ap.n = (Ordem//2)
  # Define o primeiro ponteiro da nova página.
  ApTemp.p[0] = Ap.p[(Ordem//2) + 1]
  
  # Define o Registro que irá subir para o nível superior (chave mediana).
  RegRetorno = Ap.r[(Ordem//2)]
  # Retorna a nova página criada (ApRetorno).
  ApRetorno = ApTemp
  
  return True, RegRetorno, ApRetorno # Sinaliza que houve crescimento (a chave mediana subiu).

def Insere(Reg, Ap, Ordem):
  # Função pública que inicia o processo de inserção.
  Cresceu = False
  RegRetorno = Registro()
  ApRetorno = Pagina(Ordem)
  
  # Inicia a inserção recursiva.
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem)
  
  if (Cresceu):
    # Se a inserção causou um split na raiz, é necessário criar uma nova raiz, 
    # aumentando a altura da árvore.
    ApTemp = Pagina(Ordem)
    ApTemp.n = 1
    ApTemp.r[0] = RegRetorno # O registro que subiu vira a chave da nova raiz.
    ApTemp.p[1] = ApRetorno # A página nova vira o filho da direita.
    ApTemp.p[0] = Ap        # A página antiga vira o filho da esquerda.
    Ap = ApTemp             # Atualiza Ap para ser a nova raiz.
  return Ap

# --------------------------------------------------------------------------------------------------
# --- FUNÇÕES AUXILIARES DE BUSCA NO PROJETO FLASK ---

def BuscarCPF(Ap, chave_busca, df):
    # Função para buscar um CPF específico na Árvore B e retornar os dados do cliente.
    
    reg = Registro()
    reg.Chave = chave_busca # Define o CPF (chave de busca).
    
    res = Pesquisa(reg, Ap) # Executa a busca na Árvore B.
    
    if res:
        # Se achou, 'res' é o Registro que contém o índice da linha.
        return df.iloc[res.Elemento].to_dict() # Usa o índice (res.Elemento) para buscar
                                               # a linha completa no DataFrame (clientes.csv) e
                                               # retorna como um dicionário.
    return None # CPF não encontrado.

def ListarEmOrdem(Ap, df):
    # Retorna todos os clientes em ordem crescente de CPF, percorrendo a Árvore B.
    lista = []
    
    def _percorrer(pag):
        # Percorre a árvore recursivamente em InOrder (esquerda -> raiz -> direita),
        # garantindo que as chaves sejam acessadas em ordem crescente.
        if pag:
            i = 0
            while i < pag.n:
                # 1. Visita o filho da esquerda (p[i])
                _percorrer(pag.p[i]) 
                
                # 2. Processa o nó atual (r[i])
                # Adiciona o dicionário do cliente na lista, usando o índice do Registro.
                lista.append(df.iloc[pag.r[i].Elemento].to_dict())
                
                i += 1
            # 3. Visita o último filho da direita (p[i])
            _percorrer(pag.p[i])
            
    _percorrer(Ap)
    return lista # Retorna a lista de clientes ordenada por CPF.