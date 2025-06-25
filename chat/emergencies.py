import requests
import json
import os
import asyncio
from datetime import datetime, timedelta, timezone as dt_timezone
import re
import hashlib
from django.conf import settings
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import sync_to_async
from django.utils import timezone
from chat.models import ChatRoom, Message
User = get_user_model()

# =============== Variables Estáticas de Generación de Alertas ================ #
SISMOS_API_URL = "http://www.funvisis.gob.ve/maravilla.json"
OPENWEATHER_API_KEY = getattr(settings, 'OPENWEATHER_API_KEY', None)
VENEZUELA_LAT = 10.4806
VENEZUELA_LON = -66.9036
OPENWEATHER_CURRENT_WEATHER_API_URL = f"https://api.openweathermap.org/data/2.5/weather?lat={VENEZUELA_LAT}&lon={VENEZUELA_LON}&appid={OPENWEATHER_API_KEY}&lang=es&units=metric"
RECOMENDACIONES_SISMOS = (
    "RECOMENDACIONES PARA SISMOS:\n"
    "\n<b>Antes del Sismo:</b>\n"
    "- Prepara un kit de emergencia (agua, alimentos, linterna, radio, botiquín).\n"
    "- Identifica zonas seguras en tu hogar (marcos de puertas, mesas resistentes).\n"
    "- Asegura objetos pesados y practica simulacros de evacuación.\n\n"
    "<b>Durante el Sismo:</b>\n"
    "- Mantén la calma y protégete en una zona segura.\n"
    "- Aléjate de ventanas, espejos y objetos que puedan caer.\n"
    "- Si estás en la calle, aléjate de edificios y postes de luz.\n\n"
    "<b>Después del Sismo:</b>\n"
    "- Revisa tu estado y el de los demás. Presta primeros auxilios si es necesario.\n"
    "- Evita encender fósforos o aparatos eléctricos hasta descartar fugas de gas.\n"
    "- Mantente informado a través de una radio a pilas.\n"
    "- Evacúa si tu hogar presenta daños graves y sigue las indicaciones de las autoridades.\n"
)

RECOMENDACIONES_METEOROLOGICAS = (
    "RECOMENDACIONES PARA ALERTAS METEOROLÓGICAS (TORMENTAS, LLUVIAS INTENSAS, HURACANES, VAGUADAS):\n"
    "- Permanece en un lugar seguro y evita salir durante eventos severos.\n"
    "- Desconecta aparatos eléctricos y protege tus objetos de valor.\n"
    "- No intentes cruzar ríos, quebradas o calles inundadas.\n"
    "- Mantente informado a través de fuentes oficiales (INAMEH, Protección Civil).\n"
    "- Prepara un kit de emergencia familiar y planifica una ruta de evacuación si vives en zonas de riesgo.\n"
)

# =============== Obtener usuario de Alertas Bot ================ #
@sync_to_async
def get_bot_user():
    try:
        return User.objects.get(username='alertas_bot')
    except User.DoesNotExist:
        print("ERROR: El usuario 'alertas_bot' no existe en la base de datos.")
        return None

# =============== Obtener Sala de Chat ================ #
@sync_to_async
def get_alertas_chat_room():
    return ChatRoom.get_alertas_chat_room()

# =============== Extracción y normalización de mensajes extraidos ================ #
def normalizar_mensaje(mensaje, is_sismo_message=False):
    match_sismo_id = re.search(r"data-sismo-id\s*=\s*['\"]([^'\"]*)['\"]", mensaje)
    if match_sismo_id:
        return match_sismo_id.group(1)

    if is_sismo_message:
        print(f"ADVERTENCIA_NORMALIZACION: Mensaje de sismo sin 'data-sismo-id' esperado: {mensaje[:50]}...")
        return "NO_SISMO_ID_FOUND_IN_MESSAGE"

    mensaje_sin_html = re.sub(r'<[^>]*>', '', mensaje)
    mensaje_normalizado = mensaje_sin_html.lower()
    mensaje_normalizado = re.sub(r'\s+', ' ', mensaje_normalizado).strip()
    mensaje_normalizado = re.sub(r'[^\w\s]', '', mensaje_normalizado)
    return mensaje_normalizado

