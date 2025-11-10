## **MedScribe**

> **Turning medical handwriting into structured intelligence.**

**MedScribe** is a distributed, cloud-native system designed to extract structured data from scanned medical reports (PDFs containing both printed and handwritten content).
Built on top of **DigitalOcean Kubernetes (DOKS)**, it leverages **microservice architecture**, **asynchronous pipelines**, and **AI-powered OCR/HTR** (Optical & Handwritten Text Recognition) to transform unstructured medical documents into reliable, queryable data.

---

### **Core Capabilities**

* **Smart ingestion pipeline:** Receives and validates scanned PDFs uploaded by users or integrated systems.
* **AI-powered processing:** Uses Python OCR/HTR pipelines (Tesseract + TrOCR ONNX) optimized for **CPU-only environments**.
* **Structured extraction:** Maps results into well-defined data schemas using confidence scoring and field-level bounding boxes.
* **Data APIs:** Exposes clean, normalized information through RESTful endpoints for easy integration with other platforms.
* **Scalable by design:** Horizontally scales via **KEDA** and **Helm charts**, enabling elastic workloads per document volume.

---

### **Architecture Overview**

| Component          | Description                                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Upload API**     | FastAPI service that receives PDF files, stores them in DigitalOcean Spaces (S3), and enqueues jobs to RabbitMQ.                                                  |
| **Doc Worker**     | Celery-based processor that downloads PDFs, performs OCR/HTR, applies text normalization, and stores structured results in PostgreSQL.                            |
| **Data API**       | REST service exposing document metadata, extracted fields, confidence levels, and processing status.                                                              |
| **Infrastructure** | Deployable via Helm charts (`k8s-helm-*`), with observability (Prometheus/Grafana), auto-scaling (KEDA), and secure configuration through Secrets and ConfigMaps. |

---

### **Tech Stack**

* **Language:** Python 3.12
* **Frameworks:** FastAPI, Celery
* **AI/ML:** Tesseract OCR, TrOCR (Hugging Face ONNX Runtime), OpenCV
* **Storage:** DigitalOcean Spaces (S3), PostgreSQL (Managed)
* **Messaging:** RabbitMQ
* **Deployment:** Kubernetes (DOKS) + Helm + KEDA
* **Observability:** Prometheus, Grafana, Loki, OpenTelemetry

---

### **Key Design Principles**

* **Cloud-Native & Stateless:** All components are containerized, horizontally scalable, and loosely coupled.
* **Resilient Pipelines:** Retry/backoff, DLQ support, and idempotent document handling (`sha256` hash).
* **Performance-Oriented:** Lightweight OCR models optimized for CPU; no GPU dependency.
* **Auditability:** Each extracted field is stored with confidence scores and bounding boxes for traceability.
* **Security:** TLS, restricted API keys, and encrypted storage.

---

### **Repository Structure**

```
MedScribe/
├─ apps/
│  ├─ upload-api/         → PDF ingestion and queuing
│  ├─ doc-worker/         → OCR/HTR processing pipeline
│  └─ data-api/           → Data access and integration layer
├─ k8s-helm-upload-api/   → Helm chart for Upload API
├─ k8s-helm-doc-worker/   → Helm chart for Worker + KEDA scaling
├─ k8s-helm-data-api/     → Helm chart for Data API
├─ k8s-helm-rabbitmq/     → Helm chart for RabbitMQ broker
├─ docs/                  → Architecture diagrams, runbooks, and API contracts
└─ tools/                 → Automation scripts and CI/CD utilities
```

---

### **Deployment**

```bash
# Build and push Docker images
docker build -t registry.digitalocean.com/org/medscribe-upload-api:1.0.0 apps/upload-api
docker push registry.digitalocean.com/org/medscribe-upload-api:1.0.0

# Install via Helm
helm upgrade --install upload-api ./k8s-helm-upload-api -n medscribe
helm upgrade --install doc-worker ./k8s-helm-doc-worker -n medscribe
helm upgrade --install data-api  ./k8s-helm-data-api  -n medscribe
```

---

### **Documentation**

* [Architecture Overview](docs/architecture.md)
* [Data Dictionary](docs/data-dictionary.md)
* [API Contracts (OpenAPI)](docs/api-contracts.md)
* [Runbooks & Ops Procedures](docs/ops-runbooks.md)

---

### **Contributing**

Contributions are welcome!
Please follow the [CONTRIBUTING.md](CONTRIBUTING.md) guidelines, ensure your commits are signed, and validate your changes through CI before submitting a pull request.

---

### **License**

Released under the **MIT License**.
© 2025 BRHRMASTER – MedScribe Project.
