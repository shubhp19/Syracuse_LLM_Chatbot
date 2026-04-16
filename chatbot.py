"""
SU Chatbot Engine — Groq API + ChromaDB RAG
Full featured: Students + Professors with all capabilities
"""

import chromadb
from groq import Groq
from fastembed import TextEmbedding
import json
import os
from datetime import datetime

CHROMA_DB_PATH  = "./chroma_db"
COLLECTION_NAME = "su_knowledge"
EMBED_MODEL     = "sentence-transformers/all-MiniLM-L6-v2"
GROQ_MODEL      = "llama-3.3-70b-versatile"
TOP_K           = 6
ANNOUNCEMENTS_FILE = "announcements.json"

# ── System Prompts ─────────────────────────────────────────────────────────────

STUDENT_PROMPT = """You are an AI assistant for Syracuse University helping STUDENTS.
You are knowledgeable about:
- Courses, programs, majors, and minors at SU
- Admissions requirements and application process
- Tuition, fees, financial aid, and scholarships
- Academic deadlines, registration, and calendar
- Finding professors, departments, and contacts
- Campus life, housing, health, and student services
- Academic integrity and university policies

Tone: Friendly, encouraging, clear. Students may be stressed — be warm and helpful.
Rules:
- Answer ONLY from the provided context
- If info is missing, direct to the correct SU office/website
- Never fabricate deadlines, costs, or requirements
- Always suggest a helpful next step at the end"""

PROFESSOR_PROMPT = """You are an AI assistant for Syracuse University helping FACULTY & PROFESSORS.
You are knowledgeable about:
- University academic policies and procedures
- Course catalog, curriculum, and program structures
- Department info, admin contacts, and org structure
- Registrar processes, grade submission, enrollment
- Research support and resources
- Student services professors can refer students to
- Academic integrity enforcement procedures

Tone: Professional, concise, precise. Professors need quick accurate answers.
Rules:
- Answer ONLY from the provided context
- Use proper academic/administrative terminology
- If info is missing, direct to the specific SU administrative office
- Never fabricate policies or procedures
- Cite source URLs when available in context"""


