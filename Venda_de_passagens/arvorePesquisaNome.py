import pandas as pd 

class Registro:
  def __init__(self):
    self.Chave = None    #Nome
    self.Elemento = None 

class Pagina:
  def __init__(self, ordem):
    
    self.n = 0 # quantos Registros/chaves estão armazenadas neste nó.
    
    # armazena os Registros. Um nó de ordem M armazena M-1 chaves.
    self.r = [None for i in range(ordem)] 
    
    # Lista para armazenar os Ponteiros para as Páginas Filhas. Um nó de N chaves tem N+1 ponteiros.
    self.p = [None for i in range(ordem+1)]



def Pesquisa(x, Ap):

  i = 1
  if (Ap == None):
    # Chegou a um ponteiro folha nulo. O nome não foi encontrado.
    return None
  
  # encontra a primeira chave maior ou igual a x.Chave.
  # comparação de strings
  # garante que não tentaremos acessar a Chave de um slot vazio
  while (i < Ap.n and Ap.r[i - 1] is not None and x.Chave > Ap.r[i - 1].Chave):
    i += 1
  
  # Se a página não está cheia e chegamos a um slot vazio,
  # isso significa que a chave procurada é maior que todas as chaves existentes na página.
  if Ap.r[i - 1] is None:
      # Nesses casos, a busca deve continuar descendo pelo ponteiro mais à direita
      return Pesquisa(x, Ap.p[i])
  
  # Verifica se a chave foi encontrada
  if (x.Chave == Ap.r[i - 1].Chave):
    # Nome encontrado. Retorna o Registro que contém o índice para o CSV.
    return Ap.r[i - 1]
  
  # Desce para o próximo nível
  if (x.Chave < Ap.r[i - 1].Chave):
    # O nome está à esquerda: desce pelo ponteiro filho p[i - 1].
    return Pesquisa(x, Ap.p[i - 1])
  else:
    # O nome está à direita: desce pelo ponteiro p[i].
    return Pesquisa(x, Ap.p[i])




def _InsereNaPagina(Ap, Reg, ApDir):
  # Insere um Registro (Reg) e seu filho (ApDir) em uma Página (Ap) que AINDA NÃO ESTÁ CHEIA.

  k = Ap.n
  NaoAchouPosicao = (k > 0)
  
  # Desloca as chaves maiores para a direita para abrir espaço para o novo Registro.
  while (NaoAchouPosicao):
    if ( Reg.Chave >= Ap.r[k - 1].Chave ):
      NaoAchouPosicao = False
      break
    Ap.r[k] = Ap.r[k - 1]
    Ap.p[k + 1] = Ap.p[k]
    k-= 1
    if (k < 1):
      NaoAchouPosicao = False
      
  # Insere o novo Registro e ponteiro no local correto.
  Ap.r[k] = Reg
  Ap.p[k + 1] = ApDir
  Ap.n += 1

def _Ins( Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem ):
  # Função Recursiva principal de Inserção, responsável por descer na árvore
  # e lidar com a divisão de nós quando necessário.
  i = 1
  if (Ap == None):
    # Chegou a um ponteiro nulo (folha). O elemento está pronto para ser inserido.
    return True, Reg, None # 'True' significa que a árvore vai crescer (um elemento vai subir).
    
  # Desce na árvore para encontrar a posição de inserção.
  while ( i < Ap.n and Reg.Chave > Ap.r[i - 1].Chave ):
    i+= 1
  
  # Tratamento básico de duplicatas:
  if(Reg.Chave == Ap.r[i - 1].Chave):
    # Se o nome já existe, a Árvore B não insere
    return False, RegRetorno, ApRetorno

  if(Reg.Chave < Ap.r[i - 1].Chave ):
    i-= 1
    
  #a inserção real ocorrerá no nível inferior.
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap.p[i], Cresceu, RegRetorno, ApRetorno, Ordem)
  
  if(not Cresceu):
    # Se o nível inferior não precisou dividir, a inserção terminou.
    return False, RegRetorno, ApRetorno
    
  if (Ap.n < Ordem): 
    # absorve o elemento que subiu do nível inferior.
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
    return False, RegRetorno, ApRetorno
    
  ApTemp = Pagina(Ordem) # Cria a nova página.
  #move chaves, ponteiros e promove a chave mediana.

  RegRetorno = Ap.r[(Ordem//2)] # A chave mediana que irá subir para o nó pai.
  ApRetorno = ApTemp            # A nova página criada.
  
  return True, RegRetorno, ApRetorno # Sinaliza que houve crescimento (a chave mediana subiu).

def Insere(Reg, Ap, Ordem):
  # Função pública que inicia a inserção.
  Cresceu = False
  RegRetorno = Registro()
  ApRetorno = Pagina(Ordem)
  
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem)
  
  if (Cresceu):
    # Se o 'split' ocorreu na RAIZ, a árvore cresce em altura, criando uma nova raiz.
    ApTemp = Pagina(Ordem)
    ApTemp.n = 1
    ApTemp.r[0] = RegRetorno # O elemento promovido vira a chave da nova raiz.
    ApTemp.p[1] = ApRetorno
    ApTemp.p[0] = Ap
    Ap = ApTemp # A nova Página se torna a raiz.
  return Ap


def BuscarNome(Ap, chave_busca, df):
    """
    Busca o cliente pelo Nome exato, usando a Árvore B (O(log N)).
    """
    reg = Registro()
    reg.Chave = chave_busca
    
    res = Pesquisa(reg, Ap) # Executa a busca logarítmica (rápida).
    
    if res:
        # Usa o índice de linha (res.Elemento) obtido da Árvore B para buscar
        # os dados completos no DataFrame (CSV) e retorna como dicionário.
        return df.iloc[res.Elemento].to_dict()
    return None

def ListarEmOrdem(Ap, df):
    """
    Percorre a Árvore B em ordem InOrder e retorna a lista de clientes ORDENADA ALFABETICAMENTE por Nome.
    """
    lista = []
    
    def _percorrer(pag):
        # Percorre a árvore em ordem (InOrder: esquerda -> nó -> direita)
        if pag:
            i = 0
            while i < pag.n:
                _percorrer(pag.p[i]) # Visita filho à esquerda
                
                indice_excel = pag.r[i].Elemento
                linha = df.iloc[indice_excel].to_dict() # Busca dados pelo índice
                lista.append(linha)
                
                i += 1
            _percorrer(pag.p[i]) # Visita filho à direita
            
    _percorrer(Ap)
    return lista

def ListarPorInicial(Ap, inicial, df):
    """
    Implementa o requisito de 'Listagem de clientes por inicial do nome'.
    Percorre a árvore em ordem alfabética e filtra.
    """
    lista = []
    inicial = inicial.lower()
    
    def _percorrer(pag):
        if pag:
            i = 0
            while i < pag.n:
                _percorrer(pag.p[i])
                
                # Obtém o nome da chave atual
                nome_atual = str(pag.r[i].Chave).lower()
                
                # Verifica se o nome começa com a inicial
                if nome_atual.startswith(inicial):
                    indice = pag.r[i].Elemento
                    lista.append(df.iloc[indice].to_dict())
                
                i += 1
            _percorrer(pag.p[i])
            
    _percorrer(Ap)
    return lista