Of course. Here is a comprehensive Product Requirements Document (PRD) tailored for an AI coding assistant like Cursor. It outlines the entire project in a modular, phased approach, providing detailed steps for development.

-----

### **Product Requirements Document: AI Data Agent MVP**

#### **1. Introduction & Vision**

**Product:** AI Data Agent
**Vision:** To build a conversational AI platform that empowers non-technical users to upload raw data files (Excel, CSV) and gain deep insights by asking complex business questions in natural language. The system will provide answers through a combination of textual analysis and relevant data visualizations.

#### **2. The Problem & Target Audience**

**Problem:** Huge amounts of valuable data are locked away in spreadsheets. Business users who are not proficient in SQL, Python, or data analysis tools struggle to extract timely and complex insights. They need a tool that understands their business questions and handles imperfect, real-world data without manual cleaning and coding.

**Target Audience:** Business analysts, marketing managers, operations staff, and any non-technical professional who needs to make data-driven decisions.

#### **3. High-Level Requirements & Epics**

This project is broken down into four main epics:

  * **Epic 1: Data Ingestion & Processing Pipeline:** The system must accept user-uploaded files, process them, and store them in a structured, queryable format.
  * **Epic 2: Core AI Analysis Engine:** The system's brain. It must be able to translate a natural language question into an executable analysis plan, run it against the user's data, and generate a result.
  * **Epic 3: Conversational Frontend Interface:** The user's window into the platform. It must provide a seamless, intuitive chat-based experience for uploading files, asking questions, and viewing results.
  * **Epic 4: Deployment & Integration:** The entire system must be packaged and deployed to a live, accessible environment on Vercel.

-----

### **4. Detailed Phased Development Plan**

Your task is to build the application following these modular phases.

#### **Phase 1: Backend Foundation & Data Pipeline (Epic 1)**

**Goal:** Create a robust backend service that can accept an Excel/CSV file, clean it, and store its contents in a PostgreSQL database.

**Suggested Project Structure (Backend):**

```
/backend
|-- /app
|   |-- /api
|   |   |-- __init__.py
|   |   |-- endpoints.py      # FastAPI routes (e.g., /upload, /query)
|   |-- /core
|   |   |-- __init__.py
|   |   |-- config.py         # Environment variables (DB_URL, HUGGINGFACE_KEY)
|   |-- /services
|   |   |-- __init__.py
|   |   |-- data_processor.py # Logic for cleaning & storing data
|   |   |-- ai_agent.py       # (To be built in Phase 2)
|   |-- /models
|   |   |-- __init__.py
|   |   |-- database.py       # SQLAlchemy setup and session management
|   |-- main.py               # FastAPI app entry point
|-- requirements.txt
|-- Dockerfile
```

**Step-by-Step Implementation:**

1.  **Setup FastAPI Application (`/app/main.py`, `/app/api/endpoints.py`):**

      * Initialize a FastAPI application.
      * Create a `/health` endpoint that returns `{"status": "ok"}`.
      * Create a `/api/v1/upload` endpoint that accepts a file upload (`UploadFile`). This endpoint will be a POST request.

2.  **Implement Database Connection (`/app/models/database.py`):**

      * Use SQLAlchemy to define the database engine and session maker.
      * Connect to your Neon PostgreSQL database using the connection string from your environment variables (use `python-dotenv` for local development).

3.  **Build the Data Processing Service (`/app/services/data_processor.py`):**

      * Create a function `process_and_store_file(file: UploadFile, session_id: str)`.
      * **Ingestion:** Use `pandas.read_excel()` or `pandas.read_csv()` to load the file's contents into a DataFrame. Handle multiple sheets in Excel files by processing them individually or merging them.
      * **Cleaning (Data Resilience):**
          * Sanitize column names (remove special characters, replace spaces with underscores).
          * Infer data types for each column (`pd.to_numeric`, `pd.to_datetime`, etc.).
          * Implement a strategy for handling missing values (e.g., fill with a placeholder like 'NA').
      * **Storage:**
          * Dynamically generate a unique table name for the uploaded data (e.g., `data_{session_id}_{sheet_name}`).
          * Use `DataFrame.to_sql()` with the SQLAlchemy engine to write the cleaned data to the new table in your PostgreSQL database.
          * Return metadata about the stored tables (table names, column names, data types).

4.  **Connect Endpoint to Service (`/app/api/endpoints.py`):**

      * In the `/upload` endpoint, generate a unique session ID.
      * Call the `process_and_store_file` function from the Data Processing Service.
      * Return the session ID and the data schema metadata to the client as a JSON response.

#### **Phase 2: Core AI Analysis Engine (Epic 2)**

**Goal:** Create the service that generates and executes Python code to answer user questions.

