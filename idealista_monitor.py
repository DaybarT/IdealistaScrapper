from bs4 import BeautifulSoup
import requests
import json
from datetime import datetime
import time
import re
from zoneinfo import ZoneInfo
import random

from dotenv import load_dotenv

import atexit
import os
import signal
import sys

load_dotenv()


webhook_url = os.getenv("webhook_url")
intervalo = int(os.getenv("intervalo"))

MEMORY_FILE = 'memory.txt'
memoryData = set()

# Cargar memoria al iniciar
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, 'r') as f:
        memoryData = set(line.strip() for line in f if line.strip())

# Función para guardar memoria
def save_memory():
    with open(MEMORY_FILE, 'w') as f:
        for item in memoryData:
            f.write(f"{item}\n")
    print(f"[INFO] Memoria guardada con {len(memoryData)} elementos.")

# Registrar para guardar al salir
atexit.register(save_memory)

# También guardar si se interrumpe con Ctrl+C o kill
def signal_handler(sig, frame):
    print("\n[INFO] Interrupción detectada, guardando memoria...")
    save_memory()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# El resto de tu función `scrape` permanece igual...

def load_proxies():
    if os.path.exists("proxies.txt"):
        with open("proxies.txt", "r") as f:
            return [p.strip() for p in f if p.strip()]
    return []

def get_response_with_proxy_rotation(url):
    proxies_list = load_proxies()
    if not proxies_list:
        raise RuntimeError("🚫 No hay proxies disponibles en proxies.txt")

    random.shuffle(proxies_list)  # Aleatoriza el orden
    tried = []

    for proxy_url in proxies_list:
        proxy = {"http": proxy_url, "https": proxy_url}
        print(f"🛡 Intentando con proxy: {proxy_url}")
        try:
            response = requests.get(url, headers=HEADERS, proxies=proxy, timeout=10)
            response.raise_for_status()
            print("✅ Proxy funcionó")
            return response  # ¡Éxito!
        except requests.exceptions.RequestException as e:
            print(f"❌ Proxy falló: {e}")
            tried.append(proxy_url)
            continue

    sys.exit("Todos los proxies fallaron. Abortando ejecución.")

URL = "https://www.idealista.com/venta-viviendas/alovera-guadalajara/con-publicado_ultima-semana/?ordenado-por=fecha-publicacion-desc"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                  '(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'es-ES,es;q=0.9',
    'Referer': 'https://www.idealista.com/',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
}


def scrape(url: str):
    response = get_response_with_proxy_rotation(URL)
    if response:
        print(f"🔎 Longitud del contenido recibido: {len(response.text)}")
    print(response)
    content = BeautifulSoup(response.text, "html.parser")
    main = content.find('main', attrs={'id': 'main-content'})
    sectionItems = main.find('section', attrs={'class': 'items-container items-list'})
    homes = sectionItems.select('article[data-element-id]')

    for home in reversed(homes):
        # FOTO
        img_container = home.find('picture')
        img_tag = img_container.find('picture')
        img = img_tag.find('img').get('src') if img_tag else None

        # INFO
        info_container = home.find('div', class_='item-info-container')
        if not info_container:
            continue

        # Buscar el <a> con role='heading'
        title_tag = info_container.select_one('a[role="heading"]')

        # Extraer title y href
        titulo = title_tag['title'] if title_tag and 'title' in title_tag.attrs else None
        link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
        full_link = 'https://www.idealista.com' + link if link else None

        # Extraer identificador del href
        match = re.search(r'/inmueble/(\d+)/', link or '')
        identificador = match.group(1) if match else None

        # FILTRAR SOLO IDENTIFICADORES NUMÉRICOS (evita spam o banners)
        if not (identificador and identificador.isdigit()):
            print(f"Ignorado: identificador inválido - {link}")
            continue

        # PRECIO
        price_div = info_container.select_one('div.price-row')
        precio = None
        if price_div:
            price_span = price_div.find('span')
            precio = price_span.get_text(strip=True) if price_span else None



        # Si no está en memoria, es nuevo
        if identificador not in memoryData:
            obj = {
               'identificador': identificador,
    'foto': img,
    'time': datetime.now(ZoneInfo("Europe/Madrid")).strftime('%Y-%m-%d %H:%M:%S'),
    'titulo': titulo,
    'precio': precio,
    'link': full_link
            }

            # Enviar a donde tú quieras (ejemplo de POST)
            send_to_discord(obj)
            
            print(f"[{datetime.now()}] Enviado nuevo item: {titulo} ({precio})")

            # Agregar a memoria
            memoryData.add(identificador)
            time.sleep(5)
        else:
            print(f"[{datetime.now()}] Ya visto: {titulo}")


def send_to_discord(obj):

    embed = {
        "title": obj['titulo'],                # Título visible
        "url": obj['link'],                    # Hace el título clicable
        "description": f"**Precio:** {obj['precio']}\n**Hora:** {obj['time']}",
        "color": 5814783,                      # Color azul (decimal RGB)
        "image": {"url": obj['foto']},         # Imagen de la propiedad
        "footer": {"text": "Nuevo inmueble encontrado en Idealista"}
    }

    payload = {
        "username": "ScraperBot",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",  # opcional
        "embeds": [embed]
    }
    #para evitar el ratelimit
    response = requests.post(webhook_url, json=payload)
    if response.status_code != 204:
        print(f"Error enviando a Discord: {response.status_code} - {response.text}")
    else:
        print(f"Mensaje enviado a Discord: {obj['titulo']}")


# Zona horaria de España
zona_es = ZoneInfo("Europe/Madrid")

while True:
    ahora = datetime.now(tz=zona_es)
    hora = ahora.hour
    minuto = ahora.minute

    print(f"🕒 [{ahora.strftime('%Y-%m-%d %H:%M:%S')}] Verificando si debe ejecutarse...")

    # Convertimos hora y minutos a formato decimal (ej: 13:30 → 13.5)
    hora_decimal = hora + minuto / 60

    # Condiciones de ejecución permitidas
    if (
        (10.5 <= hora_decimal < 13.5) or  # 10:30 a 13:30
        (16.5 <= hora_decimal < 20.5)     # 16:30 a 20:30
    ):
        print(f"✅ Ejecutando scrape a las {ahora.strftime('%H:%M')}")
        try:
            scrape(URL)  # Llama a tu función scrape aquí
        except Exception as e:
            print(f"❌ Error durante scrape: {e}")
    else:
        print(f"⏸ Fuera de horario. No se ejecuta scrape.")

    time.sleep(1800)