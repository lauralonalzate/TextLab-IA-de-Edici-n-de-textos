# Exporting OpenAPI Schema

## Method 1: Using the Running Server

Once the server is running, you can export the OpenAPI schema:

```bash
# Export as JSON
curl http://localhost:8000/openapi.json > openapi.json

# Export as YAML (requires yq or similar tool)
curl http://localhost:8000/openapi.json | python -m json.tool | yq eval -P > openapi.yaml
```

## Method 2: Using Python Script

Create a script `export_openapi.py`:

```python
import json
import yaml
from app.main import app

# Export as JSON
with open("openapi.json", "w") as f:
    json.dump(app.openapi(), f, indent=2)

# Export as YAML (requires PyYAML)
try:
    with open("openapi.yaml", "w") as f:
        yaml.dump(app.openapi(), f, default_flow_style=False, sort_keys=False)
except ImportError:
    print("PyYAML not installed. Install with: pip install pyyaml")
```

Run it:
```bash
python export_openapi.py
```

## Method 3: Using FastAPI CLI

```bash
# Install fastapi-cli if not already installed
pip install fastapi-cli

# Export schema
fastapi openapi app.main:app --output openapi.json
```

## Viewing the Schema

The OpenAPI schema is automatically available at:
- JSON: http://localhost:8000/openapi.json
- Interactive Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Schema Details

The exported schema includes:
- All API endpoints with request/response models
- Authentication requirements
- Example values for all schemas
- Error responses
- Query parameters and path parameters

## Updating Examples

Examples are defined in Pydantic schemas using `json_schema_extra`:

```python
class MySchema(BaseModel):
    field: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "field": "example value"
            }
        }
```

These examples automatically appear in the OpenAPI schema and in `/docs`.

