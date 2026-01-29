"""
Open-Box Deals Aggregator
Warehouse Receipt Edition - Live Browser Streaming
"""
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional
from pathlib import Path
import asyncio
import json
import time
import aiohttp
import os
from urllib.parse import quote_plus

STATIC_DIR = Path(__file__).parent.parent / "static"
MINO_API_URL = "https://mino.ai/v1/automation/run-sse"
MINO_API_KEY = os.getenv("MINO_API_KEY", "")

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(
    title="Open-Box Deals Aggregator",
    description="Warehouse Receipt Edition",
    version="3.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# =============================================================================
# SITE CONFIGURATIONS
# =============================================================================

SITES = {
    "amazon": {
        "name": "Amazon Warehouse",
        "search_url": "https://www.amazon.com/s?k={query}&i=warehouse-deals",
        "goal": "Extract the first 5 products with: name, sale_price, condition, product_url. Return as JSON array.",
        "browser_profile": "stealth",
        "proxy_config": {"enabled": True, "country_code": "US"}
    },
    "bestbuy": {
        "name": "Best Buy Outlet",
        "search_url": "https://www.bestbuy.com/site/searchpage.jsp?st={query}&qp=condition_facet%3DCondition~Open-Box",
        "goal": "Extract the first 5 open-box products with: name, original_price, sale_price, condition, product_url. Return as JSON array.",
        "browser_profile": "stealth",
        "proxy_config": {"enabled": True, "country_code": "US"}
    },
    "newegg": {
        "name": "Newegg Open Box",
        "search_url": "https://www.newegg.com/p/pl?d={query}&N=4814",
        "goal": "Extract the first 5 open-box products with: name, original_price, sale_price, product_url. Return as JSON array."
    },
    "backmarket": {
        "name": "BackMarket",
        "search_url": "https://www.backmarket.com/en-us/search?q={query}",
        "goal": "Extract the first 5 refurbished products with: name, original_price, sale_price, condition, product_url. Return as JSON array.",
        "browser_profile": "stealth"
    },
    "bhphoto": {
        "name": "B&H Photo",
        "search_url": "https://www.bhphotovideo.com/c/search?q={query}&fct=fct_condition_background%7cused",
        "goal": "Extract the first 5 deals with: name, original_price, sale_price, product_url. Return as JSON array."
    },
    "ebay": {
        "name": "eBay Refurbished",
        "search_url": "https://www.ebay.com/sch/i.html?_nkw={query}&LH_ItemCondition=2500",
        "goal": "Extract the first 5 certified refurbished products with: name, sale_price, original_price, condition, product_url. Return as JSON array.",
        "browser_profile": "stealth"
    },
    "target": {
        "name": "Target Clearance",
        "search_url": "https://www.target.com/s?searchTerm={query}&facetedValue=5zja2",
        "goal": "Extract the first 5 clearance products with: name, original_price, sale_price, product_url. Return as JSON array.",
        "browser_profile": "stealth",
        "proxy_config": {"enabled": True, "country_code": "US"}
    },
    "microcenter": {
        "name": "Micro Center",
        "search_url": "https://www.microcenter.com/search/search_results.aspx?Ntt={query}&Ntk=all&N=4294966998",
        "goal": "Extract the first 5 open box products with: name, original_price, sale_price, product_url. Return as JSON array."
    }
}


# =============================================================================
# ENDPOINTS
# =============================================================================

@app.get("/")
def root():
    index_file = STATIC_DIR / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"status": "running"}


@app.get("/api/sites")
def list_sites():
    return {
        "sites": [
            {"key": key, "name": config["name"]}
            for key, config in SITES.items()
        ]
    }


