#!/usr/bin/env python3
"""
Export OpenAPI schema from FastAPI app.

Usage:
    python export_openapi.py
"""
import json
import sys
from pathlib import Path

try:
    from app.main import app
    
    # Export as JSON
    schema = app.openapi()
    output_file = Path("openapi.json")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI schema exported to {output_file}")
    print(f"   Total endpoints: {len(schema.get('paths', {}))}")
    
    # Try to export as YAML
    try:
        import yaml
        yaml_file = Path("openapi.yaml")
        with open(yaml_file, "w", encoding="utf-8") as f:
            yaml.dump(schema, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
        print(f"✅ OpenAPI schema exported to {yaml_file}")
    except ImportError:
        print("ℹ️  PyYAML not installed. Install with: pip install pyyaml")
        print("   Only JSON format exported.")
    
except Exception as e:
    print(f"❌ Error exporting OpenAPI schema: {e}", file=sys.stderr)
    sys.exit(1)

