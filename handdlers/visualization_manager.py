import os
import re
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
import openai
import plotly.graph_objects as go
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS

class VisualizationManager:
    def create_line_chart(self, df, output_file="publicacoes_por_ano_e_fonte.png"):
        if 'Fonte Agrupada' not in df.columns:
            raise ValueError("A coluna 'Fonte Agrupada' não foi encontrada no DataFrame.")

        grouped = df.groupby(['Data de Publicação', 'Fonte Agrupada']).size().reset_index(name='Contagem')
        pivot_df = grouped.pivot(index='Data de Publicação', columns='Fonte Agrupada', values='Contagem').fillna(0)
        ordered_columns = pivot_df.sum().sort_values(ascending=False).index
        pivot_df = pivot_df[ordered_columns]

        fig = go.Figure()
        for column in pivot_df.columns:
            fig.add_trace(go.Scatter(
                x=pivot_df.index,
                y=pivot_df[column],
                mode='lines+markers',
                name=column,
                line=dict(width=2.5)
            ))

        fig.update_layout(
            title='Publicações por Ano e Fonte',
            xaxis_title='Ano',
            yaxis_title='Publicações',
            legend_title='Fonte',
            template='plotly_white',
            font=dict(size=18),
            title_font=dict(size=22),
            legend=dict(font=dict(size=16))
        )

        fig.write_image(output_file)
        fig.show()

    def generate_word_cloud(self, df, column, output_dir="word_clouds", text_type='title_summary'):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        for source in df['Fonte Agrupada'].unique():
            text = ' '.join(df[df['Fonte Agrupada'] == source][column])
            wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=800, height=400).generate(text)
            sanitized_source = re.sub(r'[^\w\s]', '', source).replace(' ', '_')
            wordcloud.to_file(f"{output_dir}/{text_type}_{sanitized_source}.png")

        general_text = ' '.join(df[column])
        general_wordcloud = WordCloud(stopwords=STOPWORDS, background_color="white", width=800, height=400).generate(general_text)
        general_wordcloud.to_file(f"{output_dir}/{text_type}_general.png")

    def create_funnel_chart(self, df, output_file="article_funnel.png"):
        if 'Stages' not in df.columns or 'Article Count' not in df.columns:
            raise ValueError("The DataFrame must contain 'Stages' and 'Article Count' columns.")

        fig = px.funnel_area(
            names=df['Stages'],
            values=df['Article Count']
        )

        fig.update_layout(
            title='Article Funnel Through Stages',
            template='plotly_white',
            font=dict(size=18),
            title_font=dict(size=22),
            legend=dict(font=dict(size=16))
        )

        fig.write_image(output_file)
        fig.show()

    def plot_clusters(self, df, method='OpenAI', output_file="clusters.png"):
        cluster_column = f'Cluster {method}'
        if cluster_column not in df.columns:
            raise ValueError(f"The column '{cluster_column}' was not found in the DataFrame.")

        pca_columns = [f'PCA_{method}_1', f'PCA_{method}_2']
        if not all(col in df.columns for col in pca_columns):
            pca = PCA(n_components=2)
            pca_result = pca.fit_transform(df[[col for col in df.columns if col.startswith('embedding_')]])
            df[pca_columns[0]], df[pca_columns[1]] = pca_result[:, 0], pca_result[:, 1]

        fig = go.Figure(data=[
            go.Scatter(
                x=df[pca_columns[0]],
                y=df[pca_columns[1]],
                mode='markers',
                marker=dict(color=df[cluster_column], colorscale='Viridis', showscale=True),
                text=df[cluster_column]
            )
        ])

        fig.update_layout(
            title=f'Article Clustering with {method} Embeddings',
            xaxis_title='Principal Component 1',
            yaxis_title='Principal Component 2',
            template='plotly_white',
            font=dict(size=18),
            title_font=dict(size=22),
            legend=dict(font=dict(size=16))
        )

        fig.write_image(output_file)
        fig.show()
