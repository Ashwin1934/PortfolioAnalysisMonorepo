# Prometheus Queries Guide

This document contains useful Prometheus queries for monitoring the inference service throughput and resource utilization.

## Throughput Metrics

### Requests Per Second
Monitor the rate of inference requests over time.

```promql
rate(inference_requests_total[1m])
```

**Interpretation:** Number of requests per second averaged over 1 minute.

### Successful Requests Per Second
Track only successful inference requests.

```promql
rate(inference_requests_total{status="success"}[1m])
```

### Error Rate
Monitor the percentage of failed requests.

```promql
rate(inference_requests_total{status="error"}[1m]) / rate(inference_requests_total[1m]) * 100
```

**Interpretation:** Percentage of requests that failed in the last 1 minute.

### Headlines Processed Per Second
Track the throughput of headlines being processed.

```promql
rate(headlines_processed_total[1m])
```

**Interpretation:** Headlines processed per second.

### Total Headlines Processed
Cumulative count of all headlines processed.

```promql
headlines_processed_total
```

### Active Inference Requests
Current number of in-flight requests.

```promql
inference_active_requests
```

**Interpretation:** How many requests are currently being processed.

### Average Batch Size
Average number of headlines per batch.

```promql
avg(inference_batch_size_bucket)
```

## Latency Metrics

### Average Request Latency
Average time taken per inference request.

```promql
avg(inference_request_duration_seconds)
```

**Interpretation:** In seconds. Lower is better.

### P50 Latency (Median)
50th percentile latency - typical request time.

```promql
histogram_quantile(0.50, rate(inference_request_duration_seconds_bucket[1m]))
```

### P95 Latency
95th percentile latency - what most users experience.

```promql
histogram_quantile(0.95, rate(inference_request_duration_seconds_bucket[1m]))
```

### P99 Latency
99th percentile latency - worst-case scenarios.

```promql
histogram_quantile(0.99, rate(inference_request_duration_seconds_bucket[1m]))
```

### Max Latency
Maximum latency observed (in the histogram buckets).

```promql
max(inference_request_duration_seconds_bucket)
```

## Resource Utilization - CPU

### CPU Usage (cores)
CPU cores being used by the inference service.

```promql
rate(container_cpu_usage_seconds_total{container_name="inference-service"}[1m])
```

**Interpretation:** In CPU cores. For example, 0.5 means 50% of one core.

### CPU Usage as Percentage
CPU usage as a percentage of the container limit.

```promql
rate(container_cpu_usage_seconds_total{container_name="inference-service"}[1m]) / container_spec_cpu_quota{container_name="inference-service"} * container_spec_cpu_period{container_name="inference-service"} * 100
```

### CPU Usage (Ingestion Service)
CPU cores used by the ingestion service.

```promql
rate(container_cpu_usage_seconds_total{container_name="ingestion-service"}[1m])
```

### Total CPU Usage (All Services)
Combined CPU usage across all monitored containers.

```promql
sum(rate(container_cpu_usage_seconds_total[1m]))
```

## Resource Utilization - Memory

### Memory Usage (Bytes)
Current memory used by the inference service.

```promql
container_memory_usage_bytes{container_name="inference-service"}
```

### Memory Usage (MB)
Memory usage converted to megabytes for readability.

```promql
container_memory_usage_bytes{container_name="inference-service"} / 1024 / 1024
```

### Memory Usage (GB)
Memory usage converted to gigabytes.

```promql
container_memory_usage_bytes{container_name="inference-service"} / 1024 / 1024 / 1024
```

### Memory Limit
Maximum memory the container can use.

```promql
container_spec_memory_limit_bytes{container_name="inference-service"} / 1024 / 1024
```

### Memory Usage as Percentage of Limit
How much of the memory limit is being used.

```promql
container_memory_usage_bytes{container_name="inference-service"} / container_spec_memory_limit_bytes{container_name="inference-service"} * 100
```

### Memory Usage (Ingestion Service)
Memory used by the ingestion service.

```promql
container_memory_usage_bytes{container_name="ingestion-service"} / 1024 / 1024
```

### Total Memory Usage (All Services)
Combined memory usage across all containers.

```promql
sum(container_memory_usage_bytes) / 1024 / 1024
```

### Memory Cache (Inference Service)
Cached memory that can be freed if needed.

```promql
container_memory_cache{container_name="inference-service"} / 1024 / 1024
```

## Comparison Queries for Model Performance

Use these queries to compare different models or techniques.

### Throughput Comparison
Headlines per second (useful for comparing model speeds).

```promql
rate(headlines_processed_total[5m])
```

Compare at different times or after deploying different models.

### Latency Comparison
P99 latency over 5 minutes.

```promql
histogram_quantile(0.99, rate(inference_request_duration_seconds_bucket[5m]))
```

### Resource Efficiency: Headlines per CPU Core
How many headlines are processed per CPU core used.

```promql
rate(headlines_processed_total[1m]) / rate(container_cpu_usage_seconds_total{container_name="inference-service"}[1m])
```

**Interpretation:** Higher is better. Shows efficiency of the model.

### Resource Efficiency: Headlines per MB of Memory
How many headlines are processed per MB of memory used.

```promql
rate(headlines_processed_total[1m]) / (container_memory_usage_bytes{container_name="inference-service"} / 1024 / 1024)
```

**Interpretation:** Higher is better.

## Dashboard Query Examples

### Overview Panel
Display multiple key metrics:

```promql
# Requests/sec
rate(inference_requests_total[1m])

# CPU usage %
rate(container_cpu_usage_seconds_total{container_name="inference-service"}[1m]) * 100

# Memory usage MB
container_memory_usage_bytes{container_name="inference-service"} / 1024 / 1024

# Error rate %
rate(inference_requests_total{status="error"}[1m]) / rate(inference_requests_total[1m]) * 100
```

### Time Series Comparison
Compare metrics over different time windows (1m, 5m, 15m):

```promql
# Throughput trends
rate(headlines_processed_total[1m])
rate(headlines_processed_total[5m])
rate(headlines_processed_total[15m])
```

## Tips for Using These Queries

1. **Time Ranges:** Adjust `[1m]`, `[5m]`, `[15m]` based on your needs:
   - Shorter ranges = more responsive but noisier
   - Longer ranges = smoother but less responsive

2. **Filtering:** Add labels to filter specific containers:
   ```promql
   {container_name="inference-service"}
   {container_name="ingestion-service"}
   {status="success"}
   {status="error"}
   ```

3. **Aggregation:** Use `sum()`, `avg()`, `min()`, `max()` to combine metrics

4. **Rate Calculation:** Use `rate()` for counters to see changes over time

## Viewing Prometheus

- **Prometheus UI:** http://localhost:9090
- **Graph Tab:** Select query, choose time range, click "Execute"
- **Table View:** See raw metric values
- **Graph View:** Visualize over time