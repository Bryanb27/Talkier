# Explorando Tecnologias de Computação em Nuvem no Desenvolvimento de uma Aplicação de Chat Web

## Descrição
Este repositório contém o código-fonte, como executar e a documentação associada ao meu Trabalho de Conclusão de Curso (TCC) sobre computação em nuvem, explorando o uso do Docker e ferramentas da Microsoft Azure. O TCC investiga como as tecnologias de contêineres e a infraestrutura em nuvem podem ser combinadas para fornecer soluções escaláveis e eficientes.

## Stack da Aplicação

Este projeto utiliza uma variedade de tecnologias para fornecer uma experiência completa. Aqui está uma visão geral da stack tecnológica:

- **Framework Python:** [Flask](https://flask.palletsprojects.com/en/2.3.x/) - Flask é um micro-framework web em Python que oferece ferramentas, bibliotecas e tecnologias que simplificam o desenvolvimento de aplicativos web.
  
- **Blueprint:** O aplicativo é estruturado usando blueprints do Flask para modularizar e organizar as rotas e os controladores.

- **Frontend:**
  - **HTML e CSS:** Para a estrutura e estilo das páginas web.
  - **Bootstrap 5:** Uma biblioteca de front-end para gerar um design responsivo e componentes de interface do usuário.
  - **JavaScript com DOM e AJAX:** Para interatividade do lado do cliente e comunicação assíncrona com o servidor.

- **Linguagem de Programação:** [Python](https://www.python.org/) - Python é a linguagem principal utilizada para desenvolver a lógica do aplicativo.

## Plataformas e Tecnologias Utilizadas

Além da stack de tecnologias mencionada anteriormente, este projeto faz uso das seguintes plataformas e tecnologias:

- **Docker Hub:** Utilizado para hospedar e distribuir imagens de contêineres Docker.

- **Azure Container Registry:** Um serviço de hospedagem de contêineres baseado no Azure para armazenamento e gerenciamento de imagens de contêineres.

- **Azure SQL:** Um serviço de banco de dados relacional baseado no Azure, usado para armazenar e gerenciar dados de forma confiável e escalonável.

- **Azure Web App:** Uma plataforma de hospedagem de aplicativos web gerenciada no Azure, usada para implantar e escalar aplicativos web de forma rápida e fácil.

- **Azure Load Test:** Um serviço de teste de carga baseado no Azure, usado para simular e analisar o desempenho de um aplicativo sob diferentes condições de carga.


## Programas Utilizados

Além das plataformas e tecnologias mencionadas anteriormente, o desenvolvimento deste projeto envolveu o uso dos seguintes programas:

- **Visual Studio Code:** Um editor de código-fonte leve mas poderoso que suporta várias linguagens de programação e possui diversas extensões para facilitar o desenvolvimento.

- **Docker Desktop:** Uma aplicação que fornece uma experiência de desenvolvimento de contêineres fácil de usar em plataformas Windows e macOS, permitindo a criação, execução e gerenciamento de contêineres Docker no ambiente local.

- **Azure Data Studio:** Uma ferramenta de gerenciamento de dados multiplataforma e de código aberto para desenvolvedores e administradores de banco de dados do SQL Server no ambiente local e na nuvem.


## Estrutura do Repositório
1. `Código/`: Contém o código-fonte do projeto.
2. `Documentação/`: Contém o artigo desenvolvido, junto com a apresentação do TCC.


## Pré-requisitos para a Execução
1. **Instalar Python**
2. **Configurar a Conexão e a Chave da API**
   - Crie um arquivo Python chamado `keys.py` com as configurações de conexão ao banco de dados e com a chave da API Kickbox.

## Como Executar Localmente
1. Após fazer o download e extrair a aplicação, abra o terminal (cmd) na pasta extraída e execute:
   ```sh
   pip install -r requirements.txt 
2. Em seguida, execute o commando:
   ```sh
   py app.py
3. No navegador, abra a URL http://127.0.0.1:5000 para acessar a aplicação.
