from typing import List

def load_corpus() -> List[str]:
    """
    Carga corpus de 500+ palabras en español.
    Incluye palabras de diferentes categorías.
    """
    
    corpus = [
        # CONECTORES (30)
        "y", "o", "pero", "sin embargo", "además", "luego", "entonces",
        "porque", "puesto que", "ya que", "aunque", "mientras", "durante",
        "después", "antes", "luego", "finalmente", "inicialmente", "por lo tanto",
        "en conclusión", "es decir", "o sea", "es más", "incluso", "tampoco",
        "ni siquiera", "a pesar de", "por contra", "al contrario", "en cambio",
        
        # VERBOS FRECUENTES (60)
        "ser", "estar", "tener", "hacer", "ir", "venir", "decir", "dar",
        "poder", "deber", "querer", "saber", "ver", "creer", "hablar", "llevar",
        "dejar", "seguir", "encontrar", "buscar", "llamar", "llegar", "partir",
        "entrar", "salir", "subir", "bajar", "sentir", "pensar", "conocer",
        "recordar", "olvidar", "esperar", "empezar", "terminar", "continuar",
        "comenzar", "parar", "cambiar", "aumentar", "disminuir", "mejorar",
        "empeorar", "ayudar", "servir", "trabajar", "estudiar", "aprender",
        "enseñar", "escuchar", "mirar", "escribir", "leer", "contar", "vivir",
        "morir", "nacer", "crecer", "beber", "comer", "dormir", "despertar",
        "cantar", "bailar", "jugar", "ganar", "perder", "comprar", "vender",
        
        # ADJETIVOS (50)
        "bueno", "malo", "grande", "pequeño", "nuevo", "viejo", "joven",
        "bonito", "feo", "hermoso", "horrible", "agradable", "desagradable",
        "rápido", "lento", "fuerte", "débil", "alto", "bajo", "largo", "corto",
        "ancho", "estrecho", "grueso", "delgado", "caliente", "frío", "tibio",
        "seco", "mojado", "limpio", "sucio", "claro", "oscuro", "brillante",
        "apagado", "fuerte", "suave", "duro", "blando", "áspero", "liso",
        "pesado", "ligero", "profundo", "superficial", "lleno", "vacío",
        "entero", "roto", "nuevo", "usado", "común", "raro", "especial",
        
        # SUSTANTIVOS BÁSICOS (80)
        "casa", "coche", "persona", "tiempo", "agua", "tierra", "fuego",
        "aire", "luz", "oscuridad", "color", "sonido", "música", "palabra",
        "voz", "mirada", "mano", "pie", "cabeza", "corazón", "mente", "cuerpo",
        "vida", "muerte", "amor", "odio", "miedo", "alegría", "tristeza",
        "esperanza", "duda", "certeza", "verdad", "mentira", "mentiroso",
        "dinero", "precio", "costo", "valor", "riqueza", "pobreza", "trabajo",
        "descanso", "noche", "día", "mañana", "tarde", "noche", "hora",
        "minuto", "segundo", "segundo", "semana", "mes", "año", "siglo",
        "momento", "instante", "eternidad", "primavera", "verano", "otoño",
        "invierno", "número", "cifra", "cantidad", "calidad", "razón", "motivo",
        "causa", "efecto", "resultado", "conclusión", "comienzo", "fin", "mitad",
        "parte", "todo", "conjunto", "grupo", "multitud", "masa", "clase",
        "tipo", "especie", "forma", "figura", "objeto", "cosa", "asunto",
        "tema", "idea", "pensamiento", "sentimiento", "emoción", "pasión",
        
        # PREPOSICIONES (20)
        "en", "de", "a", "por", "para", "con", "sin", "sobre", "bajo",
        "entre", "hacia", "desde", "hasta", "dentro", "fuera", "arriba",
        "abajo", "delante", "detrás", "cerca", "lejos",
        
        # ARTÍCULOS Y PRONOMBRES (25)
        "el", "la", "lo", "un", "una", "unos", "unas", "los", "las",
        "este", "ese", "aquel", "esta", "esa", "aquella", "esto", "eso",
        "aquello", "yo", "tú", "él", "ella", "nosotros", "vosotros",
        "ellos", "ellas", "mío", "tuyo", "suyo", "nuestro",
        
        # ADVERBIOS (40)
        "muy", "poco", "bastante", "demasiado", "apenas", "así", "ahora",
        "aún", "hoy", "mañana", "ayer", "siempre", "nunca", "jamás",
        "a veces", "algunas veces", "frecuentemente", "raramente", "aquí",
        "allí", "allá", "cerca", "lejos", "arriba", "abajo", "dentro", "fuera",
        "delante", "detrás", "bien", "mal", "mejor", "peor", "fácilmente",
        "difícilmente", "posiblemente", "probablemente", "ciertamente", "realmente",
        "verdaderamente", "completamente", "parcialmente", "más", "menos",
        
        # PALABRAS FUNCIONALES (35)
        "también", "tampoco", "qué", "cuál", "cuándo", "dónde", "cómo",
        "cuánto", "cuántos", "cuán", "si", "cuando", "donde", "como",
        "cuanto", "cuantos", "quien", "quienes", "cual", "cuales", "cuánto",
        "cuántos", "cuáles", "cuán", "sí", "no", "nunca", "jamás", "siempre",
        "posiblemente", "probablemente", "acaso", "quizá", "quizás", "tal",
        "tal vez",
        
        # PALABRAS ESPAÑOLAS ADICIONALES (100)
        "amigo", "amiga", "enemigo", "enemiga", "hermano", "hermana", "padre",
        "madre", "hijo", "hija", "abuelo", "abuela", "nieto", "nieta",
        "tío", "tía", "primo", "prima", "esposo", "esposa", "marido", "pareja",
        "nombre", "apellido", "edad", "cumpleaños", "muerte", "nacimiento",
        "boda", "divorcio", "matrimonio", "hombre", "mujer", "niño", "niña",
        "bebé", "adolescente", "adulto", "anciano", "anciana", "raza", "religión",
        "idioma", "lengua", "país", "ciudad", "pueblo", "capital", "estado",
        "región", "provincia", "río", "montaña", "bosque", "selva", "desierto",
        "playa", "costa", "isla", "océano", "mar", "lago", "laguna", "pozo",
        "puente", "camino", "calle", "avenida", "plaza", "parque", "jardín",
        "iglesia", "templo", "sinagoga", "mezquita", "monumento", "edificio",
        "castillo", "fortaleza", "muralla", "torre", "puerta", "ventana",
        "techo", "piso", "habitación", "cocina", "baño", "salón", "dormitorio",
        "comedor", "biblioteca", "oficina", "fábrica", "tienda", "mercado",
        "restaurante", "bar", "café", "escuela", "universidad", "hospital",
        "medicina", "enfermedad", "salud", "medicina", "doctor", "enfermera",
        "paciente", "cura", "síntoma", "remedio", "cura", "sanación", "muerte",
    ]
    
    return corpus