# MCP Server for Database Queries

Este servidor MCP (Model-Centric Protocol) permite a modelos LLM consultar una base de datos MySQL local mediante consultas SQL simples o complejas.

## Características

- Conexión a base de datos MySQL local
- Ejecución de consultas SQL simples y complejas
- Obtención de información del esquema de la base de datos
- Implementación siguiendo las directrices de Anthropic para MCP
- Sin autenticación (según lo solicitado)

## Requisitos

- Python 3.x
- MySQL Server
- Base de datos "peticiones" existente

## Instalación

1. Clonar o descargar este repositorio
2. Activar el entorno virtual:
   ```
   source venv/bin/activate
   ```
3. Instalar las dependencias (ya instaladas):
   ```
   pip install fastapi uvicorn sqlalchemy pymysql python-dotenv
   ```

## Configuración

El archivo `.env` contiene la configuración de conexión a la base de datos:


## Ejecución

Para iniciar el servidor:

```
python main.py
```

O alternativamente:

```
uvicorn main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## Endpoints

- `GET /`: Página de bienvenida
- `POST /query`: Ejecutar consultas SQL directamente
- `POST /schema`: Obtener información del esquema de la base de datos
- `POST /mcp`: Endpoint principal MCP siguiendo las directrices de Anthropic

## Ejemplos de uso

### Consulta SQL simple

```json
POST /query
{
  "query": "SELECT * FROM nombre_tabla LIMIT 10"
}
```

### Consulta con parámetros

```json
POST /query
{
  "query": "SELECT * FROM nombre_tabla WHERE campo = :valor",
  "parameters": {
    "valor": "ejemplo"
  }
}
```

### Obtener esquema de todas las tablas

```json
POST /schema
{}
```

### Obtener esquema de una tabla específica

```json
POST /schema
{
  "table_name": "nombre_tabla"
}
```

### Usando el endpoint MCP

```json
POST /mcp
{
  "action": "query",
  "sql": "SELECT * FROM nombre_tabla LIMIT 10"
}
```

```json
POST /mcp
{
  "action": "get_schema",
  "table_name": "nombre_tabla"
}
```
