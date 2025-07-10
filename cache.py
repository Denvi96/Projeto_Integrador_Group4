import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from config import CACHE_EXPIRATION_DAYS

class ChatCache:
    def __init__(self, db_path='chat_cache.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode = WAL")  # Melhora performance de escrita
        self._create_table()
        
    def _create_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS cache (
            id TEXT PRIMARY KEY,
            question TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            usage_count INTEGER DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_created_at ON cache(created_at);
        """
        self.conn.executescript(query)
        self.conn.commit()
    
    def _generate_id(self, question):
        """Gera ID único baseado na pergunta"""
        return hashlib.sha256(question.encode('utf-8')).hexdigest()
    
    def get_response(self, question):
        """Busca resposta em cache ou retorna None"""
        cache_id = self._generate_id(question)
        
        try:
            cursor = self.conn.execute(
                "SELECT response, usage_count FROM cache WHERE id = ?",
                (cache_id,)
            )
            
            if result := cursor.fetchone():
                response, count = result
                # Atualiza contagem de uso
                self.conn.execute(
                    "UPDATE cache SET usage_count = ? WHERE id = ?",
                    (count + 1, cache_id)
                )
                self.conn.commit()
                return json.loads(response)
            return None
        except sqlite3.Error as e:
            print(f"Erro no cache: {str(e)}")
            return None
    
    def save_response(self, question, response):
        """Salva nova resposta no cache"""
        cache_id = self._generate_id(question)
        
        try:
            self.conn.execute(
                "INSERT OR REPLACE INTO cache (id, question, response) VALUES (?, ?, ?)",
                (cache_id, question, json.dumps(response))
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao salvar no cache: {str(e)}")
            return False
    
    def clean_old_cache(self):
        """Remove entradas antigas do cache"""
        try:
            expiration_date = datetime.now() - timedelta(days=CACHE_EXPIRATION_DAYS)
            self.conn.execute(
                "DELETE FROM cache WHERE created_at < ?",
                (expiration_date.strftime('%Y-%m-%d %H:%M:%S'),)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Erro ao limpar cache: {str(e)}")
            return False
    
    def get_cache_stats(self):
        """Retorna estatísticas do cache"""
        try:
            cursor = self.conn.execute("SELECT COUNT(*) AS total, SUM(usage_count) AS total_uses FROM cache")
            stats = cursor.fetchone()
            return {
                "total_entries": stats[0],
                "total_uses": stats[1] if stats[1] else 0
            }
        except sqlite3.Error:
            return {"total_entries": 0, "total_uses": 0}
    
    def close(self):
        try:
            self.conn.close()
        except sqlite3.Error:
            pass

# Singleton para fácil acesso
cache_manager = ChatCache()