import hashlib
import importlib
import os
import numpy as np
import pickle
import requests
import sys
import tempfile
import zipfile
from time import time
from typing import Literal, Tuple
from .logger import logger

MODELS_VERSION = 1
MODELS_URL     = 'https://uc3m-my.sharepoint.com/:u:/g/personal/100424097_alumnos_uc3m_es/EbycWvG74zhNuogGOd5vFmoBm4arDIC3812ShCA9zA-psQ?download=1'
MODELS_SHA256  = 'db7b26238a6295ea0853ebc85265d84f7e21a3760fdf593f7ed85430be7ba97f'

class AbstractModel():
    def predict_proba(self, x_test: np.ndarray) -> np.ndarray:
        pass

model_dblfs: AbstractModel = None
model_dt: AbstractModel = None
model_lr: AbstractModel = None
model_rf: AbstractModel = None

def download_models():
    """Download model files from remote server if missing or outdated"""
    base_path = os.path.realpath(os.path.dirname(__file__) + '/../models')

    # Get current version
    version = None
    version_path = base_path + '/version.txt'
    if os.path.isfile(version_path):
        with open(version_path, 'r') as file:
            version = int(file.read().strip())

    # Compare versions
    logger.debug(f'Current models version is v{version}' if version else 'No local models found')
    if version == MODELS_VERSION:
        logger.debug('Models are up-to-date')
        return
    logger.info(f'Models are outdated, most recent version is v{MODELS_VERSION}')

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
        file.write(str(MODELS_VERSION))

    logger.info('Models were successfully updated')

def load_models():
    """Load models into memory"""
    global model_dblfs, model_dt, model_lr, model_rf
    base_path = os.path.realpath(os.path.dirname(__file__) + '/../models')
    logger.info('Loading models into memory...')

    # Load dependencies
    models_deps = importlib.import_module('src.models_deps')
    sys.modules['DBL_predict'] = models_deps

    # Deserialize model classes
    with open(base_path + '/dblfs.pkl', 'rb') as file:
        model_dblfs = pickle.load(file)
        logger.debug('Loaded DBLFS model')

    with open(base_path + '/dt.pkl', 'rb') as file:
        model_dt = pickle.load(file)
        logger.debug('Loaded DT model')

    with open(base_path + '/lr.pkl', 'rb') as file:
        model_lr = pickle.load(file)
        logger.debug('Loaded LR model')

    with open(base_path + '/rf.pkl', 'rb') as file:
        model_rf = pickle.load(file)
        logger.debug('Loaded RF model')

def predict(
    model_name: Literal['dblfs', 'dt', 'lr', 'rf'],
    intensities: np.ndarray
) -> list[Tuple[Literal['027', '181', 'other'], float]]:
    """Get predictions from a given model, returning result and confidence"""
    global model_dblfs, model_dt, model_lr, model_rf

    # Get model
    if model_name == 'dblfs':
        model = model_dblfs
    elif model_name == 'dt':
        model = model_dt
    elif model_name == 'lr':
        model = model_lr
    elif model_name == 'rf':
        model = model_rf
    else:
        raise ValueError(f'Invalid model name "{model_name}"')

    # Ask model
    predictions = []
    start_time = time()
    y_pred_proba = model.predict_proba(intensities)
    duration = time() - start_time
    logger.debug(f'Model {model_name.upper()} took {duration} seconds to run')

    # Parse response
    result_values = ['027', '181', 'other']
    for row in y_pred_proba:
        result = result_values[row.argmax()]
        confidence = row.max()
        predictions.append((result, confidence))

    return predictions
