import pandas as pd

class Registro:
  def __init__(self):
    # Dupla de dados que será armazenada dentro de cada nó da Árvore B.
    
    self.Chave = None    # cpf do cliente como chave
                         
    self.Elemento = None
 

class Pagina:
  def __init__(self, ordem):

    self.n = 0
    self.r = [None for i in range(ordem)]                                  
    self.p = [None for i in range(ordem+1)]

# pesquisa passa o registro x e a raiz da arvore Ap
def Pesquisa(x, Ap):
  # Busca um Registro (x) dentro da subárvore com raiz Ap.
  i = 1
  #arvore nula
  if (Ap == None):
    return None
    
  # Busca possivel posição da chave na Página
  while (i < Ap.n and x.Chave > Ap.r[i - 1].Chave):
    i += 1
    
  # Verifica se a chave foi encontrada
  if (x.Chave == Ap.r[i - 1].Chave):
    return Ap.r[i - 1]
    
  # Desce para o próximo nível 
  if (x.Chave < Ap.r[i - 1].Chave):
    # Se a chave procurada é menor, desce para o ponteiro filho à esquerda
    return Pesquisa(x, Ap.p[i - 1])
  else:
    # Se a chave procurada é maior que todas as chaves testadas, desce pelo último ponteiro
    return Pesquisa(x, Ap.p[i])

#Colocar novo registro de forma ordenada na pagina passando raiz.
def _InsereNaPagina(Ap, Reg, ApDir):
  # Começa do final do vetor de chaves (posição atual n)
  k = Ap.n 
  NaoAchouPosicao = (k > 0)
  
  # Desloca as chaves existentes para a direita até encontrar a posição correta de inserção
  while (NaoAchouPosicao):
    if ( Reg.Chave >= Ap.r[k - 1].Chave ):
      # a nova chave é maior ou igual à chave anterior.
      NaoAchouPosicao = False
      break

    # Deslocamento
    Ap.r[k] = Ap.r[k - 1]
    Ap.p[k + 1] = Ap.p[k]
    k-= 1

    # Chegou na primeira posição
    if (k < 1): 
      NaoAchouPosicao = False
      
  # Insere o novo Registro e o novo ponteiro na posição encontrada
  Ap.r[k] = Reg
  Ap.p[k + 1] = ApDir
  # Incrementa o número de chaves na Página
  Ap.n += 1 

def _Ins( Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem ):
  # Função principal de inserção, que trata a recursão e a divisão de páginas
  i = 1
  if (Ap == None):
    # Chegou ao final. A inserção deve ser aqui
    #  aqui.
    # significa que a árvore cresceu
    return True, Reg, None 
    
  #Encontra o local para descer na recursão (conta quantos nós são menores que a chave a ser inserida)
  while ( i < Ap.n and Reg.Chave > Ap.r[i - 1].Chave ):
    i+= 1
    
  # Chave Duplicada
  if(Reg.Chave == Ap.r[i - 1].Chave):
    return False, RegRetorno, ApRetorno
  # ajusta o indice para descer corretamente em casos de chaves menores
  if(Reg.Chave < Ap.r[i - 1].Chave ):
    i-= 1
    
  #Desce para o nó filho
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap.p[i], Cresceu, RegRetorno, ApRetorno, Ordem)
  
  if(not Cresceu):
    # Se o filho não cresceu, a função retorna.
    return False, RegRetorno, ApRetorno
    
  if (Ap.n < Ordem): 
    # insere o Registro que veio do nível inferior.
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
    return False, RegRetorno, ApRetorno
    
  #Caso de Página cheia, precisa dividir
  # Cria uma nova Página temporária.
  ApTemp = Pagina(Ordem) 
  ApTemp.n = 0
  ApTemp.p[0] = None
  
  # Move a chave mediana e as chaves maiores para a nova página
  # A chave que deve subir é determinada.
  if (i < (Ordem//2) + 1):
    # Move a última chave de Ap para ApTemp para liberar espaço.
    _InsereNaPagina(ApTemp, Ap.r[Ordem - 1], Ap.p[Ordem])
    Ap.n-= 1
    #insere em ap
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
  else:
    # O novo Registro será inserido na nova página
    _InsereNaPagina(ApTemp, RegRetorno, ApRetorno)
    
  # Termina de mover o restante das chaves grandes para ApTemp.
  for J in range((Ordem//2) + 2, Ordem + 1):
    _InsereNaPagina(ApTemp, Ap.r[J - 1], Ap.p[J])
    
  # Atualiza o n de ap
  Ap.n = (Ordem//2)
  # Define o primeiro ponteiro da nova página.
  ApTemp.p[0] = Ap.p[(Ordem//2) + 1]
  
  # Define o Registro que irá subir para o nível superior.
  RegRetorno = Ap.r[(Ordem//2)]
  # Retorna a nova página criada
  ApRetorno = ApTemp
  # Sinaliza que houve crescimento
  return True, RegRetorno, ApRetorno 

# Basicamente ela serve para tratar o caso de crescimento da raiz
# no caso, se a árvore crescer, uma nova raiz é criada e a altura da árvore aumenta em 1.

def Insere(Reg, Ap, Ordem):

  Cresceu = False
  RegRetorno = Registro()
  ApRetorno = Pagina(Ordem)
  
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem)
  
  if (Cresceu):
    # Se a inserção causou um split na raiz, é necessário criar uma nova raiz, 
    # aumentando a altura da árvore
    ApTemp = Pagina(Ordem)
    ApTemp.n = 1
    # O registro que subiu vira a chave da nova raiz
    ApTemp.r[0] = RegRetorno 
    # A página nova vira o filho da direita
    ApTemp.p[1] = ApRetorno 
    # A página antiga vira o filho da esquerda
    ApTemp.p[0] = Ap  
    # Atualiza Ap para ser a nova raiz
    Ap = ApTemp             
  return Ap


def BuscarCPF(Ap, chave_busca, df):

    reg = Registro()
    reg.Chave = chave_busca
    
    res = Pesquisa(reg, Ap) # Executa a busca na Árvore B.
    
    if res:
        # Se achou, 'res' é o Registro que contém o índice da linha.
        return df.iloc[res.Elemento].to_dict() # Usa o índice res.Elemento para buscar
                                               # a linha completa no DataFrame e
                                               # retorna como um dicionário.
    return None 

def ListarEmOrdem(Ap, df):
    # Retorna todos os clientes em ordem crescente de CPF, percorrendo a Árvore B.
    lista = []
    
    def _percorrer(pag):
        # Percorre a árvore recursivamente em InOrder (esquerda -> raiz -> direita),
        # garantindo que as chaves sejam acessadas em ordem crescente.
        if pag:
            i = 0
            while i < pag.n:
                # Visita o filho da esquerda (p[i])
                _percorrer(pag.p[i]) 
                
                # Processa o nó atual (r[i])
                # Adiciona o dicionário do cliente na lista, usando o índice do Registro.
                lista.append(df.iloc[pag.r[i].Elemento].to_dict())
                
                i += 1
            # Visita o último filho da direita (p[i])
            _percorrer(pag.p[i])
            
    _percorrer(Ap)
    return lista # Retorna a lista de clientes ordenada por CPF.