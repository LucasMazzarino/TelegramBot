# ChatBot de Telegram

Este proyecto es un bot de Telegram que proporciona varias funcionalidades interactivas para los usuarios. El bot está construido utilizando Python y la biblioteca `python-telegram-bot`, con soporte para manejar mensajes, obtener información meteorológica y gestionar recordatorios.

## Funcionalidades

### 1. Menú Principal

Cuando un usuario inicia el bot con el comando `/start`, se le presenta un menú principal con las siguientes opciones:
- **¡Quiero saber el clima!**: Permite a los usuarios consultar el clima actual de una ubicación.
- **¡Quiero contar!**: Permite a los usuarios iniciar un contador y ver su valor actual.
- **Agregar Recordatorio**: Permite a los usuarios establecer recordatorios para tareas.

### 2. Consulta del Clima

- **Descripción**: Los usuarios pueden obtener la información del clima actual de una ubicación específica.
- **Cómo Funciona**:
  1. El usuario selecciona la opción "¡Quiero saber el clima!".
  2. El bot solicita la ubicación en el formato "Ciudad, País".
  3. El bot consulta la API de OpenWeatherMap y devuelve la descripción del clima y la temperatura.
   4. Basado en la descripción del clima, el bot proporciona una recomendación (por ejemplo, "Lleva un paraguas" si está lloviendo).

### 3. Contador

- **Descripción**: Los usuarios pueden mantener un contador que se incrementa cada vez que interactúan con la opción de contar.
- **Cómo Funciona**:
  1. El usuario selecciona la opción "¡Quiero contar!".
  2. El bot muestra el valor actual del contador.
  3. Cada vez que el usuario selecciona la opción, el contador se incrementa en uno, el mismo es unico para cada usuario.

### 4. Funcionalidad Libre: Programar Recordatorio

- **Descripción**: Los usuarios pueden programar recordatorios para tareas específicas.
- **Cómo Funciona**:
  1. El usuario selecciona la opción "Agregar Recordatorio".
  2. El bot solicita el formato del recordatorio: 'tarea en X minutos' o 'tarea a las HH:MM'.
  3. El bot procesa la entrada y guarda el recordatorio.
  4. En el momento programado, el bot envía un mensaje al usuario con el recordatorio.

  Elegi agregar esta funcionalidad ya que me aprecio interesante la funcionalidad de enviar mensajes en forma de recordatorio ademas que es algo que yo mismo usaria.

## Instalación

Para instalar el proyecto, sigue estos pasos:

1. **Crear un entorno virtual (opcional pero recomendado):**

   Decidi utilizar Virtualenv para crear un entorno virtual para la instalacion de las dependencias del projecto para evitar conflictos con paquetes ya instalados en el sistema. Puedes crear un entorno virtual utilizando `virtualenv`:

   ```bash
   pip install virtualenv
   python -m venv env


## Configuración

1. Cree un archivo `.env` en el directorio raíz del proyecto para almacenar las API_KEY. Ese archivo siempre se omite del repositorio con el .gitignore, pero para este caso aprticular de challenge lo dejare en el repositorio

## Uso

1. Ejecuta el bot:
    ```bash
    python main.py
    ```

2. Interactúa con el bot en Telegram para usar las funcionalidades descritas.

## Funcionalidades faltantes

1. Dado el escaso tiempo no pude completar la funcion de analizar el comentario usando la API de Openai.


## Aclaraciones

1. Para mejorar la legibilidad del código decí 2 cosas. Primero, agregue algunos comentarios en las partes del código que podrían llegar a ser más complicadas de entender. Segundo, por más que Python es un lenguaje no típado decidí agregar tirado a las variables para mejorar la legibilidad y comprensión del código, además de que es una buena práctica para proyectos más grandes o de colaboración.

