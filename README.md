# StatGPT

**StatGPT** is an AI-driven Talk-To-Your-Data platform that enables users to interact with official statistics data 
using natural language. It leverages large language models to provide most relevant data from statistical databases 
through API and conversational interfaces.

## 🎯 What is StatGPT?

StatGPT bridges the gap between complex statistical databases and everyday users. It specializes in:
- Natural language querying of official statistics
- SDMX-native data processing
- Multi-source indicator discovery
- Automated data visualization
- Hallucination prevention through data grounding

## 📚 Documentation

### [Architecture & Design](./architecture/README.md)

**Highlights:**
- [Services Overview](./architecture/services.md) - Core services and dependencies
- [Architecture Overview](./architecture/overview.md) - Solution overview and core requirements
- [SDMX Compatibility](./architecture/sdmx-compatibility.md) - SDMX integration details

### Guides
- [Admin Guide](./guides/admin-guide.md) - System administration and configuration
- [GTDC Portal Guide](./guides/gtdc-portal-guide.md) - Instructions for using the GTDC (Global Trusted Data Commons) Portal.

### Development
- [Contributing](./CONTRIBUTING.md) - Contribution guidelines
- [Security Policy](./SECURITY.md) - Security and vulnerability reporting
- [Data Query Evaluation](./evaluation/data_query.md) - Evaluation methodology for SDMX data queries

## 🚀 Deployment & Source Code

### Deployment

- [StatGPT Helm Chart](https://github.com/epam/statgpt-helm) - Helm chart for deploying StatGPT on Kubernetes.
- [Generic Installation](https://github.com/epam/statgpt-helm/tree/main/charts/statgpt/examples/generic)
- [Azure Installation](https://github.com/epam/statgpt-helm/tree/main/charts/statgpt/examples/azure)

### Source Repositories

- [StatGPT Backend](https://github.com/epam/statgpt-backend) - Admin and Chat backend applications. Main logic and API.
- [StatGPT Admin Frontend](https://github.com/epam/statgpt-admin-frontend) - Admin frontend application. UI for 
  managing StatGPT configurations.
- [StatGPT Portal Frontend](https://github.com/epam/statgpt-portal-frontend) - UI Library for building custom StatGPT 
  Portal applications.
- [StatGPT Global Trusted Data Commons](https://github.com/epam/statgpt-global-trusted-data-commons) - implementation 
  of StatGPT Portal for Global Trusted Data Commons initiative.

## 🔗 AI DIAL Platform

StatGPT is built on [AI DIAL](https://dialx.ai) - an enterprise AI platform providing:
- LLM model management
- Access control and security
- Rate limiting and monitoring
- [Documentation](https://docs.dialx.ai/)

## 📧 Support

- **Issues**: Use GitHub Issues in respective repositories
- **Business**: SupportEPM-DIALStatGPT@epam.com
