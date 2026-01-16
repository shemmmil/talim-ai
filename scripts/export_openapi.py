#!/usr/bin/env python3
"""
Скрипт для экспорта OpenAPI схемы в JSON файл.
Используется для генерации типов TypeScript на фронтенде.
"""

import json
import sys
from pathlib import Path

# Добавляем корневую директорию в path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app
from fastapi.openapi.utils import get_openapi

def export_openapi_schema(output_path: str = "openapi.json"):
    """Экспортирует OpenAPI схему в JSON файл"""
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
    
    print(f"✅ OpenAPI схема экспортирована в {output_file.absolute()}")
    return output_file

if __name__ == "__main__":
    output_path = sys.argv[1] if len(sys.argv) > 1 else "openapi.json"
    export_openapi_schema(output_path)
