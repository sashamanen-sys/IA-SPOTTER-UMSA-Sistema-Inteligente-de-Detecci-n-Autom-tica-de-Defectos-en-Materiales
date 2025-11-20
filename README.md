# 💡 IA Spotter UMSA: Detección de Defectos Superficiales

## 📝 Descripción del Proyecto
IA Spotter es una aplicación de **Visión por Computadora** diseñada para la identificación automática de defectos (fisuras, corrosión, inclusiones, etc.) en materiales utilizados en la **industria metalmecánica** y la manufactura. El proyecto está orientado a la formación de estudiantes de las carreras de Ingeniería **Aeronáutica** y **Mecánica Industrial** de la UMSA.

**Motivación:** En Bolivia, la inspección manual de componentes críticos en la aviación (El Alto) y en procesos industriales de **mecanizado** y **fundición** (La Paz) es lenta y propensa a errores. Esta herramienta utiliza Redes Neuronales Convolucionales (CNN) para automatizar la detección, promoviendo la **innovación educativa** alineada con la Agenda Patriótica 2025.

| Característica | Tecnología |
| :--- | :--- |
| **Modelo ML** | **CNN** supervisada (Keras/TensorFlow). Precisión ~95% en dataset NEU-SDD. |
| **Interfaz (GUI)** | **Tkinter** con branding UMSA (azul/blanco/dorado). |
| **Multimedia** | Carga de imágenes (PIL) y captura en vivo por **OpenCV**. |
| **Persistencia** | Almacenamiento de registros en **SQLite** (`defects.db`). |

---

## 🛠️ Guía de Uso y Ejecución

Para poner en marcha el proyecto, sigue estos pasos:

1.  **Entorno Virtual:** Activa tu entorno virtual (`venv`).
2.  **Instalación:** Asegúrate de tener las dependencias instaladas (o ejecuta la línea):
    ```bash
    pip install Pillow opencv-python tensorflow
    ```
3.  **Descarga del Modelo:** El modelo **`saved_model.h5`** (entrenado previamente en Colab) debe estar ubicado en la carpeta **`model/`**.
    > **Nota:** El entrenamiento se realiza en el *notebook* `colab_training.ipynb` para aprovechar las GPUs gratuitas.
4.  **Ejecución:** Inicia la aplicación principal:
    ```bash
    python main.py
    ```
5.  **Uso:**
    * Haz clic en **"Cargar Imagen"** o **"Capturar por Cámara"**.
    * Haz clic en **"Clasificar Defecto"**.
    * El resultado se muestra en pantalla y el registro de la clasificación se almacena automáticamente en **`defects.db`**.

---

## 🧠 Explicación del Modelo ML

El corazón del proyecto es un clasificador de imágenes basado en una CNN:

* **Arquitectura:** Red Neuronal Convolucional (CNN) secuencial simple con 3 capas `Conv2D` y `MaxPooling2D`, seguida de capas `Dense`.
* **Dataset:** Más de 1800 imágenes del dataset NEU-SDD (defectos en acero). Se utilizó **Augmentación** (rotación, zoom) para mejorar la generalización.
* **Métricas:** El modelo alcanza una **Precisión (Accuracy)** en validación de aproximadamente **95%**.
* **Coherencia con la Industria:** La detección de defectos superficiales es crucial para el control de calidad en **componentes estructurales y maquinaria** dentro de la ingeniería industrial.
* **Limitación:** El *dataset* base es de acero, lo que requiere **adaptación (*fine-tuning*)** para aplicarse a otros materiales industriales o aeronáuticos específicos.

---

## 🧑‍💻 Repartición de Roles

| Estudiante | Rol Principal | Módulos Clave |
| :--- | :--- | :--- |
| **Maria Riveros** | **Machine Learning (ML)** | Desarrollo y *fine-tuning* de la CNN, *script* `ml_model.py`. |
| **Sara Zenteno** | **Fundamentación Teórica y Análisis de Impacto.** | Justificación, impacto y comunicación técnica/aplicada del proyecto |
| **Haled Laura** | **Base de Datos e Integración** | Desarrollo de la clase SQLite DB (`database.py`) y aseguramiento de la integración ML-GUI. |
| **Sasha Antequera** | **GUI y Multimedia - Documentación y Soporte** | Diseño de la Interfaz (`main_gui.py`), integración de Tkinter, PIL y OpenCV (cámara). Elaboración y mantenimiento de la documentación técnica y gestión de dependencias/entorno. |

---

## 🔗 Referencias

* **UMSA:** [https://www.umsa.bo/](https://www.umsa.bo/)
* **Dataset Base:** Kaggle NEU-SDD.
* **Frameworks:** TensorFlow & Keras.

**Desarrollado en La Paz, Bolivia - Noviembre 2025.**
