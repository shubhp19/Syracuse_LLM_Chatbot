"""
Syracuse University Web Scraper
Scrapes FAQ, courses, programs, admissions, and support pages.
"""

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class SUScraper:
    def __init__(self, max_pages: int = 300, delay: float = 1.5):
        self.base_url = "https://www.syracuse.edu"
        self.domain = "syracuse.edu"  # matches subdomains too
        self.max_pages = max_pages
        self.delay = delay
        self.visited = set()
        self.scraped_data = []

        self.headers = {
            "User-Agent": "Mozilla/5.0 (compatible; SU-ChatbotResearch/1.0)"
        }

        # SU-specific seed URLs — real verified pages
        self.seed_urls = [
            # Main site
            "https://www.syracuse.edu/academics/",
            "https://www.syracuse.edu/admissions/",
            "https://www.syracuse.edu/tuition-aid/",
            "https://www.syracuse.edu/campus-life/",
            "https://www.syracuse.edu/about/",

            # Admissions
            "https://admissions.syr.edu/",
            "https://admissions.syr.edu/apply/",
            "https://admissions.syr.edu/visit/",
            "https://admissions.syr.edu/tuition-financial-aid/",

            # Academics
            "https://www.syracuse.edu/academics/schools-and-colleges/",
            "https://www.syracuse.edu/academics/undergraduate/",
            "https://www.syracuse.edu/academics/graduate/",

            # Financial Aid
            "https://financialaid.syr.edu/",
            "https://financialaid.syr.edu/types-of-aid/",
            "https://financialaid.syr.edu/scholarships/",

            # Graduate School
            "https://graduateschool.syr.edu/",
            "https://graduateschool.syr.edu/programs/",
            "https://graduateschool.syr.edu/admissions/",

            # Student services
            "https://ese.syr.edu/",          # Enrollment & Student Experience
            "https://accessibility.syr.edu/",
            "https://counselingcenter.syr.edu/",
            "https://healthservices.syr.edu/",
            "https://career.syr.edu/",

            # Faculty/Academic policies
            "https://academicintegrity.syr.edu/",
            "https://registrar.syr.edu/",
            "https://registrar.syr.edu/students/",
            "https://registrar.syr.edu/faculty-staff/",

            # FAQ portal
            "https://answers.syr.edu/",
        ]

        # URL patterns to SKIP (not useful for chatbot)
        self.skip_patterns = [
            "news", "event", "blog", "press-release", "story", "media",
            "alumni", "giving", "donate", "athletics", "sport", "facebook",
            "twitter", "instagram", "linkedin", "youtube", "pdf", ".jpg",
            ".png", ".gif", "login", "logout", "calendar/event"
        ]

    def should_skip(self, url: str) -> bool:
        url_lower = url.lower()
        return any(p in url_lower for p in self.skip_patterns)

    def is_su_domain(self, url: str) -> bool:
        netloc = urlparse(url).netloc
        return netloc.endswith("syracuse.edu") or netloc.endswith("syr.edu")

    def clean_text(self, soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "nav", "footer", "header",
                         "iframe", "noscript", "form", "button"]):
            tag.decompose()
        text = soup.get_text(separator="\n")
        lines = [line.strip() for line in text.splitlines()]
        lines = [l for l in lines if len(l) > 25]
        return "\n".join(lines)

    def scrape_page(self, url: str) -> dict | None:
        try:
            resp = requests.get(url, headers=self.headers, timeout=12)
            resp.raise_for_status()
            if "text/html" not in resp.headers.get("Content-Type", ""):
                return None

            soup = BeautifulSoup(resp.text, "html.parser")

            title = soup.find("title")
            title = title.get_text(strip=True) if title else "Untitled"

            meta = soup.find("meta", attrs={"name": "description"})
            description = meta["content"] if meta and meta.get("content") else ""

            content = self.clean_text(soup)
            if len(content) < 150:
                return None

            links = []
            for a in soup.find_all("a", href=True):
                href = urljoin(url, a["href"]).split("#")[0].split("?")[0]
                if (self.is_su_domain(href)
                        and href not in self.visited
                        and not self.should_skip(href)):
                    links.append(href)

            return {"url": url, "title": title,
                    "description": description, "content": content,
                    "links": links}

        except Exception as e:
            logger.warning(f"Failed: {url} — {e}")
            return None

    def crawl(self) -> list[dict]:
        queue = list(set(self.seed_urls))
        logger.info(f"Starting SU crawl. Seeds: {len(queue)}, Max: {self.max_pages}")

        while queue and len(self.scraped_data) < self.max_pages:
            url = queue.pop(0)
            if url in self.visited:
                continue
            self.visited.add(url)

            logger.info(f"[{len(self.scraped_data)+1}/{self.max_pages}] {url}")
            page = self.scrape_page(url)

            if page:
                self.scraped_data.append({
                    "url": page["url"],
                    "title": page["title"],
                    "description": page["description"],
                    "content": page["content"]
                })
                for link in page["links"]:
                    if link not in self.visited:
                        queue.append(link)

            time.sleep(self.delay)

        logger.info(f"Done. Scraped {len(self.scraped_data)} pages.")
        return self.scraped_data

    def save(self, path="scraped_data.json"):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.scraped_data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved to {path}")


if __name__ == "__main__":
    scraper = SUScraper(max_pages=300, delay=1.5)
    data = scraper.crawl()
    scraper.save("scraped_data.json")
    print(f"\n✅ Done! Scraped {len(data)} pages from Syracuse University.")
