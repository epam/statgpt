# StatGPT Solution Overview

**StatGPT** is an AI-driven Talk-To-Your-Data platform that enables users to interact with official statistics data
using natural language. By leveraging large language models (LLMs) and integrating with various data sources, StatGPT
provides insights, analysis, and visualizations based on conversational queries.

## 🎯 Purpose

StatGPT bridges the gap between complex statistical databases and everyday users, making official statistics accessible
through natural conversation. Whether you're a researcher, journalist, or citizen, StatGPT helps you
discover insights without needing technical expertise in database queries or statistical software.

## 📋 Core Requirements

StatGPT is designed to simplify access to official statistics data through natural language interaction. The platform
addresses the following key requirements:

### 🔍 Data Access & Discovery

1. **[Natural Language Querying](#natural-language-querying)** - Enable users to ask questions in plain language and receive accurate, data-driven
   responses
2. **[Wide Indicator Search](#wide-indicator-search)** - Identify and suggest similar indicators across multiple datasets, allowing users to
   select the most relevant sources
3. **[SDMX-Native Support](#sdmx-native-architecture)** - Work seamlessly with SDMX metadata and datasets, leveraging their structure and semantics

### 🎯 Accuracy & Reliability

1. **[Minimum Data Hallucinations](#data-accuracy--hallucination-prevention)** - Ground all responses in actual data with clear references to sources
2. **[Glossary of Terms Support](#glossary-of-terms-support)** - Use official terminology and definitions provided by data providers
3. **[Data Precision](#data-accuracy--hallucination-prevention)** - Preserve exact values and avoid unauthorized rounding or aggregation

### 🛠️ Configuration & Flexibility

1. **[Model Configurability](#model--prompt-configurability)** - Allow selection and tuning of LLM models, embedding models, and prompts
2. **[Multi-language Support](#multi-language-support)** - Support multiple languages for queries and responses
3. **[Data Visualization](#data-visualization)** - Generate charts and graphs based on query results

### 🔒 Security & Governance

1. **[Security & Privacy](#security--privacy)** - Ensure data security and user privacy with regulatory compliance
2. **[Guardrails](#guardrails)** - Implement content filtering and usage rules to prevent misuse
3. **[Rate Limiting](#rate-limiting--cost-control)** - Control resource usage and manage costs effectively

### 📊 Operations & Performance

1. **[Scalability](#scalability--performance)** - Handle varying loads with horizontal scaling capabilities
2. **[Observability](#observability)** - Monitor performance, usage, and issues through comprehensive logging
3. **[Responsible AI](#responsible-ai)** - Ensure transparency, fairness, and accountability in all operations

## 🚀 Key Features in Detail

### Natural Language Querying

StatGPT enables users to interact with official statistics data using natural language. Users can ask questions in plain
English (or other supported languages), and the system will interpret the query, retrieve relevant data, and generate a
response.

Data Query tool is responsible for translating user questions into data queries. It leverages the structure and
semantics of SDMX metadata to construct accurate queries that can be executed against the underlying data sources. Input
of the tool includes user question and context about available datasets and their structures. The output is a valid SDMX
query that can be executed to retrieve the requested data OR information about the ambiguity that needs to be resolved
by the user.

Data Query tool uses:

- Semantic and keyword search over indexed datasets and their metadata to identify relevant datasets and indicators.
- SDMX metadata (Dataflows, DSDs, Concepts, Code Lists) to understand the structure and semantics of the data.
- Availability Queries to check if the requested data is available in the identified datasets.
- LLM reasoning to select the appropriate datasets and dimension values based on the user query.

### Wide Indicator Search

**Goal**: Provide comprehensive coverage of relevant datasets rather than just the fastest single result.

**Approach**: StatGPT combines multiple search strategies:

- Special indexing techniques for broad coverage
- Semantic search for conceptual matching
- Keyword search for exact term matching
- LLM reasoning to identify related indicators

Currently, StatGPT supports both semantic-only and hybrid semantic+fulltext search modes. Both modes utilize same embedding
model: `text-embedding-3-large` by OpenAI. Hybrid mode additionally uses ElasticSearch for fulltext search.

### Data Accuracy & Hallucination Prevention

**Strategy**: StatGPT ensures data accuracy through multiple mechanisms:

**1. Query-Based Architecture**

- All data operations use SDMX queries executed against actual databases
- Frontend independently verifies queries and results

**2. Contextual Grounding**

When query results are manageable in size, they're provided to the agent with:

- Tabular data representation in Markdown
- Complete dimension, measure, and attribute information
- Both IDs and human-readable names for coded values
- Dataset reference information

**3. Strict Agent Instructions**

The AI agent is explicitly instructed to:

- ✅ Always cite dataset sources
- ✅ Use provided data exactly as-is
- ✅ Preserve data precision without rounding
- ✅ Respond "I don't know" when data is insufficient
- ❌ Never interpret beyond provided data
- ❌ Never aggregate without explicit instruction
- ❌ Never fabricate missing values

### Glossary of Terms Support

**Purpose**: Ensure consistent use of official statistical terminology.

**Implementation**:

- Glossaries are provided in tabular format
- Integrated as tools available to the AI agent
- Support for domain-specific terminology

**Required Glossary Structure**:

| Column         | Description                       | Required   |
|----------------|-----------------------------------|------------|
| **Term**       | The term or phrase to be defined  | ✅ Yes      |
| **Definition** | Official definition of the term   | ✅ Yes      |
| **Source**     | Reference URL or document         | ⭕ Optional |
| **Domain**     | Context (e.g., economics, health) | ⭕ Optional |

→ See [StatGPT Tools documentation](./tools.md) for implementation details.

### SDMX-Native Architecture

**Design Philosophy**: Built from the ground up to leverage SDMX standards.

**Key Capabilities**:

- Native understanding of SDMX structures (DSDs, Dataflows, Concepts)
- Semantic interpretation of SDMX metadata
- Direct query construction using SDMX syntax
- Support for SDMX-specific features and constraints

→ See [SDMX Compatibility documentation](./sdmx-compatibility.md) for technical details.

### Model & Prompt Configurability

**Configurable Components**:

- **LLM Models** - Choose from various language models for different use cases
- **Embedding Models** - Select optimal models for semantic search
- **System Prompts** - Customize agent behavior and responses
- **Parameters** - Fine-tune temperature, token limits, and other settings

**Configuration Methods**:

- **AI DIAL Integration** - Access to [wide range of models](https://docs.dialx.ai/platform/supported-models)
- **Admin Interface** - Visual configuration through Admin Frontend
- **Configuration Files** - Direct parameter adjustment in backend settings

### Data Visualization

**Visualization Capabilities**:

| Component           | Functionality                           | Technology   |
|---------------------|-----------------------------------------|--------------|
| **Backend**         | Generate graphs from SDMX query results | Plotly       |
| **Portal Frontend** | Auto-select optimal chart types         | Custom logic |
| **Chart Types**     | Line, bar, pie, scatter, heatmaps       | Configurable |

### Multi-language Support

**Language Capabilities**:

- **Query Processing** - Accept questions in multiple languages
- **Response Generation** - Provide answers in user's preferred language
- **Metadata Localization** - Index and search using localized SDMX metadata
- **Glossary Translation** - Support multilingual terminology

**Implementation**:

- Configurable prompts for each language
- Language-aware indexing strategies
- SDMX localization features integration

### Rate Limiting & Cost Control

**Management Approach**: Delegated to AI DIAL platform for centralized control.

**Available Controls**:

- Per-user request limits
- Token usage quotas
- Model-specific restrictions
- Cost allocation and tracking

→ See [AI DIAL Access Control](https://docs.dialx.ai/platform/core/access-control-intro) for configuration.

### Security & Privacy

**Data Protection**:

- ✅ No personal data processing
- ✅ Authentication via AI DIAL Core
- ✅ Role-based access control
- ✅ Audit logging for compliance

**Resources**:

- [AI DIAL Access Control](https://docs.dialx.ai/platform/core/access-control-intro)
- [PII Compliance & Privacy Guidelines](https://docs.dialx.ai/platform/core/privacy)

### Guardrails

**Protection Mechanisms**:

| Layer              | Function                                           | Configuration      |
|--------------------|----------------------------------------------------|--------------------|
| **Pre-agent**      | Input validation against whitelist/blacklist rules | Admin configurable |
| **Content Filter** | Block harmful or inappropriate content             | Policy-based       |
| **Query Limits**   | Prevent resource-intensive operations              | Threshold settings |
| **Output Review**  | Ensure appropriate responses                       | LLM instructions   |

### Scalability & Performance

**Architecture Benefits**:

**Application Layer**:

- **Framework**: FastAPI with async support
- **Design**: Stateless services for horizontal scaling
- **Deployment**: Kubernetes with auto-scaling policies
- **Load Balancing**: Built-in K8s capabilities

**Data Layer**:

- **PostgreSQL + pgvector**: Scalable vector search
- **ElasticSearch**: Distributed text search
- **Independent Scaling**: Each service scales based on its load profile

**Performance Characteristics**:

- Concurrent request handling
- Linear scaling with added instances

### Observability

**Monitoring Stack**:

- **Tracing**: OpenTelemetry integration for request flow tracking
- **Metrics**: Performance and usage statistics collection
- **Logging**: Structured logs with correlation IDs
- **Dashboards**: Real-time system health visualization

**Integration**:

- Built on [AI DIAL SDK](https://github.com/epam/ai-dial-sdk)
- Compatible with standard observability platforms

→ See [AI DIAL Observability Guide](https://docs.dialx.ai/platform/observability-intro)

### Responsible AI

**Core Principles**:

| Principle          | Implementation                                     |
|--------------------|----------------------------------------------------|
| **Transparency**   | Clear data source citations and query explanations |
| **Fairness**       | Unbiased access to all available datasets          |
| **Accountability** | Complete audit trails and decision logging         |
| **Accuracy**       | Grounded responses with hallucination prevention   |
| **Privacy**        | No personal data processing or retention           |

**Supporting Features**:

- [Data Accuracy & Hallucination Prevention](#data-accuracy--hallucination-prevention)
- [Security & Privacy](#security--privacy)
- [Guardrails](#guardrails)
- [Observability](#observability)
