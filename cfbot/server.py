from flask import Flask, jsonify, request
from flask_cors import CORS
import threading
import logging
from main import InstagramBot
import json
import os
import time
import traceback

app = Flask(__name__)
# Configuração CORS mais permissiva para desenvolvimento
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Estado global
bot = None
bot_thread = None
is_running = False
processed = 0
total = 0
status_message = "Pronto"

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def bot_worker(batch_size, min_delay, max_delay, pause_after):
    global is_running, processed, total, status_message, bot
    
    try:
        is_running = True
        status_message = "Iniciando..."
        logger.info("Iniciando worker do bot")
        
        def progress_callback(current, total_items):
            global processed, total
            processed = current
            total = total_items
            logger.info(f"Progresso: {current}/{total_items}")
        
        bot = InstagramBot(
            batch_size=batch_size,
            min_delay=min_delay,
            max_delay=max_delay,
            pause_after=pause_after
        )
        bot.on_progress = progress_callback
        bot.run()
        
        status_message = "Concluído"
        logger.info("Bot concluído com sucesso")
        
    except Exception as e:
        logger.error(f"Erro durante execução: {str(e)}")
        logger.error(traceback.format_exc())
        status_message = f"Erro: {str(e)}"
    finally:
        is_running = False
        if bot:
            try:
                bot.driver.quit()
            except:
                pass
            bot = None

@app.route('/check_login', methods=['GET'])
def check_login():
    try:
        temp_bot = InstagramBot()
        is_logged = temp_bot.check_login_status()
        return jsonify({
            'success': True,
            'is_logged_in': is_logged
        })
    except Exception as e:
        logger.error(f"Erro ao verificar login: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        })
    finally:
        if temp_bot and hasattr(temp_bot, 'driver'):
            try:
                temp_bot.driver.quit()
            except:
                pass

@app.route('/export_followers', methods=['GET', 'OPTIONS'])
def export_followers():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        logger.info("Iniciando exportação de seguidores")
        global bot
        
        # Pega parâmetros de segurança
        batch_size = int(request.args.get('batchSize', 100))
        min_delay = float(request.args.get('minDelay', 0.3))
        max_delay = float(request.args.get('maxDelay', 0.8))
        pause_after = int(request.args.get('pauseAfter', 1000))
        
        logger.info(f"Parâmetros: batch={batch_size}, delay={min_delay}-{max_delay}, pause={pause_after}")
        
        bot = InstagramBot(
            batch_size=batch_size,
            min_delay=min_delay,
            max_delay=max_delay,
            pause_after=pause_after
        )
        
        def progress_callback(current, total_items):
            global processed, total
            processed = current
            total = total_items
            logger.info(f"Progresso exportação: {current}/{total_items}")
        
        bot.on_progress = progress_callback
        
        followers = bot.collect_followers()
        logger.info(f"Seguidores coletados: {len(followers)}")
        
        return jsonify({
            'success': True,
            'followers': followers
        })
    except Exception as e:
        logger.error(f"Erro ao exportar seguidores: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
    finally:
        if bot:
            try:
                bot.driver.quit()
            except:
                pass
            bot = None

@app.route('/start', methods=['POST', 'OPTIONS'])
def start_bot():
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        logger.info("Iniciando bot")
        global bot_thread, is_running
        
        if is_running:
            logger.warning("Bot já está em execução")
            return jsonify({
                'success': False,
                'error': 'Bot já está em execução'
            })
        
        # Pega parâmetros de segurança
        data = request.get_json()
        if not data:
            raise ValueError("Dados JSON não encontrados no request")
            
        batch_size = int(data.get('batchSize', 100))
        min_delay = float(data.get('minDelay', 0.3))
        max_delay = float(data.get('maxDelay', 0.8))
        pause_after = int(data.get('pauseAfter', 1000))
        
        logger.info(f"Parâmetros: batch={batch_size}, delay={min_delay}-{max_delay}, pause={pause_after}")
        
        bot_thread = threading.Thread(
            target=bot_worker,
            args=(batch_size, min_delay, max_delay, pause_after)
        )
        bot_thread.start()
        
        return jsonify({
            'success': True
        })
    except Exception as e:
        logger.error(f"Erro ao iniciar bot: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/pause', methods=['POST'])
def pause():
    global is_running, status_message
    if is_running:
        is_running = False
        status_message = "Pausado"
        return jsonify({"status": "paused"})
    return jsonify({"status": "not_running"})

@app.route('/status', methods=['GET'])
def get_status():
    try:
        logger.debug(f"Status atual: running={is_running}, processed={processed}, total={total}")
        return jsonify({
            'running': is_running,
            'processed': processed,
            'total': total,
            'status': status_message,
            'finished': not is_running and processed > 0
        })
    except Exception as e:
        logger.error(f"Erro ao obter status: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({
            'error': str(e)
        }), 500

@app.route('/test', methods=['GET'])
def test():
    """Rota de teste para verificar se o servidor está funcionando"""
    return jsonify({
        'status': 'ok',
        'message': 'Servidor está funcionando'
    })

if __name__ == '__main__':
    try:
        logger.info("Iniciando servidor na porta 5000")
        # Modo debug desligado para evitar problemas com threads
        app.run(port=5000, debug=False)
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {str(e)}")
        logger.error(traceback.format_exc())
