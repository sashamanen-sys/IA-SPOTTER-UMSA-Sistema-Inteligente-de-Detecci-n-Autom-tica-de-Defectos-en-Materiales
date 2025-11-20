import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import os
import threading
from google import genai
from google.genai.errors import APIError
from tkinter import font 

# Configuración de CustomTkinter
ctk.set_appearance_mode("Dark") 
ctk.set_default_color_theme("blue")

# --- CONSTANTES UMSA ---
UMSA_BLUE = "#003366"
UMSA_GOLD = "#D4AF37"
UMSA_TEXT_DARK = "#f0f4f8"
UMSA_BG_DARK = "#3c3f44"

# --- CONFIGURACIÓN DE LA API (USA gemini-2.5-flash) ---
MODEL_NAME = 'gemini-2.5-flash'

class DefectAssistantGUI(ctk.CTkToplevel):
    """
    Ventana de Asistente de Investigación de Defectos.
    Usa CustomTkinter para la UI y tk.Text para el área de respuesta con tags.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.title("🤖 Asistente de Investigación de Defectos")
        self.geometry("900x500")
        self.configure(fg_color="#181a1d")

        self.DEFECTOS = [
            "crazing", "inclusion", "patches", "pitted_surface",
            "rolled-in_scale", "scratches"
        ]
        self.last_defect = None
        
        # --- Inicialización del Cliente Gemini (Manejo de Fallos) ---
        self.client = None
        try:
            # Intentar inicializar el cliente
            # NOTA: Para que esto funcione, la variable de entorno GEMINI_API_KEY debe estar configurada.
            self.client = genai.Client()
        except Exception as e:
            messagebox.showwarning("Advertencia API", 
                                   "No se pudo inicializar el cliente de Gemini. "
                                   "Las funcionalidades de IA estarán deshabilitadas.")
        
        # --- Definición de Fuentes (Usando tkinter.font) ---
        self.font_normal = font.Font(family="Arial", size=13)
        self.font_bold = font.Font(family="Arial", size=13, weight="bold")
        self.font_loading = font.Font(family="Arial", size=14, weight="bold")
        self.font_user_prompt = font.Font(family="Arial", size=13, weight="bold")
        
        # --- ESTRUCTURA PRINCIPAL (Se ejecutan SIEMPRE) ---
        header_frame = ctk.CTkFrame(self, fg_color=UMSA_BLUE, corner_radius=0)
        header_frame.pack(fill="x")
        
        title_label = ctk.CTkLabel(header_frame, text="🤖 Asistente de Investigación de Defectos",
                                   font=ctk.CTkFont(size=24, weight="bold"),
                                   text_color="white", padx=20, pady=15)
        title_label.pack(side="left")
        
        subtitle_label = ctk.CTkLabel(header_frame, text="IA Spotter UMSA",
                                      font=ctk.CTkFont(size=14),
                                      text_color="white", padx=20, pady=15)
        subtitle_label.pack(side="right")

        main_content = ctk.CTkFrame(self, fg_color="#212328")
        main_content.pack(fill="both", expand=True, padx=20, pady=20)
        main_content.grid_columnconfigure(1, weight=1)
        main_content.grid_rowconfigure(0, weight=1)
        
        self._create_sidebar(main_content)
        self._create_main_area(main_content)

        # Inhabilitar la funcionalidad de IA si la inicialización falló
        if self.client is None:
            self._toggle_api_state(False)
            initial_text = "ERROR: El cliente de Gemini no está configurado. La funcionalidad de chat/consulta está deshabilitada."
        else:
             initial_text = "Selecciona un defecto del panel izquierdo para obtener una explicación técnica o usa el chat inferior."

        self.response_textbox.configure(state=tk.NORMAL)
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.insert("end", initial_text)
        self.response_textbox.configure(state=tk.DISABLED)

        self.transient(self.master)
        self.grab_set()
        
    # --------------------------------------------------------------------------
    # 1. SIDEBAR (Defectos Comunes)
    # --------------------------------------------------------------------------
    def _create_sidebar(self, parent):
        sidebar = ctk.CTkFrame(parent, width=220, corner_radius=8, fg_color="#33363b")
        sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        sidebar.grid_propagate(False)

        h2_label = ctk.CTkLabel(sidebar, text="Defectos Comunes (NEU-SDD)", 
                                font=ctk.CTkFont(size=14, weight="bold"),
                                text_color=UMSA_GOLD, pady=10)
        h2_label.pack(fill="x", padx=10)

        self.defect_buttons_frame = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        self.defect_buttons_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        self.defect_buttons = [] # Lista para almacenar los botones
        self._initialize_buttons()
        
    def _initialize_buttons(self):
        """Crea los botones de defecto."""
        for defect in self.DEFECTOS:
            btn_text = defect.upper().replace('_', ' ')
            btn = ctk.CTkButton(self.defect_buttons_frame, text=btn_text, 
                                command=lambda d=defect: self._send_prompt_for_defect(d),
                                fg_color=UMSA_GOLD, hover_color="#E0C250",
                                text_color="white", 
                                font=ctk.CTkFont(size=13, weight="bold"))
            btn.pack(fill="x", pady=5)
            self.defect_buttons.append(btn) # Almacenar la referencia

    # --------------------------------------------------------------------------
    # 2. ÁREA PRINCIPAL (Respuesta de IA y Chat)
    # --------------------------------------------------------------------------
    def _create_main_area(self, parent):
        main_area = ctk.CTkFrame(parent, corner_radius=8, fg_color="#2c2f33")
        main_area.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        main_area.grid_columnconfigure(0, weight=1)
        main_area.grid_rowconfigure(1, weight=1)

        h2_label = ctk.CTkLabel(main_area, text="Explicación Técnica Generada por IA", 
                                font=ctk.CTkFont(size=18, weight="bold"),
                                text_color=UMSA_GOLD, padx=15, pady=10)
        h2_label.grid(row=0, column=0, sticky="w")
        
        # --- Área de Respuesta (tk.Text) ---
        text_frame = ctk.CTkFrame(main_area, fg_color=UMSA_BG_DARK, corner_radius=6)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=15, pady=(0, 10))
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)
        
        self.response_textbox = tk.Text(text_frame, 
                                         bg=UMSA_BG_DARK, 
                                         fg=UMSA_TEXT_DARK, 
                                         selectbackground=UMSA_BLUE, 
                                         wrap="word", 
                                         font=self.font_normal,
                                         relief="flat", 
                                         padx=10, 
                                         pady=10)
        self.response_textbox.grid(row=0, column=0, sticky="nsew")
        
        # Configuramos los tags para tk.Text.
        self.response_textbox.tag_config("bold_text", font=self.font_bold, foreground=UMSA_TEXT_DARK)
        self.response_textbox.tag_config("loading", font=self.font_loading, foreground=UMSA_GOLD)
        self.response_textbox.tag_config("error", font=self.font_loading, foreground="red")
        self.response_textbox.tag_config("user_prompt", font=self.font_user_prompt, foreground=UMSA_BLUE)

        # --- Área de Citaciones (Oculta) ---
        self.sources_container = ctk.CTkFrame(main_area, fg_color="#2c2f33")
        self.sources_container.grid(row=2, column=0, sticky="ew", padx=15, pady=(0, 10))
        self.sources_container.grid_forget()

        # --- Input y Botón de Chat ---
        chat_frame = ctk.CTkFrame(main_area, fg_color="transparent")
        chat_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=10)
        chat_frame.grid_columnconfigure(0, weight=1)

        self.chat_entry = ctk.CTkEntry(chat_frame, placeholder_text="Pregunta a Gemini sobre un defecto o metalurgia...",
                                          font=ctk.CTkFont(size=13), height=40)
        self.chat_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.chat_entry.bind('<Return>', lambda event: self._send_custom_prompt())

        self.send_button = ctk.CTkButton(chat_frame, text="Enviar 🚀", width=100,
                                          command=self._send_custom_prompt,
                                          fg_color=UMSA_BLUE, hover_color="#004d99")
        self.send_button.grid(row=0, column=1, sticky="e")

    def _toggle_api_state(self, enabled):
        """Habilita o deshabilita los controles de la IA si el cliente falló."""
        state = "normal" if enabled else "disabled"
        
        # Deshabilitar botones de defecto
        for btn in self.defect_buttons:
            btn.configure(state=state)
        
        # Deshabilitar chat
        self.chat_entry.configure(state=state)
        self.send_button.configure(state=state)

    # --------------------------------------------------------------------------
    # 3. LÓGICA DE LA IA y UI
    # --------------------------------------------------------------------------
    def _insert_and_format_response(self, text):
        """Inserta el texto en el Textbox (tk.Text), aplicando tags para las negritas Markdown (**)."""
        
        parts = text.split('**')
        
        for i, part in enumerate(parts):
            if i % 2 == 1:
                # Parte impar: Estaba entre ** **, aplicar negrita
                self.response_textbox.insert("end", part, "bold_text")
            else:
                # Parte par: Texto normal
                self.response_textbox.insert("end", part, self.font_normal)
                
        self.response_textbox.see(tk.END) # Scroll al final

    def _set_loading(self, isLoading):
        """Maneja el estado de carga en la UI."""
        self.sources_container.grid_forget()
        
        state = tk.DISABLED if isLoading else tk.NORMAL
        self.chat_entry.configure(state=state)
        self.send_button.configure(state=state)
        
        self.response_textbox.configure(state=tk.NORMAL)
        
        if not isLoading:
            return 

        self.response_textbox.delete("1.0", "end") 
        loading_text = "Consultando a Gemini... Esto puede tardar unos segundos."
        self.response_textbox.insert("end", loading_text, "loading")
        self.response_textbox.configure(state=tk.DISABLED)

    def _send_prompt_for_defect(self, defect):
        """Maneja el click en los botones de defecto (consulta técnica)."""
        if self.client is None:
            messagebox.showwarning("API Deshabilitada", "El cliente de Gemini no se pudo inicializar. Funcionalidad de IA deshabilitada.")
            return

        self.last_defect = defect
        user_query = f"Dime todo lo relevante del defecto metalúrgico '{defect}'. Enfócate en la causa, morfología y el impacto en la calidad del material. Sé conciso, máximo 250 palabras. Usa negritas (**) para resaltar términos clave."
        
        threading.Thread(target=self._api_call_thread, args=(user_query, False)).start()


    def _send_custom_prompt(self):
        """Maneja el envío del texto del chat."""
        if self.client is None:
            messagebox.showwarning("API Deshabilitada", "El cliente de Gemini no se pudo inicializar. Funcionalidad de IA deshabilitada.")
            return

        custom_query = self.chat_entry.get().strip()
        if not custom_query:
            messagebox.showwarning("Advertencia", "Por favor, introduce una pregunta.")
            return

        self.response_textbox.configure(state=tk.NORMAL)
        
        current_content = self.response_textbox.get("1.0", "end-1c").strip()
        if "Selecciona un defecto" in current_content or current_content == "" or "ERROR" in current_content:
            self.response_textbox.delete("1.0", "end") # Borrar mensaje inicial
        
        # Añadir la pregunta del usuario
        self.response_textbox.insert("end", "\n\n[TÚ]: ", "user_prompt")
        self.response_textbox.insert("end", custom_query, self.font_normal)
        self.response_textbox.insert("end", "\n", self.font_normal)

        self.response_textbox.configure(state=tk.DISABLED)
        self.chat_entry.delete(0, tk.END)

        # 2. Iniciar la llamada a la API en un hilo
        threading.Thread(target=self._api_call_thread, args=(custom_query, True)).start()

    def _api_call_thread(self, user_query, is_chat):
        """Función que ejecuta la llamada a la API en un hilo separado."""
        
        # 1. Mostrar estado de carga (en la UI)
        self.after(0, lambda: self._set_loading(True))

        if not is_chat:
            system_prompt = "Actúa como un experto metalúrgico. Proporciona una explicación concisa y técnica (máximo 250 palabras) sobre el defecto solicitado. Utiliza negritas (**) para resaltar términos clave. La respuesta debe ser formal."
        else:
            system_prompt = "Actúa como un asistente metalúrgico. Responde de forma concisa (máximo 150 palabras) a la pregunta sobre defectos, metalurgia o calidad del material."

        try:
            # Llamada a la API de Gemini
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=user_query,
                config=dict(system_instruction=system_prompt)
            )
            
            # Procesar resultado en el hilo principal
            self.after(0, lambda: self._process_api_result(response.text, is_chat))

        except APIError as e:
            error_message = f"Ocurrió un error en la API. ¿Problemas de cuota/conexión? Detalle: {e}"
            self.after(0, lambda: self._handle_error(error_message))
        except Exception as e:
            error_message = f"Ocurrió un error inesperado. Detalle: {e}"
            self.after(0, lambda: self._handle_error(error_message))
        
    def _process_api_result(self, raw_text, is_chat):
        """Procesa el resultado y actualiza la UI (ejecutado en el hilo principal)."""
        self.response_textbox.configure(state=tk.NORMAL)
        
        if is_chat:
            # Si es chat, limpiar el indicador de carga y añadir la respuesta
            current_content = self.response_textbox.get("1.0", "end-1c").strip()
            # Limpiar solo el mensaje de carga antes de insertar la respuesta
            self.response_textbox.delete("1.0", "end")
            self.response_textbox.insert("end", current_content.replace("Consultando a Gemini... Esto puede tardar unos segundos.", ""))
            
            self.response_textbox.insert("end", "\n\n[GEMINI]: ", "bold_text")
            self._insert_and_format_response(raw_text)
        else:
            # Si es consulta técnica, reemplazar todo el contenido
            self.response_textbox.delete("1.0", "end")
            self._insert_and_format_response(raw_text)
            
        self.response_textbox.configure(state=tk.DISABLED)
        self.after(0, lambda: self._set_loading(False)) # Desactivar carga y habilitar botones

    def _handle_error(self, error_message):
        """Maneja y muestra errores en la UI (ejecutado en el hilo principal)."""
        self.after(0, lambda: self._set_loading(False)) # Desactivar carga
        
        self.response_textbox.configure(state=tk.NORMAL)
        self.response_textbox.delete("1.0", "end")
        self.response_textbox.insert("end", f"ERROR: {error_message}", "error")
        self.response_textbox.configure(state=tk.DISABLED)


# ------------------------------------------------------------------------------
# INICIO DE LA APLICACIÓN
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.getenv("GEMINI_API_KEY"):
        print("ADVERTENCIA: La variable de entorno GEMINI_API_KEY NO está definida.")
        print("El asistente se iniciará, pero las funciones de IA estarán deshabilitadas.")
    
    root = ctk.CTk()
    root.title("Ventana Principal (Base)")
    root.geometry("400x200")

    def open_assistant():
        assistant = DefectAssistantGUI(root)
        assistant.focus_set()

    btn = ctk.CTkButton(root, text="Abrir Asistente de Defectos (Gemini)", command=open_assistant)
    btn.pack(pady=50)

    root.mainloop()