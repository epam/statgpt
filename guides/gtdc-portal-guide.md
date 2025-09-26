# GTDC Portal User Guide

## Overview

The GTDC Portal is an intelligent agent specializing in statistics, economics, and the SDMX standard.

## Table of Contents

- [Getting Started](#getting-started)
- [Interface Components](#interface-components)
    - [Block 1: Start New Chat](#block-1-start-new-chat)
    - [Block 2: Search](#block-2-search)
    - [Block 3: Dialogue List/History](#block-3-dialogue-listhistory)
    - [Block 4: Question Input](#block-4-question-input)
    - [Block 5: Suggested Questions](#block-5-suggested-questions)
    - [Additional Interface Features](#additional-interface-features)
- [Using the Portal](#using-the-portal)
    - [Example Queries](#example-queries)
    - [Page Elements](#page-elements)
- [Advanced View](#advanced-view)

## Getting Started

Access the portal at: <https://portal-stg.statgpt.org/>

### Hero Section

![](./content/gtdc-portal-guide/image1.png)

## Interface Components

The first screen contains five main blocks:

1. **Start New Chat** - Button to initiate a new conversation (typically located in the top section)
2. **Search** - Field for navigating through dialogues or documents
3. **Dialogue List/History** - List of previous conversations ordered by date, allowing you to reopen and continue past
   dialogues
4. **Question Input** - Main input field where you enter your request or question
5. **Suggested Questions** - Predefined example queries to help you quickly start a dialogue or learn how to formulate
   requests

![](./content/gtdc-portal-guide/image2.png)

## Detailed Component Descriptions

### Block 1: Start New Chat

To create a conversation, click the **+ New Chat** button.

![](./content/gtdc-portal-guide/image3.png)

### Block 2: Search

Search by title, tags, or author to locate anything from your previous dialogues. After selecting the desired item, you
will be redirected to the corresponding dialogue.

![](./content/gtdc-portal-guide/image4.png)

### Block 3: Dialogue List/History

Displays recent conversations with the assistant, including the last update date and a short preview of the latest
message.

![](./content/gtdc-portal-guide/image5.png)

**Conversation Actions** (click the three dots next to the dialogue):

- Open
- Share
- Export (JSON)
- Delete

![](./content/gtdc-portal-guide/image6.png)

### Block 4: Question Input

Formulate your requests clearly and specifically. Specify the indicator of interest, the country (or group of
countries), the time period, and other relevant details.

![](./content/gtdc-portal-guide/image7.png)

### Block 5: Suggested Questions

Predefined questions and topics that the AI suggests for exploration.

![](./content/gtdc-portal-guide/image8.png)

### Additional Interface Features

You can collapse and restore the sidebar for a cleaner interface.

![](./content/gtdc-portal-guide/image9.png)

![](./content/gtdc-portal-guide/image10.png)

## Using the Portal

### Example Queries

- "What is 'inflation'?"
- "Show the unemployment rate in the US over the last 5 years."

By asking "What is 'inflation'?", you receive a detailed definition and explanation of the term, including its meaning,
use in economics, and different types of measurement.

![](./content/gtdc-portal-guide/image11.png)

**Practical Example:**

**Query:** "Show the unemployment rate in the US over the last 5 years."

**Result:** The system returns a dataset with unemployment rates for the specified period, along with the source
reference.

![](./content/gtdc-portal-guide/image12.png)

### Page Elements

**Share**

Provides options to share the retrieved data or visualization (e.g., via link, QR code).

**View Processing Steps**

Displays the sequence of operations applied to the data (e.g., filtering, aggregation, formatting). Helps track how the
final result was generated.

**Source**

Indicates the origin of the dataset or definition (e.g., IMF, World Bank, OECD). Used for data verification and
reliability.

**World Economic Outlook (WEO)**

Specific source reference — the IMF's World Economic Outlook database. Provides official macroeconomic statistics.

**URL**

Clickable link to the original dataset or documentation page. Allows direct access to the source system.

**Data**

The numerical/statistical information returned by the query. Usually displayed in tabular format for clarity.

**Chart**

A graphical representation of the retrieved data (line chart, bar chart, etc.) for easier interpretation.

**Advanced View**

An extended mode for interacting with the dataset. May include additional filters, export options, or alternative
visualizations.

**Download**

Allows you to save the retrieved data or visualization locally.

![](./content/gtdc-portal-guide/image13.png)

![](./content/gtdc-portal-guide/image14.png)

**Share**

Provides options to share the retrieved data or visualization (e.g., via link, QR code).

![](./content/gtdc-portal-guide/image15.png)

**Data**

Displays the indicators according to the selected criteria.

![](./content/gtdc-portal-guide/image14.png)

**Chart**

Displays the selected indicators on a time scale, providing a visual representation of data dynamics over the chosen
period.

![](./content/gtdc-portal-guide/image16.png)

**Download**

Allows you to save the retrieved data or visualization locally.

When clicking the Download button, you can choose:

- **Data in table** - Only the currently displayed table data
- **Full dataset** - The complete dataset from the source

![](./content/gtdc-portal-guide/image17.png)

![](./content/gtdc-portal-guide/image18.png)

**Data Format Options:**

- SDMX-JSON
- SDMX-ML (XML)
- SDMX-CSV

![](./content/gtdc-portal-guide/image19.png)

**Attribute Options:**

- **ID** - File will include only the ID column
- **ID and Name** - File will include ID and NAME in separate columns
- **Combined ID and Name** - File will include one column with ID and NAME combined as ID:Name

![](./content/gtdc-portal-guide/image20.png)

**Metadata:**

- Toggle option to include or exclude metadata in the file

![](./content/gtdc-portal-guide/image21.png)

## Advanced View

In Advanced View, you can:

- View dataset information, including the last update date
- Share or download the data
- Apply filters directly to the dataset

![](./content/gtdc-portal-guide/image22.png)

Example filters:

- **Country** - United States
- **Indicator** - Unemployment rate
- **Time period** - Jan 1, 2020 - Dec 31, 2025

These filters can be modified as needed.

![](./content/gtdc-portal-guide/image23.png)

To change the country:

1. Click on the country parameter
2. Select one or multiple options by checking the boxes
3. Use the search field to find specific countries

![](./content/gtdc-portal-guide/image24.png)

You can also change or add indicators of interest.

![](./content/gtdc-portal-guide/image25.png)

You can select the frequency. Only options available for the current selection will be displayed (e.g., Annual).

![](./content/gtdc-portal-guide/image26.png)

Time Period options:

- All years
- 5 years
- 10 years
- 20 years
- Custom period - specify the exact time range

![](./content/gtdc-portal-guide/image27.png)

After adjusting filters, you can:

- Click **Apply** to apply the changes
- Clear all filters
- Cancel the actions

![](./content/gtdc-portal-guide/image28.png)

The result will be an updated dataset with your modified filters applied.

![](./content/gtdc-portal-guide/image29.png)

### Example: Multiple Dataset Options

**Query:** "Give me the data on Japan's government debt for 2023."

When multiple datasets are available, the agent will ask for clarification:

**Agent Response:**
"There are two relevant datasets available for Japan's government debt in 2023:

- Government debt as a percent of GDP and in domestic currency (WEO)
- Detailed portfolio investment in government debt securities (BOP)

Please specify your preference. If unsure, the World Economic Outlook (WEO) dataset is recommended for a general
overview."

**User Selection:** "Detailed portfolio investment in government debt securities (BOP)"

**Agent Follow-up:**
"To provide detailed data on Japan's portfolio investment in government debt securities for 2023, please specify the
counterpart country or countries (where Japan holds these investment positions). For example: United States, Germany,
China, or all available countries."

![](./content/gtdc-portal-guide/image30.png)

You can then specify countries to refine your query.

![](./content/gtdc-portal-guide/image31.png)

![](./content/gtdc-portal-guide/image32.png)

![](./content/gtdc-portal-guide/image33.png)

### Working with Advanced View Filters

![](./content/gtdc-portal-guide/image34.png)

![](./content/gtdc-portal-guide/image35.png)

![](./content/gtdc-portal-guide/image36.png)

![](./content/gtdc-portal-guide/image37.png)
