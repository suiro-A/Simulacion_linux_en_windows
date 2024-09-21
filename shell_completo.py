import tkinter as tk
from PIL import Image, ImageTk
import os
import subprocess
from tkinter import scrolledtext
import shutil  # Importar shutil para eliminar directorios de forma recursiva
from datetime import datetime

from tkinter import ttk
import fitz  # PyMuPDF

class Shell(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)  # Llama al constructor de la clase padre (tk.Toplevel).
        self.padre = parent  # Guarda la referencia del padre.

        # Configuración básica de la ventana.
        self.title("SHELL BASICO [LINUX] ")  # Establece el título de la ventana.
        self.geometry("1200x600")  # Establece el tamaño de la ventana.
        self.configure(bg='black')  # Establece el color de fondo de la ventana a negro.

        # Configuración de la fuente.
        fuente = ("Consolas", 15)  # Define la fuente y el tamaño a usar en la interfaz.

        # Área de texto desplazable para la salida de comandos.
        self.salida = scrolledtext.ScrolledText(self, wrap=tk.WORD, state=tk.DISABLED, bg='black', fg='white', font=fuente)
        self.salida.pack(expand=True, fill=tk.BOTH)  # Empaqueta el widget para que se expanda y llene el espacio disponible.

        # Frame para la entrada de comandos.
        self.entrada_frame = tk.Frame(self, bg='black')  # Crea un frame con fondo negro para la entrada.
        self.entrada_frame.pack(fill=tk.X)  # Empaqueta el frame para que llene el ancho de la ventana.

        # Etiqueta de prompt, es decir, el root@root.
        self.prompt = tk.Label(self.entrada_frame, text=self.get_prompt(), anchor='w', fg='sky blue', bg='black', font=fuente)
        self.prompt.pack(side=tk.LEFT)  # Empaqueta la etiqueta en el lado izquierdo del frame.

        # Variable de cadena para la entrada del usuario.
        self.entrada_var = tk.StringVar()  # Crea una variable de cadena para almacenar la entrada del usuario.
        self.entrada_entry = tk.Entry(self.entrada_frame, textvariable=self.entrada_var, bg='black', fg='white', insertbackground='white', font=fuente)
        self.entrada_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)  # Empaqueta el campo de entrada para que llene el espacio disponible.
        self.entrada_entry.bind("<Return>", self.ejecutar_comando)  # Con ejecutar_comando comienza el funcionamiento del aplicativo.

        self.entrada_entry.bind("<Tab>", self.completar_comando)
        #! con el tab del teclado podemos completar el comando que tenga con la letra inicial 
        # Vincular las teclas de flecha para la navegación por el historial
        self.entrada_entry.bind("<Up>", self.navegar_historial_arriba)
        self.entrada_entry.bind("<Down>", self.navegar_historial_abajo)

        # Páginas manuales para algunos comandos básicos.
        self.paginas_manual = {
            "cd": "cd: cd [DIRECTORIO]\n    Cambia el directorio de trabajo actual a DIRECTORIO.\n    Si no se proporciona DIRECTORIO, cambia al directorio de inicio del usuario.\n   ->cd ..\n    Cambia el directorio de trabajo al directorio padre.\n",
            "pwd": "pwd: pwd\n    Imprime el directorio de trabajo actual.\n",
            "ls": "ls: Lista todos los archivos (los nombres de archivos por defecto).\n",
            "cat": "cat: cat [ARCHIVO]...\n    Mostrar el contenido del archivo.\n",
            "exit": "exit: exit\n    Termina la sesión del intérprete de comandos.\n",
            "clear": "clear: clear\n    Limpia la pantalla del terminal.\n",
            "echo": "echo: echo [CADENA] > [ARCHIVO]\n    Ingresa en CADENA el texto que guardara en archivo.\n",
            "mkdir": "mkdir: mkdir [DIRECTORIO]...\n    Crea uno o más directorios, si no existen.\n",
            "rmdir": "rmdir: rmdir [DIRECTORIO]...\n    Elimina los directorios, si están vacíos.\n",
            "touch": "touch: touch [ARCHIVO]...\n    Crea el archivo txt.\n",
            "history": "history: history\n    Muestra la lista de comandos ejecutados anteriormente.\n",
            "rm": "rm: -> rm [ARCHIVO]\n    Elimina archivos txt.\n    -> rm -r [DIRECTORIO]\n    Elimina los directorios y su contenido de forma recursiva.\n",
            "tree": "tree: Muestra la estructura jerárquica de directorios.",
            "hide": "hide: hide [ARCHIVO/DIRECTORIO]\n    Oculta el archivo o directorio especificado.\n",
            "unhide": "unhide: unhide [ARCHIVO/DIRECTORIO]\n    Muestra el archivo o directorio especificado.\n",
        }

        self.historial_comandos = []  # Lista para almacenar el historial de comandos
        self.indice_historial = -1  # Índice para rastrear la posición en el historial
        
        #! lista para usar en el autocompletado
        self.comandos = ['cd', 'pwd', 'exit', 'clear', 'ls', 'echo', 'cat', 'mkdir', 'rmdir', 'touch', 'history','rm -r','rm','man','help','tree','hide', 'unhide' ]

        # Información del usuario
        self.nombre_usuario = os.getlogin()  # Obtiene el nombre del usuario del sistema.

        self.inicializar_etiquetas()  # Inicializa las etiquetas.

    # Método para obtener el prompt.
    def get_prompt(self):
        return "root@root: "  # Devuelve el prompt del shell.


    #TODO: FUNCION PARA HACER EL AUTOCOMPLETADO
    def completar_comando(self, event):
        #! Obtiene el texto actual ingresado en el entrada_entry
        texto_actual = self.entrada_var.get()
        comandos_coincidentes = [cmd for cmd in self.comandos if cmd.startswith(texto_actual)]
        #! Si hay exactamente un comando que coincide, completa el texto en el entrada_entry
        if len(comandos_coincidentes) == 1:
            self.entrada_var.set(comandos_coincidentes[0])
            self.entrada_entry.icursor(tk.END)
        #! Si hay múltiples comandos que coinciden, muestra una lista de ellos
        elif len(comandos_coincidentes) > 1:
            self.agregar_salida(f"{self.get_prompt()}","prompt") 
            self.agregar_salida(texto_actual+"\n") 
            self.agregar_salida(" ".join(comandos_coincidentes) + "\n")
        
        return "break"
    
    # Método para ejecutar comandos.
    def ejecutar_comando(self, event):
        comando = self.entrada_var.get()  # Obtiene el comando ingresado por el usuario.
        self.entrada_var.set("")  # Limpia el campo de entrada.

        # Muestra el prompt y el comando en la salida.
        self.agregar_salida(f"{self.get_prompt()}", "prompt")  # "prompt" + el comando en la pantalla
        self.agregar_salida(f"{comando}\n")  # Esta parte será donde se mostrará el comando ingresado por pantalla

        if comando.strip():  # Si el comando no está vacío
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Obtiene la fecha y hora actuales.
            self.historial_comandos.append((comando, self.nombre_usuario, timestamp))  # Añade el comando al historial con usuario y fecha.
            self.indice_historial = -1  # Resetea el índice del historial
            # Manejo de comandos especiales.
            if comando.startswith("cd "):
                try:
                    os.chdir(comando.split(" ")[1])  # Cambia el directorio de trabajo.
                except IndexError:
                    self.agregar_salida("Error: argumento esperado para 'cd'\n")
                except FileNotFoundError:
                    self.agregar_salida(f"Error: no existe tal directorio: {comando.split(' ')[1]}\n")
            elif comando.startswith("mkdir "):
                self.crear_directorio(comando.split(" ")[1])
            elif comando.startswith("rmdir "):
                self.remover_directorio(comando.split(" ")[1])
            elif comando.startswith("touch "):
                self.crear_archivo(comando.split(" ")[1])
            elif comando.startswith("cat "):
                self.leer_archivo(comando.split(" ")[1])
            elif comando.startswith("rm -r "):
                self.confirmar_eliminar_directorio_recursivo(comando.split(" ")[2])
            elif comando.startswith("rm "):
                self.remover_archivo(comando.split(" ")[1])
            elif comando == "pwd":
                self.imprimir_directorio_trabajo()
            elif comando == "exit":
                self.quit()
            elif comando == "clear":
                self.limpiar_salida()
            elif comando == "ls":
                self.listar_directorio()
            elif comando == "history":
                self.mostrar_historial()
            elif comando == "help":
                self.mostrar_ayuda()
            elif comando == "tree":
                self.mostrar_arbol_directorios()
            elif comando.startswith("hide "):
                self.ocultar_archivo(comando.split(" ")[1])
            elif comando.startswith("unhide "):
                self.mostrar_archivo(comando.split(" ")[1])
            elif comando.startswith("man "):
                self.mostrar_manual(comando.split(" ")[1])
            elif "echo " in comando and " > " in comando:
                self.echo_a_archivo(comando)

        # Actualiza el prompt y posiciona el cursor al final.
        self.prompt.config(text=self.get_prompt())
        self.entrada_entry.icursor(tk.END)
        

    # Método para listar directorios.
    def listar_directorio(self):
        try:
            if os.name == "nt":  # Comprobar si el sistema es Windows.
                resultado = subprocess.run("dir /b", shell=True, text=True, capture_output=True)  # Ejecuta dir en Windows.
            else:
                resultado = subprocess.run(["ls"], shell=True, text=True, capture_output=True)  # Ejecuta ls en Linux.
            if resultado.stdout:
                self.agregar_salida(resultado.stdout)  # Muestra la salida estándar.
            if resultado.stderr:
                self.agregar_salida(resultado.stderr)  # Muestra la salida de error.
        except subprocess.CalledProcessError as e:
            self.agregar_salida(f"Error: {e}\n")  # Muestra el error si ocurre.

    def echo_a_archivo(self, comando):
        partes = comando.split(">")
        archivo_salida = partes[1].strip()

        parte = comando.split("echo")
        parte = parte[1].split(">")
        texto_echo = parte[0].strip().strip('"')
        try:
            with open(archivo_salida, "w") as archivo:
                archivo.write(texto_echo + '\n')
            self.agregar_salida(f"Texto '{texto_echo}' escrito en '{archivo_salida}'\n")
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")
            
    # Método para crear un directorio.
    def crear_directorio(self, nombre_directorio):
        try:
            os.mkdir(nombre_directorio)  # Crea el directorio.
            self.agregar_salida(f"Directorio '{nombre_directorio}' creado satisfactoriamente \n")  # Muestra un mensaje de éxito.
        except FileExistsError:
            self.agregar_salida(f"Error: Directorio '{nombre_directorio}' ya existe\n")  # Muestra un mensaje si el directorio ya existe.
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")  # Muestra cualquier otro error del sistema.

    def remover_directorio(self, nombre_directorio):
        try:
            os.rmdir(nombre_directorio)
            self.agregar_salida(f"Directorio '{nombre_directorio}' removido satisfactoriamente\n")
        except FileNotFoundError:
            self.agregar_salida(f"Error: Directorio '{nombre_directorio}' no encontrado\n")
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")

    # Métodos para ocultar y mostrar archivos
    def ocultar_archivo(self, nombre_archivo):
        try:
            if os.name == "nt":  # Comprobar si el sistema es Windows.
                subprocess.run(["attrib", "+h", nombre_archivo], check=True)
                self.agregar_salida(f"Archivo '{nombre_archivo}' oculto satisfactoriamente\n")
            else:
                self.agregar_salida("El comando 'hide' solo está disponible en Windows\n")
        except subprocess.CalledProcessError as e:
            self.agregar_salida(f"Error: {e}\n")

    def mostrar_archivo(self, nombre_archivo):
        try:
            if os.name == "nt":  # Comprobar si el sistema es Windows.
                subprocess.run(["attrib", "-h", nombre_archivo], check=True)
                self.agregar_salida(f"Archivo '{nombre_archivo}' mostrado satisfactoriamente\n")
            else:
                self.agregar_salida("El comando 'unhide' solo está disponible en Windows\n")
        except subprocess.CalledProcessError as e:
            self.agregar_salida(f"Error: {e}\n")

    def crear_archivo(self, nombre_archivo):
        try:
            with open(nombre_archivo, "w"):
                pass
            self.agregar_salida(f"Archivo '{nombre_archivo}' creado satisfactoriamente\n")
        except FileExistsError:
            self.agregar_salida(f"Error: Archivo '{nombre_archivo}' ya existe\n")
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")
    
    def leer_archivo(self, nombre_archivo):
        try:
            with open(nombre_archivo, "r") as archivo:
                contenido = archivo.read()
                self.agregar_salida(contenido+"\n")
        except FileNotFoundError:
            self.agregar_salida(f"Error: Archivo '{nombre_archivo}' no encontrado\n")
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")

    def navegar_historial_arriba(self, event):
        if self.historial_comandos and self.indice_historial < len(self.historial_comandos) - 1:
            self.indice_historial += 1
            self.entrada_var.set(self.historial_comandos[-(self.indice_historial + 1)][0])
            self.entrada_entry.icursor(tk.END)

    def navegar_historial_abajo(self, event):
        if self.historial_comandos and self.indice_historial >= 0:
            self.indice_historial -= 1
            if self.indice_historial >= 0:
                self.entrada_var.set(self.historial_comandos[-(self.indice_historial + 1)][0])
            else:
                self.entrada_var.set("")
            self.entrada_entry.icursor(tk.END)


    def confirmar_eliminar_directorio_recursivo(self, nombre_directorio):
        self.agregar_salida(f"¿Estás seguro de que quieres eliminar '{nombre_directorio}' y todo su contenido? [y/n]\n")

        def on_confirm(event):
            respuesta = self.entrada_var.get().strip().lower()
            self.entrada_var.set("")
            self.agregar_salida(f"{self.get_prompt()}", "prompt")
            self.agregar_salida(f"{respuesta}\n")

            if respuesta == 'y':
                self.remover_directorio_recursivo(nombre_directorio)
            else:
                self.agregar_salida("Operación cancelada.\n")

            self.entrada_entry.unbind("<Return>")
            self.entrada_entry.bind("<Return>", self.ejecutar_comando)

        self.entrada_entry.bind("<Return>", on_confirm)

    def remover_directorio_recursivo(self, nombre_directorio):
        try:
            shutil.rmtree(nombre_directorio)
            self.agregar_salida(f"Directorio '{nombre_directorio}' removido satisfactoriamente\n")
        except FileNotFoundError:
            self.agregar_salida(f"Error: Directorio '{nombre_directorio}' no encontrado\n")
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")

    def imprimir_directorio_trabajo(self):
        self.agregar_salida(f"{os.getcwd()}\n")

    def remover_archivo(self, nombre_archivo):
        try:
            os.remove(nombre_archivo)
            self.agregar_salida(f"Archivo '{nombre_archivo}' eliminado satisfactoriamente\n")
        except FileNotFoundError:
            self.agregar_salida(f"Error: Archivo '{nombre_archivo}' no encontrado\n")
        except OSError as e:
            self.agregar_salida(f"Error: {e}\n")

    # Método para inicializar las etiquetas de la salida.
    def inicializar_etiquetas(self):
        self.salida.tag_config('prompt', foreground='sky blue')  # Configura la etiqueta 'prompt' con color azul cielo.
        self.salida.tag_config('oculto', foreground='red')  # Configura la etiqueta 'oculto' con color rojo

    # Método para mostrar manuales.
    def mostrar_manual(self, comando):
        texto_manual = self.paginas_manual.get(comando, f"No hay entradas manuales para {comando}\n")  # Obtiene el texto del manual para el comando.
        self.agregar_salida(texto_manual)  # Muestra el texto del manual.
    
    def mostrar_arbol_directorios(self, path='.', nivel=0):
        try:
            if nivel == 0:
                self.agregar_salida(f"{path}\n")
            else:
                is_hidden = self.es_oculto(path)  # Verifica si el directorio es oculto
                if is_hidden:
                    self.agregar_salida('│   ' * (nivel - 1) + '├── ' + os.path.basename(path) + ' (oculto)\n', 'oculto')
                else:
                    self.agregar_salida('│   ' * (nivel - 1) + '├── ' + os.path.basename(path) + '\n')
            
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                is_hidden = self.es_oculto(item_path)  # Verifica si el archivo o directorio es oculto
                if os.path.isdir(item_path):
                    if is_hidden:
                        self.mostrar_arbol_directorios(item_path, nivel + 1)
                    else:
                        self.mostrar_arbol_directorios(item_path, nivel + 1)
                else:
                    if is_hidden:
                        self.agregar_salida('│   ' * nivel + '├── ' + item + ' (oculto)\n', 'oculto')
                    else:
                        self.agregar_salida('│   ' * nivel + '├── ' + item + '\n')
        except PermissionError:
            self.agregar_salida('│   ' * nivel + '├── ' + '[Permission Denied]\n')

    def es_oculto(self, item_path):
        if os.name == 'nt':
            # En Windows, verifica el atributo de archivo oculto
            try:
                attribute = os.stat(item_path).st_file_attributes
                return attribute & 2  # FILE_ATTRIBUTE_HIDDEN
            except AttributeError:
                return False  # Si no se puede obtener el atributo, no se considera oculto
        else:
            # En Unix, los archivos ocultos comienzan con un punto ('.')
            return os.path.basename(item_path).startswith('.')
    
    # Método para agregar texto a la salida.
    def agregar_salida(self, texto, etiqueta=None):
        self.salida.config(state=tk.NORMAL)  # Permite modificar el área de texto.
        if etiqueta:
            self.salida.insert(tk.END, texto, etiqueta)  # Inserta texto con una etiqueta de formato.
        else:
            self.salida.insert(tk.END, texto)  # Inserta texto sin etiqueta.
        self.salida.config(state=tk.DISABLED)  # Vuelve a deshabilitar el área de texto.
        self.salida.see(tk.END)  # Desplaza el área de texto para ver la última línea.

    def mostrar_ayuda(self):
        for cmd, desc in self.paginas_manual.items():
            # Si la descripción comienza con el comando, elimínalo
            if desc.startswith(cmd):
                desc = desc[len(cmd):].strip()
            # Agregar el comando seguido de la descripción completa
            self.agregar_salida(f"{cmd}: {desc}\n")

    # Método para limpiar la salida.
    def limpiar_salida(self):
        self.salida.config(state=tk.NORMAL)  # Permite modificar el área de texto.
        self.salida.delete(1.0, tk.END)  # Elimina todo el contenido del área de texto.
        self.salida.config(state=tk.DISABLED)  # Vuelve a deshabilitar el área de texto.
    
    # Método para mostrar el historial de comandos desde el momento de ingresar un comando.
    def mostrar_historial(self):
        for i, (comando, nombre_usuario, timestamp) in enumerate(self.historial_comandos, 1):
            self.agregar_salida(f"{i}  {comando} - {nombre_usuario} -{timestamp}\n")    

