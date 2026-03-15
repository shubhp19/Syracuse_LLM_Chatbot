"""
Data Ingestion Pipeline
Chunks scraped data and stores embeddings in ChromaDB.
Run once after scraping, or whenever you re-scrape.
"""

import json
import re
import chromadb
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

SCRAPED_DATA_PATH = "scraped_data.json"
CHROMA_DB_PATH    = "./chroma_db"
COLLECTION_NAME   = "su_knowledge"
EMBED_MODEL       = "all-MiniLM-L6-v2"
CHUNK_SIZE        = 600
CHUNK_OVERLAP     = 120


def chunk_text(text: str) -> list[str]:
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    chunks, start = [], 0
    while start < len(text):
        chunk = text[start:start + CHUNK_SIZE].strip()
        if len(chunk) > 60:
            chunks.append(chunk)
        start += CHUNK_SIZE - CHUNK_OVERLAP
    return chunks


def ingest():
    logger.info("Loading scraped data...")
    with open(SCRAPED_DATA_PATH, "r", encoding="utf-8") as f:
        pages = json.load(f)
    logger.info(f"Loaded {len(pages)} pages.")

    logger.info(f"Loading embedding model: {EMBED_MODEL}")
    embedder = SentenceTransformer(EMBED_MODEL)

    client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass

    collection = client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )

    all_docs, all_ids, all_metas = [], [], []

    for page in pages:
        url     = page.get("url", "")
        title   = page.get("title", "")
        content = page.get("content", "")
        full    = f"Page: {title}\nURL: {url}\n\n{content}"

        for i, chunk in enumerate(chunk_text(full)):
            all_docs.append(chunk)
            all_ids.append(f"{url}__chunk_{i}")
            all_metas.append({"url": url, "title": title, "chunk_index": i})

    logger.info(f"Generated {len(all_docs)} chunks. Embedding & storing...")

    BATCH = 128
    for i in range(0, len(all_docs), BATCH):
        b_docs  = all_docs[i:i+BATCH]
        b_ids   = all_ids[i:i+BATCH]
        b_metas = all_metas[i:i+BATCH]
        embeds  = embedder.encode(b_docs, show_progress_bar=False).tolist()
        collection.add(documents=b_docs, embeddings=embeds,
                       ids=b_ids, metadatas=b_metas)
        logger.info(f"  Stored {min(i+BATCH, len(all_docs))}/{len(all_docs)}")

    logger.info(f"✅ Ingestion complete! {len(all_docs)} chunks in ChromaDB.")


if __name__ == "__main__":
    ingest()
