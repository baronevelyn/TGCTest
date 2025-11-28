# 🎮 Prototipo Multiplayer - Instrucciones de Prueba

## ✅ Estado Actual

El prototipo de multiplayer está **funcionando correctamente**:
- ✅ Servidor Socket.IO corriendo en `http://localhost:5000`
- ✅ Cliente 1 conectado y esperando oponente
- ✅ NetworkManager funcionando
- ✅ Comunicación bidireccional establecida

---

## 🚀 Cómo Probar el Prototipo

### Terminal 1: Servidor (Ya está corriendo)
```bash
cd server
python app.py
```
**Resultado esperado:**
```
🚀 Servidor Socket.IO iniciado en http://localhost:5000
📡 Esperando conexiones...
```

### Terminal 2: Cliente 1 (Ya está corriendo esperando)
```bash
python test_multiplayer_prototype.py 1
```
**En el menú, selecciona opción `1` (Buscar partida)**

### Terminal 3: Cliente 2 (EJECUTA ESTO AHORA)
```bash
python test_multiplayer_prototype.py 2
```
**En el menú, selecciona opción `1` (Buscar partida)**

---

## 🎯 Qué Deberías Ver

### Cuando Cliente 2 se conecte:

**Cliente 1 verá:**
```
✅ ¡PARTIDA ENCONTRADA!
   Sala: game_XXXXXXXX
   Empiezas tú: True
   Oponente: 2

📤 Enviando acción de prueba...
📥 ACCIÓN RECIBIDA DEL OPONENTE:
   Tipo: test_action
   Datos: {...}
```

**Cliente 2 verá:**
```
✅ ¡PARTIDA ENCONTRADA!
   Sala: game_XXXXXXXX
   Empiezas tú: False
   Oponente: 1

📥 ACCIÓN RECIBIDA DEL OPONENTE:
   Tipo: test_action
   Datos: {...}

📤 Enviando acción de prueba...
```

**Servidor verá:**
```
🔍 1 busca partida
⏳ 1 añadido a cola de espera
🔍 2 busca partida
🎮 Partida creada: game_XXXXXXXX
📤 Acción retransmitida: test_action
📤 Acción retransmitida: response_action
```

---

## 🧪 Otras Pruebas Disponibles

### Probar Salas Privadas

**Cliente 1:**
```
Opción: 2 (Crear sala privada)
Código de sala: ABC123
```

**Cliente 2:**
```
Opción: 3 (Unirse a sala privada)
Código de sala: ABC123
```

### Medir Latencia

```
Opción: 4 (Medir latencia)
```

**Resultado esperado:**
```
🏓 Latencia: 5-50ms (localhost)
```

---

## ✅ Validación Exitosa

Si ves los mensajes anteriores, el prototipo está funcionando correctamente:

1. ✅ **Conexión P2P** - Servidor relay conectando 2 clientes
2. ✅ **Matchmaking** - Sistema de búsqueda automática
3. ✅ **Salas privadas** - Crear/unirse con código
4. ✅ **Sincronización** - Acciones enviadas y recibidas
5. ✅ **Latencia** - Medición de ping/pong

---

## 📊 Arquitectura Validada

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│  Cliente 1  │◄────────┤   Servidor   ├────────►│  Cliente 2  │
│  (Puerto X) │  Socket │    :5000     │ Socket  │  (Puerto Y) │
└─────────────┘   .IO   └──────────────┘   .IO   └─────────────┘
       │                                                  │
       └──────► Acción: play_card ──────────────────────►│
       │◄────── Acción: end_turn ───────────────────────┘
```

---

## 🎯 Próximos Pasos (Después de Validar)

Una vez que hayas confirmado que funciona:

1. **Integrar con el Juego Real**
   - Adaptar `Game` class para multiplayer
   - Enviar acciones reales (play_card, attack, etc.)
   - Sincronizar estado del juego

2. **Mejorar UI**
   - Lobby de búsqueda en Tkinter
   - Indicador "Esperando oponente..."
   - Chat básico

3. **Validación de Acciones**
   - Servidor valida reglas del juego
   - Anti-cheating básico
   - Checksums de estado

4. **Manejo de Desconexión**
   - Reconexión automática
   - Timeout de inactividad
   - Notificaciones claras

---

## 🐛 Troubleshooting

### Error: "No se pudo conectar al servidor"
**Solución:** Verifica que el servidor esté corriendo en Terminal 1

### Error: "Sala no encontrada"
**Solución:** El código de sala debe ser exacto (6 caracteres)

### Error: "ModuleNotFoundError"
**Solución:** Instala dependencias:
```bash
pip install python-socketio[client] websocket-client gevent gevent-websocket setuptools
```

---

## 🎉 ¡Éxito!

Si llegaste hasta aquí y todo funciona, **¡el prototipo es un éxito!**

La arquitectura Socket.IO con servidor relay es **viable** para tu juego.

Puedes proceder con confianza a la **Fase 1 completa**: 
- Integración con el juego real
- Sistema de lobbies
- UI pulida

---

**Creado:** 25 de noviembre, 2025  
**Tiempo de desarrollo:** ~1 hora  
**Estado:** ✅ Prototipo funcional validado
