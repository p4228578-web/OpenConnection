import gi
import os
import subprocess
import threading  # <-- ¡Invocamos el poder de los multihilos!
import time  # Nos servirá para que el hilo descanse unos segundos entre escaneos
import webbrowser  # Para abrir enlaces en el navegador

# Configuramos GTK 4 nativo de Ubuntu
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib

class OpenConnection(Gtk.Application):
    def __init__(self):
        super().__init__(application_id='com.blinv.openconnection',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        # 1. CREACIÓN DE LA INTERFAZ (Hilo Principal)
        window = Gtk.ApplicationWindow(application=self)
        window.set_title("Open Connection")
        window.set_default_size(400, 450)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        main_box.set_margin_top(25)
        main_box.set_margin_bottom(25)
        main_box.set_margin_start(25)
        main_box.set_margin_end(25)
        window.set_child(main_box)

        title_label = Gtk.Label(label="OpenConnection")
        title_label.add_css_class("title-1")
        main_box.append(title_label)

        # Nuestra etiqueta de estado que el hilo va a modificar a tiempo real
        self.status_label = Gtk.Label(label="Buscando dispositivo...")
        self.status_label.add_css_class("body")
        main_box.append(self.status_label)

        # Botón de transmisión
        self.btn_mirror = Gtk.Button(label="Transmitir Pantalla")
        self.btn_mirror.set_size_request(-1, 50)
        self.btn_mirror.add_css_class("suggested-action")
        self.btn_mirror.connect("clicked", self.on_transmitir_clicked)
        main_box.append(self.btn_mirror)
 
        guide_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        guide_box.set_margin_top(15)
        main_box.append(guide_box)

        guide_title = Gtk.Label(label="Cómo conectar tu dispositivo:")
        guide_title.set_halign(Gtk.Align.START) # Alineado a la izquierda owo
        guide_title.add_css_class("heading") # Estilo de sub-título nativo
        guide_box.append(guide_title)

        # Instrucciones en viñetas limpias
        paso1 = Gtk.Label(label="1. Ve a Ajustes > Sistema > Opciones de desarrollador.")
        paso1.set_halign(Gtk.Align.START)
        guide_box.append(paso1)

        paso2 = Gtk.Label(label="2. Activa la casilla de 'Depuración por USB'.")
        paso2.set_halign(Gtk.Align.START)
        guide_box.append(paso2)

        paso3 = Gtk.Label(label="3. Conecta el celular a la computadora mediante el cable USB.")
        paso3.set_halign(Gtk.Align.START)
        guide_box.append(paso3)

        paso4 = Gtk.Label(label="4. Acepta el mensaje de '¿Permitir depuración?' en el cel.")
        paso4.set_halign(Gtk.Align.START)
        guide_box.append(paso4)

        importante = Gtk.Label(label="¡Importante tener adb instalado e iniciearlo antes de usar la app!")
        importante.set_halign(Gtk.Align.START)
        importante.add_css_class("caption") # Estilo de nota al pie
        guide_box.append(importante)

        # Deshabilitamos el botón al inicio porque no hay celular detectado todavía owo
        self.btn_mirror.set_sensitive(False)

        footer_label = Gtk.Label(label="Desarrollado por Blinv • Se uso IA en el desarrollo")
        footer_label.add_css_class("caption")
        main_box.append(footer_label)

        window.present()

        # 2. ENCIENDE EL MOTOR OCULTO (Crear el hilo secundario)
        # daemon=True hace que si cierras la ventana, el hilo de fondo también muera limpiamente
        self.hilo_activo = True
        self.hilo_inspector = threading.Thread(target=self.vigesima_inspeccion_usb, daemon=True)
        self.hilo_inspector.start() # ¡Arranca el hilo en segundo plano! 🚀

    # 🧵 ESTO SE EJECUTA EN EL HILO SECUNDARIO (En segundo plano)
    def vigesima_inspeccion_usb(self):
        print("[HILO] Iniciando inspección de ADB en segundo plano...")
        while self.hilo_activo:
            try:
                # Le preguntamos en silencio a ADB si hay algo conectado
                resultado = subprocess.check_output(["adb", "devices"]).decode("utf-8")
                
                # Buscamos si tu Motorola está en la lista
                if "device\n" in resultado or "\tdevice" in resultado:
                    # ¡Hacker tip!: GTK 4 no permite que hilos secundarios alteren la interfaz directamente.
                    # Usamos GLib.idle_add para mandarle de forma segura la actualización al hilo principal nwn/
                    GLib.idle_add(self.actualizar_interfaz_conectado)
                else:
                    GLib.idle_add(self.actualizar_interfaz_desconectado)
                    
            except Exception as e:
                print(f"[HILO ERROR] No se pudo escanear ADB: {e}")
            
            # El hilo duerme por 2 segundos antes de volver a revisar el puerto USB
            time.sleep(2)

    # 🎨 FUNCIONES QUE ACTUALIZAN LA INTERFAZ (Ejecutadas de forma segura)
    def actualizar_interfaz_conectado(self):
        self.status_label.set_label("Telefono conectado")
        self.btn_mirror.set_sensitive(True) # ¡Ya puedes picarle al botón! 😎⚡

    def actualizar_interfaz_desconectado(self):
        self.status_label.set_label("Desconectado. Conecta por USB")
        self.btn_mirror.set_sensitive(False) # Se bloquea si quitas el cable

    # Lógica del botón al hacer clic
    def on_transmitir_clicked(self, button):
        print("[INFO] Lanzando espejo de pantalla...")
        os.system("scrcpy --always-on-top &")

if __name__ == "__main__":
    app = OpenConnection()
    app.run(None)