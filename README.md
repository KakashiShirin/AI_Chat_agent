# AI Data Agent: Conversational Business Intelligence

An intelligent conversational interface for business intelligence that allows users to ask complex analytical questions of a SQL database in plain English and receive accurate, easy-to-understand answers with auto-generated charts and tables.

## Project Overview

This project implements an AI-powered data agent that:
- Processes natural language questions about business data
- Generates accurate SQL queries using a hybrid approach (rule-based + AI)
- Provides natural language summaries of results
- Automatically generates relevant visualizations and tables
- Handles complex, "dirty" data from real-world e-commerce datasets
- Optimized for Vercel deployment with cost-effective AI integration

## Technical Stack

- **Frontend**: React with Vite, Material-UI (MUI), Recharts
- **Backend**: Python with FastAPI
- **Database**: PostgreSQL
- **AI Model**: Hybrid approach - Rule-based + Hugging Face AI (microsoft/DialoGPT-small)
- **Deployment**: Vercel

## Dataset

Brazilian E-Commerce Public Dataset by Olist (9 interconnected tables):
- `olist_customers_dataset`
- `olist_geolocation_dataset`
- `olist_order_items_dataset`
- `olist_order_payments_dataset`
- `olist_order_reviews_dataset`
- `olist_orders_dataset`
- `olist_products_dataset`
- `olist_sellers_dataset`
- `product_category_name_translation`

## Project Structure

```
├── backend/          # FastAPI backend application
├── frontend/         # React frontend application
├── docs/            # Project documentation
├── data/            # Dataset files and analysis
├── scripts/         # Utility scripts
└── README.md        # This file
```

## Development Phases

1. **Phase 1**: Project Setup & Data Foundation ✅
2. **Phase 2**: Backend Core - AI Agent ✅
3. **Phase 3**: Frontend Interface (In Progress)
4. **Phase 4**: Integration, Refinement & Deployment

### Phase 2 Implementation Details

**Hybrid AI Approach**: 
- **Rule-based generation** for simple queries (COUNT, TOP, AVERAGE, SUM)
- **Hugging Face AI** for complex queries (1,000 free requests/month)
- **Automatic fallback** to rule-based if AI fails
- **Smart query routing** based on complexity detection

**Vercel Optimization**:
- Lightweight dependencies (no heavy ML models)
- Fast startup and response times (0.01-0.03s)
- Cost-effective AI integration
- Free tier compatible

## Getting Started

### Prerequisites

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+
- Git

### Installation

1. Clone the repository
2. Set up PostgreSQL database
3. Import the Olist dataset
4. Install backend dependencies
5. Install frontend dependencies
6. Run the application

## License

This project is part of the SDE Hiring Assignment for bulba.app.