@app.get("/api/search/live")
async def search_live(
    q: str = Query(..., min_length=2),
    max_price: Optional[float] = Query(None)
):
    """Stream live browser sessions + results"""
    
    async def event_generator():
        start_time = time.time()
        
        yield f"data: {json.dumps({'type': 'search_start', 'query': q, 'sites': list(SITES.keys())})}\n\n"
        
        event_queue = asyncio.Queue()
        
        async def scrape_site(site_key: str, site_config: dict):
            search_url = site_config["search_url"].format(query=quote_plus(q))
            
            payload = {
                "url": search_url,
                "goal": site_config["goal"]
            }
            
            if "browser_profile" in site_config:
                payload["browser_profile"] = site_config["browser_profile"]
            
            if "proxy_config" in site_config:
                payload["proxy_config"] = site_config["proxy_config"]
            
            headers = {
                "X-API-Key": MINO_API_KEY,
                "Content-Type": "application/json"
            }
            
            # Send initial status
            await event_queue.put({
                "type": "session_status",
                "site": site_key,
                "site_name": site_config["name"],
                "status": "connecting"
            })
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        MINO_API_URL,
                        headers=headers,
                        json=payload,
                        timeout=aiohttp.ClientTimeout(total=300)
                    ) as response:
                        
                        if response.status != 200:
                            await event_queue.put({
                                "type": "session_error",
                                "site": site_key,
                                "site_name": site_config["name"],
                                "error": f"HTTP {response.status}"
                            })
                            await event_queue.put({"type": "session_done", "site": site_key})
                            return
                        
                        streaming_url_sent = False
                        result_data = None
                        buffer = ""
                        
                        print(f"[{site_key}] Starting to read response...")
                        
                        async for chunk in response.content.iter_any():
                            buffer += chunk.decode('utf-8', errors='ignore')
                            
                            # Process complete lines
                            while '\n' in buffer:
                                line, buffer = buffer.split('\n', 1)
                                line = line.strip()
                                
                                if line.startswith("data: "):
                                    try:
                                        event = json.loads(line[6:])
                                        print(f"[{site_key}] Event keys: {list(event.keys())}")
                                        
                                        # Send streaming URL immediately
                                        if event.get("streamingUrl") and not streaming_url_sent:
                                            await event_queue.put({
                                                "type": "session_start",
                                                "site": site_key,
                                                "site_name": site_config["name"],
                                                "streamingUrl": event["streamingUrl"],
                                                "searchUrl": search_url
                                            })
                                            streaming_url_sent = True
                                        
                                        # Check for result in various locations (Mino uses resultJson)
                                        if event.get("resultJson"):
                                            result_data = event["resultJson"]
                                        elif event.get("result"):
                                            result_data = event["result"]
                                        elif event.get("data") and isinstance(event.get("data"), (list, dict)):
                                            result_data = event["data"]
                                        elif event.get("products"):
                                            result_data = event["products"]
                                        
                                        # Check for error
                                        if event.get("error"):
                                            await event_queue.put({
                                                "type": "session_error",
                                                "site": site_key,
                                                "site_name": site_config["name"],
                                                "error": str(event["error"])[:50]
                                            })
                                            await event_queue.put({"type": "session_done", "site": site_key})
                                            return
                                            
                                    except json.JSONDecodeError:
                                        continue
                        
                        # Process any remaining buffer
                        if buffer.strip().startswith("data: "):
                            try:
                                event = json.loads(buffer.strip()[6:])
                                if event.get("resultJson"):
                                    result_data = event["resultJson"]
                                elif event.get("result"):
                                    result_data = event["result"]
                                elif event.get("products"):
                                    result_data = event["products"]
                            except:
                                pass
                        
                        if result_data:
                            print(f"[{site_key}] Got result_data type: {type(result_data)}")
                            print(f"[{site_key}] result_data preview: {str(result_data)[:200]}")
                            products = extract_products(result_data)
                            print(f"[{site_key}] Extracted {len(products)} products")
                            if max_price:
                                products = filter_by_price(products, max_price)
                            
                            await event_queue.put({
                                "type": "session_result",
                                "site": site_key,
                                "site_name": site_config["name"],
                                "products": products,
                                "count": len(products)
                            })
                        else:
                            await event_queue.put({
                                "type": "session_error",
                                "site": site_key,
                                "site_name": site_config["name"],
                                "error": "No results"
                            })
                            
            except asyncio.TimeoutError:
                await event_queue.put({
                    "type": "session_error",
                    "site": site_key,
                    "site_name": site_config["name"],
                    "error": "Timeout"
                })
            except Exception as e:
                await event_queue.put({
                    "type": "session_error",
                    "site": site_key,
                    "site_name": site_config["name"],
                    "error": str(e)[:50]
                })
            
            await event_queue.put({"type": "session_done", "site": site_key})
        
        tasks = [
            asyncio.create_task(scrape_site(key, config))
            for key, config in SITES.items()
        ]
        
        sites_done = 0
        total_sites = len(SITES)
        
        while sites_done < total_sites:
            try:
                event = await asyncio.wait_for(event_queue.get(), timeout=1.0)
                
                if event["type"] == "session_done":
                    sites_done += 1
                else:
                    yield f"data: {json.dumps(event)}\n\n"
                    
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'type': 'heartbeat', 'elapsed': round(time.time() - start_time, 1)})}\n\n"
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        total_time = round(time.time() - start_time, 2)
        yield f"data: {json.dumps({'type': 'complete', 'total_time': total_time})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )


def extract_products(result_data) -> list:
    if isinstance(result_data, list):
        return result_data
    if isinstance(result_data, dict):
        for key in ["products", "result", "data", "items"]:
            if key in result_data and isinstance(result_data[key], list):
                return result_data[key]
        for value in result_data.values():
            if isinstance(value, list) and value and isinstance(value[0], dict):
                if "name" in value[0] or "title" in value[0]:
                    return value
    return []


def filter_by_price(products: list, max_price: float) -> list:
    filtered = []
    for p in products:
        price_str = p.get("sale_price") or p.get("price") or ""
        try:
            price = float(''.join(c for c in str(price_str) if c.isdigit() or c == '.'))
            if price <= max_price:
                filtered.append(p)
        except:
            filtered.append(p)
    return filtered