# =============== Chequeo de alertas existentes ================ #
@sync_to_async
def check_message_exists_and_save(chat_room, sender_user, message_content, timestamp_obj, alert_type="normal"):
    incoming_identifier = normalizar_mensaje(message_content, is_sismo_message=alert_type.startswith("sismo_"))
    
    found_duplicate = False

    if alert_type.startswith("sismo_"):
        if incoming_identifier == "NO_SISMO_ID_FOUND_IN_MESSAGE":
            print(f"DEBUG_DEDUP: Sismo entrante sin ID válido, permitiendo guardar para corregir formato: {message_content[:50]}...")
            pass
        else:
            existing_bot_messages_query = Message.objects.filter(
                chatroom=chat_room,
                sender=sender_user,
                content__contains=f"data-sismo-id='{incoming_identifier}'"
            )
            
            print(f"DEBUG_DEDUP: Incoming Sismo ID: {incoming_identifier[:20]}...")

            for msg in existing_bot_messages_query:
                extracted_sismo_id = normalizar_mensaje(msg.content, is_sismo_message=True)
                print(f"DEBUG_DEDUP: Checking existing msg.content (partial): {msg.content[:100]}...")
                print(f"DEBUG_DEDUP: Extracted Sismo ID from existing: {extracted_sismo_id[:20] if extracted_sismo_id else 'None'}")
                
                if extracted_sismo_id and extracted_sismo_id == incoming_identifier:
                    found_duplicate = True
                    print(f"DEBUG_DEDUP: DUPLICADO DE SISMO ENCONTRADO! Incoming ID: {incoming_identifier[:20]}, Existing ID: {extracted_sismo_id[:20]}")
                    break
            
            if found_duplicate:
                print(f"DEBUG: Mensaje de sismo ya reportado (ID: {incoming_identifier[:20]}...). No se guardó.")
                return None

    else:
        message_date = timestamp_obj.date()

        existing_messages_for_date = Message.objects.filter(
            chatroom=chat_room,
            sender=sender_user,
            timestamp__date=message_date
        )
        
        print(f"DEBUG_DEDUP: Incoming weather content (normalized): {incoming_identifier[:50]}...")

        for msg in existing_messages_for_date:
            existing_normalized_content = normalizar_mensaje(msg.content, is_sismo_message=False)
            print(f"DEBUG_DEDUP: Checking existing msg.content (partial): {msg.content[:100]}...")
            print(f"DEBUG_DEDUP: Extracted weather content (normalized) from existing: {existing_normalized_content[:50]}")
            if existing_normalized_content == incoming_identifier:
                found_duplicate = True
                print(f"DEBUG_DEDUP: DUPLICADO METEOROLÓGICO ENCONTRADO! Incoming content: {incoming_identifier[:50]}")
                break
        
        if found_duplicate:
            print(f"DEBUG: Mensaje de alerta meteorológica ya reportado (contenido: {incoming_identifier[:50]}...). No se guardó.")
            return None

    try:
        new_message = Message.objects.create(
            chatroom=chat_room,
            sender=sender_user,
            content=message_content,
            timestamp=timestamp_obj
        )
        print(f"DEBUG: Nuevo mensaje de alerta guardado en DB: {message_content[:50]}...")
        return new_message
    except IntegrityError as e:
        print(f"ERROR al guardar mensaje en DB (posible duplicado o integridad): {e}")
        return None

# =============== Obtención de Datos de Funvisis ================ #
def obtener_datos_funvisis_sync():
    try:
        response = requests.get(SISMOS_API_URL)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de Funvisis: {e}")
        return 0 # Retornar 0 o None para indicar fallo, no una lista vacía

