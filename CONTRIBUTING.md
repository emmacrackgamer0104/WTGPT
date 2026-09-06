# Contribuir a WTGPT

¡Ayuda a ampliar la base de datos de WTGPT! 🚀

WTGPT necesita información de muchos vehículos de War Thunder, y la comunidad puede colaborar añadiendo vehículos y corrigiendo datos.

## Añadir un vehículo

La forma recomendada es abrir una **Issue** usando la plantilla `Agregar vehículo`.

Incluye, siempre que sea posible:

- Nombre exacto del vehículo
- Nación
- Tipo: Tanque, Avión, Helicóptero o Naval
- BR
- Rol
- Fuente de los datos

No inventes estadísticas. Si un dato no está confirmado, déjalo como `null` o indícalo como pendiente.

## Cambios mediante Pull Request

También puedes proponer cambios directamente en `vehicles.json` mediante un Pull Request. Los cambios serán revisados antes de incorporarse a la base principal.

### Formato de vehículo

```json
{
  "name": "Nombre del vehículo",
  "nation": "Nación",
  "type": "Tanque",
  "br": null,
  "role": "Rol"
}
```

## Reglas básicas

1. No subas contraseñas, tokens, API keys ni otros secretos.
2. No elimines vehículos existentes sin explicar el motivo.
3. Evita duplicados.
4. Usa nombres consistentes y datos verificables.
5. Mantén `vehicles.json` como datos JSON válidos.

## Objetivo

Construir una base de datos comunitaria amplia y fiable para que WTGPT pueda analizar y comparar vehículos de War Thunder.
