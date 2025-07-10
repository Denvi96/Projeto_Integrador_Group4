from utils import limpar_tela, mostrar_cabecalho
from scraper import carregar_contexto
from chat_manager import iniciar_chat
from config import URLS_PARA_SCRAPING, USE_CACHE
import logging
from logging_config import configurar_logging
from sentence_transformers import util
util.http_get = lambda *args, **kwargs: requests.get(*args, **kwargs, stream=False)


def main():
    configurar_logging()
    logging.info("Iniciando aplicação")
    
    try:
        limpar_tela()
        print("Iniciando o Chatbot JP...")
        
        contexto = carregar_contexto(URLS_PARA_SCRAPING, USE_CACHE)
        if not contexto:
            raise RuntimeError("Não foi possível carregar o contexto necessário")
            
        mostrar_cabecalho()
        iniciar_chat(contexto)

    
    except Exception as e:
        logging.critical(f"Erro fatal: {str(e)}")
        print(f"\n🚨 Ocorreu um erro crítico: {str(e)}")
        print("Por favor, tente novamente mais tarde.")

    finally:
        from cache import cache_manager
        cache_manager.close()
        logging.info("Cache fechado corretamente")

if __name__ == "__main__":
    main()