class AnnouncementManager:
    """Handles professor announcements stored locally."""

    def __init__(self, filepath=ANNOUNCEMENTS_FILE):
        self.filepath = filepath
        self._load()

    def _load(self):
        if os.path.exists(self.filepath):
            with open(self.filepath, "r") as f:
                self.data = json.load(f)
        else:
            self.data = []

    def _save(self):
        with open(self.filepath, "w") as f:
            json.dump(self.data, f, indent=2)

    def post(self, professor: str, course: str, title: str, body: str) -> dict:
        ann = {
            "id": len(self.data) + 1,
            "professor": professor,
            "course": course,
            "title": title,
            "body": body,
            "posted_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "active": True
        }
        self.data.append(ann)
        self._save()
        return ann

    def get_all(self, active_only=True) -> list:
        if active_only:
            return [a for a in self.data if a.get("active", True)]
        return self.data

    def get_by_course(self, course: str) -> list:
        return [a for a in self.data
                if course.lower() in a["course"].lower() and a.get("active", True)]

    def delete(self, ann_id: int) -> bool:
        for a in self.data:
            if a["id"] == ann_id:
                a["active"] = False
                self._save()
                return True
        return False

    def edit(self, ann_id: int, title: str = None, body: str = None) -> bool:
        for a in self.data:
            if a["id"] == ann_id and a.get("active", True):
                if title: a["title"] = title
                if body:  a["body"] = body
                a["edited_at"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                self._save()
                return True
        return False


class SUChatbot:
    def __init__(self, api_key: str, role: str = "student"):
        self.role = role.lower()
        self.client = Groq(api_key=api_key)
        self.announcements = AnnouncementManager()

        print("Loading embedding model...")
        self.embedder = TextEmbedding(EMBED_MODEL)

        print("Connecting to ChromaDB...")
        db = chromadb.PersistentClient(path=CHROMA_DB_PATH)
        try:
            self.collection = db.get_collection(COLLECTION_NAME)
            count = self.collection.count()
            if count == 0:
                raise ValueError("Empty collection")
            print(f"✅ Ready [{self.role.upper()} mode] — {count} chunks loaded.")
        except Exception as e:
            print(f"⚠️ Collection not found ({e}), rebuilding from scraped_data.json...")
            self.collection = self._build_collection(db)
            print(f"✅ Rebuilt — {self.collection.count()} chunks loaded.")

        self.history = []

    def _build_collection(self, db):
        import re
        with open("scraped_data.json", "r", encoding="utf-8") as f:
            pages = json.load(f)
        try:
            db.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
        collection = db.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        chunk_size, overlap = 600, 120
        all_docs, all_ids, all_metas = [], [], []
        for page in pages:
            url, title, content = page.get("url",""), page.get("title",""), page.get("content","")
            text = re.sub(r'\n{3,}', '\n\n', f"Page: {title}\nURL: {url}\n\n{content}").strip()
            start = 0
            while start < len(text):
                chunk = text[start:start + chunk_size].strip()
                if len(chunk) > 60:
                    all_docs.append(chunk)
                    all_ids.append(f"{url}__chunk_{len(all_ids)}")
                    all_metas.append({"url": url, "title": title, "chunk_index": len(all_ids)})
                start += chunk_size - overlap
        batch = 128
        for i in range(0, len(all_docs), batch):
            b_docs = all_docs[i:i+batch]
            embeds = [list(self.embedder.embed([d]))[0].tolist() for d in b_docs]
            collection.add(documents=b_docs, embeddings=embeds,
                           ids=all_ids[i:i+batch], metadatas=all_metas[i:i+batch])
        return collection

    @property
    def system_prompt(self):
        return STUDENT_PROMPT if self.role == "student" else PROFESSOR_PROMPT

    def retrieve(self, query: str) -> list[dict]:
        embedding = [list(self.embedder.embed([query]))[0].tolist()]
        results = self.collection.query(
            query_embeddings=embedding,
            n_results=TOP_K,
            include=["documents", "metadatas", "distances"]
        )
        chunks = []
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0]
        ):
            chunks.append({
                "content": doc,
                "url":   meta.get("url", ""),
                "title": meta.get("title", ""),
                "score": round(1 - dist, 3)
            })
        return chunks

    def build_context(self, chunks: list[dict]) -> str:
        parts = []
        for i, c in enumerate(chunks, 1):
            parts.append(f"[Source {i}: {c['title']}]\n{c['content']}\nURL: {c['url']}")
        return "\n\n---\n\n".join(parts)

    def chat(self, user_message: str) -> dict:
        chunks  = self.retrieve(user_message)
        context = self.build_context(chunks)

        # Inject active announcements for students
        ann_context = ""
        if self.role == "student":
            active = self.announcements.get_all()
            if active:
                ann_lines = [
                    f"- [{a['course']}] {a['title']}: {a['body']} (Posted by {a['professor']} on {a['posted_at']})"
                    for a in active[-5:]  # Last 5 announcements
                ]
                ann_context = "\n\nACTIVE PROFESSOR ANNOUNCEMENTS:\n" + "\n".join(ann_lines)

        augmented = f"""Context from Syracuse University website:
{context}{ann_context}

---
Question: {user_message}

Answer based on the context above."""

        messages = [{"role": "system", "content": self.system_prompt}]
        messages += self.history[-8:]
        messages.append({"role": "user", "content": augmented})

        try:
            response = self.client.chat.completions.create(
                model=GROQ_MODEL,
                messages=messages,
                temperature=0.3,
                max_tokens=1024
            )
            answer = response.choices[0].message.content
        except Exception as e:
            answer = f"❌ Groq API error: {e}"

        self.history.append({"role": "user",      "content": user_message})
        self.history.append({"role": "assistant",  "content": answer})

        return {
            "answer": answer,
            "sources": [
                {"title": c["title"], "url": c["url"], "score": c["score"]}
                for c in chunks if c["score"] > 0.25
            ][:4]
        }

    def set_role(self, role: str):
        self.role = role.lower()
        self.history = []

    def reset(self):
        self.history = []
