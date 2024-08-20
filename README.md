# DocQA Project

The [DocQA project](<repository_url>) aims to enhance information retrieval by providing precise responses along with identifying the source document and specific page for each answer. Integrated with visual content analysis, DocQA improves user experience and decision-making by reducing manual search efforts.

## Table of Contents

1. [Objectives](#objectives)
2. [Setup](#setup)
3. [Data Preparation](#data-preparation)
4. [Execution](#execution)
5. [Architecture Diagram](#architecture-diagram)
6. [Conclusion](#conclusion)
7. [References](#references)

## Objectives

- **Accurate Information Extraction and Storage**: Extract relevant information from various document formats (PDFs, Word documents, text files) and store it in a persistent database.
- **Integrated Visual Content Analysis**: Analyze and interpret visual content within documents for comprehensive answers to user queries.
- **Source Identification**: Identify the origin of extracted information, including document titles and page numbers, ensuring transparency and traceability.
- **Scalability and Adaptability**: Handle large volumes of documents and adapt to different document structures and formats.
- **Real-time Response**: Provide prompt responses to user queries for timely decision-making.

## Setup

1. **Install Dependencies**:
    - Install Python Version 3.10 or above from [Python's official site](https://www.python.org/downloads/).
    - Clone the repository using:
      ```bash
      git clone <repository_url>
      ```
    - Navigate to the project directory:
      ```bash
      cd <project_directory>
      ```
    - Create and activate a virtual environment:
      ```bash
      python -m venv venv
      ```
      - **Linux/Mac/Unix**:
        ```bash
        source venv/bin/activate
        ```
      - **Windows**:
        ```bash
        venv\Scripts\activate
        ```
    - Install required Python packages:
      ```bash
      pip install -r requirements.txt
      ```

2. **Configure Environment Variables**:
    - Create a `.env` file in the project root directory and add your OpenAI API key:
      ```
      OPENAI_API_KEY=<your_openai_api_key>
      ```
      [Get OpenAI API Key](https://platform.openai.com/signup)

## Data Preparation

1. **Organize PDF Documents**:
    - Create a folder named `input_folder` in the root directory of the project and place your PDF documents there.
    - If you prefer a different folder name, update `config.json`:
      - Open `config.json`.
      - Locate the `settings` object.
      - Change the value of the `"input_folder"` key to your preferred folder name.

## Execution

1. **Run the Main Script**:
    - Execute the `main.py` script:
      ```bash
      python main.py
      ```
      This script processes PDFs and populates the database.

2. **Querying the Indexed Documents**:
    - After processing is complete, enter your query to retrieve answers from the indexed documents. Results will be stored in an Excel file named `Question_Responses_Output.xlsx` in a folder named `output_folder`.

3. **Retrieving the Output from Excel**:
    - Navigate to the folder named `output_folder` in the root directory of your project.
    - Search for the Excel file named `Question_Responses_Output.xlsx`.
    - Open this file to view the results of your queries.

## Architecture Diagram

To understand the architecture of the DocQA system, refer to the diagram below:

![Architecture Diagram](Images/RAG_team14_arch_diagram%20(3).jpeg)

## Conclusion

By following these steps, you will set up and execute the DocQA system efficiently, ensuring accurate document analysis and information retrieval.

## References

- **[OpenAI](https://platform.openai.com/docs)**: Provides powerful language models for natural language understanding and generation.
- **[LangChain and ChromaDB](https://python.langchain.com/v0.2/docs/integrations/vectorstores/chroma/)**: A framework for developing applications powered by language models, and ChromaDB, a vector database for embeddings and document search.
- **[pdfplumber](https://github.com/jsvine/pdfplumber)**: A library for extracting text, tables, and metadata from PDF files.


## Authors

- **Addepalli Venkata Parasaran**
- **Pavan Ram Chandar Yendluri**
- **Preetam Preetam**
- **Ritika Singh**
- **R Triambak**


