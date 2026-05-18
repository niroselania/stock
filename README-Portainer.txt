Buscador de stock - Portainer

Archivos incluidos:
- stock-buscador.html: la app.
- Dockerfile: arma una imagen Nginx con la app como index.html.
- nginx.conf: configuracion del servidor web.
- docker-compose.yml: Stack para Portainer.

Opcion recomendada en Portainer con Stack:
1. Subi esta carpeta a un repositorio Git o a una carpeta accesible por tu servidor Docker.
2. En Portainer entra a Stacks > Add stack.
3. Elegi Repository si lo subiste a Git, o usa Web editor si ya tenes la imagen creada.
4. Usa este compose:

services:
  stock-buscador:
    build: .
    container_name: stock-buscador
    restart: unless-stopped
    ports:
      - "8088:80"

5. Deploy the stack.
6. Abrilo en http://IP-DE-TU-SERVIDOR:8088

Si Portainer no permite build desde tu metodo de carga:
1. Crea la imagen en el servidor con:
   docker build -t stock-buscador:latest .

2. En Portainer usa este compose:

services:
  stock-buscador:
    image: stock-buscador:latest
    container_name: stock-buscador
    restart: unless-stopped
    ports:
      - "8088:80"

Notas:
- Si el puerto 8088 esta ocupado, cambialo por otro, por ejemplo "8090:80".
- La planilla Excel se carga desde el navegador de cada usuario; no queda guardada en el servidor.
