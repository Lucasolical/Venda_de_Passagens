Para criar um `README.md` profissional e completo para o seu projeto, você deve focar em explicar o que o sistema faz, quais tecnologias foram usadas (para valorizar o uso de Grafos e Árvores B) e, principalmente, como instalar as dependências.

Com base no código que você me mostrou (`routes.py`) e nos arquivos anteriores (`utils_grafo.py`), aqui está o conteúdo exato que você deve colocar no seu **README.md**.

Copie e cole o código abaixo no seu arquivo:

```markdown
# ✈️ Sistema de Vendas de Passagens - Linhas Aéreas ED-II

Este projeto é um sistema web completo para gestão e venda de passagens aéreas, desenvolvido em Python com Flask. O sistema foi criado como parte da disciplina de **Estruturas de Dados II**, implementando conceitos avançados como **Grafos** (para rotas), **Árvores B** (para indexação de clientes) e **Inteligência Artificial** (para recomendações).

## 📋 Funcionalidades

### 👤 Módulo do Passageiro
- **Busca de Voos:** Pesquisa por origem e destino.
- **Compra de Passagens:** Pagamento via dinheiro ou milhas.
- **Minhas Reservas:** Histórico de viagens e gestão de milhas.
- **Simulação de Rotas (Grafos):** Visualização gráfica do menor caminho entre destinos usando algoritmo de Dijkstra.
- **Assistente Virtual (IA):** Chatbot integrado (via Groq AI) que recomenda destinos com base no perfil do usuário.

### 🛠️ Módulo Administrativo
- **Gestão de Voos:** Cadastrar, editar e excluir voos (CRUD).
- **Gestão de Clientes:** Consulta otimizada de clientes utilizando índices em Árvore B (por CPF e Nome).

---

## 💻 Pré-requisitos e Instalação

Para rodar este projeto, você precisará do **Python 3.10+** instalado.

### 1. Clonar ou baixar o repositório
Salve os arquivos em uma pasta local.

### 2. Instalar as Dependências
O projeto utiliza bibliotecas para interface web, manipulação de dados, grafos e IA. Execute o comando abaixo no terminal para instalar todas de uma vez:

```bash
pip install flask pandas groq networkx matplotlib igraph

```

> **Nota:** A biblioteca `igraph` é usada para os cálculos de rota e o `networkx` + `matplotlib` para gerar as imagens dos grafos. A `groq` é usada para o chat de IA.

---

##🚀 Como Rodar o Projeto1. Certifique-se de estar na pasta raiz do projeto (onde está o `main.py`).
2. Execute o servidor Flask:

```bash
python main.py

```

3. Acesse no seu navegador:
👉 **https://www.google.com/search?q=http://127.0.0.1:5000**

---

##🔑 Acesso AdministrativoPara acessar o painel de gestão (adicionar voos, ver clientes), utilize as credenciais padrão:

* **Usuário:** `Lucas`
* **Senha:** `matoseco`

---

##🧠 Estruturas de Dados Utilizadas1. **Dicionários (Hash Maps):** Armazenamento em memória de voos e logins para acesso rápido O(1).
2. **Árvore B (B-Tree):** Implementação manual para indexação e busca eficiente de clientes por CPF e Nome no arquivo CSV.
3. **Grafos (Graphs):** Modelagem da malha aérea onde os vértices são aeroportos e as arestas são os voos.
* Algoritmo de **Dijkstra** utilizado para encontrar a rota mais barata/curta.



---

##🤖 Configuração da IA (Opcional)O sistema utiliza a API da **Groq** para o assistente de viagens.
A chave da API já está configurada no código para fins de demonstração, mas caso expire, você pode gerar uma nova em [console.groq.com](https://console.groq.com) e atualizar no arquivo `routes.py`.

```

### O que este README cobriu:
1.  **Bibliotecas:** Identifiquei pelo seu código que você precisa de `flask`, `pandas`, `groq` (pelo import novo), `networkx`, `matplotlib` e `igraph` (pelos arquivos de grafo anteriores).
2.  **Como Rodar:** Instruções simples de comando.
3.  **Login:** Deixei o login do "Lucas" explícito para facilitar para quem for corrigir seu trabalho.
4.  **Valorização Acadêmica:** A seção "Estruturas de Dados Utilizadas" é essencial para o professor ver que você aplicou a matéria (Árvores B e Grafos).

```