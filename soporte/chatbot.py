from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Dataset de entrenamiento: frases de ejemplo por intención.
# Mientras más variedad de frases agregues, mejor detecta el modelo.
DATOS_ENTRENAMIENTO = {
    "horarios": [
        "cual es el horario", "a que hora abren", "a que hora cierran",
        "que dias atienden", "estan abiertos ahora", "horario de atencion",
        "hasta que hora puedo comprar", "cuando abren la tienda",
        "en que horario trabajan", "todos los dias abren",
        "atienden los domingos", "atienden feriados",
        "hasta que hora entregan pedidos", "horarios de tienda",
        "estan atendiendo ahorita", "a que ora abren", "que horario tienen",
        "trabajan las 24 horas", "abren los feriados",
        "puedo comprar de madrugada", "hasta que hora funcionan",
    ],
    "pagos": [
        "que metodos de pago aceptan", "puedo pagar con yape",
        "aceptan plin", "puedo pagar con tarjeta", "se puede pagar en efectivo",
        "como pago mi pedido", "formas de pago disponibles", "puedo pagar contra entrega",
        "con que puedo pagar", "aceptan visa", "aceptan mastercard",
        "puedo pagar cuando me llegue el pedido", "que tarjetas aceptan",
        "se puede pagar por transferencia", "puedo pagar en efectivo al repartidor",
        "cuales son las formas de pago", "aceptan pago movil",
        "se puede pagar con yape o plin", "como cancelo mi compra con tarjeta",
        "tienen pago contraentrega",
    ],
    "entregas": [
        "cuanto demora la entrega", "a que zonas hacen envios",
        "cuanto cuesta el envio", "hacen entregas a todo lima",
        "tiempo de entrega estimado", "cuales son las zonas de reparto",
        "costo de delivery", "cuanto se demoran en llegar",
        "hacen delivery a mi zona", "cuanto cuesta el delivery",
        "hasta donde hacen entregas", "cuanto tiempo tarda mi pedido",
        "en cuanto tiempo llega mi compra", "hacen envios a mi distrito",
        "cuanto es el costo de envio", "llegan rapido los pedidos",
        "puedo rastrear mi pedido", "donde esta mi pedido",
        "por que se demora tanto mi pedido",
    ],
    "pedido": [
        "como hago un pedido", "como compro en la pagina",
        "pasos para comprar", "como agrego productos al carrito",
        "como realizo una compra", "no se como comprar",
        "quiero comprar algo", "como funciona la compra",
        "como uso el carrito de compras", "quiero hacer un pedido",
        "necesito ayuda para comprar", "como se hace un pedido aqui",
        "quiero comprar productos", "no entiendo como comprar",
        "como agrego algo a mi carrito", "explicame como comprar",
    ],
    "cancelar": [
        "como cancelo mi pedido", "quiero cancelar una compra",
        "puedo anular mi pedido", "como anulo una orden",
        "ya no quiero mi pedido", "puedo cancelar despues de pagar",
        "como elimino un pedido", "quiero anular mi compra",
        "me equivoque en mi pedido puedo cancelarlo",
        "como hago para cancelar una orden",
    ],
    "soporte": [
        "quiero hablar con soporte", "necesito ayuda de un humano",
        "tengo un problema con mi pedido", "quiero hacer un reclamo",
        "como contacto a alguien", "necesito ayuda urgente",
        "quiero quejarme", "mi pedido llego mal", "tengo un reclamo",
        "necesito hablar con alguien de la tienda", "mi pedido nunca llego",
        "el producto llego dañado", "quiero hacer una queja",
        "necesito soporte tecnico", "como reporto un problema",
        "quiero contactar a un asesor",
    ],
    "productos": [
        "que productos tienen", "tienen frutas y verduras",
        "que marcas manejan", "tienen productos de limpieza",
        "hay ofertas disponibles", "tienen descuentos",
        "que categorias de productos hay", "buscan un producto especifico",
        "tienen stock de un producto", "hay promociones esta semana",
    ],
    "saludo": [
        "hola", "buenas", "buenos dias", "buenas tardes", "que tal",
        "hola como estas", "hey", "buenas noches", "hola buenas",
        "aloo", "hola necesito ayuda", "buenas quisiera preguntar",
    ],
    "despedida": [
        "gracias", "muchas gracias", "listo gracias", "ok gracias",
        "eso era todo gracias", "chau", "hasta luego", "nos vemos",
        "de acuerdo gracias por la ayuda", "perfecto muchas gracias",
    ],
}

RESPUESTAS = {
    "horarios": "Atendemos todos los días de 7:00 a.m. a 11:00 p.m. Nuestra tienda online está disponible las 24 horas.",
    "pagos": "Aceptamos Yape, Plin, tarjetas Visa/MasterCard, transferencia bancaria y pago contra entrega.",
    "entregas": "Hacemos entregas en Cercado, Norte, Sur y Este de Lima, cada zona con su propia tarifa y tiempo estimado. Puedes ver el detalle de tu envío en 'Mis pedidos'.",
    "pedido": "Para comprar: explora el catálogo, agrega productos al carrito, ve al checkout, elige zona/dirección y método de pago. ¡Así de fácil!",
    "cancelar": "Puedes cancelar un pedido no pagado desde la sección 'Mis pedidos', mientras no tenga un pago confirmado.",
    "soporte": "Puedes crear un ticket de soporte y nuestro equipo te contactará pronto.",
    "productos": "Contamos con abarrotes, frutas y verduras, productos de limpieza y más. Puedes explorar todo el catálogo y usar el buscador para encontrar algo específico.",
    "saludo": "¡Hola! Soy el asistente de Tienda Mass. Pregúntame sobre horarios, pagos, entregas o cómo hacer un pedido.",
    "despedida": "¡De nada! Si necesitas algo más, aquí estaré. Que tengas un buen día 😊",
    "desconocido": "No estoy seguro de haber entendido tu pregunta. ¿Podrías reformularla, o prefieres hablar con soporte?",
}

UMBRAL_CONFIANZA = 0.22


class ChatbotClasificador:
    def __init__(self):
        textos, etiquetas = [], []
        for intencion, frases in DATOS_ENTRENAMIENTO.items():
            for frase in frases:
                textos.append(frase)
                etiquetas.append(intencion)

        self.vectorizador = TfidfVectorizer()
        X = self.vectorizador.fit_transform(textos)

        self.modelo = MultinomialNB()
        self.modelo.fit(X, etiquetas)

    def predecir(self, mensaje):
        mensaje = mensaje.lower().strip()
        X = self.vectorizador.transform([mensaje])
        probabilidades = self.modelo.predict_proba(X)[0]
        clases = self.modelo.classes_

        idx_max = probabilidades.argmax()
        confianza = probabilidades[idx_max]
        intencion = clases[idx_max]

        if confianza < UMBRAL_CONFIANZA:
            return RESPUESTAS["desconocido"]

        return RESPUESTAS[intencion]


_clasificador = ChatbotClasificador()


def obtener_respuesta(mensaje):
    return _clasificador.predecir(mensaje)