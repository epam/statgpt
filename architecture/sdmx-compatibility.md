# SDMX Compatibility & Requirements

This document outlines the SDMX compatibility requirements and metadata standards necessary for StatGPT to function
effectively with statistical data sources.

> **📝 Note**: StatGPT relies on the [sdmx1 library](https://github.com/khaeru/sdmx) for SDMX requests, therefore the
> requirements are dictated by what is supported in that library.

## 📊 SDMX Technical Requirements

### Version Support

| Version      | Support Level         | Notes                                            |
|--------------|-----------------------|--------------------------------------------------|
| **SDMX 2.1** | ✅ Full Support        | Complete functionality via sdmx1 library         |
| **SDMX 3.0** | ⚠️ Restricted Support | Limited compatibility dependent on sdmx1 library |

### Format Requirements

- **Structure Endpoints**: SDMX-ML only (SDMX-JSON not supported)
- **Data Endpoints**: SDMX-ML or SDMX-JSON

### Required API Endpoints

#### Structure Endpoints

- ✅ Code Lists
- ✅ Concept Schemes
- ✅ Data Structure Definitions (DSDs)
- ✅ Dataflows

#### Data Endpoints

- ✅ Available Constraint endpoint
- ✅ Data endpoint

## 📐 Supported Data Models

StatGPT is an indicator-search-based system and supports only the **conventional
(multi-indicator dataflow)** data model. Providers whose indicator is encoded by *which
dataflow (or table)* you pick — the **shared DSD** (e.g. OECD) and **indicator-per-dataflow /
dedicated-DSD-per-dataset** (e.g. Eurostat, ISTAT, ABS, ILO) models — are **not supported yet**.

The three data models, their example providers, and why StatGPT supports one of them are
described in a dedicated document:

➡️ **[SDMX Data Models & StatGPT Support](./sdmx-data-models.md)**

## 🌐 Connectivity Requirements

### API Availability

- **Access**: Public API availability required
- **Authentication**: No authentication or service-to-service auth supported (e.g., client credentials, basic auth, API
  key)
- **Rate Limits**: Ability to increase limits for StatGPT if they exist

### Performance Requirements

| Endpoint Type            | Request Scenario                      | Max Latency |
|--------------------------|---------------------------------------|-------------|
| **Structure**            | Single structure (no reference stubs) | < 1 sec     |
| **Data**                 | 20 series                             | < 1 sec     |
| **Available Constraint** | 300 series                            | < 1 sec     |

## 📋 Structural Metadata Requirements

### General Requirements

All structural metadata must adhere to these standards:

1. **Localization**
    - ✅ English localizations required (minimum)
    - ✅ Additional localizations must be consistent across all structures

2. **Clarity & Precision**
    - ✅ Unambiguous, clear, and descriptive metadata
    - ✅ Context and meaning must be easily interpretable by LLM
    - ✅ Include agency ID, names, and descriptions for all artifacts

3. **Versioning**
    - ✅ Follow SDMX versioning conventions (2.1 or 3.0)
    - ✅ Ensure clarity on updates and changes

### Structure-Specific Requirements

#### 📊 Data Structure Definitions (DSDs)

**Purpose**: Define dataset structure including dimensions, attributes, and measures.

**Requirements**:

- ✅ Well-defined following SDMX best practices
- ✅ Clear component definitions with descriptive IDs
- ✅ Consistent naming conventions
- ✅ All components must have either:
    - Local representation, OR
    - Reference to a concept with specific type defined

**Component Clarity**:

- Dimensions, attributes, and measures must have IDs that clearly indicate their purpose
- Names and descriptions should be self-explanatory for LLM interpretation

#### 🏷️ Concept Schemes

**Purpose**: Define concepts used in datasets with their relationships and meanings.

**Requirements**:

- ✅ Well-defined following SDMX best practices
- ✅ Meaningful IDs, names, and descriptions
- ✅ Clear indication of concept purpose and business meaning
- ⭕ Optional: Annotations for additional context

#### 📝 Code Lists

**Purpose**: Essential for indexing series and providing business meaning to queries.

**Requirements**:

| Requirement                  | Description                                                  | Priority |
|------------------------------|--------------------------------------------------------------|----------|
| **Unique Names**             | Avoid duplicate names to prevent ambiguity                   | Critical |
| **Clear IDs**                | Meaningful identifiers for each code item                    | Critical |
| **Descriptions**             | Business-meaningful descriptions                             | Critical |
| **Hierarchical Consistency** | If hierarchical, must be well-defined with no contradictions | Required |
| **Annotations**              | Additional context when needed                               | Optional |

**Best Practices**:

- ⚠️ **Avoid duplicate names** - Ambiguity makes it difficult to determine which code list item is meant in queries
- ✅ Use descriptive names that clearly indicate the item's purpose
- ✅ Maintain consistency in naming patterns across related code lists

#### 📁 Dataflows

**Purpose**: Provide context about available datasets and enable dataset selection.

**Utilized Metadata**:

- Agency ID
- Dataflow ID
- Name & Description
- Version
- Annotations (when available)

**Requirements**:

- ✅ Meaningful and descriptive agency, ID, name, and description
- ✅ Clear indication of dataflow purpose
- ✅ Semantic versioning for clarity on updates
- ⭕ Optional: Annotations for last update date or other relevant context

## 🔍 Metadata Quality Checklist

Use this checklist to ensure your SDMX metadata meets StatGPT requirements:

### Essential Requirements

- [ ] All metadata has English localization
- [ ] No ambiguous or duplicate names in code lists
- [ ] DSDs have clear component definitions
- [ ] Concept schemes have meaningful descriptions
- [ ] Dataflows clearly indicate their purpose
- [ ] Version numbering follows SDMX conventions

### Performance Requirements

- [ ] Structure endpoints respond in < 1 second
- [ ] Data endpoints handle 20 series in < 1 second
- [ ] Available constraint handles 300 series in < 1 second

### Connectivity Requirements

- [ ] Public API availability
- [ ] No authentication required OR service credentials available
- [ ] Rate limits adequate or increasable

## 📚 Additional Resources

- [SDMX Official Documentation](https://sdmx.org/)
- [sdmx1 Library Documentation](https://github.com/khaeru/sdmx)

## ⚠️ Common Issues to Avoid

1. **Duplicate Code List Names**: Creates ambiguity in natural language queries
2. **Missing English Localizations**: Prevents proper LLM understanding
3. **Inconsistent Hierarchies**: Causes logical contradictions in data interpretation
4. **Vague Component IDs**: Makes it difficult for LLM to understand data structure
5. **Missing Concept Definitions**: Reduces context understanding
6. **Slow API Response Times**: Degrades user experience
7. **Authentication Complexity**: Currently not supported by StatGPT
8. **Unsupported Data Model**: Only the conventional multi-indicator dataflow model is supported — see [Supported Data Models](#-supported-data-models) and [SDMX Data Models & StatGPT Support](./sdmx-data-models.md)

## 💡 Recommendations for Data Providers

1. **Invest in Metadata Quality**: Clear, descriptive metadata improves StatGPT's ability to answer queries accurately
2. **Use Annotations**: Provide additional context where standard fields are insufficient
3. **Maintain Consistency**: Use the same terminology and patterns across all structures
4. **Test Performance**: Ensure your endpoints meet the latency requirements
5. **Document Special Cases**: If your implementation has unique features, document them clearly
