import asyncio
import csv
import random
import re
from playwright.async_api import async_playwright

# Configuration
SEARCH_KEYWORDS = ["kitchen gadgets", "office supplies", "fitness equipment"]
MAX_PAGES = 1
OUTPUT_FILE = "amazon_products.csv"

# Filters
MIN_PRICE = 20.0
MAX_BSR = 1000000
MIN_SELLERS = 1
MAX_SELLERS = 20
MIN_RATING = 3.5

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
]

async def get_product_details(page, url):
    """Scrapes BSR and Seller Count from the product detail page."""
    if not url:
        return None, None
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        await asyncio.sleep(random.uniform(2, 4))
        
        content = await page.content()
        
        # Extract BSR
        bsr = None
        bsr_match = re.search(r'#([0-9,]+)\s+in\s+', content)
        if bsr_match:
            bsr = int(bsr_match.group(1).replace(',', ''))
        else:
            bsr_match = re.search(r'Best Sellers Rank.*?#([0-9,]+)', content, re.DOTALL)
            if bsr_match:
                bsr = int(bsr_match.group(1).replace(',', ''))

        # Extract Seller Count
        seller_count = 1
        seller_match = re.search(r'New\s+\(([0-9]+)\)\s+from', content)
        if seller_match:
            seller_count = int(seller_match.group(1))
        else:
            seller_match = re.search(r'([0-9]+)\s+Offers', content)
            if seller_match:
                seller_count = int(seller_match.group(1))
                
        return bsr, seller_count
    except Exception as e:
        print(f"Error fetching details for {url}: {e}")
        return None, None

async def scrape_amazon():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent=random.choice(USER_AGENTS))
        page = await context.new_page()
        
        results = []
        
        for keyword in SEARCH_KEYWORDS:
            print(f"Searching for: {keyword}")
            for page_num in range(1, MAX_PAGES + 1):
                search_url = f"https://www.amazon.com/s?k={keyword.replace(' ', '+')}&page={page_num}"
                try:
                    await page.goto(search_url, wait_until="domcontentloaded", timeout=60000)
                    await asyncio.sleep(random.uniform(3, 5))
                    
                    products = await page.query_selector_all('div[data-component-type="s-search-result"]')
                    print(f"Found {len(products)} products on page.")
                    
                    for product in products:
                        try:
                            # Title
                            title_el = await product.query_selector('h2 a span')
                            if not title_el:
                                title_el = await product.query_selector('h2 a')
                            title = await title_el.inner_text() if title_el else "N/A"
                            
                            # Link
                            link_el = await product.query_selector('h2 a')
                            link = await link_el.get_attribute('href') if link_el else None
                            if link and not link.startswith('http'):
                                link = "https://www.amazon.com" + link
                            
                            # Price
                            price_el = await product.query_selector('.a-price .a-offscreen')
                            price_text = await price_el.inner_text() if price_el else "$0"
                            price = float(price_text.replace(',', '').replace('$', ''))
                            
                            # Rating
                            rating_el = await product.query_selector('span[aria-label*="out of 5 stars"]')
                            rating_text = await rating_el.get_attribute('aria-label') if rating_el else "0"
                            rating = float(rating_text.split(' ')[0]) if rating_text else 0.0
                            
                            print(f"Checking: {title[:30]} | Price: {price} | Rating: {rating}")
                            
                            if price >= MIN_PRICE:
                                detail_page = await context.new_page()
                                bsr, sellers = await get_product_details(detail_page, link)
                                await detail_page.close()
                                
                                if bsr is not None:
                                    print(f"Found: {title[:50]}... | BSR: {bsr} | Sellers: {sellers} | Price: {price} | Rating: {rating}")
                                    if bsr < MAX_BSR and MIN_SELLERS <= sellers <= MAX_SELLERS and rating >= MIN_RATING:
                                        results.append({
                                            "Title": title,
                                            "Price": price,
                                            "Rating": rating,
                                            "BSR": bsr,
                                            "Sellers": sellers,
                                            "URL": link
                                        })
                        except Exception as e:
                            print(f"Error processing product: {e}")
                            continue
                except Exception as e:
                    print(f"Error on search page: {e}")
                    
        # Save to CSV
        if results:
            keys = results[0].keys()
            with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
                dict_writer = csv.DictWriter(f, fieldnames=keys)
                dict_writer.writeheader()
                dict_writer.writerows(results)
            print(f"Successfully saved {len(results)} products to {OUTPUT_FILE}")
        else:
            print("No products found matching the criteria.")
            
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_amazon())
