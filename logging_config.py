import logging
import os

def configurar_logging():
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler("chatbot.log"),
            logging.StreamHandler()
        ]
    )
    
    # Reduzir verbosidade de algumas bibliotecas
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("google").setLevel(logging.WARNING)