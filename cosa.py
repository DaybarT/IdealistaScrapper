# import requests
# from datetime import datetime

# test_embed = {
#     "title": "Prueba Imagen Idealista",
#     "url": "https://www.idealista.com/inmueble/107828892/",
#     "description": "**Precio:** 200.000 €",
#     "color": 5814783,
#     "image": {
#         "url": "https://img4.idealista.com/blur/480_360_mq/0/id.pro.es.image.master/a4/38/c1/1325553975.jpg"
#     },
#     "footer": {"text": "Test de imagen visible"}
# }

# payload = {
#     "username": "ScraperBot",
#     "embeds": [test_embed]
# }

# webhook_url = "https://discord.com/api/webhooks/1377973617412800542/CZpI7svt5qZ86DfetT7Nih9BLWxFqkydv4v3TrMtOmG4DYad-qjjwBnoiFhon-YVjt-z"
# r = requests.post(webhook_url, json=payload)
# print("Status:", r.status_code)
# print("Response:", r.text)
# # print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),)