# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os

from azureml.automl.core.shared import logging_utilities
from azureml.automl.dnn.vision.classification.inference.score import _score_with_model
from azureml.automl.dnn.vision.common.logging_utils import get_logger
from azureml.automl.dnn.vision.common.model_export_utils import (
    load_model, run_inference_helper)
from azureml.automl.dnn.vision.common.utils import _set_logging_parameters
from azureml.contrib.services.aml_request import rawhttp
from azureml.contrib.services.aml_response import AMLResponse
from azureml.core.model import Model

TASK_TYPE = 'image-classification'
logger = get_logger('azureml.automl.core.scoring_script_images')


def init():
    global model

    # Set up logging
    _set_logging_parameters(TASK_TYPE, {})

    model_path = os.path.join(os.getenv('AZUREML_MODEL_DIR'), 'model.pt')
    if not os.path.exists(model_path):
        model_path = Model.get_model_path(model_name='AutoML648a1ce9e0')

    try:
        logger.info("Loading model from path: {}.".format(model_path))
        model_settings = {"valid_resize_size": 256, "valid_crop_size": 224, "train_crop_size": 224}
        model = load_model(TASK_TYPE, model_path, **model_settings)
        logger.info("Loading successful.")
    except Exception as e:
        logging_utilities.log_traceback(e, logger)
        raise


@rawhttp
def run(request):
    logger.info("Request: [{0}]".format(request))
    if request.method == "GET":
        response_body = str.encode(request.full_path)
        return AMLResponse(response_body, 200)

    elif request.method == "POST":
        request_body = request.get_data()
        logger.info("Running inference.")
        result = run_inference_helper(model, request_body, _score_with_model, TASK_TYPE)
        logger.info("Finished inferencing.")
        return AMLResponse(result, 200)
    else:
        return AMLResponse("bad request", 500)
