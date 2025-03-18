from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import json
from database import get_db
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

app = FastAPI(title="MCP Server for Database Queries")

# Añadir middleware CORS para permitir solicitudes desde cualquier origen
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = None

class SchemaInfoRequest(BaseModel):
    table_name: Optional[str] = None

@app.get("/")
def read_root():
    return {"message": "Welcome to the MCP Server for Database Queries"}

@app.post("/query")
async def execute_query(request: QueryRequest, db: Session = Depends(get_db)):
    """
    Execute a SQL query against the database.
    
    This endpoint allows an LLM to execute SQL queries against the database.
    It supports both simple and complex queries.
    """
    try:
        # Execute the query with parameters if provided
        if request.parameters:
            result = db.execute(text(request.query), request.parameters)
        else:
            result = db.execute(text(request.query))
        
        # Convert the result to a list of dictionaries
        if result.returns_rows:
            columns = result.keys()
            rows = []
            for row in result:
                rows.append({col: value for col, value in zip(columns, row)})
            return {"success": True, "data": rows}
        else:
            return {"success": True, "message": "Query executed successfully. No rows returned."}
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )

@app.post("/schema")
async def get_schema_info(request: SchemaInfoRequest, db: Session = Depends(get_db)):
    """
    Get schema information about the database or a specific table.
    
    This endpoint allows an LLM to understand the database structure.
    """
    try:
        if request.table_name:
            # Get information about a specific table
            query = text(f"""
                SELECT 
                    COLUMN_NAME, 
                    DATA_TYPE, 
                    IS_NULLABLE, 
                    COLUMN_KEY, 
                    COLUMN_DEFAULT, 
                    EXTRA
                FROM 
                    INFORMATION_SCHEMA.COLUMNS 
                WHERE 
                    TABLE_SCHEMA = '{db.bind.url.database}' 
                    AND TABLE_NAME = :table_name
                ORDER BY 
                    ORDINAL_POSITION
            """)
            result = db.execute(query, {"table_name": request.table_name})
            
            columns = []
            for row in result:
                columns.append({
                    "name": row.COLUMN_NAME,
                    "type": row.DATA_TYPE,
                    "nullable": row.IS_NULLABLE == "YES",
                    "key": row.COLUMN_KEY,
                    "default": row.COLUMN_DEFAULT,
                    "extra": row.EXTRA
                })
            
            return {"success": True, "table": request.table_name, "columns": columns}
        else:
            # Get list of all tables in the database
            query = text(f"""
                SELECT 
                    TABLE_NAME, 
                    TABLE_TYPE,
                    ENGINE,
                    TABLE_ROWS,
                    CREATE_TIME
                FROM 
                    INFORMATION_SCHEMA.TABLES 
                WHERE 
                    TABLE_SCHEMA = '{db.bind.url.database}'
                ORDER BY 
                    TABLE_NAME
            """)
            result = db.execute(query)
            
            tables = []
            for row in result:
                tables.append({
                    "name": row.TABLE_NAME,
                    "type": row.TABLE_TYPE,
                    "engine": row.ENGINE,
                    "rows": row.TABLE_ROWS,
                    "created": row.CREATE_TIME.isoformat() if row.CREATE_TIME else None
                })
            
            return {"success": True, "tables": tables}
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )

@app.options("/")
@app.options("/mcp")
async def mcp_options():
    """
    Handle OPTIONS requests for the MCP endpoint.
    This is needed for CORS and to inform clients about the capabilities of this MCP server.
    """
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }
    return JSONResponse(
        content={
            "name": "Local Peticiones DB",
            "description": "Servidor MCP local para consultar la base de datos 'peticiones'",
            "version": "1.0.0",
            "vendor": "Custom",
            "actions": ["query", "get_schema"]
        },
        headers=headers
    )

@app.post("/mcp")
async def mcp_endpoint(request: Request, db: Session = Depends(get_db)):
    """
    Main MCP endpoint following Anthropic's guidelines.
    
    This endpoint allows an LLM to interact with the database through a structured protocol.
    """
    try:
        # Parse the request body
        body = await request.json()
        
        # Check if the request contains a valid action
        if "action" not in body:
            raise HTTPException(status_code=400, detail="Missing 'action' field in request")
        
        action = body["action"]
        
        if action == "query":
            # Execute a SQL query
            if "sql" not in body:
                raise HTTPException(status_code=400, detail="Missing 'sql' field for query action")
            
            sql = body["sql"]
            params = body.get("parameters", {})
            
            result = db.execute(text(sql), params)
            
            if result.returns_rows:
                columns = result.keys()
                rows = []
                for row in result:
                    rows.append({col: value for col, value in zip(columns, row)})
                return {"success": True, "data": rows}
            else:
                return {"success": True, "message": "Query executed successfully. No rows returned."}
        
        elif action == "get_schema":
            # Get schema information
            table_name = body.get("table_name")
            
            if table_name:
                # Get information about a specific table
                query = text(f"""
                    SELECT 
                        COLUMN_NAME, 
                        DATA_TYPE, 
                        IS_NULLABLE, 
                        COLUMN_KEY, 
                        COLUMN_DEFAULT, 
                        EXTRA
                    FROM 
                        INFORMATION_SCHEMA.COLUMNS 
                    WHERE 
                        TABLE_SCHEMA = '{db.bind.url.database}' 
                        AND TABLE_NAME = :table_name
                    ORDER BY 
                        ORDINAL_POSITION
                """)
                result = db.execute(query, {"table_name": table_name})
                
                columns = []
                for row in result:
                    columns.append({
                        "name": row.COLUMN_NAME,
                        "type": row.DATA_TYPE,
                        "nullable": row.IS_NULLABLE == "YES",
                        "key": row.COLUMN_KEY,
                        "default": row.COLUMN_DEFAULT,
                        "extra": row.EXTRA
                    })
                
                return {"success": True, "table": table_name, "columns": columns}
            else:
                # Get list of all tables in the database
                query = text(f"""
                    SELECT 
                        TABLE_NAME, 
                        TABLE_TYPE,
                        ENGINE,
                        TABLE_ROWS,
                        CREATE_TIME
                    FROM 
                        INFORMATION_SCHEMA.TABLES 
                    WHERE 
                        TABLE_SCHEMA = '{db.bind.url.database}'
                    ORDER BY 
                        TABLE_NAME
                """)
                result = db.execute(query)
                
                tables = []
                for row in result:
                    tables.append({
                        "name": row.TABLE_NAME,
                        "type": row.TABLE_TYPE,
                        "engine": row.ENGINE,
                        "rows": row.TABLE_ROWS,
                        "created": row.CREATE_TIME.isoformat() if row.CREATE_TIME else None
                    })
                
                return {"success": True, "tables": tables}
        
        else:
            # Unknown action
            raise HTTPException(status_code=400, detail=f"Unknown action: {action}")
    
    except Exception as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
