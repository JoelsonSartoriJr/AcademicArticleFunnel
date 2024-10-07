from handdlers.funnel_manager import FunnelManager
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()

if __name__ == "__main__":
    # Query completa e abrangente para busca
    query = (
        "(transformer OR transformers OR transformer architecture OR transformer model OR transformer-based OR transformer networks) AND "
        "(attention mechanism OR self-attention OR multi-head attention OR attention layer OR attention module OR attention-based)"
    )

    # Título do projeto para a análise de similaridade
    project_title = "Alterando o mecanismo de atenção na arquitetura Transformers aplicando funções de (pré-)agregação"

    # Chave da API da OpenAI
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("API key da OpenAI não foi definida. Verifique as variáveis de ambiente.")

    # Inicializa o funil com a query e a chave da OpenAI
    funnel = FunnelManager(query, project_title, openai_api_key)

    # Roda o funil completo
    funnel.run_funnel()

    # Título e resumo do texto fornecido
    provided_title = "Alterando o mecanismo de atenção na arquitetura Transformers aplicando funções de (pré-)agregação"
    provided_abstract = """
    This study proposes an innovative technical approach to enhance Transformers and Vision Transformers (ViTs) models by integrating FG-functional aggregation functions into the self-attention mechanism. The primary objective was to investigate how these functions can improve the models’ ability to capture complex dependencies in high-dimensional data, both in spatial and temporal contexts. Specifically, the research introduces an adapted version of the Choquet integral as a novel formulation for the self-attention mechanism, replacing traditional matrix multiplication with more sophisticated aggregation functions, such as the sum of minima and the maximum of products, aiming for more robust and expressive data analysis.

    Experiments were conducted using high-complexity datasets, including CIFAR-10, CIFAR-100, CALTECH-101, and a dataset for ASL sign language recognition. The results demonstrated that the use of alternative aggregation functions, particularly the adapted version of the Choquet integral, provides performance comparable to the traditional self-attention mechanism, with significant improvements in terms of generalization capacity and robustness in complex classification tasks. This study advances the theoretical understanding of Transformers and opens new avenues for developing more adaptable and efficient AI models. The integration of these advanced aggregation functions represents a substantial advancement in the state of the art, providing a solid foundation for future research in machine learning and artificial intelligence.
    """

    # Realiza a comparação do título e resumo fornecidos com os artigos coletados
    # Certifique-se de que o método compare_title_and_abstract está implementado na classe FunnelManager
    df_final = funnel.compare_title_and_abstract(provided_title, provided_abstract, funnel.search_manager.collect_articles())
    if df_final is not None:
        df_final.to_csv("final.csv", index=False, mode='w')
        print(df_final.head())
    else:
        print("A comparação não retornou resultados.")