# Funciones para abrir las ventanas
def abrir_autores():
    doc_ventana = tk.Toplevel()
    doc_ventana.title("AUTORES")
    doc_ventana.geometry("400x200")
    texto_documentacion = (
        "\n\nESTUDIANTES DE ESCUELA DE INFORMA DE LA UNT\n"
        "Arteaga Rodríguez Aaron Kaleb\n "
        "Cruz Rebaza Stalin Ricardo\n"
        "Flores Lozano Julio Isidro\n "
        "Herrera Cruz Maria Pia\n"
        "Segura Gutiérrez Diego Alonso\n "
    )
    mensaje_doc = tk.Label(doc_ventana, text=texto_documentacion, wraplength=400, justify="left")
    mensaje_doc.pack()

def abrir_ventana_hola_mundo():
    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("AUTORES")
    nueva_ventana.geometry("200x100")
    mensaje = tk.Label(nueva_ventana, text="Hola Mundo")
    mensaje.pack(pady=20)

def abrir_shell():
    shell = Shell(ventana_principal)  # Pasa la ventana principal como padre al Shell


def crear_seccion(titulo, row, column, command):
    etiqueta = tk.Label(ventana_principal, text=titulo, bg=color_fondo, fg=color_texto, font=("Helvetica", 16))
    etiqueta.grid(row=row, column=column, pady=(20, 10))
    boton = tk.Button(ventana_principal, text="ABRIR", command=command, bg=color_boton_fondo, fg=color_boton_texto, font=("Helvetica", 12))
    boton.grid(row=row, column=column, pady=(120, 20))

