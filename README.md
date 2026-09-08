# Extração e Processamento de Dados Acadêmicos da UFPel

Este repositório contém uma solução automatizada em Python para extração e processamento de dados do portal institucional da Universidade Federal de Pelotas.

## Ferraemntas Utilizadas

* **Python 3.14+**
* **BeautifulSoup4**: Extração e navegação pela árvore HTML.
* **Requests**: Realização de requisições HTTP dinâmicas.
* **Pandas**: Manipulação, limpeza e exportação dos dados estruturados em CSV.
* **Pathlib**: Gestão do sistema de arquivos.

## Estrutura do Repositório

```text
ufpel-scraping/
├── data/
│   ├── input/      # Arquivos de entrada estáticos (HTMLs locais)
│   └── output/     # Arquivos CSV estruturados gerados pelos scripts
├── src/
│   ├── file-parsing.py  # Script de processamento de arquivos HTML locais
│   └── web-scraping.py  # Script de varredura web das turmas e projetos
├── .gitignore      # Proteção contra envio de venvs e arquivos temporários
├── requirements.txt # Dependências do ambiente
└── README.md        # Documentação do projeto
```

## Como Executar

### Clone o repositório
```bash
git clone [https://github.com/FPetiz/ufpel-scraping.git](https://github.com/FPetiz/ufpel-scraping.git)
cd ufpel-scraping
```

### Crie e ative o ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate
```

### Instale as dependências

```bash
pip install -r requirements.txt
```

### Execute os scripts a partir da pasta raiz

```bash
python3 src/file-parsing.py
python3 src/web-scraping.py
```