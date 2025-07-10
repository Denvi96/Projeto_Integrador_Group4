import google.generativeai as genai
import time
import threading
from config import GOOGLE_API_KEY, MODEL_NAME, GENERATION_CONFIG, SAFETY_SETTINGS, MAX_HISTORY, TAMANHO_MAXIMO_PERGUNTA
from utils import Colors
import logging
from cache import cache_manager
from datetime import datetime

logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, contexto):
        genai.configure(api_key=GOOGLE_API_KEY)
        
        self.model = genai.GenerativeModel(
            MODEL_NAME,
            generation_config=GENERATION_CONFIG,
            safety_settings=SAFETY_SETTINGS
        )
        
        self.prompt_inicial = self._criar_prompt_inicial(contexto)
        self.chat = self._iniciar_sessao_chat()
        
    def _criar_prompt_inicial(self, contexto):
        return f"""
Você é o JP, um assistente virtual do Programa Jovem Programador. Seu tom é amigável e prestativo.

--- REGRAS OBRIGATÓRIAS ---
1.  **FOCO ESTRITO:** Responda usando APENAS o CONTEÚDO DE REFERÊNCIA.
2.  **REGRA DA IDADE:** O requisito é ter 16 anos ou mais. Nunca diga que a pessoa é velha demais.
3.  **PROIBIÇÃO DE OUTROS ASSUNTOS:** Para temas fora do programa, responda: 'Desculpe, minha função é responder apenas sobre o Programa Jovem Programador.'
4.  **PROATIVIDADE FOCADA:** Ao final de cada resposta, sugira um próximo passo relacionado ao conteúdo.
5. **MEMÓRIA CACHE** : Mantenha o contexto da conversa.
6. **PERCEPTIVO** : Adapte-se ao nível técnico do usuário.
7. **FOCO:** Traga informações solicitadas mesmo com respostas curtas do usuário.
8. **FORMATO DE RESPOSTA**:
   - Parágrafos curtos
   - Emojis relevantes
   - Negrito para termos importantes
   - Listas com marcadores quando apropriado
   
{contexto}
--- FIM DO CONTEÚDO DE REFERÊNCIA ---
"""
    
    def _iniciar_sessao_chat(self):
        return self.model.start_chat(history=[
            {"role": "user", "parts": [self.prompt_inicial]},
            {"role": "model", "parts": ["Olá! Sou o JP, assistente virtual do Jovem Programador. Em que posso te ajudar hoje? 😊"]}
        ])
    
    def _manter_historico(self):
        if len(self.chat.history) > MAX_HISTORY * 2:
            self.chat.history = self.chat.history[-MAX_HISTORY * 2:]
    
    def enviar_mensagem(self, pergunta):
        # Verificar cache primeiro (nova implementação)
        if cached_response := cache_manager.get_response(pergunta):
            logger.info(f"Resposta recuperada do cache para: {pergunta[:30]}...")
            return cached_response
        
        try:
            # Validação original mantida
            if len(pergunta) > TAMANHO_MAXIMO_PERGUNTA:
                return "❌ Sua pergunta é muito longa. Por favor, resuma em até 500 caracteres."
            
            # Spinner original mantido
            stop_spinner = threading.Event()
            spinner_thread = threading.Thread(target=self._mostrar_spinner, args=(stop_spinner,))
            spinner_thread.start()
            
            # Chamada à API original
            response = self.chat.send_message(pergunta)
            self._manter_historico()
            
            # Salvar no cache (nova implementação)
            cache_manager.save_response(pergunta, response.text)
            logger.info(f"Nova resposta salva no cache para: {pergunta[:30]}...")
            
            return response.text
        
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {str(e)}")
            return "⚠️ Desculpe, estou com dificuldades técnicas. Poderia repetir sua pergunta?"
        finally:
            stop_spinner.set()
            spinner_thread.join()
    
    def _mostrar_spinner(self, stop_event):
        chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
        while not stop_event.is_set():
            for char in chars:
                print(f"\r{Colors.BLUE}🤖 JP:{Colors.RESET} Processando {char} ", end='', flush=True)
                time.sleep(0.1)
        print("\r", end='', flush=True)
    
    # Nova função para estatísticas (transição)
    def mostrar_estatisticas_cache(self):
        stats = cache_manager.get_usage_stats()
        print(f"\n{Colors.YELLOW}📊 Estatísticas do Cache:{Colors.RESET}")
        print(f"• Total de perguntas em cache: {stats['total_entries']}")
        print(f"• Total de acessos ao cache: {stats['total_uses']}")
        print(f"• Top perguntas:")
        for q, count in stats['top_questions'].items():
            print(f"  - {q[:30]}...: {count} acessos")

def iniciar_chat(contexto):
    # Limpeza inicial do cache (nova implementação)
    cache_manager.clean_old_cache()
    
    chat_manager = ChatManager(contexto)
    primeira_resposta = chat_manager.chat.history[-1].parts[0].text
    print(f"\n{Colors.BLUE}🤖 JP:{Colors.RESET} {primeira_resposta}")
    
    while True:
        try:
            pergunta = input(f"{Colors.GREEN}> Você:{Colors.RESET} ").strip()
            
            if not pergunta:
                continue
                
            # Comandos especiais (novos)
            if pergunta.lower() == '/stats':
                chat_manager.mostrar_estatisticas_cache()
                continue
                
            if pergunta.lower() in ['sair', 'exit', 'quit']:
                print(f"\n{Colors.BLUE}Até a próxima! 👋{Colors.RESET}")
                break
            
            resposta = chat_manager.enviar_mensagem(pergunta)
            print(f"{Colors.BLUE}🤖 JP:{Colors.RESET} {resposta}")
            
        except KeyboardInterrupt:
            print(f"\n{Colors.BLUE}Conversa encerrada pelo usuário.{Colors.RESET}")
            break
        except Exception as e:
            logger.error(f"Erro no loop de chat: {str(e)}")
            print(f"\n{Colors.RED}⚠️ Ocorreu um erro inesperado. Continuando...{Colors.RESET}")