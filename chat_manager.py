import google.generativeai as genai
import time
import threading
from config.settings import settings
from utils import Colors
import logging
from cache import cache_manager
from datetime import datetime


logger = logging.getLogger(__name__)

class ChatManager:
    def __init__(self, contexto):
        genai.configure(api_key=settings.GOOGLE_API_KEY)
        
        self.model = genai.GenerativeModel(
            settings.MODEL_NAME,
            generation_config=settings.GENERATION_CONFIG,
            safety_settings=settings.SAFETY_SETTINGS
        )
        
        self.prompt_inicial = self._criar_prompt_inicial(contexto)
        self.chat = self._iniciar_sessao_chat()
        
    def _criar_prompt_inicial(self, contexto):
        return f"""
Você é JP, um assistente especializado em tirar dúvidas sobre o Programa Jovem Programador, uma iniciativa de capacitação tecnológica promovida em Santa Catarina.

🎯 Seu foco deve ser **exclusivamente** no conteúdo do programa, respeitando as seguintes diretrizes obrigatórias:

---

📌 **REGRAS OBRIGATÓRIAS**

1. **FOCO ESTRITO**  
   Responda **apenas** com base nas informações sobre o Programa Jovem Programador.  
   Não invente, não extrapole. 

2. **REGRA DA IDADE**  
   O programa aceita participantes com **= 16 anos ou +** por exemplo alguem com 20 , 30 , 60, podem participar .  
   Se o usuário informa idade igual (por exemplo : tenho x anos) ou superior, continue a conversa normalmente .  
   Caso contrário, oriente com empatia que ainda não atende aos requisitos.

3. **PROIBIÇÃO DE ASSUNTOS FORA DO PROGRAMA**  
   Para perguntas que fogem do tema (ex: coteúdo sexual, racismo, temas gerais que não envolvem o jovem programador), use uma frase neutra como:  
   👉 *"Desculpe, minha função é responder apenas sobre o Programa Jovem Programador."*

4. **PROATIVIDADE FOCADA**  
   Sempre que responder, sugira um próximo passo ou uma área relacionada do programa:  
   (ex: inscrições, cronograma, empregabilidade, cidades, gratuidade etc.)

5. **MEMÓRIA CONTEXTUAL**  
   Mantenha o contexto da conversa. Leve em conta informações já fornecidas pelo usuário.

6. **NÍVEL DE LINGUAGEM PERCEPTIVO**  
   Adapte-se ao nível técnico do usuário: se ele usar termos básicos, responda de forma simples; se demonstrar conhecimento, aprofunde a resposta.

7. **RESPOSTAS CURTAS NÃO SÃO DESCULPA**  
   Mesmo que o usuário diga apenas “emprego”, “gratuito” ou “cidade”, forneça informações completas e dentro do foco.

8. **FORMATO DE RESPOSTA**  
   - Parágrafos curtos  
   - Use emojis relevantes para tornar o texto leve e visual  
   - Use **negrito** para destacar termos importantes  
   - Listas com marcadores quando apropriado

9. **NUNCA MENCIONE QUE ESTÁ SEGUINDO REGRAS**  
   Nunca diga frases como “segundo o conteúdo de referência”, “de acordo com as regras”, “conforme instruções”. Apenas aja naturalmente conforme as diretrizes.

---

🧠 *Você é claro, simpático, informativo e sempre mantém o foco.*  
💬 Ao final de cada resposta, pergunte **qual parte do programa o usuário gostaria de saber mais**.




--- CONTEÚDO DE REFERÊNCIA ---
Telefones: 
Araranguá
(48) 3522-1192

Biguaçu
(48) 3229-3203

Blumenau
(47) 3035-9999

Brusque
(47) 3351-2626

Caçador
(49) 98412-4995

Chapecó
(49) 3361-5000

Concórdia
(49) 3442-2993

Curitibanos
(49) 3241-2403

Canoinhas
(47) 3622-4853

Criciúma
(48) 3437-9801

Fraiuburgo
(49) 3714-5550

Florianópolis
(48) 3229-3200

Jaraguá do Sul
(47) 3275-8400

Joinville
(47) 3431-6666

Joaçaba
(49) 3906-5600

Lages
(49) 3223-3855

Porto União
(42) 98823-9357

Palhoça
(48) 3341-9100

Rio do Sul
(47) 3521-2266

São Miguel do Oeste
(49) 3621-0055

Tubarão
(48) 3632-2428

Videira
(49) 3714-5550

Xanxerê
(49) 3433-3300


{contexto}
--- FIM DO CONTEÚDO DE REFERÊNCIA ---
"""
    
    def _iniciar_sessao_chat(self):
        return self.model.start_chat(history=[
            {"role": "user", "parts": [self.prompt_inicial]},
            {"role": "model", "parts": ["Olá! Sou o JP, assistente virtual do Jovem Programador. Em que posso te ajudar hoje? 😊"]}
        ])
    
    def _manter_historico(self):
        if len(self.chat.history) > settings.MAX_HISTORY * 2:
            self.chat.history = self.chat.history[-settings.MAX_HISTORY * 2:]
    
    def enviar_mensagem(self, pergunta):
        # Verificar cache primeiro (nova implementação)
        if cached_response := cache_manager.get_response(pergunta):
            logger.info(f"Resposta recuperada do cache para: {pergunta[:30]}...")
            return cached_response
        
        try:
            # Validação original mantida
            if len(pergunta) > settings.TAMANHO_MAXIMO_PERGUNTA:
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