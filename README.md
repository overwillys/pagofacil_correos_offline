"# pagofacil_correos_offline" 
1º Configurar IMAP en tu gmail
2º Obtene la contraseña creando una APP en la sección de Gmail activación en 2 pasos
3º Conecta tu Bucket de S3
4º Conecta tu wincp a tu Servidor usando una "key" suponiendo que se trate de un Ligtsail de amazon.
5 Ejecutar.


El script lo que hace es escanear tu bandeja de entrada de Gmail deacuerdo a un asunto específico.
Luego descargar el archivo.txt que trae como adjunto.
Abrirá dicho archivo, y comenzará a recopilar la información para luego, esta misma, poder hacer inserciones SQL.
A su vez, el archivo, se descargará en el disco y se subira a una bucket de S3.
También lo pondrá dentro de tu host, para poder usarlo en el sistema.