def mostrar_pdf(pagina):
    pix = pagina.get_pixmap(matrix=fitz.Matrix(2, 2))  # Ajusta el factor de zoom según tus necesidades
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    return ImageTk.PhotoImage(img)

def abrir_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    nueva_ventana = tk.Toplevel()
    nueva_ventana.title("Documento PDF")
    nueva_ventana.geometry("1200x800")

    canvas = tk.Canvas(nueva_ventana)
    scrollbar = ttk.Scrollbar(nueva_ventana, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    for page_num in range(len(doc)):
        pagina = doc.load_page(page_num)
        pdf_imagen = mostrar_pdf(pagina)
        label_pdf = tk.Label(scrollable_frame, image=pdf_imagen)
        label_pdf.image = pdf_imagen
        label_pdf.pack(pady=10)

    def _on_mouse_wheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    canvas.bind_all("<MouseWheel>", _on_mouse_wheel)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

def abrir_pdf_documentacion():
    abrir_pdf("C:/Users/rodrigo/Desktop/VisualStudio/SISTEMAS OPERATIVOS/interfaz/Documentación de la shell.pdf")

def abrir_pdf_conceptos_shell():
    abrir_pdf("C:/Users/rodrigo/Desktop/VisualStudio/SISTEMAS OPERATIVOS/interfaz/Conceptos de la shell.pdf")

def crear_boton(titulo, row, column, command):
    tk.Label(ventana_principal, text=titulo, bg='black', fg='white', font=("Helvetica", 16)).grid(row=row, column=column, pady=(20, 10))
    tk.Button(ventana_principal, text="ABRIR", command=command, bg='lightblue', fg='blue', font=("Helvetica", 12)).grid(row=row, column=column, pady=(120, 20))


ventana_principal = tk.Tk()
ventana_principal.title("Interfaz")
ventana_principal.geometry("900x600")
ventana_principal.configure(bg='black')

# Cargar y escalar la imagen
image_path = "./SISTEMAS OPERATIVOS/interfaz/UNT.png"  # Reemplaza con la ruta de tu imagen
image = Image.open(image_path)
scaled_image = image.resize((100, 100), Image.LANCZOS)  # Escala la imagen a 100x100 píxeles
photo = ImageTk.PhotoImage(scaled_image)

# Crear el Label para la imagen
label_image = tk.Label(ventana_principal, image=photo, bg='black')
label_image.image = photo  # Guardar una referencia para evitar que la imagen sea eliminada por el recolector de basura

# Colocar el Label en una posición específica
label_image.place(x=10, y=10)  # Ajusta las coordenadas x e y según sea necesario

# Configuración del grid layout
ventana_principal.columnconfigure(0, weight=1, minsize=450)
ventana_principal.columnconfigure(1, weight=1, minsize=450)
ventana_principal.rowconfigure(0, weight=1, minsize=300)
ventana_principal.rowconfigure(1, weight=1, minsize=300)

# Colores
color_fondo = 'black'; color_texto = 'white'
color_boton_fondo = 'lightblue'; color_boton_texto = 'blue'

# Crear secciones
crear_seccion("AUTORES", 0, 0, abrir_autores)
crear_seccion("DOCUMENTACIÓN", 0, 1, abrir_pdf_documentacion)
crear_seccion("CONCEPTOS SOBRE LA SHELL", 1, 0, abrir_pdf_conceptos_shell)
crear_seccion("SIMULACIÓN DE LA SHELL", 1, 1, abrir_shell)

ventana_principal.mainloop()
