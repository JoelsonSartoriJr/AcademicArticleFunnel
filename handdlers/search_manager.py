import os
import json
import time
import pandas as pd
from dotenv import load_dotenv
from scholarly import scholarly, MaxTriesExceededException

class SearchManager:
    def __init__(self, query, num_results=100, delay=20):
        load_dotenv()
        self.query = query
        self.num_results = num_results
        self.delay = delay

    def collect_articles(self, output_file="artigos_google_scholar.json"):
        """
        Coleta artigos utilizando o Scholarly e salva em um arquivo JSON.
        """
        if os.path.exists(output_file):
            print(f"O arquivo {output_file} já existe. Carregando resultados do arquivo.")
            all_results = self._load_from_file(output_file)
        else:
            print("Arquivo não encontrado. Iniciando nova busca...")
            all_results = self._search_articles(output_file)

        if not all_results:
            raise ValueError("Nenhum resultado encontrado. Verifique a coleta de artigos ou o arquivo de entrada.")
        articles_list = self._process_articles_to_dataframe(all_results)
        return pd.DataFrame(articles_list)

    def _load_from_file(self, file_path):
        """
        Carrega os artigos de um arquivo JSON salvo anteriormente.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar o arquivo {file_path}: {e}")
            return None

    def _search_articles(self, output_file):
        """
        Faz a busca de artigos utilizando a biblioteca Scholarly e salva em um arquivo JSON.
        """
        search_query = scholarly.search_pubs(self.query)
        all_results = []

        try:
            for i, article in enumerate(search_query):
                if i >= self.num_results:
                    break
                all_results.append(article)
                print(f"Artigos coletados: {len(all_results)}")
                time.sleep(self.delay)  # Delay to avoid being blocked by Google Scholar
        except MaxTriesExceededException as e:
            print(f"Cannot fetch from Google Scholar: {e}")
        except Exception as e:
            print(f"Erro ao buscar artigos: {e}")

        if all_results:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(all_results, f, ensure_ascii=False, indent=4)
            print(f"Total de artigos salvos: {len(all_results)} em {output_file}")
        return all_results

    def _process_articles_to_dataframe(self, all_results):
        """
        Processa os resultados do Scholarly e os converte em um DataFrame do pandas.
        """
        articles_list = []
        for article in all_results:
            try:
                title = article.get("bib", {}).get("title", "")
                link = article.get("pub_url", "")
                snippet = article.get("bib", {}).get("abstract", "")
                authors = article.get("bib", {}).get("author", [])
                date = article.get("bib", {}).get("pub_year", "")
                venue = article.get("bib", {}).get("venue", "")

                articles_list.append({
                    "Título": title,
                    "Link": link,
                    "Snippet": snippet,
                    "Autores": ", ".join(authors),
                    "Data de Publicação": date,
                    "Fonte": venue
                })
            except Exception as e:
                print(f"Erro ao processar um artigo: {e}")
                continue
        return articles_list

# Exemplo de como você iniciaria o processo
if __name__ == "__main__":
    query = "transformer"
    search_manager = SearchManager(query=query, num_results=20, delay=20)
    df = search_manager.collect_articles()
    print(df)