# =============== Formatear mensaje de alerta de Funvisis ================ #
def formatear_mensaje_sismo(sismo_properties):
    fecha_str = sismo_properties.get("postalCode", "N/A")
    hora_str = sismo_properties.get("city", "N/A")
    magnitud = sismo_properties.get("phone", "N/A")
    latitud = sismo_properties.get("lat", "N/A")
    longitud = sismo_properties.get("long", "N/A")
    localizado = sismo_properties.get("address", "N/A")
    profundidad = sismo_properties.get("phoneFormatted", "N/A")

    mensaje = (
        "<b>Información del Sismo:</b>\n"
        f"Fecha: {fecha_str}\n"
        f"Hora (HLV): {hora_str}\n"
        f"<b>Magnitud:</b> {magnitud}\n"
        "Epicentro\n"
        f"* Latitud: {latitud}°\n"
        f"* Longitud: {longitud}°\n"
        f"* <b>Localizado a:</b> <i>{localizado}</i>\n"
        f"Profundidad: {profundidad} km\n"
    )
    return mensaje, fecha_str, hora_str, magnitud, localizado

# =============== Procesar datos formateados de Funvisis ================ #
async def procesar_alertas_sismos(bot_user, general_room, channel_layer):
    print("INFO: Procesando alertas de sismos...")
    datos = await sync_to_async(obtener_datos_funvisis_sync)()
    if not datos or "features" not in datos:
        print("INFO: No se pudieron obtener datos de sismos o el formato es inesperado.")
        return 0

    sismos_nuevos_count = 0
    current_date = timezone.now().date() 

    for sismo in reversed(datos["features"]):
        sismo_properties = sismo.get("properties", {})

        mensaje_base, fecha_str, hora_str, magnitud_str, localizado = \
            formatear_mensaje_sismo(sismo_properties)

        try:
            magnitud = float(magnitud_str)
        except ValueError:
            print(f"ADVERTENCIA: Magnitud no válida: {magnitud_str}. Saltando sismo.")
            continue

        try:
            fecha_hora_str = f"{fecha_str} {hora_str}"
            naive_timestamp_obj = datetime.strptime(fecha_hora_str, "%d-%m-%Y %H:%M")
            timestamp_obj = timezone.make_aware(naive_timestamp_obj)
        except ValueError as e:
            print(f"ADVERTENCIA: No se pudo parsear la fecha/hora del sismo ({fecha_hora_str}): {e}. Saltando sismo.")
            continue

        if timestamp_obj.date() != current_date:
            continue

        sismo_id = sismo.get("id")
        if not sismo_id:
            print("ADVERTENCIA: Sismo sin ID de Funvisis. Se generará un hash como fallback.")
            fecha_hora_str_for_hash = f"{sismo_properties.get('postalCode', '')} {sismo_properties.get('city', '')}"
            magnitud_for_hash = sismo_properties.get("phone", "N/A")
            latitud_for_hash = sismo_properties.get("lat", "N/A")
            longitud_for_hash = sismo_properties.get("long", "N/A")
            unique_str_for_hash = f"{latitud_for_hash}-{longitud_for_hash}-{magnitud_for_hash}-{fecha_hora_str_for_hash}"
            sismo_hash = hashlib.sha256(unique_str_for_hash.encode()).hexdigest()
            unique_identifier_for_deduplication = sismo_hash
        else:
            unique_identifier_for_deduplication = sismo_id

        mensaje_final = mensaje_base
        tipo_alerta = "sismo_normal"

        if magnitud > 4.0 and "Caracas" not in localizado:
            mensaje_final = f"¡¡¡ALERTA SISMO IMPORTANTE!!!\n\n{mensaje_base}\n{RECOMENDACIONES_SISMOS}"
            tipo_alerta = "sismo_importante"
        elif "Caracas" in localizado:
            mensaje_final = f"¡¡¡ALERTA SISMO IMPORTANTE EN <b>CARACAS</b>!!!\n\n{mensaje_base}\n{RECOMENDACIONES_SISMOS}"
            tipo_alerta = "sismo_caracas"

        mensaje_para_guardar = f"{mensaje_final}<span data-sismo-id='{unique_identifier_for_deduplication}' style='display:none;'></span>"

        message_obj = await check_message_exists_and_save(
            general_room,
            bot_user,
            mensaje_para_guardar,
            timestamp_obj,
            tipo_alerta
        )
        print(f"DEBUG_RESULT: check_message_exists_and_save returned: {'SAVED' if message_obj else 'SKIPPED'} for ID: {unique_identifier_for_deduplication[:20]}...")

        if message_obj:
            group_name = f"chat_{general_room.id}"
            await channel_layer.group_send(
                group_name,
                {
                    'type': 'chat_message',
                    'message': mensaje_final,
                    'sender_username': bot_user.username,
                    'sender_full_name': (
                        f"{bot_user.first_name} {bot_user.last_name}" if hasattr(bot_user, 'first_name') else ""
                    ).strip() or bot_user.username,
                    'sender_id': bot_user.id,
                    'timestamp': message_obj.timestamp.isoformat(),
                    'alert_type': tipo_alerta,
                }
            )
            print(f"INFO: Alerta de sismo enviada a la web (ID: {unique_identifier_for_deduplication[:20]}...).")
            sismos_nuevos_count += 1
        else:
            print(f"INFO: Sismo (ID: {unique_identifier_for_deduplication[:20]}...) ya procesado o no válido. No se envió.")
    return sismos_nuevos_count

