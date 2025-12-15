from flask import render_template, request, redirect, url_for                                                          
import os
import json 
import pandas as pd
from igraph import *

from routes import carregar_dados

def testegrafo():
    dados = carregar_dados()
    g = Graph(directed=True)
    g.add_vertices(len(dados['voos']))
    cidades = []
    for codigo_voo in dados['voos']:
        voo_info = dados['voos'][codigo_voo]
        cidades.append(voo_info['destino'])

    for i in range(len(g.vs)):
        g.vs[i]["id"] = i
        g.vs[i]["label"] = cidades[i]
    print(g.vs["label"])

if __name__ == "__main__":  
    testegrafo()