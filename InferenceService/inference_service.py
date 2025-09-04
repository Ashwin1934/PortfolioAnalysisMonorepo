import grpc
from concurrent import futures
import threading
import time
import torch
import logging

import inference_pb2
import inference_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


class InferenceService(inference_pb2_grpc.InferenceServiceServicer):

    def __init__(self, model_path):
        super().__init__()
        self.model = torch.load(model_path, map_location="cpu") # TODO experiment with Torch loading etc
        self.model.eval()

        # preprocessing should be loaded here, tokenizer vocab etc
    
    def RunInference(self, request, context):
        # TODO run inference from the model, populate response object
        logger.info("Received inference request")

        response = inference_pb2.InferenceResponse()
        return response

def serve():
    '''
        When new requests come in, they are passed off to a thread pool of 5 threads.
        If more than 5 requests come in they are put onto a queue and processed when a thread frees up.
        This is a simple way to handle concurrency in gRPC servers, can likely be optimized further.
    '''
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(
        InferenceService("model.pt"), # TODO upload model etc
        server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("gRPC Inference Server running on port 50051")
    server.wait_for_termination()


if (__name__ == "__main__"):
    serve()