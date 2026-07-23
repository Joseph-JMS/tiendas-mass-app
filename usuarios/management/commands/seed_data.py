from django.core.management.base import BaseCommand
from django.db import transaction

from catalogo.models import Categoria, Producto
from logistica.models import Zona
from usuarios.models import Usuario, PerfilCliente, PerfilEmpleado, PerfilRepartidor


class Command(BaseCommand):
    help = "Inicializa la base de datos con datos de prueba (usuarios, categorías, productos, zonas)"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Creando datos de prueba...")

        # --- ZONAS (distritos de Arequipa) ---
        zonas_data = [
            {"nombre": "Cercado", "tarifa_envio": 5.00, "tiempo_estimado_min": 30},
            {"nombre": "Yanahuara", "tarifa_envio": 6.00, "tiempo_estimado_min": 35},
            {"nombre": "Cayma", "tarifa_envio": 6.50, "tiempo_estimado_min": 40},
            {"nombre": "José Luis Bustamante y Rivero", "tarifa_envio": 7.00, "tiempo_estimado_min": 45},
            {"nombre": "Paucarpata", "tarifa_envio": 7.50, "tiempo_estimado_min": 50},
            {"nombre": "Cerro Colorado", "tarifa_envio": 8.00, "tiempo_estimado_min": 55},
        ]
        zonas = {}
        for z in zonas_data:
            zona, _ = Zona.objects.get_or_create(nombre=z["nombre"], defaults=z)
            zonas[z["nombre"]] = zona
        self.stdout.write(self.style.SUCCESS(f"  {len(zonas)} zonas listas"))

        # --- CATEGORÍAS ---
        categorias_data = ["Abarrotes", "Bebidas", "Lácteos", "Limpieza", "Frutas y Verduras", "Snacks"]
        categorias = {}
        for nombre in categorias_data:
            cat, _ = Categoria.objects.get_or_create(nombre=nombre)
            categorias[nombre] = cat
        self.stdout.write(self.style.SUCCESS(f"  {len(categorias)} categorías listas"))

        # --- PRODUCTOS ---
        productos_data = [
            {"nombre": "Arroz Costeño 5kg", "categoria": "Abarrotes", "precio": 18.90, "stock": 50},
            {"nombre": "Aceite Primor 1L", "categoria": "Abarrotes", "precio": 12.50, "stock": 40},
            {"nombre": "Fideos Don Vittorio 500g", "categoria": "Abarrotes", "precio": 4.20, "stock": 60},
            {"nombre": "Coca Cola 1.5L", "categoria": "Bebidas", "precio": 7.50, "stock": 35},
            {"nombre": "Agua San Luis 2.5L", "categoria": "Bebidas", "precio": 3.50, "stock": 45},
            {"nombre": "Leche Gloria 1L", "categoria": "Lácteos", "precio": 5.20, "stock": 30},
            {"nombre": "Yogurt Laive 1L", "categoria": "Lácteos", "precio": 8.90, "stock": 20},
            {"nombre": "Detergente Ariel 1kg", "categoria": "Limpieza", "precio": 15.00, "stock": 25},
            {"nombre": "Lejía Clorox 1L", "categoria": "Limpieza", "precio": 4.80, "stock": 3},  # stock bajo a propósito
            {"nombre": "Manzana Israel (kg)", "categoria": "Frutas y Verduras", "precio": 6.50, "stock": 40},
            {"nombre": "Plátano de seda (kg)", "categoria": "Frutas y Verduras", "precio": 3.80, "stock": 4},  # stock bajo
            {"nombre": "Papas Lays 150g", "categoria": "Snacks", "precio": 6.90, "stock": 50},
        ]
        for p in productos_data:
            Producto.objects.get_or_create(
                nombre=p["nombre"],
                defaults={
                    "categoria": categorias[p["categoria"]],
                    "precio": p["precio"],
                    "stock": p["stock"],
                    "stock_minimo": 5,
                    "activo": True,
                }
            )
        self.stdout.write(self.style.SUCCESS(f"  {len(productos_data)} productos listos"))

        # --- USUARIOS ---

        # Cliente de prueba
        if not Usuario.objects.filter(username="cliente_prueba").exists():
            cliente = Usuario.objects.create_user(
                username="cliente_prueba",
                email="cliente@mass.com",
                password="cliente123",
                rol=Usuario.Rol.CLIENTE,
                dni="12345678",
                telefono="987654321",
            )
            PerfilCliente.objects.create(usuario=cliente)
            self.stdout.write(self.style.SUCCESS("  Cliente creado: cliente_prueba / cliente123"))

        # Administrador de prueba (no superusuario, solo rol admin funcional)
        if not Usuario.objects.filter(username="admin_prueba").exists():
            Usuario.objects.create_user(
                username="admin_prueba",
                email="admin@mass.com",
                password="admin123",
                rol=Usuario.Rol.ADMIN,
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS("  Admin creado: admin_prueba / admin123"))

        # Repartidor de prueba (con sus 3 niveles: Usuario -> PerfilEmpleado -> PerfilRepartidor)
        if not Usuario.objects.filter(username="repartidor_prueba").exists():
            repartidor_user = Usuario.objects.create_user(
                username="repartidor_prueba",
                email="repartidor@mass.com",
                password="repartidor123",
                rol=Usuario.Rol.REPARTIDOR,
            )
            perfil_empleado = PerfilEmpleado.objects.create(
                usuario=repartidor_user,
                cargo=PerfilEmpleado.Cargo.COORDINADOR_ENTREGAS,
            )
            PerfilRepartidor.objects.create(
                empleado=perfil_empleado,
                zona=zonas["Cercado"],
                estado=PerfilRepartidor.Estado.DISPONIBLE,
            )
            self.stdout.write(self.style.SUCCESS("  Repartidor creado: repartidor_prueba / repartidor123"))

        # Usuario de soporte de prueba
        if not Usuario.objects.filter(username="soporte_prueba").exists():
            Usuario.objects.create_user(
                username="soporte_prueba",
                email="soporte@mass.com",
                password="soporte123",
                rol=Usuario.Rol.SOPORTE,
            )
            self.stdout.write(self.style.SUCCESS("  Soporte creado: soporte_prueba / soporte123"))

        self.stdout.write(self.style.SUCCESS("\n  Datos de prueba generados correctamente."))