# micro-service-helm-elk
Micro-service orchestration with build-in observability and CIS compliance using Helm.

[![Kubernetes](https://img.shields.io/badge/Kubernetes-Helm-blue?logo=kubernetes)](https://helm.sh)
[![Python](https://img.shields.io/badge/Python-3.9+-yellow?logo=python)](https://www.python.org/)
[![ELK Stack](https://img.shields.io/badge/Observability-ELK-cc0000?logo=elastic)](https://www.elastic.co/what-is/elk-stack)
[![Docker](https://img.shields.io/badge/Container-Docker-2496ED?logo=docker)](https://www.docker.com/)

Helm chart + Python app for a **time-series microservice** with built-in observability via **ELK** (Elasticsearch, Logstash, Kibana) and Security.

This repo demonstrates how to deploy a Python-based microservice on Kubernetes using Helm, with:  
- **Sidecar-based log collection** via Filebeat  
- **Multi-stage Docker builds** to reduce image size  
- **CIS benchmark adherence** by running as a non-root user  
- **SRE focus** (improved MTTD/MTTR, meeting SLI/SLOs) 

---

## 📊 Observability Flow

1. The Python app writes logs to a **shared volume**.  
2. A **Filebeat sidecar container** (running inside the same pod) tails logs from this volume.  
3. Filebeat forwards logs to **Logstash** for processing.  
4. Logs are indexed in **Elasticsearch**.  
5. **Kibana** provides dashboards, search, and monitoring.  

---

## 🧩 Sidecar Concept (Filebeat Integration)

- Each pod consists of **two containers**:  
  - The **app container** (Python microservice).  
  - A **Filebeat sidecar container**.  
- They share a `volumeMount` (e.g., `emptyDir{}`) where the app writes logs.  
- Filebeat tails the log files in that shared volume and ships them out.  

This ensures logs never leave the pod uncollected, and keeps observability consistent across microservices.

---

## 🔎 SRE Benefits (MTTD, MTTR, SLI/SLO)

This setup isn’t just about collecting logs — it directly improves **Site Reliability Engineering (SRE) metrics**:

- ⏱ **Reduced MTTD (Mean Time to Detect):**  
  Real-time log shipping and Kibana dashboards let you detect issues faster.  
- ⚡ **Reduced MTTR (Mean Time to Recovery):**  
  Engineers can pinpoint failures (node, pod, or service-level) quickly and apply fixes.  
- 🎯 **Better adherence to SLI/SLOs:**  
  Faster detection & recovery keeps error budgets safe and service reliability high.  
- 🔄 **Continuous feedback loop:**  
  Logs → Insights → Faster iteration → Improved reliability.  

This makes the system **self-serving for both Dev and Ops teams**, ensuring observability drives reliability.

---

## ✅ Benefits

- Observability baked in from **Day 1**.  
- Real-time insights into health, errors, and latency.  
- **Sidecar approach** keeps log collection tightly coupled with app lifecycle.  
- SRE-focused improvements in **MTTD, MTTR, and SLO adherence**.  
- Reusable Helm setup for other microservices.  
- Extensible: plug in Prometheus, OpenTelemetry, tracing, etc.

## 📖 Getting Started
- Clone the repo:
  ```
  git clone https://github.com/neeabhishek/time-series-helm-elk.git](https://github.com/neeabhishek/micro-service-helm-elk.git)
  cd micro-service-helm-elk
  ```
  
- Build & deploy:
  ```
  helm package helm-chart
  helm lint time-series*.tar.gz
  helm template time-series*.tar.gz --debug
  helm install time-series time-series*.tar.gz
  ```
  
- Verification:
  ```
  kubectl get all -n app -o wide
  ```
  
## (Optional) 🎯 Important Considerations for Productions
- Use storageClass or PV for volumes in Production.
- Enable security features at elasticsearch, logstash, and kibana layer through ConfigMap.
- If application is generating logs at /var then use `` add_kubernetes_metadata `` in file-beat ConfigMap for kubernetes metadata. Service account, CluserRole, and ClusterRoleBinding exists in the templates directory for commuication to kube-apiserver.
