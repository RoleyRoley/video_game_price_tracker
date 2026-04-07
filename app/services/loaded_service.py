import json
import re

from typing import Dict, Optional
from urllib.parse import urlparse, quote

import cloudscraper
from bs4 import BeautifulSoup

class LoadedService:
    def __init__(self):
        self.session = cloudscraper.create_scraper()
        self.timeout = 15  # seconds
        self._algolia_config: Optional[Dict] = None

    def _get_algolia_config(self) -> Optional[Dict]:
        if self._algolia_config:
            return self._algolia_config
        try:
            r = self.session.get("https://www.loaded.com/", timeout=self.timeout)
            match = re.search(r"window\.algoliaConfig\s*=\s*(\{.*?\});", r.text, re.DOTALL)
            if not match:
                return None
            config = json.loads(match.group(1))
            sorting_indices = config.get("sortingIndices", [])
            index_name = sorting_indices[0]["name"] if sorting_indices else config.get("indexName")
            self._algolia_config = {
                "app_id": config["applicationId"],
                "api_key": config["apiKey"],
                "index": index_name,
            }
            return self._algolia_config
        except Exception:
            return None

    def search_games(self, name: str) -> list[Dict]:
        cfg = self._get_algolia_config()
        if not cfg:
            return []
        try:
            resp = self.session.post(
                f"https://{cfg['app_id']}-dsn.algolia.net/1/indexes/{cfg['index']}/query",
                headers={
                    "X-Algolia-Application-Id": cfg["app_id"],
                    "X-Algolia-API-Key": cfg["api_key"],
                },
                json={
                    "query": name,
                    "hitsPerPage": 10,
                    "attributesToRetrieve": ["name", "url"],
                },
                timeout=self.timeout,
            )
            resp.raise_for_status()
        except Exception:
            return []

        results = []
        for hit in resp.json().get("hits", []):
            url = hit.get("url", {}).get("default", "")
            hit_name = hit.get("name", {}).get("default", "")
            if url and hit_name:
                results.append({"name": hit_name, "url": url})

        # Prefer base game PC Steam results (no DLC, no bundle)
        pc_steam = [
            r for r in results
            if "pc" in r["url"] and "steam" in r["url"] and "dlc" not in r["url"]
        ]
        return pc_steam if pc_steam else results

    def _is_loaded_url(self, url: str) -> bool:
        try:
            # Check if the URL is from loaded.com
            parsed = urlparse(url)
            # Check if the netloc ends with "loaded.com" to allow for subdomains like "www.loaded.com"
            return parsed.netloc.endswith("loaded.com")
        except Exception:
            return False
    
    def _fetch_html(self, url: str) -> str:
        
        # Validate the URL before making the request
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        return response.text
    
    def _extract_price_data(self, html: str) -> list[Dict]:
        # Parse the HTML and extract blocks that may contain price information.
        
        soup = BeautifulSoup(html, "html.parser")
        json_blocks = []
        
        # Look for <script> tags that contain JSON data, which often includes price information.
        for tag in soup.find_all("script", type="application/ld+json"):
            
            if not tag.string:
                continue
            
            try:
                data = json.loads(tag.string)
                if isinstance(data, list):
                    json_blocks.extend(data)
                else:
                    json_blocks.append(data)
            except json.JSONDecodeError:
                continue
        return json_blocks
    
    def _find_product_json(self, json_blocks: list[Dict]) -> Optional[Dict]:
        # Look through the extracted JSON blocks to find one that contains product information.
        for block in json_blocks:
            if isinstance(block, dict) and block.get("@type") == "Product":
                return block
        
        # Some sites nest Product inside graph structures
        for block in json_blocks:
            if not isinstance(block, dict):
                continue

            graph = block.get("@graph")
            if isinstance(graph, list):
                for item in graph:
                    if isinstance(item, dict) and item.get("@type") == "Product":
                        return item

        return None

    def _parse_price_to_pence(self, raw_price: str) -> Optional[int]:
    
        # Convert a price string like '29.99' or '£29.99' to pence.
    
        if raw_price is None:
            return None

        # Remove any non-numeric characters except for '.' and ',' and convert to a float, then to pence.
        cleaned = re.sub(r"[^\d.,]", "", str(raw_price)).replace(",", "")
        if not cleaned:
            return None

        try:
            return int(round(float(cleaned) * 100))
        except ValueError:
            return None

    def get_game_details(self, product_url: str) -> Optional[Dict]:
        """
        Fetch a Loaded product page and return normalized pricing data.

        Returns:
        {
            "store": "Loaded",
            "name": "...",
            "price": 2999,
            "currency": "GBP",
            "url": "https://www.loaded.com/...",
        }
        """
        
        # Validate the URL
        if not self._is_loaded_url(product_url):
            raise ValueError("URL must be a loaded.com product URL")

        html = self._fetch_html(product_url)

        json_blocks = self._extract_price_data(html)
        product = self._find_product_json(json_blocks)

        
        if product:
            name = product.get("name")

            offers = product.get("offers")
            if isinstance(offers, list):
                offers = offers[0] if offers else None

            if isinstance(offers, dict):
                raw_price = offers.get("price")
                currency = offers.get("priceCurrency", "GBP")
                price = self._parse_price_to_pence(raw_price)

                if name and price is not None:
                    return {
                        "store": "Loaded",
                        "name": name,
                        "price": price,
                        "currency": currency,
                        "url": product_url,
                    }

        

    