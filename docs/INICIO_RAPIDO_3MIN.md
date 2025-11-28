# 🚀 INICIO RÁPIDO - 3 MINUTOS

## ⚡ Para Probar EN 3 MINUTOS (Mismo PC)

### Paso 1: Abrir 3 Terminales PowerShell

```
📁 C:\Users\Victor\Desktop\TGCTest\
```

### Paso 2: Terminal 1 - SERVIDOR
```powershell
cd server
python app.py
```

**Espera a ver:**
```
🚀 Servidor Socket.IO iniciado en http://localhost:5000
📡 Esperando conexiones...
```

### Paso 3: Terminal 2 - JUGADOR 1
```powershell
python main_menu.py
```

**En el menú:**
1. Click → **🌐 MULTIJUGADOR**
2. Servidor ya dice: `http://localhost:5000` ✅
3. Click → **Connect**
4. Espera: `✓ Connected to server` (verde)
5. Click → **Find Match**
6. Verás: "Searching for opponent..." (azul)

### Paso 4: Terminal 3 - JUGADOR 2
```powershell
python main_menu.py
```

**En el menú:**
1. Click → **🌐 MULTIJUGADOR**
2. Servidor ya dice: `http://localhost:5000` ✅
3. Click → **Connect**
4. Espera: `✓ Connected to server` (verde)
5. Click → **Find Match**

### Paso 5: ¡JUEGA!

**Ambos jugadores verán:**
```
✓ Match found! Room: game_XXXXXX
```

**El juego se abre automáticamente.**

- **Jugador 1:** "Your turn - You go first!"
- **Jugador 2:** "Opponent's turn - Waiting..."

**¡Ya pueden jugar!**

---

## 🌐 Para Probar ENTRE DOS PCs

### PC 1 (Servidor + Cliente)

#### Terminal 1 - Configuración
```powershell
python setup_server.py
```

**Anota tu IP, por ejemplo:**
```
📍 Tu IP Local: 192.168.1.100
```

#### Terminal 2 - Servidor
```powershell
cd server
python app.py
```

#### Terminal 3 - Cliente 1
```powershell
python main_menu.py
```
- Multijugador → `http://localhost:5000`
- Connect → **Create Room** (anota el código: ej. `ABC123`)

### PC 2 (Cliente)

```powershell
python main_menu.py
```
- Multijugador → `http://192.168.1.100:5000` (¡TU IP DEL PC 1!)
- Connect → **Join Room** → Escribe `ABC123`

### ¡Ya pueden jugar!

---

## 🎮 Controles del Juego

### Durante Tu Turno:
- **Click en carta de tu mano** → Juega la carta
- **Click en carta en tablero** → Activa habilidad (si tiene)
- **Click en "Attack" en tu carta** → Selecciona objetivo
- **Click en "End Turn"** → Termina tu turno

### El Oponente Verá:
- Tus cartas aparecen en su tablero
- Tus ataques en tiempo real
- El log de acciones se actualiza

---

## 🔥 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| "Connection failed" | ¿Servidor corriendo? Verifica Terminal 1 |
| No encuentran oponente | Ambos deben hacer Click "Find Match" |
| Código de sala no funciona | Verifica los 6 caracteres exactos |
| Lag / No sincroniza | Revisa logs del servidor (Terminal 1) |

---

## 📋 Verificación Pre-Juego

```powershell
python test_multiplayer_setup.py
```

Debe mostrar:
```
✅ TODAS LAS PRUEBAS PASARON
🚀 El sistema está listo para usar!
```

---

## 🎯 Checklist de Validación

- [ ] Servidor corriendo (Terminal 1: "Esperando conexiones...")
- [ ] Cliente 1 conectado (verde: "Connected to server")
- [ ] Cliente 2 conectado (verde: "Connected to server")
- [ ] Match encontrado ("Match found! Room: ...")
- [ ] Ventana de juego abierta en ambos
- [ ] Jugador 1 puede jugar su primer turno
- [ ] Jugador 2 ve "Opponent's turn"
- [ ] Cartas jugadas se ven en ambos lados
- [ ] Turnos cambian correctamente

---

## ✅ Si Todo Funciona

**¡Felicidades! El multiplayer está funcionando correctamente.**

Ahora puedes:
- Jugar partidas completas
- Probar con diferentes mazos
- Experimentar con diferentes campeones
- Invitar amigos a jugar

---

## 📚 Más Información

- **Guía completa:** `docs/MULTIPLAYER_TESTING_GUIDE.md`
- **Documentación:** `docs/MULTIPLAYER_README.md`
- **Estado:** `FASE1_MULTIPLAYER_COMPLETA.md`

---

**¡Disfruta jugando! 🎮✨**
