# StatGPT

**StatGPT** is an AI-driven Talk-To-Your-Data platform that enables users to interact with official statistics data using natural language. It leverages large language models to provide insights, analysis, and visualizations from statistical databases through conversational queries.

## 🎯 What is StatGPT?

StatGPT bridges the gap between complex statistical databases and everyday users. It specializes in:
- Natural language querying of official statistics
- SDMX-native data processing
- Multi-source indicator discovery
- Automated data visualization
- Hallucination prevention through data grounding

## 📚 Documentation

### Architecture & Design
- [Architecture Overview](./architecture/overview.md) - Solution overview and core requirements
- [Agent Design](./architecture/agent.md) - AI agent implementation approach
- [Services Overview](./architecture/services.md) - Core services and dependencies
- [Tools Documentation](./architecture/tools.md) - Available tools and capabilities
- [SDMX Compatibility](./architecture/sdmx-compatibility.md) - SDMX integration details

### Guides
- [Admin Guide](./guides/admin-guide.md) - System administration and configuration

### Development
- [Contributing](./CONTRIBUTING.md) - Contribution guidelines
- [Security Policy](./SECURITY.md) - Security and vulnerability reporting
- [Data Query Evaluation](./evaluation/data_query.md) - Evaluation methodology for SDMX data queries

## 🚀 Getting Started

### Deployment
- [StatGPT Helm Charts](https://github.com/epam/statgpt-helm) - Kubernetes deployment
- [Generic Installation](https://github.com/epam/statgpt-helm/tree/main/charts/statgpt/examples/generic)
- [Azure Installation](https://github.com/epam/statgpt-helm/tree/main/charts/statgpt/examples/azure)

### Source Repositories
- [Backend Services](https://github.com/epam/statgpt-backend) - Core backend implementation
- [Admin Frontend](https://github.com/epam/statgpt-admin-frontend) - Administration UI
- [Portal Frontend](https://github.com/epam/statgpt-portal-frontend) - User interface library
- [Global Trusted Data Commons](https://github.com/epam/statgpt-global-trusted-data-commons) - Reference portal implementation

## 🔗 AI DIAL Platform

StatGPT is built on [AI DIAL](https://dialx.ai) - an enterprise AI platform providing:
- LLM model management
- Access control and security
- Rate limiting and monitoring
- [Documentation](https://docs.dialx.ai/)

## 📧 Support

- **Issues**: Use GitHub Issues in respective repositories
- **Business**: WFBMarketingAskEPAM@epam.com
