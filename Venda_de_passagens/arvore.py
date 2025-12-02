import pandas as pd

class Registro:
  def __init__(self):
    self.Chave = None
    self.Elemento = None

class Pagina:
  def __init__(self, ordem):
    self.n = 0
    self.r = [None for i in range(ordem)]
    self.p = [None for i in range(ordem+1)]

def Pesquisa(x, Ap):
  i = 1
  if (Ap == None):
    return None
  while (i < Ap.n and x.Chave > Ap.r[i - 1].Chave):
    i += 1
  if (x.Chave == Ap.r[i - 1].Chave):
    return Ap.r[i - 1]
  if (x.Chave < Ap.r[i - 1].Chave):
    return Pesquisa(x, Ap.p[i - 1])
  else:
    return Pesquisa(x, Ap.p[i])

def _InsereNaPagina(Ap, Reg, ApDir):
  k = Ap.n
  NaoAchouPosicao = (k > 0)
  while (NaoAchouPosicao):
    if ( Reg.Chave >= Ap.r[k - 1].Chave ):
      NaoAchouPosicao = False
      break
    Ap.r[k] = Ap.r[k - 1]
    Ap.p[k + 1] = Ap.p[k]
    k-= 1
    if (k < 1):
      NaoAchouPosicao = False
  Ap.r[k] = Reg
  Ap.p[k + 1] = ApDir
  Ap.n += 1

def _Ins( Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem ):
  i = 1
  if (Ap == None):
    return True, Reg, None

  while ( i < Ap.n and Reg.Chave > Ap.r[i - 1].Chave ):
    i+= 1

  if(Reg.Chave == Ap.r[i - 1].Chave):
    return False, RegRetorno, ApRetorno

  if(Reg.Chave < Ap.r[i - 1].Chave ):
    i-= 1

  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap.p[i], Cresceu, RegRetorno, ApRetorno, Ordem)

  if(not Cresceu):
    return False, RegRetorno, ApRetorno
  if (Ap.n < Ordem): 
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
    return False, RegRetorno, ApRetorno

  ApTemp = Pagina(Ordem)
  ApTemp.n = 0
  ApTemp.p[0] = None
  if (i < (Ordem//2) + 1):
    _InsereNaPagina(ApTemp, Ap.r[Ordem - 1], Ap.p[Ordem])
    Ap.n-= 1
    _InsereNaPagina(Ap, RegRetorno, ApRetorno)
  else:
    _InsereNaPagina(ApTemp, RegRetorno, ApRetorno)
  for J in range((Ordem//2) + 2, Ordem + 1):
    _InsereNaPagina(ApTemp, Ap.r[J - 1], Ap.p[J])
  Ap.n = (Ordem//2)
  ApTemp.p[0] = Ap.p[(Ordem//2) + 1]
  RegRetorno = Ap.r[(Ordem//2)]
  ApRetorno = ApTemp
  return True, RegRetorno, ApRetorno

def _Insere(Reg, Ap, Ordem):
  Cresceu = False
  RegRetorno = Registro()
  ApRetorno = Pagina(Ordem)
  Cresceu, RegRetorno, ApRetorno = _Ins(Reg, Ap, Cresceu, RegRetorno, ApRetorno, Ordem)
  if (Cresceu):
    ApTemp = Pagina(Ordem)
    ApTemp.n = 1
    ApTemp.r[0] = RegRetorno
    ApTemp.p[1] = ApRetorno
    ApTemp.p[0] = Ap
    Ap = ApTemp
  return Ap
  
def _InserirElementos(Ap, ordem, dataframe, chave):
  tam_lin, tam_col = dataframe.shape
  for i in range(tam_lin):
      reg = Registro()
      #  Garante que o CPF seja tratado como número para a árvore
      try:
          reg.Chave = int(dataframe.iloc[i, 0])
          reg.Elemento = i
          Ap = _Insere(reg, Ap, ordem)
          chave += 1
      except ValueError:
          continue
  return Ap, chave

# Função de Busca Para o Flask
def BuscarCliente(Ap, chave_busca, df):
    reg_busca = Registro()
    reg_busca.Chave = chave_busca
    resultado = Pesquisa(reg_busca, Ap)
    
    if resultado is not None:
        indice_excel = resultado.Elemento
        # Converte a linha do DataFrame para uma lista Python
        dados_cliente = df.iloc[indice_excel].values.tolist()
        return dados_cliente
    return None

def ListarEmOrdem(Ap, df):
    """
    Percorre a Árvore B em ordem e retorna 
    uma lista de dicionários com os dados do DataFrame.
    """
    resultado = []
    
    def _percorrer(pagina):
        if pagina is not None:
            i = 0
            while i < pagina.n:
                # Visita filho esquerda
                _percorrer(pagina.p[i])
                
                # Pega o dado atual
                indice_excel = pagina.r[i].Elemento
                # Converte a linha do DataFrame para dicionário
                linha = df.iloc[indice_excel].to_dict()
                resultado.append(linha)
                
                i += 1
            # Visita último filho a direita
            _percorrer(pagina.p[i])

    _percorrer(Ap)
    return resultado