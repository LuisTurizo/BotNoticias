import asyncio
import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os

# CONFIGURACIÓN DEL BOT
TOKEN = os.environ['TELEGRAM_BOT_TOKEN']
MI_CHAT_ID = "1259839619"
bot = Bot(token=TOKEN)

# URL de la página de noticias
URL = 'https://www.uniatlantico.edu.co/noticias/'

# Nombre del archivo donde se guarda el último titular enviado
ARCHIVO_ULTIMO_TITULAR = "ultimo_titular.txt"

# Intentar leer el último titular guardado desde el archivo
def obtener_ultimo_titular_guardado():
    if os.path.exists(ARCHIVO_ULTIMO_TITULAR):
        with open(ARCHIVO_ULTIMO_TITULAR, 'r') as file:
            return file.read().strip()
    return None

# Guardar el último titular enviado
def guardar_ultimo_titular(titular):
    with open(ARCHIVO_ULTIMO_TITULAR, 'w') as file:
        file.write(titular)

# Obtener los titulares más recientes de la página
def obtener_titulares():
    response = requests.get(URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    titulares = []

    for h3 in soup.find_all('h3'):
        enlace = h3.find('a')
        if enlace:
            texto = enlace.get_text(strip=True)
            url = enlace['href']
            if texto and url:
                titulares.append((texto, url))

    return titulares  # los titulares más recientes son los primeros en la lista

# Enviar los titulares nuevos
async def enviar_titulares(titulares):
    for titular, url in reversed(titulares):  # enviar del más viejo al más nuevo
        mensaje = f"📰 {titular}\n🔗 Lee más: {url}"
        try:
            await bot.send_message(chat_id=MI_CHAT_ID, text=mensaje)
            print(f"✅ Enviado: {titular}")
        except Exception as e:
            print(f"❌ Error al enviar: {titular}")
            print(f"🛑 Detalle del error: {e}")

async def main():
    ultimo_titular = obtener_ultimo_titular_guardado()  # obtener el último enviado
    while True:
        titulares = obtener_titulares()
        nuevos = []

        # Solo enviar los titulares que son más recientes que el último enviado
        for titular, url in titulares:
            if titular == ultimo_titular:  # Cuando encontramos el último enviado, dejamos de agregar
                break
            nuevos.append((titular, url))

        if nuevos:
            print(f"✉️ Enviando {len(nuevos)} titulares nuevos...")
            await enviar_titulares(nuevos)

        if titulares:
            ultimo_titular = titulares[0][0]  # actualizamos con el más reciente
            guardar_ultimo_titular(ultimo_titular)  # guardamos el último enviado

        await asyncio.sleep(300)  # espera 5 minutos

if __name__ == "__main__":
    asyncio.run(main())
