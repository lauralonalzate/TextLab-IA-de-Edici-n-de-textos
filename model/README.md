# Modelo de Corrección de Textos

## Descripción
Este módulo contiene el modelo MVP para corrección de textos usando la API de DeepSeek.

## Autor
Laura Londono Alzate

## Uso

### Importar el modelo
```python
from model.text_correction import TextCorrectionModel

# Crear instancia
modelo = TextCorrectionModel(api_key="sk-8a962e866b444597a4adea698ba3a28b")

# Corregir texto
resultado = modelo.corregir_texto("texto con herrores")

print(resultado)
```

### Respuesta esperada
```python
{
    "success": True,
    "texto_original": "texto con herrores",
    "texto_corregido": "texto con errores",
    "mensaje": "Texto corregido exitosamente"
}
```

## Requisitos
- Python 3.7+
- requests

## API Key
1. Visita https://platform.deepseek.com
2. Regístrate o inicia sesión
3. Ve a la sección de API keys
4. Genera una nueva key

## Notas para el equipo
- El backend debe pasar la API key como variable de entorno
- El modelo devuelve un diccionario con el resultado
- Incluye manejo de errores para casos edge
