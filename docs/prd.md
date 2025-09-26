Of course. As the Product Manager for this project, I have synthesized the information from the product brief into a formal Product Requirements Document (PRD). This document will serve as our guiding charter for development.

***

## Product Requirements Document (PRD): AI Data Agent

**Version:** 1.0  
**Date:** September 26, 2025  
**Author:** BMad Agent (Product Manager)  
**Status:** In Review

### 1. Introduction & Vision

This document outlines the requirements for the **AI Data Agent**, an intelligent conversational interface for business intelligence.

The vision is to create an AI agent that empowers any user, regardless of technical skill, to ask complex analytical questions of a SQL database in plain English. The agent will deliver accurate, easy-to-understand answers, not as raw data, but as a synthesized natural language summary accompanied by relevant, auto-generated charts and tables.

### 2. Problem Statement

Business users and analysts often struggle to get quick, insightful answers from complex and imperfect databases. They face significant challenges with "dirty" data, poorly designed schemas, and the technical barrier of writing complex SQL queries. This creates a bottleneck that slows down critical decision-making processes. Our AI Data Agent aims to eliminate this friction.

### 3. Target Audience

* **Primary Audience**: The evaluation team for the SDE Hiring Assignment at "bulba.app".
* **Secondary Audience**: Non-technical business users, analysts, and decision-makers who need to derive insights from data without writing code.

### 4. Features & Functional Requirements

#### 4.1. Core Feature: Conversational BI Agent
The agent is the core of the product. It must be able to process a user's natural language question and return a complete, multi-faceted answer.

* **FR-1: Natural Language Question Input**: The system shall provide a chat-like interface where users can input questions in plain English.
* **FR-2: Vague Question Interpretation**: The backend agent must be able to parse and understand the intent behind "vague questions".
* **FR-3: Intelligent SQL Query Generation**: The agent will translate the user's question into an accurate and efficient SQL query.
* **FR-4: Natural Language Summarization**: The agent will process the raw SQL results and generate a concise, human-readable summary of the key insights.
* **FR-5: Dynamic Visualization Generation**: The agent will automatically select and generate appropriate charts (e.g., bar, line) and/or tables to visually represent the data.
* **FR-6: Unified Response Delivery**: The frontend will render the complete response in a single, coherent view, displaying the natural language summary, charts, and tables together.

#### 4.2. User Stories
* **As a Business Analyst**, I want to ask "Which advisors have the most students failing their courses?" so that I can identify areas for student support.
* **As a Department Head**, I want to ask "What are the most popular courses among students with a GPA below 3.0?" so that I can understand curriculum engagement for at-risk students.
* **As a non-technical user**, I want to receive my answer with a simple chart and a one-sentence summary so that I can quickly understand the key takeaway.

Of course. Switching to a business-focused dataset is a great idea to make the project even more relevant to a real-world scenario.

Based on that, I recommend we use the **Brazilian E-Commerce Public Dataset by Olist**. It's a fantastic, real-world dataset available on Kaggle that perfectly fits our needs.

### **Why the Olist E-commerce Dataset?**
* **Business-Relevant**: It contains a rich collection of real e-commerce transactions, covering everything from order placement and payment to shipping and customer reviews. This allows for very realistic and complex business questions.
* **Complex Schema**: The dataset is spread across **9 different tables**, requiring complex `JOIN`s to answer meaningful questions. This directly addresses the "Very complex database" challenge.
* **Real-World "Dirty" Data**: It contains the kind of data quality issues you'd expect in a real business environment: missing timestamps, varied data formats, and occasional inconsistencies.

---

**5. Technical Stack & Components**
*(No changes to this section)*

* **Frontend**: ReactJS
* **Frontend Visualization Library**: Recharts
* **Backend**: Python with FastAPI
* **Database**: PostgreSQL
* **Core AI Model**: A T5-based Text-to-SQL model from Hugging Face Transformers
* **Data Analysis (Initial Setup)**: Pandas and pandas-profiling
* **Deployment Platform**: Vercel

**6. Database Source, Setup, and Schema (Revised)**

#### **6.1. Data Source**
To simulate a complex and realistic business environment, the project will use the **Brazilian E-Commerce Public Dataset by Olist**, available on Kaggle.

#### **6.2. Database Setup**
1.  Install a local instance of PostgreSQL.
2.  Create a dedicated database for the project.
3.  Download the 9 CSV files from the Olist dataset.
4.  Import each CSV file as a separate table into the PostgreSQL database.

#### **6.3. Anticipated Schema**
The database will contain the following inter-related tables. The agent's primary challenge will be to understand and navigate these relationships to answer questions.

* `olist_customers_dataset`: Contains customer identifiers and location data.
* `olist_geolocation_dataset`: Contains Brazilian zip code and lat/long coordinates.
* `olist_order_items_dataset`: Contains data about the items purchased in each order.
* `olist_order_payments_dataset`: Contains data about the payment options for orders.
* `olist_order_reviews_dataset`: Contains customer reviews for orders.
* `olist_orders_dataset`: The core dataset with information about each order.
* `olist_products_dataset`: Contains data about the products sold by Olist.
* `olist_sellers_dataset`: Contains data about the sellers on Olist.
* `product_category_name_translation`: Translates product category names to English.

This new dataset will allow us to ask much more interesting business questions, such as:
* "What are the top 5 product categories by revenue in the Southeast region?"
* "Which sellers have the highest average review scores for orders with late deliveries?"
* "What is the average shipping time for customers in São Paulo vs. Rio de Janeiro?"


### 7. AI Model Implementation

The core of the agent's intelligence will be driven by a pre-trained Large Language Model.

* **Model**: We will start with a T5 (Text-to-Text Transfer Transformer) model fine-tuned for Text-to-SQL tasks, such as `t5-base-finetuned-wikiSQL`.
* **Integration**: The model will be loaded into the FastAPI backend using the Hugging Face Transformers library. An abstraction layer will be created that takes a user's question and the database schema as input, and outputs a SQL query.

### 8. Out of Scope

To ensure focus and timely completion, the following features are explicitly out of scope for this version:
* User authentication and accounts.
* Conversation history.
* Real-time database updates or write operations.
* Agent fine-tuning or retraining capabilities.

### 9. Success Metrics

The primary success metric is the **quality and accuracy of the agent's responses**. This will be evaluated based on its ability to consistently provide accurate, insightful, and well-visualized answers to extremely complicated analytical questions posed in natural language.