**Step-by-Step Implementation (`/app/services/ai_agent.py`):**

1.  **Setup Hugging Face API Client:**

      * Create a function to securely call the Hugging Face Inference API. It should take a `prompt` and return the model's text generation. Store your API key in environment variables.

2.  **Implement the `get_answer(query: str, session_id: str)` function:**

      * **Schema Retrieval:** Query the database to get the table names and schemas associated with the `session_id`.
      * **Prompt Engineering:** Create a `generate_pandas_prompt` function. This is critical. The prompt must include:
          * **Context:** "You are an expert Python data analyst."
          * **Data Schema:** "You are working with the following tables and columns: {schema\_info}."
          * **Task:** "The user's question is: '{query}'."
          * **Instructions:** "Write a single, executable Python script using the pandas library to answer this question. Load the data from the SQL database into a pandas DataFrame. Print only the final result (e.g., a number, a list, or a JSON representation of a DataFrame)."
      * **API Call:** Send the generated prompt to the Hugging Face API (`Mixtral` or `CodeLlama`).
      * **Secure Code Execution:**
          * Receive the Python code as a string from the API.
          * **CRITICAL:** Create a sandboxed environment to execute this code. Use a library like `RestrictedPython` or a carefully configured `exec` scope that only has access to necessary libraries (`pandas`, `sqlalchemy`) and the database connection. **Do not run `exec()` on untrusted code in an open environment.**
          * Capture the `stdout` (the printed result) from the execution.
      * **Result Synthesis:**
          * Take the raw output from the executed code.
          * Create a second prompt: `generate_synthesis_prompt`. This prompt includes the original question and the raw data result. The instruction is: "Given the user's question '{query}' and the resulting data '{data}', formulate a friendly, natural language answer. Also, suggest a suitable chart type ('bar', 'pie', 'line', 'table') for this data."
          * Call the Hugging Face API again with this synthesis prompt.
      * **Return:** Parse the final response and return a JSON object containing the natural language answer and the suggested visualization data.

3.  **Create Endpoint (`/app/api/endpoints.py`):**

      * Create a `/api/v1/query` POST endpoint that accepts a `query` and a `session_id`.
      * Call the `ai_agent.get_answer` function and return its JSON response.

#### **Phase 3: Conversational Frontend Interface (Epic 3)**

**Goal:** Build the React-based user interface.

**Suggested Project Structure (Frontend):**

```
/frontend
|-- /src
|   |-- /components
|   |   |-- ChatWindow.js
|   |   |-- Message.js
|   |   |-- UploadButton.js
|   |   |-- ChartRenderer.js
|   |-- /hooks
|   |   |-- useChat.js        # Logic for managing conversation state
|   |-- App.js
|   |-- index.js
```

**Step-by-Step Implementation:**

1.  **Setup UI:**

      * Create a main layout in `App.js` with a file upload area and a chat interface.
      * Use a UI component library like Material-UI or Ant Design for a modern look.

2.  **File Upload (`/components/UploadButton.js`):**

      * Create a component that allows users to select a file.
      * On file selection, make a `POST` request to the `/api/v1/upload` backend endpoint.
      * On a successful response, store the returned `session_id` in the application's state.

3.  **Chat Interface (`/hooks/useChat.js`, `/components/ChatWindow.js`):**

      * Manage the conversation history in a state hook (e.g., `useState`).
      * When a user sends a message, add it to the history and make a `POST` request to the `/api/v1/query` endpoint, sending the message and the current `session_id`.
      * Display a loading indicator while waiting for the backend response.
      * When the response is received, add the AI's message to the chat history.

4.  **Render Visualizations (`/components/ChartRenderer.js`):**

      * Create a component that takes the visualization data from the AI's response.
      * Use a library like `Recharts` or `Chart.js`.
      * Conditionally render the correct chart type (`bar`, `pie`, etc.) based on the AI's suggestion.

#### **Phase 4: Deployment & Integration (Epic 4)**

**Goal:** Deploy the full-stack application to Vercel.

1.  **Configure Vercel Project:**

      * Create a new Vercel project and link it to your GitHub repository.
      * Configure the project as a monorepo, with separate build commands and output directories for the frontend and backend.
      * Vercel will automatically detect the FastAPI backend and deploy it as serverless functions.

2.  **Environment Variables:**

      * In the Vercel project settings, add your `DATABASE_URL` and `HUGGINGFACE_API_KEY` as environment variables.

3.  **CORS:**

      * In your FastAPI application (`/app/main.py`), configure CORS middleware to allow requests from your Vercel frontend domain.

4.  **Test:**

      * Deploy the application and perform end-to-end testing to ensure the frontend can communicate with the backend and the entire data analysis pipeline works as expected.