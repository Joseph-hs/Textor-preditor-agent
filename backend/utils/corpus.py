from typing import List

RAW_CORPUS = """
Hoy quiero escribir un mensaje claro y directo.
Necesito ordenar mis ideas antes de empezar el informe.
Quiero redactar una respuesta breve pero amable.
El texto debe sonar natural y fácil de entender.
Cada párrafo tiene que aportar una idea concreta.
Es mejor usar frases cortas cuando la explicación es compleja.
También conviene mantener un tono cercano y profesional.
Si una palabra no aporta valor, es mejor quitarla.
La introducción presenta el tema principal del documento.
Después desarrollo los puntos más importantes con calma.
Al final cierro el texto con una conclusión simple.
Primero reviso el contexto y luego propongo una solución.
Cuando el problema es ambiguo, necesito más ejemplos reales.
La precisión mejora cuando el modelo entiende el contexto.
Una buena sugerencia debe aparecer en el momento correcto.
El usuario escribe mejor cuando la interfaz no distrae.
Quiero que el sistema aprenda sin romper el flujo de escritura.
Las recomendaciones deben ser útiles y fáciles de aceptar.
Si la predicción falla, la experiencia se vuelve más lenta.
Por eso necesito sugerencias más estables y precisas.
La herramienta funciona mejor con frases reales en español.
Un corpus pequeño puede servir, pero limita el contexto.
Un corpus más amplio permite aprender patrones frecuentes.
Sin embargo, la calidad del corpus importa más que el tamaño.
No basta con guardar palabras sueltas sin relación entre ellas.
El modelo necesita ejemplos de cómo se conectan las ideas.
Por lo tanto, conviene entrenar con oraciones completas.
También ayuda incluir preguntas, respuestas y explicaciones.
En muchos casos, la siguiente palabra depende de varias anteriores.
Por esa razón, el contexto corto no siempre es suficiente.
La frase empieza con una intención y termina con un objetivo.
Quiero escribir una propuesta para mejorar el producto.
Necesito presentar los cambios con argumentos claros.
El equipo quiere una solución simple de mantener.
La aplicación debe abrir rápido y responder sin demora.
Cuando una persona escribe, espera continuidad y no fricción.
Cada sugerencia debería ahorrar tiempo al usuario.
La predicción ideal completa la idea sin cambiar el tono.
En una conversación formal, el vocabulario suele ser más preciso.
En un mensaje casual, el lenguaje puede ser más flexible.
La misma palabra cambia de peso según la oración.
Por ejemplo, una respuesta técnica requiere términos concretos.
En cambio, una nota breve puede usar palabras más comunes.
Necesito entender por qué una sugerencia fue seleccionada.
También quiero saber cuándo una recomendación fue ignorada.
Esos datos ayudan a medir el valor real del sistema.
La precisión no depende solo del modelo neuronal.
También depende de la tokenización y de la limpieza del texto.
Si la entrada y el corpus no comparten la misma normalización, fallan las coincidencias.
Los acentos pueden afectar la búsqueda si no se procesan bien.
La letra ñ debe mantenerse porque cambia el significado.
No es lo mismo decir ano que decir año.
El sistema debe reconocer palabras con y sin tilde.
Si el usuario escribe rapido, aún debería sugerir rápido.
Si escribe cancion, el modelo debe entender canción.
Ese tipo de tolerancia mejora mucho la experiencia.
El autocompletado y la predicción de siguiente palabra no son lo mismo.
Cuando la última palabra está incompleta, conviene completar el prefijo.
Cuando la oración ya cerró una palabra, conviene sugerir la siguiente.
Separar esos dos casos mejora el ranking final.
Una lista de sugerencias desordenada genera desconfianza.
Una lista coherente transmite sensación de inteligencia.
Quiero que el texto sugerido respete el estilo del usuario.
Si una persona usa ciertas palabras con frecuencia, el sistema debe recordarlo.
Con el tiempo, esa memoria vuelve más personal la experiencia.
La adaptación debe ser gradual para no sesgar demasiado el resultado.
Un buen equilibrio mezcla contexto global y preferencias locales.
El motor de n gramas responde rápido y suele acertar en frases comunes.
El modelo recurrente ayuda cuando hay dependencias menos obvias.
Ambos enfoques funcionan mejor si comparten un vocabulario consistente.
Si el trie conoce la frecuencia de cada palabra, autocompleta con más criterio.
No todas las coincidencias por prefijo tienen el mismo valor.
Una palabra frecuente debería aparecer antes que una palabra rara.
La evaluación también necesita ejemplos representativos.
No tiene sentido medir solo casos fáciles y repetidos.
Quiero probar frases de trabajo, estudio y conversación diaria.
Necesito ejemplos con conectores, verbos y sustantivos frecuentes.
También quiero ver cómo responde el sistema ante preguntas.
¿Cómo puedo mejorar la precisión del modelo?
¿Qué cambios hacen falta para obtener mejores sugerencias?
La respuesta más útil suele empezar por el diagnóstico.
Después conviene priorizar los cambios de mayor impacto.
Primero se corrige la base de datos lingüística.
Luego se ajusta la lógica de predicción.
Después se mejora el aprendizaje personalizado.
Finalmente se compara el resultado con métricas reales.
El reporte debe incluir top uno, top tres y top cinco.
Así puedo saber si el sistema mejora de forma consistente.
Una buena métrica evita decisiones tomadas por intuición.
También conviene guardar ejemplos de aciertos y errores.
Cuando reviso esos casos, encuentro patrones que antes no veía.
Muchas fallas vienen de contextos demasiado cortos.
Otras aparecen porque la sugerencia correcta no está en el vocabulario.
Por eso ampliar el corpus sigue siendo importante.
Pero ampliar el corpus sin estructura no resuelve el problema.
Necesito datos limpios, variados y cercanos al uso real.
Un texto de prueba puede hablar sobre trabajo en equipo.
El equipo revisa el diseño antes de publicar una nueva versión.
La diseñadora propone una interfaz más limpia y serena.
El desarrollador implementa los cambios en el frontend y en el backend.
La persona que prueba la app espera una respuesta rápida.
Si la página tarda demasiado, la experiencia pierde calidad.
Cada detalle visual influye en la percepción del producto.
Los tonos crema y café pueden transmitir calma y claridad.
Una cabecera bien escrita guía mejor la interacción.
Un área de texto amplia invita a redactar con comodidad.
Los botones deben ser visibles sin romper la armonía general.
El sistema también puede sugerir verbos después de ciertos sujetos.
Yo quiero aprender a escribir con más precisión.
Tú puedes revisar el texto antes de enviarlo.
Ella necesita una conclusión breve para cerrar el correo.
Nosotros buscamos una solución práctica para el equipo.
Ellos quieren mejorar el rendimiento sin complicar el mantenimiento.
La expresión por eso aparece con frecuencia en textos explicativos.
La expresión en cambio suele introducir una idea de contraste.
La expresión sin embargo aparece con frecuencia en textos argumentativos.
La expresión por lo tanto conecta causas y conclusiones.
La expresión tal vez suele introducir una posibilidad.
A veces la palabra correcta depende del objetivo del mensaje.
En conclusión, el sistema mejora cuando entiende mejor las secuencias reales.
Por ahora quiero una base más sólida para seguir iterando.
Después podré experimentar con modelos más ambiciosos.
Mientras tanto, necesito que las sugerencias sean confiables.
Con una base consistente, el producto tendrá una evolución más clara.
"""


def load_corpus() -> List[str]:
    """
    Carga un corpus de oraciones reales para mejorar contexto y secuencia.
    """
    return [
        sentence.strip()
        for sentence in RAW_CORPUS.strip().splitlines()
        if sentence.strip()
    ]
