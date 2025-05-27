from flask import Flask, jsonify, request
import os

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <h1>Geo News MCP Server</h1>
    <p>Model Context Protocol server for news data</p>
    <p>MCP endpoint: /mcp</p>
    <p>Status: ✅ Running</p>
    """

@app.route("/mcp", methods=["GET", "POST"])
def mcp_endpoint():
    """MCP endpoint as required by Smithery"""
    # Basic MCP response for testing
    return jsonify({
        "jsonrpc": "2.0",
        "result": {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "geo-news-mcp",
                "version": "1.0.0"
            }
        }
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)