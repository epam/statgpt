# 📐 StatGPT Architecture Documentation

This directory contains comprehensive technical documentation for the StatGPT platform architecture, covering system
design, services, tools, and integration requirements.

## 📚 Documentation Structure

### Core Documentation

| Document                                             | Description                                               | Key Topics                                                                                                             |
|------------------------------------------------------|-----------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| **[📋 Overview](./overview.md)**                     | Complete platform overview with requirements and features | • Natural language querying<br>• Data accuracy & reliability<br>• Security & governance<br>• Performance & scalability |
| **[🏭 Services](./services.md)**                     | Core services and dependencies architecture               | • Chat Backend (DIAL app)<br>• Admin Backend & Frontend<br>• Portal Frontend<br>• Third-party integrations             |
| **[🔧 Tools](./tools.md)**                           | Agent tools and capabilities documentation                | • Data query tools<br>• Publications RAG<br>• Glossary management<br>• Web search integration                          |
| **[🔌 Application MCP](./mcp.md)**                   | Agentic access via Model Context Protocol                 | • Channel tools surfaced to AI agents<br>• DIAL Application registration<br>• MCP-spec discovery + IDP OAuth flow      |
| **[📊 SDMX Compatibility](./sdmx-compatibility.md)** | SDMX standards and requirements guide                     | • Version support (2.1/3.0)<br>• Metadata requirements<br>• Performance standards<br>• Quality checklist               |

### Design Documentation/res

| Document                          | Description                                   | Key Topics                                                                        |
|-----------------------------------|-----------------------------------------------|-----------------------------------------------------------------------------------|
| **[🤖 Agent Design](./agent.md)** | StatGPT agent architecture and implementation | • Tool-calling approach<br>• Dynamic history management<br>• Contextual grounding |

## 🗺️ Quick Navigation Guide

### Getting Started

1. **New to StatGPT?** → Start with [Overview](./overview.md) for platform understanding
2. **Setting up services?** → Review [Services](./services.md) for deployment architecture
3. **Integrating data sources?** → Check [SDMX Compatibility](./sdmx-compatibility.md) requirements
4. **Understanding the AI agent?** → Read [Agent Design](./agent.md) for technical details

## 🎯 Key Architecture Principles

### 1. **SDMX-Native Design**

StatGPT is built from the ground up to work with SDMX (Statistical Data and Metadata eXchange) standards, ensuring
seamless integration with official statistics providers.

### 2. **Tool-Calling Agent Architecture**

The AI agent uses a structured tool-calling approach rather than code generation, ensuring reliable and secure data
operations.

### 3. **Multi-Layer Search Strategy**

Combines keyword, semantic, and LLM-based search to provide comprehensive data discovery across multiple datasets.

### 4. **Grounded Responses**

All data responses are grounded in actual query results, preventing hallucinations and ensuring accuracy.

### 5. **Scalable Microservices**

Stateless services design enables horizontal scaling to handle varying loads efficiently.

## 🔗 Related Resources

### Implementation Repositories

- [StatGPT Backend](https://github.com/epam/statgpt-backend) - Core services implementation
- [StatGPT Admin Frontend](https://github.com/epam/statgpt-admin-frontend) - Administrative interface
- [StatGPT Portal Frontend](https://github.com/epam/statgpt-portal-frontend) - User interface library
- [StatGPT Helm](https://github.com/epam/statgpt-helm) - Kubernetes deployment charts

### External Documentation

- [AI DIAL Platform](https://docs.dialx.ai/) - Core platform documentation
- [SDMX Standards](https://sdmx.org/) - Official SDMX documentation
- [sdmx1 Library](https://github.com/khaeru/sdmx) - Python SDMX library used by StatGPT

## 📊 Visual Resources

### Architecture Diagrams

- [`agent_high_level.svg`](./content/agent_high_level.svg) - High-level agent architecture
- [`architecture_high_level.svg`](content/architecture_high_level.svg) - High-level services architecture
- [`architecture_detailed.svg`](./content/architecture_detailed.svg) - Detailed architecture diagram
- [`dynamic_history_block.svg`](./content/dynamic_history_block.svg) - History management approach
- [`history_example.svg`](./content/history_example.svg) - Example conversation flow

## 🚀 Next Steps

1. **Understanding the System** → Read documents in this order:
    - [Overview](./overview.md) → [Services](./services.md) → [Agent Design](./agent.md) → [Tools](./tools.md)

2. **Integration Planning** → Focus on:
    - [SDMX Compatibility](./sdmx-compatibility.md) for data requirements
    - [Services](./services.md) for technical dependencies

3. **Implementation** → Refer to:
    - GitHub repositories linked above
    - [Deployment guides](../deployment/) for infrastructure setup

## 📝 Documentation Standards

All architecture documentation follows these principles:

- **Clarity**: Technical accuracy with clear explanations
- **Structure**: Consistent formatting with tables and visual indicators
- **Navigation**: Internal links and cross-references for easy browsing
- **Completeness**: Comprehensive coverage of technical requirements
- **Maintenance**: Regular updates as the platform evolves
