import json
import logging
import os
import time
from datetime import datetime
from typing import List, Dict
import pandas as pd
from tqdm import tqdm

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/automation.log'),
        logging.StreamHandler()
    ]
)

class ProgressManager:
    def __init__(self, checkpoint_file: str = 'data/checkpoint.json'):
        self.checkpoint_file = checkpoint_file
        self.progress = self._load_checkpoint()
        
    def _load_checkpoint(self) -> Dict:
        """Carrega o último checkpoint ou cria um novo"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return {
            'processed_users': [],
            'last_index': 0,
            'total_processed': 0,
            'last_update': None
        }
    
    def save_checkpoint(self, processed_users: List[str], current_index: int):
        """Salva o progresso atual"""
        self.progress['processed_users'].extend(processed_users)
        self.progress['last_index'] = current_index
        self.progress['total_processed'] = len(self.progress['processed_users'])
        self.progress['last_update'] = datetime.now().isoformat()
        
        os.makedirs(os.path.dirname(self.checkpoint_file), exist_ok=True)
        with open(self.checkpoint_file, 'w') as f:
            json.dump(self.progress, f, indent=4)
        
        # Criar backup
        backup_file = f'data/checkpoint_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(backup_file, 'w') as f:
            json.dump(self.progress, f, indent=4)
    
    def get_last_index(self) -> int:
        """Retorna o último índice processado"""
        return self.progress['last_index']
    
    def get_processed_users(self) -> List[str]:
        """Retorna a lista de usuários já processados"""
        return self.progress['processed_users']

class InstagramHelper:
    @staticmethod
    def save_followers(followers: List[str], filename: str = 'data/followers.csv'):
        """Salva lista de seguidores em CSV"""
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        df = pd.DataFrame(followers, columns=['username'])
        df.to_csv(filename, index=False)
    
    @staticmethod
    def load_followers(filename: str = 'data/followers.csv') -> List[str]:
        """Carrega lista de seguidores do CSV"""
        if os.path.exists(filename):
            df = pd.read_csv(filename)
            return df['username'].tolist()
        return []

def retry_on_failure(max_attempts: int = 3, delay: int = 5):
    """Decorator para retry em caso de falhas"""
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    if attempts == max_attempts:
                        logging.error(f"Falha após {max_attempts} tentativas: {str(e)}")
                        raise
                    logging.warning(f"Tentativa {attempts} falhou: {str(e)}. Tentando novamente em {delay} segundos...")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator
