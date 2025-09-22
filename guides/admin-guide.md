# Administrator Guide

This document covers StatGPT Admin Frontend, it's features and StatGPT Configurations.

## Administrator App

StatGPT Admin is an application that focuses solely on managing StatGPT configurations, including data sources,
datasets and channels. The application does not cover user management, authentication, authorization, monitoring or
cost control, which are handled by DIAL platform.

## Concepts

In StatGPT we have several key concepts that will be used throughout the document:

1. Data Source - a source of data that can be queried using SDMX protocol. Examples of data sources are IMF, Eurostat,
   World Bank, etc.
2. Dataset - a dataset is a direct representation of SDMX dataflow in datasource, with addition of StatGPT-specific
   configurations.
3. Channel - a channel is a representation of StatGPT application for the end users. Each channel has its own
   configuration,
   datasets and index. Having multiple channels allows to experiment with different LLM/index/datasets configurations.
   Each channel is represented by a separate DIAL Application.

## Add Data Source

To add a new data source:

1. Navigate to the "Data Sources" tab and click on the "Add" button
   ![DataSource List](./content/datasource-list.png)
2. Fill in the required fields in the form, including selecting datasource type:
   ![Add Data Source](./content/datasource-type.png)
3. Fill the configuration fields for the selected datasource type and save the datasource:
   ![Add Data Source Config](./content/datasource-config.png)

Configuration for IMF SDMX 2.1 datasource with English locale is as follows:

```yaml
locale: en  # Locale for the datasource, e.g., 'en' for English. Used for indexing and querying.
sdmxConfig:
  id: IMF_SDMX21  # Unique identifier for the datasource
  url: https://api.imf.org/external/sdmx/2.1  # IMF SDMX 2.1 REST API endpoint
  name: Public IMF SDMX 21 Registry  # Human-readable name for the datasource
  headers: # HTTP headers for specific structures and data requests
    data:
      accept: Text/JSON
    codelist:
      accept: application/xml
    dataflow:
      accept: application/xml
    agencyscheme:
      accept: application/xml
    conceptscheme:
      accept: application/xml
    datastructure:
      accept: application/xml
    categoryscheme:
      accept: application/xml
    provisionagreement:
      accept: application/xml
    availableconstraint:
      accept: application/xml
    hierarchicalcodelist:
      accept: application/xml
  supports: # Supported SDMX features
    data: true
    preview: true
    codelist: true
    dataflow: true
    agencyscheme: true
    conceptscheme: true
    datastructure: true
    categoryscheme: true
    provisionagreement: true
    availableconstraint: true
    hierarchicalcodelist: true
  data_content_type: JSON
authEnabled: false  # Whether authentication is required to access the datasource
description: ""  # Optional description of the datasource
annotationsUrl: https://api.imf.org/external/sdmx/3.0  # Optional URL for annotations
```

## Datasets

To add a new dataset from already configured datasource:

1. Navigate to the "Datasets" tab and click on the "Add" button
2. Select the datasource from the table and click "Next":
   ![Select Datasource](./content/dataset-datasource.png)
3. You will be provided with the table of datasets available in the selected datasource. Select the dataset from the
   table and click "Next":
   ![Select Dataset](./content/dataset-select.png)
4. Fill in the required fields in the form and save the dataset:
   ![Add Dataset](./content/dataset-config.png)

Configuration for IMF WEO dataset is as follows:

```yaml
urn: IMF.RES:WEO(6.0.0)  # SDMX urn of the dataset
citation: # citation for the dataset
  url: https://data.imf.org/en/datasets/IMF.RES:WEO  # URL to the dataset web page
  provider: IMF.RES  # data provider
  description: &weo_description >  # detailed description of the dataset
    The World Economic Outlook (WEO) database contains selected macroeconomic
    data series from the statistical appendix of the World Economic Outlook
    report, which presents the IMF staff's analysis and projections of economic
    developments at the global level, in major country groups and in many
    individual countries. The WEO is released in April and September/October
    each year. Use this database to find data on national accounts, gross
    domestic product (GDP), inflation, unemployment rates, balance of payments,
    fiscal indicators, trade for countries and country groups (aggregates), and
    commodity prices whose data are reported by the IMF. Data are available from
    1980 to the present, and projections are given for the next two years.
    Additionally, medium-term projections are available for selected indicators.
    For some countries, data are incomplete or unavailable for certain years.
isOfficial: false  # whether the dataset is from an official source (usually country-level sources are considered official and prioritized in answers for specific country queries)
pinnedColumns: # list of columns to pin in the dataset table
  - FREQUENCY_Name
  - COUNTRY_Name
  - INDICATOR_Name
useTitleFromSrc: true  # whether to use the title from the source Dataflow
countryDimension: COUNTRY  # dimension representing the country or region
includeAttributes: # list of attributes to include in the AI Agent context
  - SCALE
  - UNIT
  - PUBLISHER
  - SOURCE
indicatorDimensions: # list of the dimensions representing the dataset indicators
  - INDICATOR
updatedAtAnnotation: lastUpdatedAt  # SDMX annotation to use for the "last updated at" information
countryDimensionAlias: Country/Reference area  # alias for the country dimension (dimensions can be named differently in different datasets, therefore alias helps to unify the naming for indexing and querying)
dimensionDefaultQueries:
  TIME_PERIOD:
    - values:
        - "2020"
        - "2025"
      operator: between
indicatorDimensionsRequiredForQuery: # indicator dimension that required to be filled for querying the dataset
  - INDICATOR

indexer: # indexer configuration for the dataset
  indicator:
    unpack: true  # whether to unpack the indicator dimensions (e.g. in WEO packed indicators are used, therefore unpack=true)
    use_code_list_description: false  # whether to use code list description for indexing
  description: *weo_description  # description to use for indexing
```

## Channels

To add a new channel:

1. Navigate to the "Channels" tab and click on the "Add" button
2. Fill in the required fields in the form and save the channel:
   ![Add Channel](./content/channel-create.png)
3. Add channel configurations as described in the next section:
   ![Channel Configurations](./content/channel-config.png)
4. Once the channel is created you will be redirected to the channel details page. Here you can add datasets to the
   channel:
   ![Add Dataset to Channel](./content/channel-add-dataset.png)

Configuration for Global Data channel is as follows:

```yaml
conversationStarters: # predefined conversation starters to show in the chat interface
  introText: What would you like to learn about?
  buttons:
    - title: Check available data
      text: What datasets are available?
    - title: Annual US investment in Mexico
      text: What was the annual total investment of the US economy in the Mexican
        economy?
    - title: What is inflation?
      text: What is inflation and how it's used in economy and statistics?
namedEntityTypes: # list of named entity types to recognize in user queries. Used for non-indicator dimensions recognition. Set of named entity types depends on the datasets composition in the channel.
  - Time frequency
  - Counterpart area/country
  - Currency/Unit of measure
countryNamedEntityType: Country/Reference area   # named entity type representing countries/regions
supremeAgent: # main agent configuration
  name: StatGPT  # agent name to be used in the agent context
  domain: Statistics, economics and SDMX.  # agent domain to be used in the agent context
  terminologyDomain: economics, statistics and SDMX  # domain for the terminology to be used in the agent context
  languageInstructions: # additional language instructions for the agent
    - Use more formal/business tone, but be friendly, polite and helpful.
    - Avoid using exclamation marks, emojis, or slang.
  maxAgentIterations: 5  # maximum number of agent iterations (tool calls) per user query
  llmModelConfig:
    apiVersion: 2024-08-01-preview  # LLM API version
    deployment: gpt-4.1-2025-04-14  # LLM deployment name
    temperature: 0  # LLM temperature
    seed: 820288  # LLM seed for reproducibility
outOfScope: # configurations of the out-of-scope filter of the agent
  domain: Statistics, economics and SDMX.  # domain to be used in the out-of-scope filter context
  customInstructions: null  # additional custom instructions for the out-of-scope filter
tokenUsage: # token usage tracking configuration
  debugOnly: false  # whether to track token usage only in debug mode
  stageName: Token Usage  # name of the DIAL stage to log token usage
availableDatasets: # configurations for the Available_Datasets tool
  type: AVAILABLE_DATASETS
  name: Available_Datasets
  description: >-  # Extensive description of the tool and its usage instructions, will be provided to the agent's context
    Provides a list of all available datasets onboarded to the `Query_Data` tool
    with metadata and some details about them. Details include the name and
    description of the dataset, the provider (agency), and the last update date.

    This tool does not accept any arguments.

    For questions about the availability of indicators you should refer to the
    `Query_Data` tool.
  details:
    fakeCall: # fake tool call to put the tool call along with tool response in the agent's context by default
      toolCallId: call_EBJJeaOMKeCzm8h378ubURQN
      args: "{}"
    stagesConfig:
      debugOnly: true
      rules: [ ]
    version: full
dataQuery: # Data Query tool configuration
  type: DATA_QUERY
  name: Query_Data
  description: >-
    Executing sdmx query on available datasets. Some datasets include forecasts
    for next years.

    Constructed query is used to fetch indicators from one of the datasets.

    Instructions:

    * Don't try to expand country groups or regions, it's done by tool itself

    * Summarize but DON'T REPHRASE time filter: "from now to 2030" must remain
    "from now to 2030"

    * Tool works best for single indicator query (e.g. GDP, inflation)

    * Tool supports star-queries for countries, e.g. "Give GDP for all
    countries"

    * Tool may ask clarifications if query is unclear. If query is modified
    accordingly, tool will provide
      requested data.
    * Good query example: "Please give me wage information of USA"

    * Bad query example: "What are the recent economy indicators for Baltic
    countries?"
      Reason: ambiguous query, specific indicators should be mentioned, e.g. GDP, unemployment rate

    Keep in mind: tool works best when detailed and concise query is provided
  details:
    stagesConfig: # configurations of the different stages of the tool execution to be shown to user
      debugOnly: true
      rules:
        - pattern: Constructing Data Queries
          debugOnly: false
        - pattern: Extracting Named Entities
          debugOnly: false
        - pattern: Executing Data Queries
          debugOnly: false
        - pattern: Normalizing Query
          debugOnly: false
        - pattern: Selecting Indicators
          debugOnly: false
    version: v2  # version of the tool
    indexerVersion: hybrid  # version of the indexer used for the tool
    indicatorSelectionVersion: hybrid  # version of the indicator selection algorithm used for the tool
    llmModels: # Configurations of the LLM models used in different stages of the tool execution
      datasetsSelectionModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      dimensionsSelectionModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      indicatorsSelectionModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      incompleteQueriesModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      groupExpanderModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      namedEntitiesModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      timePeriodModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
      queryNormalizationModelConfig:
        apiVersion: 2024-08-01-preview
        deployment: gpt-4.1-2025-04-14
        temperature: 0
        seed: 820288
    messages: # predefined messages to be used in different situations during the tool execution
      noDataForCountry: No data was found for {country_details}. Try to change the query.
      noData: No data was found for the provided query. Try to change the query.
      dataQueryExecutedAgentOnly: >-
        If the executed query is only remotely related to the user query, you
        must mention that fact to the user,

        to not mislead them. It is recommended to search in other sources using
        tools available.

        Result of the executed query is shown to the user in the table
        attachment.
      multipleDatasetsAgentOnly: >-
        If the executed query is only remotely related to the user query, it is
        recommended to mention that fact to

        the user, instead of suggesting user to choose one of the datasets.
        Other tools might be used to search for

        the data.
    attachments: # configurations of the attachments to be provided to user along with the tool response
      customTable:
        enabledStr: "True"
        name: "Data: {dataset_source_id}"
      plotlyGrid:
        enabledStr: $env:{DIAL_SHOW_PLOTLY_GRID|False}
        name: "Plotly Grid: {dataset_source_id}"
      csvFile:
        enabledStr: "True"
        name: "Data (CSV): {dataset_source_id}.csv"
      plotlyGraphs:
        enabledStr: "True"
        name: "Graph: {figure_title}"
      jsonQuery:
        enabledStr: "True"
        name: "Query (JSON): {dataset_source_id}"
      pythonCode:
        enabledStr: "True"
        name: "Python Code: {dataset_source_id}"
availableTerms: # configurations for the Available_Terms tool
  type: AVAILABLE_TERMS
  name: Available_Terms
  description: >-  # Extensive description of the tool and its usage instructions, will be provided to the agent's context
    Use this tool to:

    * Retrieve a comprehensive list of all terms currently available in the
    glossary.

    * Confirm whether a specific term exists in the glossary.


    Detailed Guidance:

    * The list of available glossary terms provided by this tool is complete;
    there are no additional terms beyond
      what is returned.
    * Whenever referring to or explaining to user any glossary terms you must
    obtain the definitions of any listed
      terms using the "Term_Definitions" tool.
  details:
    fakeCall: # fake tool call to put the tool call along with tool response in the agent's context by default
      toolCallId: call_EBJJeaOMKeCzm8h378ubU003
      args: "{}"
    includeDomain: false
    includeSource: false
termDefinitions: # configurations for the Term_Definitions tool
  type: TERM_DEFINITIONS
  name: Term_Definitions
  description: >-  # Extensive description of the tool and its usage instructions, will be provided to the agent's context
    Use this tool to:

    * Retrieve definitions for up to 10 requested terms that appear in the
    glossary.

    * Consult the "Available_Terms" tool if you are unsure which terms are in
    the glossary.


    Detailed Guidance:

    * Confirm availability of terms using the "Available_Terms" tool first.
  details:
    stagesConfig:
      toolCallName: Glossary search result
      debugOnly: true
      rules: [ ]
    limit: 10
```

