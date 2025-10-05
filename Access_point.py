 # Importa el módulo 'network' para manejar las interfaces de red del ESP32
import network

 # Crea una instancia de la interfaz Wi-Fi en modo Punto de Acceso
ap_if = network.WLAN(network.AP_IF)

 # Activa la interfaz AP para que el ESP32 comience a emitir su propia red Wi-Fi
ap_if.active(True)

 # Configura el nombre de la red Wi-Fi (SSID) que el ESP32 emitirá
ap_if.config(essid="ESP-AccessPoint")

 # Establece el modo de autenticación y la contraseña de la red
 # authmode=2 corresponde a WPA-PSK (Wi-Fi Protected Access Pre-Shared Key)
 # La contraseña debe tener al menos 8 caracteres para ser válida
ap_if.config(authmode=2, password="12345678")

 # Define el número máximo de dispositivos que pueden conectarse simultáneamente
ap_if.config(max_clients=2)

# Selecciona el canal Wi-Fi en el que operará el AP (valores típicos entre 1 y 11)
ap_if.config(channel=10)

 # Establece si la red será visible (hidden=0) u oculta (hidden=1)
 # Si la red está oculta, no aparecerá en las búsquedas de redes Wi-Fi, 
 # pero aún es posible conectarse si se conoce el SSID
ap_if.config(hidden=0)

 # Imprime el SSID de la red configurada
print("Nombre de la red(SSID):", ap_if.config('essid'))

# Muestra la configuración de red asignada al AP: Dirección IP, Máscara de subred, Puerta de 
# enlace y Servidor DNS
print("Configuración de red (IP/Máscara de subred/Puerta de enlace/DNS):", ap_if.ifconfig())

# Imprime el modo de autenticación utilizado por la red
 # Los modos de autenticación pueden ser:
 # 0 - Open (Abierta, sin contraseña)
 # 1 - WEP
 # 2 - WPA-PSK
 # 3 - WPA2-PSK
 # 4 - WPA/WPA2-PSK
print("Modo de autenticación:", ap_if.config("authmode"))

 # Muestra el número máximo de clientes que pueden conectarse al AP
print("Número máximo de clientes:", ap_if.config("max_clients"))

# Indica el canal Wi-Fi en el que el AP está operando
print("Canal Wi-Fi:", ap_if.config("channel"))

# Indica si la red está oculta (True) o visible (False)
print("Red oculta (True=Sí/False=No):", ap_if.config("hidden"))

 # Verifica y muestra si la interfaz AP está activa (True) o inactiva (False)
print("Interfaz AP activa (True=Sí/False=No):", ap_if.active())

# Desactiva la interfaz AP si ya no se necesita (opcional
# ap_if.active(False)
