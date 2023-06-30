import numpy as np
import os
import shutil
import subprocess
import zipfile
from datetime import datetime
from io import StringIO
from pymysql import Connection
from tempfile import mkdtemp
from .database import db_connect, db_disconnect, db_query
from .logger import logger
from .models import MODELS_VERSION, predict

MAX_BATCH_SIZE = 250

def run_analyzer():
    """Run single analysis batch"""
    db = db_connect()

    # Get samples to analyze
    samples = db_query(db,
        """
        SELECT digest
        FROM samples
        WHERE analyzer_version IS NULL
        OR analyzer_version<%s
        """,
        [MODELS_VERSION]
    )
    samples: list[str] = [x['digest'].hex() for x in samples]

    # Analyze samples in batches
    if samples:
        logger.info(f'Found {len(samples)} sample(s) that need to be analyzed')
        for i in range(0, len(samples), MAX_BATCH_SIZE):
            chunk = samples[i:i+MAX_BATCH_SIZE]
            _process_batch(chunk, db)
    else:
        logger.debug('No samples to analyze')

    # Disconnect from database
    db_disconnect(db)

def _process_batch(digests: list[str], db: Connection):
    """Process batch of digests"""
    tmp_path = mkdtemp(dir=os.environ['SAMPLES_TMP_DIR'])
    logger.debug(f'Using {tmp_path} as temporary directory')

    # Extract all samples
    for digest in digests:
        logger.debug(f'Extracting sample {digest}...')
        sample_zip_path = os.environ['SAMPLES_DATA_DIR'] + '/' + digest[0:2] + '/' + digest[2:4] + '/' + digest + '.zip'
        sample_tmp_path = tmp_path + '/' + digest + '/0_A1/1/1SLin'
        with zipfile.ZipFile(sample_zip_path) as zip:
            zip.extractall(sample_tmp_path)

    # Preprocess samples
    logger.debug('Preprocessing samples...')
    intensities = []
    successful_digests: list[str] = []
    preprocess_path = os.path.realpath(os.path.dirname(__file__) + '/../preprocess.R')
    preprocess_output = subprocess.check_output(
        ['Rscript', preprocess_path, tmp_path],
        universal_newlines=True,
        stderr=subprocess.DEVNULL,
    )
    for item in preprocess_output.split('['):
        if not item: continue
        digest, data = item.split(']')
        data = np.loadtxt(StringIO(data), delimiter=',')
        intensities.append(data[:18000, 1])
        successful_digests.append(digest)
    for missing_digest in set(digests).difference(successful_digests):
        logger.warn(f'Failed to preprocess sample {missing_digest}')

    # Clear temporary files
    shutil.rmtree(tmp_path)
    logger.debug('Deleted temporary directory')

    # Predict ribotypes
    logger.debug('Predicting ribotypes in samples...')
    intensities = np.array(intensities) * 1e4
    predictions_dblfs = predict('dblfs', intensities)
    predictions_dt = predict('dt', intensities)
    predictions_lr = predict('lr', intensities)
    predictions_rf = predict('rf', intensities)

    # Persist in database
    for i, digest in enumerate(successful_digests):
        now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        db_query(db,
            """
            UPDATE samples
            SET analyzed_at=%s, analyzer_version=%s,
                dblfs_result=%s, dblfs_confidence=%s,
                dt_result=%s,
                lr_result=%s, lr_confidence=%s,
                rf_result=%s, rf_confidence=%s
            WHERE digest=UNHEX(%s)
            """,
            [
                now, MODELS_VERSION,
                predictions_dblfs[i][0], predictions_dblfs[i][1],
                predictions_dt[i][0],    # No confidence for this model
                predictions_lr[i][0],    predictions_lr[i][1],
                predictions_rf[i][0],    predictions_rf[i][1],
                digest,
            ]
        )

    logger.info(f'Persisted results for {len(successful_digests)} sample(s)')
