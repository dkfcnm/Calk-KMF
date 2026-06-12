
import sys
import json
import traceback
import argparse
import os

# Ensure we can import from code/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from code.common.db_manager import db

def log(msg):
    # Log to stderr to avoid interfering with stdout JSON-RPC
    sys.stderr.write(f"[MCP-DB] {msg}\n")
    sys.stderr.flush()

def list_tools():
    return [
        {
            "name": "query_db",
            "description": "Execute a SQL query against the connected PostgreSQL database.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The SQL query to execute."
                    }
                },
                "required": ["query"]
            }
        },
        {
            "name": "list_tables",
            "description": "List all tables in the database.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            }
        }
    ]

def list_resources():
    return [
        {
            "uri": "postgres://schema",
            "name": "Database Schema",
            "mimeType": "text/plain"
        }
    ]

def get_schema():
    try:
        query = """
            SELECT table_name, column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'public'
            ORDER BY table_name, ordinal_position;
        """
        rows = db.fetch_all(query)
        
        schema_lines = []
        current_table = None
        for row in rows:
            table_name, col_name, dtype, nullable = row
            if table_name != current_table:
                if current_table:
                    schema_lines.append(")")
                schema_lines.append(f"CREATE TABLE {table_name} (")
                current_table = table_name
            
            schema_lines.append(f"  {col_name} {dtype} {'NULL' if nullable=='YES' else 'NOT NULL'},")
            
        if current_table:
            schema_lines.append(")")
            
        return "\n".join(schema_lines)
    except Exception as e:
        return str(e)

def execute_query(query):
    try:
        # Simple check for SELECT to decide execution method
        if query.strip().upper().startswith("SELECT") or "RETURNING" in query.strip().upper():
            rows = db.fetch_all(query)
            # We need column names for better context, but DBManager.fetch_all returns tuples
            # Let's try to be smart or adjust DBManager. 
            # For now, just return rows.
            return json.dumps(rows, default=str)
        else:
            db.execute_query(query)
            return "Query executed successfully."
    except Exception as e:
        return f"Error: {e}"

def execute_list_tables():
    try:
        query = "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
        rows = db.fetch_all(query)
        return json.dumps([r[0] for r in rows])
    except Exception as e:
        return f"Error: {e}"

def main():
    parser = argparse.ArgumentParser()
    # Arguments are kept for compatibility but ignored as we use db_config
    parser.add_argument("--main-db", help="Ignored")
    parser.add_argument("--ref-db", help="Ignored")
    args = parser.parse_args()

    log(f"Started PostgreSQL MCP Server.")

    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break
            
            request = json.loads(line)
            method = request.get("method")
            req_id = request.get("id")
            
            response = {"jsonrpc": "2.0", "id": req_id}
            
            if method == "initialize":
                response["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {
                        "tools": {},
                        "resources": {}
                    },
                    "serverInfo": {
                        "name": "project-postgres-mcp",
                        "version": "1.0.0"
                    }
                }
            
            elif method == "tools/list":
                response["result"] = {
                    "tools": list_tools()
                }
                
            elif method == "tools/call":
                params = request.get("params", {})
                name = params.get("name")
                args_tool = params.get("arguments", {})
                
                if name == "query_db":
                    query = args_tool.get("query")
                    res = execute_query(query)
                    response["result"] = {
                        "content": [{"type": "text", "text": res}]
                    }
                        
                elif name == "list_tables":
                    res = execute_list_tables()
                    response["result"] = {
                        "content": [{"type": "text", "text": res}]
                    }
                else:
                    response["error"] = {"code": -32601, "message": "Method not found"}
                    
            elif method == "resources/list":
                response["result"] = {
                    "resources": list_resources()
                }
                
            elif method == "resources/read":
                params = request.get("params", {})
                uri = params.get("uri")
                
                if uri == "postgres://schema":
                    content = get_schema()
                    response["result"] = {
                        "contents": [{"uri": uri, "mimeType": "text/plain", "text": content}]
                    }
                else:
                    response["error"] = {"code": -32602, "message": "Invalid URI"}
                    
            elif method == "ping":
                response["result"] = {}

            # Handle notifications (no id)
            if req_id is not None:
                sys.stdout.write(json.dumps(response) + "\n")
                sys.stdout.flush()
                
        except Exception as e:
            log(f"Error processing request: {e}\n{traceback.format_exc()}")

if __name__ == "__main__":
    main()
