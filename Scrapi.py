import requests
from bs4 import BeautifulSoup
import json
import datetime

cabecalhos = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

url = "https://www.jovemprogramador.com.br/duvidas.php"

try:
    resposta = requests.get(url, headers=cabecalhos, timeout=10)
    resposta.raise_for_status()

    sopa = BeautifulSoup(resposta.text, 'html.parser')
    dados_faq = []

    # Encontrar todas as seções de perguntas
    for secao in sopa.select('div.accordion'):
        # Encontrar todos os itens de pergunta dentro da seção
        for item in secao.select('div[id^="heading-"]'):
            # Extrair ID único da pergunta
            id_pergunta = item['id'].split('-')[-1]
            
            # Extrair pergunta
            elemento_pergunta = item.select_one('h4')
            if elemento_pergunta:
                # Remover o ícone de seta se existir
                for i in elemento_pergunta.select('i.fa-arrow-down'):
                    i.decompose()
                pergunta = elemento_pergunta.get_text(strip=True)
            else:
                pergunta = "Pergunta não encontrada"
            
            # Encontrar a resposta correspondente
            id_resposta = item['id'].replace('heading', 'collapse')
            elemento_resposta = secao.select_one(f'div[id="{id_resposta}"]')
            if elemento_resposta:
                resposta_texto = elemento_resposta.select_one('div.card-body').get_text(strip=True)
            else:
                resposta_texto = "Resposta não encontrada"
            
            # Adicionar ao dataset com ID único
            dados_faq.append({
                "id": id_pergunta,
                "pergunta": pergunta,
                "resposta": resposta_texto,
                "tags": ["frequente"],
                "contexto": "Jovem Programador FAQ"
            })

    # Obter data atual para metadata
    data_extracao = datetime.datetime.now().isoformat()
    
    # Salvar os dados em formato JSON otimizado para chatbots
    with open("dataset_perguntas.json", "w", encoding="utf-8") as arquivo:
        json.dump({
            "metadata": {
                "fonte": url,
                "data_extracao": data_extracao,
                "total_perguntas": len(dados_faq)
            },
            "perguntas": dados_faq
        }, arquivo, ensure_ascii=False, indent=4)

    print(f"Dataset criado com sucesso! {len(dados_faq)} perguntas processadas.")

except requests.exceptions.RequestException as erro:
    print(f"Erro na conexão: {erro}")
except Exception as erro:
    print(f"Ocorreu um erro inesperado: {erro}")