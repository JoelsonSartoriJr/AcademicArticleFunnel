import openai
import pandas as pd
from handdlers.search_manager import SearchManager
from handdlers.data_processor import DataProcessor
from handdlers.visualization_manager import VisualizationManager

class FunnelManager:
    def __init__(self, query, project_title, openai_api_key, max_articles=1000):
        self.search_manager = SearchManager(query, num_results=max_articles)
        self.data_processor = DataProcessor()
        self.visualization_manager = VisualizationManager()
        self.project_title = project_title
        self.openai_api_key = openai_api_key
        openai.api_key = openai_api_key

    def run_funnel(self):
        # Etapa 0: Validação dos Dados Coletados
        print("Etapa 0: Validando os dados coletados...")
        df = self.search_manager.collect_articles()
        if df.empty:
            raise ValueError("Nenhum artigo foi coletado. O processo será interrompido.")
        print(f"Total de artigos coletados: {len(df)}")

        # Etapa 1: Coleta de Artigos e Pré-processamento
        print("Etapa 1: Coletando artigos e fazendo pré-processamento...")
        df = self.data_processor.preprocess_data(df)
        print(f"Total de artigos após pré-processamento: {len(df)}")

        # Etapa 2: Filtragem por Fontes Relevantes e Criação de Gráfico
        print("Etapa 2: Filtrando por fontes relevantes e criando gráfico...")
        df_filtered_sources = self.data_processor.filter_by_top_sources(df)
        print(f"Total de artigos após filtragem por fontes: {len(df_filtered_sources)}")
        self.visualization_manager.create_line_chart(df_filtered_sources, output_file="artigos_filtrados_por_fonte_ano.png")

        # Etapa 3: Geração de Nuvem de Palavras
        print("Etapa 3: Gerando nuvens de palavras...")
        self.visualization_manager.generate_word_cloud(df_filtered_sources, 'Título', output_dir="nuvens_palavras_titulo")
        self.visualization_manager.generate_word_cloud(df_filtered_sources, 'Snippet', output_dir="nuvens_palavras_resumo")

        # Etapa 4: Filtragem por Similaridade de Resumos usando GPT-4o Mini
        print("Etapa 4: Filtrando artigos com base na similaridade de resumos com GPT-4o Mini...")
        df_similar_summaries = self.filter_by_summary_similarity(df_filtered_sources)

        # Ajuste para garantir pelo menos 10 artigos
        if len(df_similar_summaries) < 10:
            print("Menos de 10 artigos após a filtragem por resumos. Afrouxando as restrições para incluir mais artigos.")
            df_similar_summaries = df_filtered_sources  # Afrouxa a filtragem, retornando ao conjunto filtrado por fonte
        print(f"Total de artigos após filtragem por similaridade de resumos: {len(df_similar_summaries)}")
        self.visualization_manager.create_line_chart(df_similar_summaries, output_file="artigos_filtrados_por_resumo_ano.png")

        # Etapa 5: Análise de Similaridade com o Título do Projeto usando GPT-4o Mini
        print("Etapa 5: Analisando similaridade com o título do projeto usando GPT-4o Mini...")
        similar_articles = self.analyze_similarity(df_similar_summaries)

        # Garantir pelo menos 10 artigos após análise de similaridade
        if len(similar_articles) < 10:
            print("Menos de 10 artigos semelhantes ao título. Afrouxando as restrições para incluir mais artigos.")
            similar_articles = df_similar_summaries  # Usa o conjunto filtrado por resumo se o número for insuficiente
        print(f"Total de artigos semelhantes ao título do projeto: {len(similar_articles)}")
        self.visualization_manager.create_line_chart(similar_articles, output_file="artigos_similares_por_fonte.png")

        # Etapa 6: Refinamento Final
        print("Etapa 6: Refinamento final dos artigos...")
        refined_df = self.analyze_summary_similarity(similar_articles)

        # Garantir pelo menos 10 artigos após o refinamento final
        if len(refined_df) < 10:
            print("Menos de 10 artigos após o refinamento final. Afrouxando as restrições.")
            refined_df = similar_articles  # Retorna ao conjunto anterior se o refinamento resultar em menos de 10 artigos
        print(f"Total de artigos após refinamento final: {len(refined_df)}")

        # Etapa Final: Gráfico de Funil mostrando a redução
        article_counts = [
            len(df),  # Artigos coletados
            len(df_filtered_sources),  # Após filtragem por fontes
            len(df_similar_summaries),  # Após filtragem por resumos
            len(similar_articles),  # Após análise de similaridade
            len(refined_df)  # Refinamento final
        ]

        # Criar e plotar o gráfico de funil
        funnel_data = pd.DataFrame({
            'Etapas': ['Coletados', 'Filtrados por Fonte', 'Filtrados por Resumo', 'Similares ao Título', 'Refinamento Final'],
            'Quantidade de Artigos': article_counts
        })
        self.visualization_manager.create_funnel_chart(funnel_data, output_file="funil_de_artigos.png")

    def filter_by_summary_similarity(self, df):
        """
        Filtra os artigos com base na similaridade dos resumos com o título do projeto usando GPT-4o Mini, de forma menos restritiva.
        """
        if 'Snippet' not in df.columns:
            raise ValueError("A coluna 'Snippet' não foi encontrada no DataFrame.")

        completions = []
        for snippet in df['Snippet']:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de artigos científicos."},
                    {"role": "user", "content": f"Compare o seguinte resumo com o título do projeto: {self.project_title}. Resumo: {snippet}"}
                ],
                max_tokens=50
            )
            completions.append(response['choices'][0]['message']['content'].strip())

        # Adiciona as respostas ao DataFrame
        df['Similaridade Resumo'] = completions
        # Menos restritivo: mantém artigos que contêm uma mínima similaridade, ou seja, em vez de "similar", aceita "relacionado" ou variações
        return df[df['Similaridade Resumo'].str.contains('similar|relevante|relacionado', case=False, na=False)].copy()

    def analyze_similarity(self, df):
        """
        Análise de similaridade entre os artigos coletados e o título do projeto usando GPT-4o Mini, de forma menos restritiva.
        """
        if 'Título' not in df.columns:
            raise ValueError("A coluna 'Título' não foi encontrada no DataFrame.")

        # Remover linhas que possuem títulos vazios ou sem significado (menos de 3 caracteres)
        df = df[df['Título'].str.len() > 3]

        # Verificar se há títulos válidos após a limpeza
        if df.empty:
            raise ValueError("Nenhum artigo possui título válido após a limpeza.")

        completions = []
        for title in df['Título']:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de artigos científicos."},
                    {"role": "user", "content": f"Compare o seguinte título com o título do projeto: {self.project_title}. Título do Artigo: {title}"}
                ],
                max_tokens=50
            )
            completions.append(response['choices'][0]['message']['content'].strip())

        df['Similaridade'] = completions
        # Menos restritivo: aceita variações como "relacionado", "relevante", além de "similar"
        return df[df['Similaridade'].str.contains('similar|relevante|relacionado', case=False, na=False)].copy()

    def analyze_summary_similarity(self, df):
        """
        Análise de similaridade entre os resumos dos artigos coletados e o resumo do meu artigo usando GPT-4o Mini.
        """
        if 'Snippet' not in df.columns:
            raise ValueError("A coluna 'Snippet' não foi encontrada no DataFrame.")

        # Remover linhas que possuem resumos vazios ou sem significado (menos de 3 caracteres)
        df = df[df['Snippet'].str.len() > 3]

        # Verificar se há resumos válidos após a limpeza
        if df.empty:
            raise ValueError("Nenhum artigo possui resumo válido após a limpeza.")

        completions = []
        for snippet in df['Snippet']:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em análise de artigos científicos."},
                    {"role": "user", "content": f"Compare o seguinte resumo com o resumo do meu artigo: {self.project_title}. Resumo do Artigo: {snippet}"}
                ],
                max_tokens=50
            )
            completions.append(response['choices'][0]['message']['content'].strip())

        df['Similaridade Resumo'] = completions
        # Menos restritivo: aceita variações como "relacionado", "relevante", além de "similar"
        return df[df['Similaridade Resumo'].str.contains('similar|relevante|relacionado', case=False, na=False)].copy()

    def compare_title_and_abstract(self, provided_title, provided_abstract, df):
        """
        Compara o título e o resumo fornecidos com os artigos coletados usando embeddings.
        """
        if 'Título' not in df.columns or 'Snippet' not in df.columns:
            raise ValueError("As colunas 'Título' ou 'Snippet' não foram encontradas no DataFrame.")

        # Gerar embeddings para o título e resumo fornecidos
        print("Gerando embeddings para o título e resumo fornecidos...")
        response_title = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=provided_title
        )
        title_embedding = response_title['data'][0]['embedding']

        response_abstract = openai.Embedding.create(
            model="text-embedding-ada-002",
            input=provided_abstract
        )
        abstract_embedding = response_abstract['data'][0]['embedding']

        # Gerar embeddings para os artigos
        print("Gerando embeddings para os artigos...")
        article_embeddings = []
        for title, snippet in zip(df['Título'], df['Snippet']):
            response = openai.Embedding.create(
                model="text-embedding-ada-002",
                input=f"{title} {snippet}"
            )
            article_embeddings.append(response['data'][0]['embedding'])

        # Calcular similaridade entre o título e resumo fornecidos e os artigos
        from sklearn.metrics.pairwise import cosine_similarity
        title_similarities = cosine_similarity([title_embedding], article_embeddings)[0]
        abstract_similarities = cosine_similarity([abstract_embedding], article_embeddings)[0]

        # Adicionar similaridades ao DataFrame
        df['Similaridade com Título'] = title_similarities
        df['Similaridade com Resumo'] = abstract_similarities

        # Ordenar DataFrame por similaridade média
        df['Similaridade Média'] = (df['Similaridade com Título'] + df['Similaridade com Resumo']) / 2
        df_sorted = df.sort_values(by='Similaridade Média', ascending=False)

        # Retornar DataFrame ordenado
        return df_sorted
