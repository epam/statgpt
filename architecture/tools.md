# StatGPT Tools Documentation

This document describes the tools available to the StatGPT agent for interacting with data sources, publications, and
other resources. Each tool is designed to handle specific types of queries and return structured information.

## 📚 Tool Categories

The StatGPT agent leverages the following tool categories:

### 1. 📊 Data Tools

Tools for querying structured SDMX datasets

- **Available Datasets** - List available datasets with metadata
- **Data Query** - Build and execute SDMX queries

### 2. 📄 Publications Tools

Tools for querying unstructured publication data

- **Available Publications** - List publication types with metadata
- **Publications RAG** - Query publications using Retrieval Augmented Generation

### 3. 📖 Glossary Tools

Tools for accessing terminology and definitions

- **Glossary Terms** - Query available terms with metadata (excluding definitions)
- **Glossary Definitions** - Retrieve definitions for specific terms

### 4. 🌐 Web Tools

Tools for web-based information retrieval

- **Web Search** - Search and retrieve web content using RAG approach

### 5. 🔧 Other Tools

Utility tools for various purposes

- **Plain Content** - Retrieve file content with environment variable substitution

## 📊 Data Tools

**Purpose**: Enable users to query structured SDMX datasets and receive data in formats like tables and charts.

### Available Datasets

**Function**: Retrieves the list of available datasets with their metadata.

**Metadata Fields**:

| Field            | Description         | Source                                  |
|------------------|---------------------|-----------------------------------------|
| **Name**         | Dataset name        | SDMX dataflow or admin configuration    |
| **Description**  | Dataset description | SDMX dataflow or admin configuration    |
| **Provider**     | Data provider       | SDMX dataflow or admin configuration    |
| **URN**          | Unique identifier   | SDMX dataflow                           |
| **Last Updated** | Update timestamp    | SDMX annotations or admin configuration |
| **URL**          | Portal page link    | Admin configuration                     |

**Output Format**: Markdown list  
**Access Control**: Availability query determines user access

### Data Query

**Function**: Builds and executes SDMX queries from natural language input.

**Input**: Natural language query

**Processing Pipeline**:

- Query normalization
- Country groups processing
- Time period extraction
- Named entity recognition
- Keyword search
- Semantic search
- Availability queries
- Query execution

**Possible Outcomes**:

#### ✅ Success - Query Built and Executed

Returns:

- SDMX query structure
- Data in tabular format
- Query URL
- Time series charts (when applicable)
- Python code samples for data retrieval

#### ⚠️ Clarification Needed

- Query partially built
- Prompts user for additional information

#### ❌ Data Unavailable

- Notifies user that requested data cannot be found

**Output Handling**:

- CSV data accessible in agent context
- Attachments (tables, charts) displayed to user

## 📄 Publications Tools

**Purpose**: Query unstructured publication data and return information as structured natural language responses.

### Available Publications

**Function**: Retrieves available publication types with metadata.

**Metadata Fields**:

- **Name** - Publication type identifier
- **Description** - Detailed explanation of content and information scope

**Output Format**: Markdown list

### Publications RAG

**Function**: Queries publications using Retrieval Augmented Generation.

**Input**: Natural language query  
**Architecture**: Connects to external RAG application

**Processing Stages**:

1. **Pre-filtering**
    - Publication types
    - Time periods

2. **Document Retrieval**
    - Keyword search
    - Semantic search
    - Multimodal semantic search
    - Page description search

3. **Response Generation**
    - Synthesizes information from retrieved chunks

**Possible Outcomes**:

#### ✅ Information Found

- Natural language response
- Citations to source documents

#### ❌ No Relevant Information

- User notification of unsuccessful search

## 📖 Glossary Tools

**Purpose**: Access standardized terminology and definitions in structured formats.

### Glossary Terms and Definitions

**Configuration**: Admin-managed via CRUD API  
**Storage**: Database with channel-specific glossaries

**Metadata Structure**:

| Field          | Description           | Example                     |
|----------------|-----------------------|-----------------------------|  
| **Term**       | The terminology entry | "GDP"                       |
| **Definition** | Official definition   | "Gross Domestic Product..." |
| **Domain**     | Subject area          | "Economics", "Statistics"   |
| **Source**     | Origin reference      | "SDMX", "IMF"               |

#### Glossary Terms Tool

**Function**: Lists available terms with metadata (excluding definitions)  
**Arguments**: None  
**Output**: Markdown list of terms with metadata

#### Glossary Definitions Tool

**Function**: Retrieves definitions for specified terms  
**Arguments**: Array of glossary terms  
**Output**: Markdown-formatted definitions with metadata

**Use Case**: Enables agencies to standardize terminology for both LLM context and user reference.

## 🌐 Web Tools

**Purpose**: Search and retrieve web-based information in structured natural language format.

### Web Search

**Function**: Web search with RAG-based result processing.

**Arguments**:

1. **Query** - Natural language search query
2. **Domains** - Admin-configured list of allowed web domains

**Processing Pipeline**:

| Stage                 | Action                                   |
|-----------------------|------------------------------------------|
| **1. Search**         | Execute web search via configured engine |
| **2. Download**       | Retrieve identified documents            |
| **3. RAG Processing** | Apply RAG approach to downloaded content |

**Output**: Similar to Publications RAG tool results

## 🔧 Other Tools

**Purpose**: Provide utility functions and specialized capabilities outside main tool categories.

### Plain Content

**Function**: Retrieves file content with dynamic variable substitution.

**Features**:

- Retrieves admin-configured files from DIAL storage
- Replaces environment variables with runtime values
- Provides static content to agent or users

**Example Use Case**: Portal guides with dynamic information about available pages and features.