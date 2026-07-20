import logging


class BaseDatosLogHandler(logging.Handler):
    """
    Handler personalizado que guarda los logs del sistema en el modelo LogError,
    además del comportamiento normal de logging (consola/archivo).
    """

    def emit(self, record):
        # Import diferido: evita problemas de carga circular al iniciar Django
        from soporte.models import LogError

        nivel_map = {
            logging.INFO: LogError.Nivel.INFO,
            logging.WARNING: LogError.Nivel.WARNING,
            logging.ERROR: LogError.Nivel.ERROR,
            logging.CRITICAL: LogError.Nivel.CRITICAL,
        }
        nivel = nivel_map.get(record.levelno, LogError.Nivel.INFO)

        try:
            LogError.objects.create(
                nivel=nivel,
                modulo=record.name,  # ej. "django.request", "ventas.views"
                mensaje=self.format(record),
                traceback=self._extraer_traceback(record),
            )
        except Exception:
            # Si falla el guardado en BD (ej. BD caída), no queremos que
            # esto genere un loop infinito de errores. Se ignora silenciosamente.
            pass

    def _extraer_traceback(self, record):
        if record.exc_info:
            import traceback
            return ''.join(traceback.format_exception(*record.exc_info))
        return ''