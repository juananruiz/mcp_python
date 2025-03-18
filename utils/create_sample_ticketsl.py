import mysql.connector
from datetime import datetime, timedelta
import random

# Conexión a la base de datos
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="tlaquepaque891",
            database="peticiones"
        )
        print("Conexión exitosa a la base de datos")
        return conn
    except mysql.connector.Error as err:
        print(f"Error de conexión: {err}")
        return None

# Función para obtener IDs existentes
def get_existing_ids(conn, table_name, id_column="id"):
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {id_column} FROM {table_name}")
        ids = [row[0] for row in cursor.fetchall()]
        return ids
    except mysql.connector.Error as err:
        print(f"Error al obtener IDs de {table_name}: {err}")
        return []
    finally:
        cursor.close()

# Datos de ejemplo para los tickets
def generate_sample_data(user_ids, category_ids):
    if not user_ids or not category_ids:
        print("No hay usuarios o categorías disponibles para crear tickets")
        return []
    
    titulos = [
        "Error al iniciar sesión en el sistema",
        "Solicitud de nuevo equipo informático",
        "Problema con la impresora de la planta 2",
        "Actualización de software necesaria",
        "Fallo en la conexión a internet",
        "Solicitud de acceso a la base de datos",
        "Problema con el correo electrónico",
        "Solicitud de formación en Excel avanzado",
        "Instalación de nuevo software",
        "Problema con la VPN corporativa"
    ]
    
    descripciones = [
        "No puedo acceder al sistema con mis credenciales habituales. He intentado restablecer la contraseña pero sigo sin poder entrar.",
        "Necesito un nuevo ordenador para el departamento de marketing. El actual tiene más de 5 años y es muy lento.",
        "La impresora de la planta 2 muestra un error de papel atascado, pero no hay ningún papel atascado visible.",
        "Necesito actualizar el software de diseño gráfico a la última versión para poder abrir archivos de clientes.",
        "Desde esta mañana no puedo conectarme a internet desde mi puesto de trabajo. Otros compañeros no tienen este problema.",
        "Solicito acceso a la base de datos de clientes para poder realizar informes de ventas mensuales.",
        "No recibo correos externos desde hace dos días. Los correos internos funcionan correctamente.",
        "Solicito formación en Excel avanzado para poder mejorar la gestión de datos del departamento.",
        "Necesito que se instale el software de videoconferencia en mi equipo para reuniones con clientes internacionales.",
        "No puedo conectarme a la VPN corporativa desde mi domicilio. He seguido todos los pasos del manual."
    ]
    
    estados = ['open', 'in_progress', 'resolved', 'closed']
    prioridades = ['low', 'medium', 'high', 'critical']
    
    tickets = []
    now = datetime.now()
    
    for i in range(min(len(titulos), len(user_ids) * 2)):  # Crear hasta 2 tickets por usuario
        estado = random.choice(estados)
        fecha_creacion = now - timedelta(days=random.randint(1, 30))
        fecha_actualizacion = fecha_creacion + timedelta(days=random.randint(1, 5))
        fecha_resolucion = fecha_actualizacion + timedelta(days=random.randint(1, 10)) if estado in ['resolved', 'closed'] else None
        
        requester_id = random.choice(user_ids)
        assignee_id = random.choice(user_ids)
        category_id = random.choice(category_ids)
        
        ticket = {
            'title': titulos[i],
            'description': descripciones[i],
            'status': estado,
            'priority': random.choice(prioridades),
            'created_at': fecha_creacion,
            'updated_at': fecha_actualizacion,
            'resolved_at': fecha_resolucion,
            'category_id': category_id,
            'requester_id': requester_id,
            'assignee_id': assignee_id,
            'sla_due_date': fecha_creacion + timedelta(days=random.randint(3, 7))
        }
        tickets.append(ticket)
    
    return tickets

# Función para insertar tickets en la base de datos
def insert_tickets(conn, tickets):
    if not tickets:
        print("No hay tickets para insertar")
        return
    
    cursor = conn.cursor()
    try:
        for ticket in tickets:
            query = """
            INSERT INTO tickets (
                title, description, status, priority, 
                created_at, updated_at, resolved_at,
                category_id, requester_id, assignee_id, sla_due_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                ticket['title'], ticket['description'], ticket['status'], ticket['priority'],
                ticket['created_at'], ticket['updated_at'], ticket['resolved_at'],
                ticket['category_id'], ticket['requester_id'], ticket['assignee_id'], ticket['sla_due_date']
            )
            cursor.execute(query, values)
        
        conn.commit()
        print(f"Se han insertado {len(tickets)} tickets en la base de datos")
    except mysql.connector.Error as err:
        print(f"Error al insertar tickets: {err}")
    finally:
        cursor.close()

# Función principal
def main():
    conn = connect_to_db()
    if conn:
        # Obtener IDs existentes
        user_ids = get_existing_ids(conn, "users")
        category_ids = get_existing_ids(conn, "categories")
        
        print(f"Usuarios disponibles: {len(user_ids)}")
        print(f"Categorías disponibles: {len(category_ids)}")
        
        # Generar y insertar tickets
        tickets = generate_sample_data(user_ids, category_ids)
        insert_tickets(conn, tickets)
        
        conn.close()
        print("Proceso completado")

if __name__ == "__main__":
    main()
