# System Architecture & Component Design

## Overview
The **Tross LinkedIn Profile API** is designed as a modular, high-performance asynchronous REST service built with **FastAPI**, **Pydantic v2**, and **HTTPX**.

The architecture adheres to the **Clean Architecture / Hexagonal Architecture** principles, strictly decoupling network communication, data validation, domain parsing, and upstream data retrieval.

---

## Architectural Layers

```mermaid
flowchart TD
    Client["HTTP Client / Evaluator"] --> Router["FastAPI Router"]
    
    subgraph Security["Security and Routing"]
        Router --> Validator["URL Validator and SSRF Guard"]
        Validator --> Service["Profile Service"]
    end

    subgraph Providers["Provider Abstraction"]
        Service --> Factory["ProfileDataProvider Factory"]
        Factory --> Mock["Mock Profile Provider"]
        Factory -.-> Live["Candidate Live Provider"]
    end

    subgraph Processing["Parsing and Normalization"]
        Mock --> Raw["Raw Payload"]
        Live --> Raw
        Raw --> Parser["Profile Parser"]
        Parser --> Normalizer["Profile Normalizer"]
        Normalizer --> Models["Pydantic Models"]
    end

    Models --> Router
    Router --> Response["Structured JSON Response"]
    Response --> Client
```

---

## Component Responsibilities

### 1. API & Security Guard Layer (`app/api/`, `app/utils/url.py`)
- **`POST /v1/profile`**: Accepts `ProfileRequest` containing `url`.
- **`GET /health`**: Health status and provider probe.
- **SSRF Defense**: Strict regex domain whitelist restricting hostnames strictly to `linkedin.com` and `*.linkedin.com`. Rejects non-profile paths (`/company/`, `/jobs/`, `/feed/`, etc.), IP addresses, localhost, and cloud metadata services (`169.254.169.254`).

### 2. Service Orchestrator (`app/services/profile_service.py`)
- Coordinates the workflow: URL validation -> Vanity ID extraction -> Provider retrieval -> Parsing -> Normalization -> Response formatting.

### 3. Provider Abstraction (`app/providers/base.py`)
- Defines the `ProfileDataProvider` protocol:
  ```python
  class ProfileDataProvider(Protocol):
      @property
      def provider_name(self) -> str: ...
      async def get_raw_profile(self, vanity_id: str) -> Dict[str, Any]: ...
  ```
- Allows swapping between `MockProfileProvider` (synthetic test personas) and candidate live providers without modifying the API, contracts, parsers, or tests.

### 4. Parser & Normalizer Layer (`app/providers/parser.py`, `app/providers/normalizer.py`)
- **`ProfileParser`**: Defensive, format-agnostic extractor handling diverse data structures.
- **`ProfileNormalizer`**: Standardizes date formats (`YearMonth`), location breakdown, employment duration, and computes metadata (`sections_found`, `sections_missing`, `warnings`).

### 5. Domain Models (`app/models/response.py`, `app/models/errors.py`)
- Strictly typed Pydantic models ensuring reliable serialization and OpenAPI auto-generation.

---

## Error Handling Matrix

| HTTP Status | Error Code | Description |
| :--- | :--- | :--- |
| `400 Bad Request` | `INVALID_URL` | Malformed URL, unsupported host, or invalid profile path |
| `404 Not Found` | `PROFILE_NOT_FOUND` | Profile vanity ID does not exist |
| `429 Too Many Requests` | `RATE_LIMITED` | Rate limit encountered |
| `500 Internal Error` | `INTERNAL_ERROR` | Unhandled server exception |
| `502 Bad Gateway` | `PROVIDER_UNAVAILABLE` | Upstream provider failure or network error |
