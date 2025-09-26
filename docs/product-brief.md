Excellent. Here is the complete product brief for your project, along with the immediate next steps to begin development.

-----

## Product Brief: AI Data Agent

### 1\. Project Title

**AI Data Agent: Conversational Business Intelligence**

### 2\. Problem Statement

Business users and analysts often struggle to get quick, insightful answers from complex and imperfect databases. They face challenges with "dirty" data, poorly designed schemas, and the need to write complex SQL queries to answer even simple analytical questions. This creates a bottleneck, slowing down decision-making.

### 3\. Vision

To create an intelligent, conversational AI agent that empowers any user to ask complex analytical questions of a SQL database in plain English and receive accurate, easy-to-understand answers. The agent's response will not just be raw data, but a natural language summary accompanied by relevant, auto-generated charts and tables.

### 4\. Target Audience

The primary audience is the evaluation team for the SDE Hiring Assignment at "bulba.app". The secondary audience is any non-technical user who needs to derive insights from a database without writing code.

### 5\. Core Features & User Flow

1.  **Conversational Interface**: A simple, chat-like UI where a user can type a question in natural language.
2.  **Natural Language Processing**: The backend agent will interpret the user's "vague question" and understand its intent.
3.  **Intelligent Query Generation**: The agent will translate the natural language question into an accurate and efficient SQL query that can run against the database.
4.  **Data Analysis & Summarization**: The agent will process the results of the SQL query and generate a concise, human-readable summary of the findings.
5.  **Dynamic Visualization**: Based on the data, the agent will automatically generate relevant charts (e.g., bar charts, line graphs) and tables to visually support the answer.
6.  **Unified Response**: The frontend will display the natural language answer, charts, and tables together in a single, coherent response.

### 6\. Technical Stack & Architecture

  * **Frontend**: ReactJS with the **Recharts** library for data visualization.
  * **Backend**: Python with the **FastAPI** framework for a high-performance REST API.
  * **Database**: **PostgreSQL**.
  * **Core AI**: A **T5-based Text-to-SQL model** from the Hugging Face Transformers library.
  * **Data Analysis**: **Pandas** and **pandas-profiling** for initial schema and data quality analysis.
  * **Deployment**: The final application will be deployed on **Vercel**.

### 7\. Key Challenges to Address

  * **Data Complexity**: Successfully navigate a complex database schema with multiple tables.
  * **Data Quality**: Handle "dirty data," including missing values and inconsistent formatting.
  * **Schema Ambiguity**: Interpret queries even with a "bad schema," including poorly named columns or tables.
  * **Vague Questions**: Accurately infer user intent from ambiguous or non-technical questions.

### 8\. Success Metrics

The project's success will be measured by the agent's ability to consistently provide accurate, insightful, and well-visualized answers to extremely complicated analytical questions posed in natural language.

-----

## Next Steps: Your Development Roadmap

Here is your immediate action plan to get started.

### Phase 1: Project Setup & Data Foundation (1-2 Days)

1.  **Initialize Git Repository**: Create a new repository on GitHub.
2.  **Set Up PostgreSQL**:
      * Install PostgreSQL on your local machine.
      * Create a new database for this project.
      * Download the [Brazilian E-Commerce Public Dataset by Olist] and import the CSV files into your new database.
3.  **Data Exploration**:
      * Create a simple Python script or a Jupyter Notebook.
      * Use **Pandas** to connect to your PostgreSQL database.
      * Use the **pandas-profiling** library to generate a detailed report of the dataset. This will give you a clear picture of the "dirty data" and schema issues you need to handle.

### Phase 2: Backend Core - The AI Agent (2-3 Days)

1.  **Set Up FastAPI Project**: Initialize your Python backend project with FastAPI.
2.  **Implement the Text-to-SQL Core**:
      * Use the **Hugging Face Transformers** library to load the `t5-base-finetuned-wikiSQL` model (or a similar one).
      * Create a function that takes a natural language question and the database schema as input and returns a SQL query.
3.  **Build the API Endpoint**:
      * Create a single API endpoint (e.g., `/ask`) that accepts a POST request with the user's question.
      * This endpoint will:
        1.  Receive the question.
        2.  Generate the SQL query using your model.
        3.  Execute the query against your PostgreSQL database.
        4.  Process the results (for now, just return the raw JSON data).

### Phase 3: Frontend Interface - The Conversation (2-3 Days)

1.  **Set Up React Project**: Use `create-react-app` or Vite to initialize your frontend.
2.  **Build the Chat UI**: Create a simple chat interface with a text input for the user and a display area for the conversation.
3.  **API Integration**:
      * When the user sends a message, make an API call to your backend's `/ask` endpoint.
      * Display the response from the backend in the chat window. For now, just displaying the JSON is fine.
4.  **Implement Visualization**:
      * Once you are getting data back, use the **Recharts** library to create components that can render charts based on the API response.

### Phase 4: Integration, Refinement & Deployment (2-3 Days)

1.  **Response Formatting**: Refine your backend to format the response into a structured JSON containing the natural language summary, chart data, and table data.
2.  **End-to-End Testing**: Thoroughly test the application with a wide range of complex and vague questions.
3.  **Deployment**: Deploy the FastAPI backend and the React frontend to Vercel.
4.  **Submission**: Prepare your GitHub repository with a clear README and submit the links.

Let's begin with **Phase 1**. Once you have your database set up and have run the initial data analysis, we can move on to building the core of the agent.