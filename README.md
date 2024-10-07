# Projeto de Pesquisa Automatizada com Google Scholar e OpenAI

Este projeto automatiza a coleta, filtragem, análise e comparação de artigos científicos utilizando a API do Google Scholar via SerpAPI e a API da OpenAI para análise de similaridade com um arquivo PDF fornecido. O projeto também inclui visualizações gráficas dos resultados.

## Funcionalidades Principais

1. Coleta de artigos do Google Scholar com base em uma query definida.
2. Geração de gráficos sobre a quantidade de artigos por fonte e por ano.
3. Geração de nuvens de palavras com base nos títulos e resumos dos artigos.
4. Análise de similaridade dos artigos com o título do seu projeto ou um PDF fornecido.
5. Refinamento e filtragem dos artigos em várias etapas, com visualizações gráficas de cada fase.

## Requisitos

- Python 3.8+
- Poetry para gerenciamento de dependências

## Instalação

### 1. Clone este repositório:

```bash
git clone https://github.com/seu-usuario/seu-repositorio.git
cd seu-repositorio
```

### 2. Instale as dependências com o Poetry:

```bash
poetry install
```

### 3. Configure as variáveis de ambiente

Você precisará de uma chave de API da [SerpAPI](https://serpapi.com/) para acessar o Google Scholar e uma chave da [OpenAI](https://beta.openai.com/) para a análise de similaridade.

#### 3.1. Obtenha a chave da API da SerpAPI

- Crie uma conta na [SerpAPI](https://serpapi.com/).
- Após o login, acesse o seu painel para obter sua **API Key**.
- Coloque a chave da API no arquivo `.env` no diretório raiz do projeto:

```bash
touch .env
```

No arquivo `.env`, adicione sua chave da API da SerpAPI e OpenAI:

```
SERPAPI_API_KEY=sua_chave_da_serpapi
OPENAI_API_KEY=sua_chave_da_openai
```

#### 3.2. Obtenha a chave da API da OpenAI

- Crie uma conta na [OpenAI](https://beta.openai.com/).
- Acesse seu perfil para obter a **API Key**.
- Adicione a chave ao mesmo arquivo `.env` descrito acima.

### 4. Como usar o projeto

#### Estrutura do Projeto

O projeto contém as seguintes classes principais:

- **`SearchManager`**: Faz a coleta de artigos do Google Scholar usando a SerpAPI.
- **`DataProcessor`**: Preprocessa os dados, faz a filtragem por fontes relevantes e refina os artigos com base em palavras-chave.
- **`VisualizationManager`**: Gera gráficos de linha para a quantidade de artigos por ano e fonte, nuvens de palavras e o gráfico de funil.
- **`FunnelManager`**: Coordena todo o fluxo do funil de coleta, filtragem, geração de gráficos e análise de similaridade com o título do projeto ou um PDF.

#### Executando o projeto

Após configurar o ambiente e obter as chaves da API, você pode rodar o projeto.

```bash
poetry run python main.py
```

Isso executará todas as etapas do funil, desde a coleta de artigos, até a análise de similaridade com um arquivo PDF fornecido.

#### Exemplo de Execução

No arquivo `main.py`, você pode configurar a query para pesquisa de artigos e definir o título do projeto ou fornecer um arquivo PDF para comparação.

```python
from handdlers.funnel_manager import FunnelManager
import PyPDF2
import os
from dotenv import load_dotenv

load_dotenv()

def extract_text_from_pdf(pdf_path):
    reader = PyPDF2.PdfFileReader(open(pdf_path, "rb"))
    text = ""
    for page_num in range(reader.numPages):
        text += reader.getPage(page_num).extract_text()
    return text

if __name__ == "__main__":
    query = (
        "(transformer OR transformers OR transformer architecture OR transformer model OR transformer-based OR transformer networks) AND "
        "(attention mechanism OR self-attention OR multi-head attention OR attention layer OR attention module OR attention-based) AND "
        "(aggregation function OR aggregation functions OR aggregating functions OR pre-aggregation function OR pre-aggregation functions OR aggregation methods OR aggregation techniques OR aggregation strategy) AND "
        "(modify OR alter OR apply OR modifying OR altering OR applying OR enhance OR enhancing OR improve OR improving OR optimize OR optimizing OR refine OR refining)"
    )

    project_title = "Meu Trabalho de Pesquisa"
    openai_api_key = os.getenv("OPENAI_API_KEY")

    # Inicializa o funil
    funnel = FunnelManager(query, project_title, openai_api_key)

    # Roda o funil
    funnel.run_funnel()

    # Comparação com PDF fornecido
    pdf_text = extract_text_from_pdf("artigo.pdf")
    if pdf_text:
        df_final = funnel.compare_pdf_with_articles(pdf_text, funnel.search_manager.collect_articles())
        print(df_final.head())
    else:
        print("O texto do PDF não pôde ser extraído.")
```

### 5. O que cada classe faz

#### 5.1 SearchManager

- **Função**: Gerencia a coleta de artigos do Google Scholar usando a API da SerpAPI.
- **Principais métodos**:
  - `collect_articles`: Coleta os artigos com base em uma query fornecida e retorna um DataFrame.
  - `_search_articles_via_api`: Realiza as consultas à SerpAPI.
  - `_process_articles_to_dataframe`: Processa os resultados da API e os converte em um DataFrame.

#### 5.2 DataProcessor

- **Função**: Processa e refina os dados coletados, além de realizar a filtragem por palavras-chave e fontes.
- **Principais métodos**:
  - `preprocess_data`: Limpa e normaliza os dados.
  - `filter_by_top_sources`: Filtra os artigos pelas fontes mais relevantes.
  - `filter_by_keywords`: Filtra os artigos com base nas palavras-chave fornecidas.
  - `final_refinement`: Realiza o refinamento final dos artigos.

#### 5.3 VisualizationManager

- **Função**: Gera gráficos para visualizar os resultados.
- **Principais métodos**:
  - `create_line_chart`: Gera gráficos de linha mostrando a quantidade de publicações por ano e por fonte.
  - `generate_word_cloud`: Gera nuvens de palavras baseadas nos títulos e resumos dos artigos.
  - `create_funnel_chart`: Gera um gráfico de funil mostrando a redução de artigos em cada etapa.

#### 5.4 FunnelManager

- **Função**: Coordena o fluxo do funil, desde a coleta de artigos até a geração de gráficos e análise de similaridade.
- **Principais métodos**:
  - `run_funnel`: Executa todas as etapas do funil.
  - `analyze_similarity`: Realiza a análise de similaridade entre os artigos coletados e o título do projeto.
  - `compare_pdf_with_articles`: Compara o conteúdo de um PDF com os artigos coletados usando a API da OpenAI.

## Gráficos Gerados

- **Gráfico de Funil**: Mostra a redução progressiva dos artigos à medida que o funil é aplicado.
- **Gráficos de Linha**: Exibe a quantidade de artigos por fonte e ano em cada etapa.
- **Nuvens de Palavras**: Gera nuvens de palavras com base nos títulos e resumos dos artigos.
