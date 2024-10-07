import pandas as pd
import re

class DataProcessor:
    def preprocess_data(self, df):
        """
        Limpa e normaliza os dados coletados.
        """
        # Limpeza da coluna 'Data de Publicação'
        if 'Data de Publicação' in df.columns:
            # Converter para numérico e tratar valores ausentes
            df['Data de Publicação'] = pd.to_numeric(df['Data de Publicação'], errors='coerce').fillna(0).astype(int)
        else:
            print("Aviso: Coluna 'Data de Publicação' não encontrada. Adicionando uma coluna com valores padrão.")
            df['Data de Publicação'] = 0  # Adiciona coluna com valor 0 por padrão

        # Normalizar a coluna 'Fonte'
        df['Fonte Normalizada'] = df['Fonte'].apply(self.normalizar_fonte)

        return df

    def normalizar_fonte(self, fonte):
        """
        Normaliza nomes de fontes semelhantes usando regex.
        Se nenhuma correspondência for encontrada, retorna "Outras".
        """
        if isinstance(fonte, str):
            fonte = fonte.lower()

            # Mapeamento de fontes utilizando regex
            mapeamentos = {
                r'.*ieee.*': 'IEEE',
                r'.*arxiv.*': 'Arxiv',
                r'.*neural.*': 'Neural Networks',
                r'.*proceedings.*': 'Proceedings',
                r'.*springer.*': 'Springer',
                r'.*elsevier.*': 'Elsevier',
                r'.*wiley.*': 'Wiley',
                r'.*nature.*': 'Nature',
                r'.*science.*': 'Science',
                r'.*sensors.*': 'Sensors',
                r'.*remote sensing.*': 'Remote Sensing',
                r'.*expert systems.*': 'Expert Systems',
                r'.*pattern recognition.*': 'Pattern Recognition'
            }

            # Iterar sobre o dicionário de regex e aplicar a normalização
            for padrao, nome_normalizado in mapeamentos.items():
                if re.match(padrao, fonte):
                    return nome_normalizado

        return 'Outras'  # Se não houver correspondência, retorna "Outras"

    def filter_by_top_sources(self, df, top_n=10):
        """
        Filtra os artigos pelas top N fontes mais relevantes.
        """
        contagem_fonte = df['Fonte Normalizada'].value_counts()
        top_fontes = contagem_fonte.nlargest(top_n).index.tolist()
        df['Fonte Agrupada'] = df['Fonte Normalizada'].apply(lambda x: x if x in top_fontes else 'Outras')
        return df

    def filter_by_keywords(self, df):
        """
        Filtra os artigos com base em palavras-chave relevantes.
        Exemplo: apenas artigos que mencionam 'transformer', 'attention', 'aggregation'.
        """
        keywords = ['transformer', 'attention', 'aggregation']
        pattern = '|'.join(keywords)
        return df[df['Título'].str.contains(pattern, case=False, na=False)]

    def final_refinement(self, df):
        """
        Refinamento final dos artigos, como filtragem por ano de publicação recente ou número de citações.
        Exemplo: filtrando artigos publicados após 2015.
        """
        if 'Data de Publicação' not in df.columns:
            raise KeyError("A coluna 'Data de Publicação' não foi encontrada no DataFrame durante o refinamento.")

        # Filtrar apenas artigos publicados após 2015
        return df[df['Data de Publicação'] > 2015]

    def check_columns(self, df):
        """
        Verifica se as colunas essenciais estão presentes no DataFrame.
        """
        required_columns = ['Título', 'Fonte', 'Data de Publicação']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise KeyError(f"As seguintes colunas estão faltando: {', '.join(missing_columns)}")
