import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger():
    # Crear directorio de logs si no existe
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Configurar el logger
    logger = logging.getLogger('medical_expert_system')
    logger.setLevel(logging.INFO)

    # Handler para archivo
    file_handler = RotatingFileHandler(
        'logs/medical_expert_system.log',
        maxBytes=1024 * 1024,  # 1MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s: %(message)s')
    )

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger