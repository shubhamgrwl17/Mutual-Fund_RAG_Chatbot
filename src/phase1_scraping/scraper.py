"""
Groww web scraper using __NEXT_DATA__ extraction.

Fetches a Groww mutual fund page via HTTP GET and extracts the
structured JSON from the <script id="__NEXT_DATA__"> tag.

Features:
- Retry with exponential backoff (3 attempts)
- Proper User-Agent headers to avoid bot detection
- Configurable timeout
"""

import json
import logging
from time import sleep

import requests
from bs4 import BeautifulSoup

from src.phase1_scraping.config import (
    MAX_RETRIES,
    REQUEST_HEADERS,
    REQUEST_TIMEOUT,
    RETRY_BACKOFF_BASE,
)

logger = logging.getLogger(__name__)


class ScraperError(Exception):
    """Raised when scraping fails after all retries."""
    pass


class NextDataNotFoundError(ScraperError):
    """Raised when __NEXT_DATA__ script tag is not found in the page."""
    pass


def fetch_page(url: str) -> str:
    """
    Fetch the HTML content of a Groww page with retry logic.

    Args:
        url: The Groww mutual fund page URL.

    Returns:
        The raw HTML string.

    Raises:
        ScraperError: If all retry attempts fail.
    """
    last_exception = None

    for attempt in range(MAX_RETRIES):
        try:
            logger.info(f"Fetching {url} (attempt {attempt + 1}/{MAX_RETRIES})")
            response = requests.get(
                url,
                headers=REQUEST_HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            response.raise_for_status()
            logger.info(f"Successfully fetched {url} ({len(response.text)} bytes)")
            return response.text

        except requests.RequestException as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                wait_time = RETRY_BACKOFF_BASE ** attempt
                logger.warning(
                    f"Attempt {attempt + 1} failed for {url}: {e}. "
                    f"Retrying in {wait_time}s..."
                )
                sleep(wait_time)
            else:
                logger.error(f"All {MAX_RETRIES} attempts failed for {url}: {e}")

    raise ScraperError(
        f"Failed to fetch {url} after {MAX_RETRIES} attempts: {last_exception}"
    )


def extract_next_data(html: str) -> dict:
    """
    Extract the __NEXT_DATA__ JSON from a Groww page's HTML.

    Groww is built on Next.js, which embeds all page data as structured
    JSON inside a <script id="__NEXT_DATA__"> tag. This function finds
    that tag and parses the JSON.

    Args:
        html: The raw HTML string of a Groww page.

    Returns:
        The parsed JSON as a Python dict.

    Raises:
        NextDataNotFoundError: If the __NEXT_DATA__ script tag is missing.
    """
    soup = BeautifulSoup(html, "html.parser")
    script_tag = soup.find("script", id="__NEXT_DATA__")

    if not script_tag or not script_tag.string:
        raise NextDataNotFoundError(
            "Could not find <script id='__NEXT_DATA__'> tag in the page HTML. "
            "Groww may have changed their page structure."
        )

    try:
        data = json.loads(script_tag.string)
    except json.JSONDecodeError as e:
        raise ScraperError(f"Failed to parse __NEXT_DATA__ JSON: {e}")

    return data


def get_mf_data(next_data: dict) -> dict:
    """
    Navigate the __NEXT_DATA__ JSON to get the fund data object.

    The fund data is usually located at:
    __NEXT_DATA__ > props > pageProps > mfServerSideData

    If that path fails, we search for common alternative keys to ensure
    resilience against frontend structural changes.
    """
    try:
        page_props = next_data.get("props", {}).get("pageProps", {})
        
        # 1. Primary path (Standard Groww structure)
        if "mfServerSideData" in page_props:
            mf_data = page_props["mfServerSideData"]
        # 2. Alternative path (observed in some Next.js updates)
        elif "data" in page_props:
            mf_data = page_props["data"]
        # 3. Fallback: Check if the data itself is flattened into pageProps
        elif "scheme_name" in page_props:
            mf_data = page_props
        else:
            available_keys = list(page_props.keys())
            raise ScraperError(
                f"Could not find fund data in pageProps. Available keys: {available_keys}. "
                f"Groww structure may have changed significantly."
            )

    except (KeyError, TypeError) as e:
        raise ScraperError(
            f"Unexpected __NEXT_DATA__ structure — could not access pageProps: {e}"
        )

    if not isinstance(mf_data, dict):
        raise ScraperError(
            f"Extracted data is not a dict, got: {type(mf_data).__name__}"
        )

    return mf_data


def scrape_groww_fund(url: str) -> dict:
    """
    Full pipeline: Fetch page → Extract __NEXT_DATA__ → Return fund data.

    This is the main entry point for scraping a single Groww fund page.

    Args:
        url: The Groww mutual fund page URL.

    Returns:
        The mfServerSideData dict with all fund information.

    Raises:
        ScraperError: If fetching or extraction fails.
    """
    html = fetch_page(url)
    next_data = extract_next_data(html)
    mf_data = get_mf_data(next_data)

    logger.info(
        f"Extracted fund data: {mf_data.get('scheme_name', 'Unknown')} "
        f"(NAV: {mf_data.get('nav', 'N/A')})"
    )

    return mf_data
