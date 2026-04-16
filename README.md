# Syracuse University LLM Chatbot

An AI-powered chatbot built to help Syracuse University students get quick, accurate answers to common questions — without having to dig through multiple websites or wait for a response from staff.

Here is for anyone who want to access SU Chatbot: https://syracusellmchatbot-su.streamlit.app/

## The Problem

Students at Syracuse University often struggle to find information about:
- Academic programs and requirements
- Campus resources and services
- Deadlines, policies, and procedures

This information is scattered across dozens of pages, and reaching faculty or advisors can take time. Students need fast, reliable answers — especially during stressful periods like registration or application deadlines.

## The Solution

This chatbot uses a Retrieval-Augmented Generation (RAG) approach:

1. **Scrape** — Collects and curates content from official Syracuse University web sources
2. **Ingest** — Parses, cleans, and indexes the content into a vector database (ChromaDB)
3. **Retrieve & Answer** — When a student asks a question, the most relevant content is retrieved and passed to an LLM to generate a grounded, accurate response

The result is a conversational assistant that answers student questions based on real SU content, not hallucinated facts.

## Tech Stack

- **Python** — Core application logic
- **ChromaDB** — Vector database for semantic search and retrieval
- **LLM (via API)** — Generates natural language responses grounded in retrieved content
- **Streamlit / Flask** — Web interface (`app.py`)
- **BeautifulSoup / Requests** — Web scraping (`scraper.py`)

## Project Structure

```
├── app.py            # Web app entry point
├── chatbot.py        # Core chatbot logic (retrieval + generation)
├── ingest.py         # Data ingestion pipeline into ChromaDB
├── scraper.py        # Web scraper for SU content
├── scraped_data.json # Curated scraped content
├── chroma_db/        # Vector database store
└── requirements.txt  # Python dependencies
```

## Faculty Sponsors

- Jeffrey Saltz
- Ingrid Erickson

*Syracuse University — School of Information Studies*
