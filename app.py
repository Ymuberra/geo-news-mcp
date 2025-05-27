from flask import Flask, jsonify, request
import os
import requests
import json

app = Flask(__name__)

# MCP Tools tanımları
MCP_TOOLS = {
    "get_news_by_country": {
        "name": "get_news_by_country",
        "description": "Get latest news from a specific country",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {
                    "type": "string",
                    "description": "Country code (e.g., 'us', 'tr', 'gb')"
                },
                "category": {
                    "type": "string",
                    "description": "News category",
                    "enum": ["business", "entertainment", "general", "health", "science", "sports", "technology"]
                }
            },
            "required": ["country"]
        }
    },
    "search_news": {
        "name": "search_news",
        "description": "Search for news articles by keyword",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "language": {
                    "type": "string",
                    "description": "Language code (e.g., 'en', 'tr')"
                }
            },
            "required": ["query"]
        }
    }
}

@app.route("/")
def home():
    return """
    <h1>Geo News MCP Server</h1>
    <p>Model Context Protocol server for geographical news data</p>
    <p>Available tools: get_news_by_country, search_news</p>
    <p>MCP endpoint: /mcp</p>
    <p>Status: ✅ Running</p>
    """

@app.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    """MCP endpoint as required by Smithery"""
    if request.method == "GET":
        # Return server capabilities
        return jsonify({
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "tools": {
                        "listChanged": True
                    }
                },
                "serverInfo": {
                    "name": "geo-news-mcp",
                    "version": "1.0.0"
                }
            }
        })

    # Handle POST requests (MCP calls)
    data = request.get_json()
    method = data.get("method")

    if method == "tools/list":
        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "tools": list(MCP_TOOLS.values())
            }
        })

    elif method == "tools/call":
        params = data.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})

        if tool_name == "get_news_by_country":
            result = get_news_by_country(arguments)
        elif tool_name == "search_news":
            result = search_news(arguments)
        else:
            return jsonify({
                "jsonrpc": "2.0",
                "id": data.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            })

        return jsonify({
            "jsonrpc": "2.0",
            "id": data.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": result
                    }
                ]
            }
        })

    return jsonify({
        "jsonrpc": "2.0",
        "id": data.get("id"),
        "error": {
            "code": -32601,
            "message": f"Unknown method: {method}"
        }
    })

def get_news_by_country(arguments):
    """Get news by country using NewsAPI"""
    country = arguments.get("country", "us")
    category = arguments.get("category", "general")
    api_key = os.environ.get("NEWS_API_KEY", "f6f44383e2f24650acf005a04bba7cf1")

    try:
        url = f"https://newsapi.org/v2/top-headlines"
        params = {
            "country": country,
            "category": category,
            "apiKey": api_key,
            "pageSize": 5
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])
            if not articles:
                return f"No news found for country: {country}, category: {category}"

            result = f"📰 Latest {category} news from {country.upper()}:\n\n"
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                result += f"{i}. **{title}**\n{description}\n🔗 {url}\n\n"

            return result
        else:
            return f"Error fetching news: {data.get('message', 'Unknown error')}"

    except Exception as e:
        return f"Error: {str(e)}"

def search_news(arguments):
    """Search news by keyword using NewsAPI"""
    query = arguments.get("query")
    language = arguments.get("language", "en")
    api_key = os.environ.get("NEWS_API_KEY", "f6f44383e2f24650acf005a04bba7cf1")

    try:
        url = f"https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "language": language,
            "apiKey": api_key,
            "pageSize": 5,
            "sortBy": "publishedAt"
        }

        response = requests.get(url, params=params)
        data = response.json()

        if data.get("status") == "ok":
            articles = data.get("articles", [])
            if not articles:
                return f"No news found for query: {query}"

            result = f"🔍 Search results for '{query}':\n\n"
            for i, article in enumerate(articles, 1):
                title = article.get("title", "No title")
                description = article.get("description", "No description")
                url = article.get("url", "")
                published = article.get("publishedAt", "")
                result += f"{i}. **{title}**\n{description}\n📅 {published}\n🔗 {url}\n\n"

            return result
        else:
            return f"Error searching news: {data.get('message', 'Unknown error')}"

    except Exception as e:
        return f"Error: {str(e)}"

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)