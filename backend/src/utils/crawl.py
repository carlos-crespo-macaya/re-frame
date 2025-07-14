import asyncio
from pathlib import Path
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig


async def extract_links(html: str, base_url: str, domain: str) -> set:
    """Extract all links from HTML that belong to the same domain."""
    soup = BeautifulSoup(html, "html.parser")
    links = set()

    for tag in soup.find_all(["a", "link"]):
        href = tag.get("href") if hasattr(tag, "get") else None
        if href and isinstance(href, str):
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            parsed = urlparse(full_url)

            # Only include links from the same domain
            if parsed.netloc == domain or parsed.netloc == "":
                # Clean up the URL
                clean_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
                if clean_url.startswith(("http://", "https://")):
                    links.add(clean_url.rstrip("/"))

    return links


async def crawl_site(start_url: str, max_pages: int = 50):
    """Crawl a website recursively starting from the given URL."""

    # Parse the start URL to get the domain
    parsed = urlparse(start_url)
    domain = parsed.netloc
    base_url = f"{parsed.scheme}://{domain}"

    # Configuration without LLM filtering
    config = CrawlerRunConfig(
        excluded_tags=["nav", "header", "footer", "aside", "script", "style"],
        scan_full_page=True,
        screenshot=False,
    )

    # Ensure output directory exists
    docs_dir = Path(__file__).parent.parent.parent / "docs/examples"
    docs_dir.mkdir(exist_ok=True)

    # Track visited URLs and URLs to visit
    visited: set[str] = set()
    to_visit: set[str] = {start_url}

    async with AsyncWebCrawler() as crawler:
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop()

            if url in visited:
                continue

            print(f"[{len(visited)+1}/{max_pages}] Crawling: {url}")

            try:
                result = await crawler.arun(url, config=config)

                if result and hasattr(result, "markdown") and result.markdown:
                    # Extract new links from the page
                    if hasattr(result, "html") and result.html:
                        new_links = await extract_links(result.html, url, domain)
                        # Add unvisited links to the queue
                        to_visit.update(new_links - visited)

                    # Generate filename from URL
                    rel_path = url.replace(base_url, "").strip("/")

                    if rel_path == "":
                        filename = "index.md"
                    else:
                        # Create directory structure for nested paths
                        parts = rel_path.split("/")
                        if len(parts) > 1:
                            # Create subdirectories
                            subdir = docs_dir / "/".join(parts[:-1])
                            subdir.mkdir(parents=True, exist_ok=True)
                            filename = "/".join(parts) + ".md"
                        else:
                            filename = rel_path + ".md"

                    filepath = docs_dir / filename

                    # Save the markdown content
                    filepath.write_text(result.markdown, encoding="utf-8")
                    print(f"  ✓ Saved: {filepath}")

                    visited.add(url)
                else:
                    print(f"  ✗ Failed to crawl: {url}")

            except Exception as e:
                print(f"  ✗ Error crawling {url}: {e!s}")

    print("\nCrawling complete!")
    print(f"Total pages crawled: {len(visited)}")
    print(f"Documentation saved to: {docs_dir}")

    # Create an index file listing all crawled pages
    index_content = "# Crawled Documentation Index\n\n"
    for page in sorted(visited):
        rel_path = page.replace(base_url, "").strip("/") or "index"
        index_content += f"- [{rel_path}]({rel_path}.md)\n"

    (docs_dir / "_index.md").write_text(index_content, encoding="utf-8")
    print(f"Created index at: {docs_dir / '_index.md'}")


async def main():
    # Starting URL - change this to crawl different sites
    # start_url = "https://google.github.io/adk-docs/"
    start_url = "https://github.com/google/adk-samples/tree/main/python/agents"

    # Maximum number of pages to crawl (to avoid crawling entire internet)
    max_pages = 20

    await crawl_site(start_url, max_pages)


if __name__ == "__main__":
    asyncio.run(main())
