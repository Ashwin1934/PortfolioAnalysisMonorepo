import grpc
from concurrent import futures
import threading
import time
import logging
from prometheus_client import Counter, Histogram, Gauge, start_http_server

import inference_pb2
import inference_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(threadName)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

# Prometheus metrics
inference_requests_total = Counter(
    'inference_requests_total',
    'Total number of inference requests',
    ['status']
)

inference_request_duration_seconds = Histogram(
    'inference_request_duration_seconds',
    'Inference request latency in seconds',
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0, 7.5, 10.0)
)

inference_active_requests = Gauge(
    'inference_active_requests',
    'Number of active inference requests'
)

headlines_processed_total = Counter(
    'headlines_processed_total',
    'Total number of headlines processed'
)

inference_batch_size = Histogram(
    'inference_batch_size',
    'Size of inference batches',
    buckets=(1, 2, 5, 10, 25, 50)
)


class InferenceService(inference_pb2_grpc.InferenceServiceServicer):

    def __init__(self):
        super().__init__()
        logger.info("InferenceService initialized")
        # TODO: Implement an interface/abstract class for inference logic
    
    def RunInference(self, request, context):
        # TODO run inference from the model, populate response object
        inference_active_requests.inc()
        start_time = time.time()
        
        try:
            logger.info(f"Received inference request with {len(request.headlines) if hasattr(request, 'headlines') else 1} headlines")
            
            # For now, just track that we received it
            batch_size = len(request.headlines) if hasattr(request, 'headlines') else 1
            inference_batch_size.observe(batch_size)
            headlines_processed_total.inc(batch_size)
            
            response = inference_pb2.InferenceResponse()
            inference_requests_total.labels(status='success').inc()
            
            return response
        except Exception as e:
            logger.error(f"Error processing inference request: {e}")
            inference_requests_total.labels(status='error').inc()
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise
        finally:
            # Record latency
            elapsed = time.time() - start_time
            inference_request_duration_seconds.observe(elapsed)
            inference_active_requests.dec()

def serve():
    '''
        When new requests come in, they are passed off to a thread pool of 5 threads.
        If more than 5 requests come in they are put onto a queue and processed when a thread frees up.
        This is a simple way to handle concurrency in gRPC servers, can likely be optimized further.
    '''
    # Start Prometheus metrics server on port 8000
    start_http_server(8000)
    logger.info("📊 Prometheus metrics server started on port 8000")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=5))
    inference_pb2_grpc.add_InferenceServiceServicer_to_server(
        InferenceService(),
        server)
    server.add_insecure_port("[::]:50051")
    server.start()
    logger.info("🚀 gRPC Inference Server running on port 50051")
    server.wait_for_termination()


if (__name__ == "__main__"):
    serve()