import imaplib
import email
import os
from datetime import datetime, timedelta
import boto3
import tempfile
import re  # Agregamos el módulo de expresiones regulares para extraer el número de mes
import shutil
import codecs
import os
import subprocess

# Configuración de la cuenta de correo y servidor IMAP de Gmail
correo = "tu_correo@gmail.com"

# Contraseña de tu aplicación creada en Gmail.
contraseña = "elpassAPP"

# Ruta donde se descargan los archivos
ruta_destino = "C:\\Ejemplo\\williams\\Downloads\\CORREOS\\"


# Conectar al servidor IMAP de Gmail
imap = imaplib.IMAP4_SSL("imap.gmail.com")
imap.login(correo, contraseña)

# Seleccionar la bandeja de entrada
imap.select("inbox")

# Calcular la fecha de referencia (por ejemplo, el día actual menos un día)
fecha_referencia = (datetime.now() - timedelta(days=1)).strftime("%d-%b-%Y")

# Buscar correos electrónicos del remitente deseado (por ejemplo, mmontivero@elit.com.ar) desde la fecha de referencia
#search_criteria = f'FROM "notificaciones@sibs.com.ar"'
search_criteria = f'FROM "remitente_correo@gmail.com"'
status, email_ids = imap.search(None, search_criteria)

# Obtener los IDs de los correos encontrados
email_ids = email_ids[0].split()


# Configura las credenciales de AWS (si no las tienes configuradas en tu entorno)
aws_access_key_id = 'aws_access_key_id'
aws_secret_access_key = 'aws_secret_access_key'
region = 'us-east-1'
s3 = boto3.client('s3', region_name=region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
# Conexión a Amazon S3
#s3 = boto3.client('s3', region_name='us-east-1')  # Cambia 'us-east-1' a tu región

# Carpeta base en S3
carpeta_base = "archivos/"


# Mapeo de números de mes a nombres de meses
meses = {
    "01": "Enero",
    "02": "Febrero",
    "03": "Marzo",
    "04": "Abril",
    "05": "Mayo",
    "06": "Junio",
    "07": "Julio",
    "08": "Agosto",
    "09": "Septiembre",
    "10": "Octubre",
    "11": "Noviembre",
    "12": "Diciembre"
}

# Mapeo de los últimos dos dígitos del año a los años correspondientes
anios = {
    "22": "2022",
    "23": "2023",
    "24": "2024",
    "25": "2025"
    # Agrega más mapeos según sea necesario
}


# Función para crear la ruta local según el mes y el año
def crear_ruta_local(numero_mes, ultimos_dos_digitos_anio, filename):
    # Verificar si el número de mes está en el mapeo
    if numero_mes in meses:
        carpeta_mes = meses[numero_mes]
    else:
        carpeta_mes = "Otro Mes"

    # Verificar si los últimos dos dígitos del año están en el mapeo
    if ultimos_dos_digitos_anio in anios:
        carpeta_anio = anios[ultimos_dos_digitos_anio]
    else:
        carpeta_anio = "Otro Año"

    # Crear la ruta local con el año, el mes y el nombre completo del archivo
    ruta_local = os.path.join(ruta_destino, carpeta_anio, carpeta_mes, filename)
    return ruta_local

# Descargar los adjuntos de los correos encontrados y subirlos a S3
for email_id in email_ids:
    status, msg_data = imap.fetch(email_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])
    subject = msg['Subject']
    
    #Si el email tiene en su subjesct algo como " -OFFLINE"
    if '-OFFLINE' in subject:
            for part in msg.walk():        
                if part.get_content_disposition() and part.get("Content-Disposition").startswith("attachment"):
                    filename = part.get_filename()
            #tipo_archivo = filename[0:7]
            
            # Extraer el número de mes y los últimos dos dígitos del año del nombre del archivo (por ejemplo, "OFFLINEPF030723.txt" -> "07" y "23")
            numero_mes, ultimos_dos_digitos_anio = re.search(r'(\d{2})(\d{2})\.', filename).groups()
            if numero_mes and ultimos_dos_digitos_anio:
                # Crear la ruta local según el mes y el año
                ruta_local = crear_ruta_local(numero_mes, ultimos_dos_digitos_anio, filename)   
                             
                  # Verificar si el archivo ya existe en la ubicación local
                if not os.path.exists(ruta_local):
                    os.makedirs(os.path.dirname(ruta_local), exist_ok=True)  # Crear las carpetas necesarias
                    with open(ruta_local, 'wb') as f:
                        f.write(part.get_payload(decode=True))
                                                            
                # Ruta al ejecutable de WinSCP.com
                WINSCP_PATH = r'C:\\Program Files (x86)\WinSCP\\WinSCP.com'
                codecs.open(os.path.dirname(__file__) + "\comandos_descarga.txt", 'w', "utf-8").close()
                commandsFile = codecs.open(os.path.dirname(__file__) + "\comandos_descarga.txt", "w+", "utf-8")                                                        
                
                commandsFile.write("open sftp://bitnami@184.214.552.33/ -privatekey=\"" + os.path.dirname(__file__) + "\\aws-lightsail-key.ppk\"\r\n")           
                commandsFile.write("cd /opt/bitnami/apache/htdocs/archivos_offline\r\n")
                # Upload the file to current working directory
                commandsFile.write("put -permissions=777 " + ruta_local + "\r\n")
                commandsFile.write("close\r\n")
                commandsFile.write("exit\r\n")
                commandsFile.close()   
                                
                # Ejecuta el comando WINCP                
                try:
                    subprocess.run([WINSCP_PATH, "/script=" + os.path.dirname(__file__) + "\comandos_descarga.txt"], shell=True)
                    
                    print("Se subio el archivo a SFTP.")                    
                except subprocess.CalledProcessError as e:                    
                    print(f"No se subió el archivo al SFTP': {e}")
                    
                                                       
                # Verificar si el número de mes está en el mapeo
                if numero_mes in meses:
                    carpeta_mes = meses[numero_mes]
                else:
                    carpeta_mes = "Otro Mes"

                # Verificar si los últimos dos dígitos del año están en el mapeo
                if ultimos_dos_digitos_anio in anios:
                    carpeta_anio = anios[ultimos_dos_digitos_anio]
                else:
                    carpeta_anio = "Otro Año"
            else:
                # En caso de que no se pueda extraer el número de mes o los últimos dos dígitos del año, utilizar carpetas por defecto
                carpeta_mes = "Otro Mes"
                carpeta_anio = "Otro Año"

            # Crear la ruta en S3 con el año y el mes (por ejemplo, "2023 - Julio/")
            carpeta_s3 = f"{carpeta_anio} - {carpeta_mes}/"

            # Verificar si el archivo ya existe en S3
            s3_object_key = carpeta_base + carpeta_s3 + filename
                        
            try:
                s3.head_object(Bucket="pagofacildescargas", Key=s3_object_key)
                print(f"El archivo {filename} ya existe en S3, no se subirá nuevamente.")
            except Exception as e:
                # El archivo no existe en S3, subirlo
                with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                    temp_file.write(part.get_payload(decode=True))

                # Subir el archivo temporal a S3
                with open(temp_file.name, 'rb') as f:
                    s3.upload_fileobj(f, "pagofacildescargas", s3_object_key)
                    
                

                # Eliminar el archivo temporal
                os.remove(temp_file.name)


    
# Cerrar la conexión IMAP
imap.logout()

