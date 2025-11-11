1) Una vez clonado el repositorio, te encontrarás en la rama Main. Por lo tanto, abriras la terminal y el primer paso es utilizar el comando: "git fetch origin" para traer los cambios del repositorio en remoto.

2) Creas una nueva rama a partir de la rama "develop" remota, que es la mas actualizada. Lo haces usando este comando: "git checkout -b develop origin/develop". Una vez utilizado ese comando te encontrarás en la nueva rama.

3) A continuación crearas un entorno virtual con el comando: "python -m venv venv"

4) Accederás al entorno virtual con el comando: "venv/Scripts/activate". Sino te funciona ese comando, usa: ".\venv\Scripts\activate"

5) Una vez estes dentro del entorno virtual (el cual estará en curso si se ejecuto bien el paso anterior) se deben instalar las dependencias del proyecto con el comando: "pip install -r requirements.txt".

6) Ahora, deberás crear un archivo .env el cual contendrá esta información:

# Database Configuration PostgreSQL
DB_NAME=Finanzas-Backend-DB
DB_USER=postgres
DB_PASSWORD=2016kawaii
DB_HOST=127.0.0.1
DB_PORT=5432

#DATABASE_URL=sqlite:///db.sqlite
# Email Configuration
EMAIL_HOST_USER=sado56hdgm@gmail.com
EMAIL_HOST_PASSWORD=orfl vkzn dern pbos
DEFAULT_FROM_EMAIL=Soporte DS2 <sado56hdgm@gmail.com>

7) abre tu pgAdmin para crear la base de datos, los datos deberán de coindir con la configuración de PostgreSQL del paso anterior. Una vez hecho, con este comando sabrás si tu potgress esta en curso: "Get-Service | findstr postgre
"
8) Con la base de datos creada, ejecuta las migraciones para que Django genere las tablas necesarias dentro de ella.
Usa los siguientes comandos:"
python manage.py makemigrations
python manage.py migrate
"
Esto asegura que la estructura de la base de datos coincida con los modelos del proyecto.

9) Finalmente corre el servidor por medio del comando: "python manage.py runserver" y con ello todo el proyecto estaría inicializado.