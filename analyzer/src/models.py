import hashlib
import os
import requests
import tempfile
import zipfile
from .logger import logger

MODELS_VERSION = '2023-06-18 00:00:00'
MODELS_URL     = 'https://uc3m-my.sharepoint.com/:u:/g/personal/100424097_alumnos_uc3m_es/EbycWvG74zhNuogGOd5vFmoBm4arDIC3812ShCA9zA-psQ?download=1'
MODELS_SHA256  = 'db7b26238a6295ea0853ebc85265d84f7e21a3760fdf593f7ed85430be7ba97f'

def download_models():
    """Download model files from remote server if missing or outdated"""
    base_path = os.path.realpath(os.path.dirname(__file__) + '/../models')

    # Get current version
    version = None
    version_path = base_path + '/version.txt'
    if os.path.isfile(version_path):
        with open(version_path, 'r') as file:
            version = file.read().strip()

    # Compare versions
    logger.debug(f'Current models version is {version}')
    if version == MODELS_VERSION:
        logger.debug('Models are up-to-date')
        return
    logger.info(f'Models are outdated, most recent version is {MODELS_VERSION}')

    # Download latest models
    with tempfile.NamedTemporaryFile() as file:
        hash = hashlib.sha256()

        logger.info('Downloading models...')
        headers = {
            'User-Agent': 'Mozilla/5.0',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
        }
        with requests.get(MODELS_URL, stream=True, headers=headers) as response:
            response.raise_for_status()
            for chunk in response.iter_content(chunk_size=1024*1024*2):
                file.write(chunk)
                hash.update(chunk)

        digest = hash.digest().hex()
        if digest != MODELS_SHA256:
            logger.error(f'Invalid models hash, expected {MODELS_SHA256} but got {digest} instead')
            logger.error('Cannot keep running without up-to-date models')
            exit(1)

        logger.info('Extracting models...')
        with zipfile.ZipFile(file) as zip_ref:
            zip_ref.extractall(base_path)

    # Update current version
    with open(version_path, 'w', newline='\n') as file:
        file.write(MODELS_VERSION)

    logger.info('Models were successfully updated')
