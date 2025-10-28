"""
Modelo MVP para corrección de textos usando DeepSeek API
Autor: Laura Londono
Fecha: Octubre 2025
Proyecto: TextLab - Edición de textos con IA
"""

import requests
import json
from typing import Dict, Optional


class TextCorrectionModel:
    """
    Modelo simple para corregir textos usando la API de DeepSeek.
    Este modelo será consumido por el backend del proyecto.
    """
    
    def __init__(self, api_key: str):
        """
        Inicializa el modelo con la API key de DeepSeek
        
        Args:
            api_key (str): sk-8a962e866b444597a4adea698ba3a28b
        """
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
    def corregir_texto(self, texto_original: str) -> Dict:
        """
        Corrige un texto usando DeepSeek
        
        Args:
            texto_original (str): El texto a corregir
            
        Returns:
            dict: Diccionario con el texto original, corregido y metadata
        """
        # Validar que el texto no esté vacío
        if not texto_original or not texto_original.strip():
            return {
                "success": False,
                "texto_original": texto_original,
                "texto_corregido": None,
                "mensaje": "El texto no puede estar vacío"
            }
        
        try:
            # Preparar el prompt para DeepSeek
            prompt = f"""Eres un corrector de textos profesional en español. 
Tu tarea es corregir el siguiente texto manteniendo su significado original.
Corrige errores de:
- Ortografía
- Gramática
- Puntuación
- Redacción

Devuelve SOLO el texto corregido, sin explicaciones adicionales.

Texto a corregir:
{texto_original}"""
            
            # Preparar el payload para la API
            payload = {
                "model": "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "Eres un asistente experto en corrección de textos en español."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,  # Baja temperatura para respuestas más consistentes
                "max_tokens": 2000
            }
            
            # Hacer la petición a la API
            response = requests.post(
                self.api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            # Verificar si la petición fue exitosa
            response.raise_for_status()
            
            # Extraer el texto corregido
            resultado = response.json()
            texto_corregido = resultado['choices'][0]['message']['content'].strip()
            
            return {
                "success": True,
                "texto_original": texto_original,
                "texto_corregido": texto_corregido,
                "mensaje": "Texto corregido exitosamente"
            }
            
        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "texto_original": texto_original,
                "texto_corregido": None,
                "mensaje": f"Error en la petición a DeepSeek: {str(e)}"
            }
        except KeyError as e:
            return {
                "success": False,
                "texto_original": texto_original,
                "texto_corregido": None,
                "mensaje": f"Error al procesar la respuesta de la API: {str(e)}"
            }
        except Exception as e:
            return {
                "success": False,
                "texto_original": texto_original,
                "texto_corregido": None,
                "mensaje": f"Error inesperado: {str(e)}"
            }


def crear_modelo(api_key: str) -> TextCorrectionModel:
    """
    Función helper para crear una instancia del modelo.
    Útil para el backend.
    
    Args:
        api_key (str): sk-8a962e866b444597a4adea698ba3a28b
        
    Returns:
        TextCorrectionModel: Instancia del modelo
    """
    return TextCorrectionModel(api_key)


# Ejemplo de uso para pruebas
if __name__ == "__main__":
    print("=" * 60)
    print("MODELO DE CORRECCIÓN DE TEXTOS - MVP")
    print("TextLab - Edición de textos asistida")
    print("=" * 60)
    
    # IMPORTANTE: Para uso en producción, la API key debe venir de variables de entorno
    # Este es solo un ejemplo para pruebas
    API_KEY = "sk-8a962e866b444597a4adea698ba3a28b"
    
    # Validar que se configuró la API key
    if API_KEY == "sk-8a962e866b444597a4adea698ba3a28b":
        print("\n⚠️  ADVERTENCIA: Debes configurar tu API key de DeepSeek")
        print("Reemplaza 'sk-8a962e866b444597a4adea698ba3a28b' con tu clave real.\n")
    else:
        # Crear instancia del modelo
        modelo = TextCorrectionModel(API_KEY)
        
        # Texto de prueba con errores
        texto_prueba = """hola como estas yo estoi bien pero tengo que aser 
        un travajo de la universida y no se como empesar espero que todo salga vien"""
        
        print(f"\n📝 Texto original:\n{texto_prueba}\n")
        
        # Corregir el texto
        resultado = modelo.corregir_texto(texto_prueba)
        
        if resultado["success"]:
            print(f"✅ {resultado['mensaje']}\n")
            print(f"📖 Texto corregido:\n{resultado['texto_corregido']}\n")
        else:
            print(f"❌ {resultado['mensaje']}\n")
        
        print("=" * 60)