# =============== Obtener datos de Openweathermap ================ #
def obtener_datos_openweathermap_sync(lat, lon, api_key):
    if not api_key:
        print("ERROR: OPENWEATHER_API_KEY no configurado.")
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&lang=es&units=metric"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener datos de OpenWeatherMap 2.5: {e}")
        return None

# =============== Procesar Alertas Meteorológicas de Openweathermap ================ #
async def procesar_alertas_meteorologicas(bot_user, general_room, channel_layer):
    print("INFO: Procesando alertas meteorológicas (OpenWeatherMap 2.5 - custom logic)...")
    nuevas_alertas_count = 0

    datos_meteo = await sync_to_async(obtener_datos_openweathermap_sync)(
        VENEZUELA_LAT, VENEZUELA_LON, OPENWEATHER_API_KEY
    )

    if not datos_meteo:
        print("INFO: No se obtuvieron datos meteorológicos de OpenWeatherMap 2.5.")
        return 0

    main_data = datos_meteo.get('main', {})
    wind_data = datos_meteo.get('wind', {})
    rain_data = datos_meteo.get('rain', {})
    weather_desc_data = datos_meteo.get('weather', [{}])[0]

    temp_c = main_data.get('temp')
    wind_speed_mps = wind_data.get('speed')
    rain_1h_mm = rain_data.get('1h', 0)
    weather_description = weather_desc_data.get('description', '').lower()

    timestamp_unix = datos_meteo.get('dt', int(datetime.now(dt_timezone.utc).timestamp()))
    current_timestamp_aware = datetime.fromtimestamp(timestamp_unix, tz=dt_timezone.utc)

    alert_messages_list = []

    if wind_speed_mps is not None and wind_speed_mps > 10:
        alert_content = (
            f"<b>ALERTA METEOROLÓGICA: ¡Vientos Fuertes!</b>\n"
            f"Velocidad del viento: {wind_speed_mps:.1f} m/s ({wind_speed_mps * 3.6:.1f} km/h).\n"
            f"Descripción: {weather_description.capitalize()}."
        )
        mensaje_final = alert_content + "\n\n" + RECOMENDACIONES_METEOROLOGICAS
        tipo_alerta = "meteorologica_viento_fuerte"

        message_obj = await check_message_exists_and_save(general_room, bot_user, mensaje_final, timestamp_obj=current_timestamp_aware, alert_type=tipo_alerta)
        if message_obj:
            group_name = f"chat_{general_room.id}"
            await channel_layer.group_send(group_name, {
                'type': 'chat_message', 'message': mensaje_final,
                'sender_username': bot_user.username, 'sender_full_name': (
                    f"{bot_user.first_name} {bot_user.last_name}" if hasattr(bot_user, 'first_name') else ""
                ).strip() or bot_user.username, 'sender_id': bot_user.id,
                'timestamp': message_obj.timestamp.isoformat(), 'alert_type': tipo_alerta,
            })
            print(f"INFO: Alerta meteorológica enviada (Tipo: {tipo_alerta}): {mensaje_final[:50]}...")
            nuevas_alertas_count += 1
            alert_messages_list.append(True)

    if rain_1h_mm is not None and rain_1h_mm > 5:
        alert_content = (
            f"<b>ALERTA METEOROLÓGICA: ¡Lluvia Intensa!</b>\n"
            f"Volumen de lluvia (última hora): {rain_1h_mm:.1f} mm.\n"
            f"Descripción: {weather_description.capitalize()}."
        )
        mensaje_final = alert_content + "\n\n" + RECOMENDACIONES_METEOROLOGICAS
        tipo_alerta = "meteorologica_lluvia_intensa"
        message_obj = await check_message_exists_and_save(general_room, bot_user, mensaje_final, timestamp_obj=current_timestamp_aware, alert_type=tipo_alerta)
        if message_obj:
            group_name = f"chat_{general_room.id}"
            await channel_layer.group_send(group_name, {
                'type': 'chat_message', 'message': mensaje_final,
                'sender_username': bot_user.username, 'sender_full_name': (
                    f"{bot_user.first_name} {bot_user.last_name}" if hasattr(bot_user, 'first_name') else ""
                ).strip() or bot_user.username, 'sender_id': bot_user.id,
                'timestamp': message_obj.timestamp.isoformat(), 'alert_type': tipo_alerta,
            })
            print(f"INFO: Alerta meteorológica enviada (Tipo: {tipo_alerta}): {mensaje_final[:50]}...")
            nuevas_alertas_count += 1
            alert_messages_list.append(True)

    if "tormenta" in weather_description or "thunderstorm" in weather_description:
        alert_content = (
            f"<b>ALERTA METEOROLÓGICA: ¡Tormenta Eléctrica!</b>\n"
            f"Descripción: {weather_description.capitalize()}."
        )
        mensaje_final = alert_content + "\n\n" + RECOMENDACIONES_METEOROLOGICAS
        tipo_alerta = "meteorologica_tormenta"
        message_obj = await check_message_exists_and_save(general_room, bot_user, mensaje_final, timestamp_obj=current_timestamp_aware, alert_type=tipo_alerta)
        if message_obj:
            group_name = f"chat_{general_room.id}"
            await channel_layer.group_send(group_name, {
                'type': 'chat_message', 'message': mensaje_final,
                'sender_username': bot_user.username, 'sender_full_name': (
                    f"{bot_user.first_name} {bot_user.last_name}" if hasattr(bot_user, 'first_name') else ""
                ).strip() or bot_user.username, 'sender_id': bot_user.id,
                'timestamp': message_obj.timestamp.isoformat(), 'alert_type': tipo_alerta,
            })
            print(f"INFO: Alerta meteorológica enviada (Tipo: {tipo_alerta}): {mensaje_final[:50]}...")
            nuevas_alertas_count += 1
            alert_messages_list.append(True)

    if not alert_messages_list:
        print("INFO: No se generaron nuevas alertas meteorológicas basadas en los umbrales actuales.")

    return nuevas_alertas_count

# =============== Enviar Mensajes de Alertas al Chat Room ================ #
async def enviar_alertas():
    print("INFO: Iniciando verificación de todas las alertas para la web...")

    bot_user = await get_bot_user()
    general_room = await get_alertas_chat_room()

    if not bot_user:
        print("ERROR: No se pudo obtener el usuario del bot. Abortando alertas.")
        return
    if not general_room:
        print("ERROR: No se pudo obtener la sala de chat general. Abortando alertas.")
        return

    channel_layer = get_channel_layer()
    total_nuevas_alertas = 0

    total_nuevas_alertas += await procesar_alertas_sismos(bot_user, general_room, channel_layer)

    total_nuevas_alertas += await procesar_alertas_meteorologicas(bot_user, general_room, channel_layer)

    print(f"INFO: Verificación de todas las alertas finalizada. Se procesaron {total_nuevas_alertas} nuevas alertas en total.")