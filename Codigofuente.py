import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import yt_dlp
import os
from datetime import datetime
import threading
import re
from ttkthemes import ThemedTk
import subprocess
import vlc
import json
import queue
import time
from pathlib import Path
import sys
import platform
import webbrowser
from PIL import Image, ImageTk
import requests
from io import BytesIO
import concurrent.futures
import shutil

class ModernDownloadManager:
    def __init__(self, root):
        self.root = root
        self.root.title("Media Downloader Pro - Universal Download Manager")
        self.root.geometry("1100x750+50+50")
        self.root.minsize(900, 600)
        
        # Configuración de temas modernos
        self.themes = {
            "🌙 Dark Matrix": "equilux",
            "☀️ Light Blue": "arc",
            "🎮 Cyber Punk": "plastik",
            "🌊 Ocean Deep": "blue",
            "🔮 Purple Haze": "breeze",
            "🌌 Space Black": "black",
            "🏔️ Arctic White": "clearlooks",
            "🔥 Fire Red": "radiance",
            "🌿 Forest Green": "itft1",
            "💎 Crystal": "keramik"
        }
        
        # Variables de configuración
        self.transparency = tk.DoubleVar(value=0.95)
        self.current_theme = tk.StringVar(value="🌙 Dark Matrix")
        self.dark_mode = tk.BooleanVar(value=True)
        
        # Configurar el tema inicial
        self.root.set_theme(self.themes[self.current_theme.get()])
        self.root.attributes('-alpha', self.transparency.get())
        
        # Variables principales
        self.url_var = tk.StringVar()
        self.status_var = tk.StringVar(value="🟢 Listo para descargar")
        self.progress_var = tk.DoubleVar()
        self.download_speed_var = tk.StringVar(value="Velocidad: --")
        self.time_remaining_var = tk.StringVar(value="Tiempo restante: --")
        self.current_file_var = tk.StringVar(value="Archivo: Ninguno")
        
        # Cola de descargas
        self.download_queue = queue.Queue()
        self.download_history = []
        self.active_downloads = []
        self.is_downloading = False
        self.cancel_flag = False
        
        # Configuración de formatos
        self.supported_platforms = {
            "YouTube": ["youtube.com", "youtu.be"],
            "Facebook": ["facebook.com", "fb.watch"],
            "Instagram": ["instagram.com"],
            "Twitter/X": ["twitter.com", "x.com"],
            "TikTok": ["tiktok.com"],
            "Twitch": ["twitch.tv"],
            "Vimeo": ["vimeo.com"],
            "Dailymotion": ["dailymotion.com"],
            "Reddit": ["reddit.com"],
            "SoundCloud": ["soundcloud.com"],
            "LinkedIn": ["linkedin.com"],
            "Tumblr": ["tumblr.com"],
            "Pinterest": ["pinterest.com"],
            "9GAG": ["9gag.com"],
            "Bilibili": ["bilibili.com"],
            "Rumble": ["rumble.com"],
            "OK.ru": ["ok.ru"],
            "Likee": ["likee.video"],
            "Kwai": ["kwai.com"],
            "Snapchat": ["snapchat.com"],
            "Spotify": ["spotify.com"],
            "Apple Music": ["music.apple.com"]
        }
        
        # Formatos de salida
        self.video_formats = {
            "MP4 (H.264)": "mp4",
            "MP4 (H.265/HEVC)": "mp4[height<=?1080]",
            "WebM (VP9)": "webm",
            "MKV (Matroska)": "mkv",
            "AVI (Xvid)": "avi",
            "MOV (Apple)": "mov",
            "FLV (Flash)": "flv",
            "3GP (Móvil)": "3gp"
        }
        
        self.audio_formats = {
            "MP3 (128kbps)": "mp3",
            "MP3 (192kbps)": "mp3[abr=192]",
            "MP3 (320kbps)": "mp3[abr=320]",
            "AAC (M4A)": "m4a",
            "OGG Vorbis": "ogg",
            "WAV (Lossless)": "wav",
            "FLAC (Lossless)": "flac",
            "Opus": "opus",
            "WMA": "wma"
        }
        
        # Calidades de video
        self.video_qualities = [
            "Mejor calidad disponible",
            "8K (4320p) - Ultra HD",
            "4K (2160p) - Ultra HD", 
            "1440p (2K) - QHD",
            "1080p - Full HD",
            "720p - HD",
            "480p - SD",
            "360p - SD",
            "240p - LD",
            "144p - Mínima"
        ]
        
        # Configuración de la aplicación
        self.config_file = os.path.join(os.path.expanduser("~"), ".mediadownloader_config.json")
        self.load_config()
        
        # Información de la aplicación
        self.app_info = {
            "name": "Media Downloader Pro",
            "version": "2.0.0",
            "author": "Fredis Aguas",
            "nickname": "Akwarius",
            "year": "2024",
            "email": "fredisaguas@gmail.com",
            "website": "https://github.com/akwarius",
            "description": "Gestor universal de descargas multimedia\nSoporte para 20+ plataformas\nConversión a múltiples formatos"
        }
        
        # Inicializar VLC para previsualización
        try:
            self.vlc_instance = vlc.Instance('--no-xlib')
            self.player = self.vlc_instance.media_player_new()
        except:
            self.vlc_instance = None
            self.player = None
            
        # Configurar interfaz
        self.setup_modern_ui()
        
        # Iniciar monitor de descargas
        self.monitor_downloads()
        
        # Cargar historial de descargas
        self.load_download_history()

    def setup_modern_ui(self):
        """Configura la interfaz de usuario moderna"""
        # Estilo personalizado
        self.style = ttk.Style()
        self.configure_styles()
        
        # Frame principal con pestañas
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Pestaña 1: Descargas
        self.download_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.download_tab, text="🎬 Descargas")
        
        # Pestaña 2: Conversión
        self.convert_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.convert_tab, text="🔄 Conversión")
        
        # Pestaña 3: Historial
        self.history_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.history_tab, text="📊 Historial")
        
        # Pestaña 4: Configuración
        self.settings_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.settings_tab, text="⚙️ Configuración")
        
        # Configurar cada pestaña
        self.setup_download_tab()
        self.setup_convert_tab()
        self.setup_history_tab()
        self.setup_settings_tab()
        
        # Barra de estado
        self.setup_status_bar()

    def configure_styles(self):
        """Configura estilos personalizados"""
        # Colores para modo oscuro
        if self.dark_mode.get():
            bg_color = "#1a1a1a"
            fg_color = "#ffffff"
            accent_color = "#00ff88"
            secondary_bg = "#2d2d2d"
        else:
            bg_color = "#f5f5f5"
            fg_color = "#000000"
            accent_color = "#007acc"
            secondary_bg = "#e0e0e0"
            
        self.style.configure("Custom.TFrame", background=bg_color)
        self.style.configure("Title.TLabel", 
                           font=("Segoe UI", 16, "bold"),
                           foreground=accent_color)
        
        # Barra de progreso personalizada
        self.style.configure("Custom.Horizontal.TProgressbar",
                           troughcolor=secondary_bg,
                           background=accent_color,
                           bordercolor=accent_color,
                           lightcolor=accent_color,
                           darkcolor=accent_color)

    def setup_download_tab(self):
        """Configura la pestaña de descargas"""
        # Frame principal
        main_frame = ttk.Frame(self.download_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, 
                 text="📥 Descargador Universal",
                 style="Title.TLabel").pack(side=tk.LEFT)
        
        # Indicador de plataforma detectada
        self.platform_indicator = ttk.Label(title_frame, 
                                          text="🌐 Plataforma: --",
                                          font=("Segoe UI", 10))
        self.platform_indicator.pack(side=tk.RIGHT, padx=10)
        
        # Frame de entrada de URL
        url_frame = ttk.LabelFrame(main_frame, text="🔗 Enlace del contenido", padding=15)
        url_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Entrada de URL con placeholder
        url_container = ttk.Frame(url_frame)
        url_container.pack(fill=tk.X)
        
        self.url_entry = ttk.Entry(url_container, 
                                  textvariable=self.url_var,
                                  font=("Segoe UI", 11),
                                  width=60)
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.url_entry.bind("<KeyRelease>", self.analyze_url)
        
        # Botones de URL
        btn_container = ttk.Frame(url_container)
        btn_container.pack(side=tk.RIGHT)
        
        ttk.Button(btn_container, 
                  text="📋 Pegar",
                  command=self.paste_url,
                  width=12).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(btn_container,
                  text="🧹 Limpiar",
                  command=self.clear_url,
                  width=12).pack(side=tk.LEFT, padx=2)
        
        # Frame de opciones
        options_frame = ttk.LabelFrame(main_frame, text="⚙️ Opciones de descarga", padding=15)
        options_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Grid para opciones
        options_grid = ttk.Frame(options_frame)
        options_grid.pack(fill=tk.X)
        
        # Tipo de contenido
        ttk.Label(options_grid, text="Tipo:", font=("Segoe UI", 10)).grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.content_type = tk.StringVar(value="Video + Audio")
        content_combo = ttk.Combobox(options_grid,
                                    textvariable=self.content_type,
                                    values=["Video + Audio", "Solo Video", "Solo Audio"],
                                    state="readonly",
                                    width=20)
        content_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        content_combo.bind("<<ComboboxSelected>>", self.update_format_options)
        
        # Calidad
        ttk.Label(options_grid, text="Calidad:", font=("Segoe UI", 10)).grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        self.quality_var = tk.StringVar(value="Mejor calidad disponible")
        quality_combo = ttk.Combobox(options_grid,
                                    textvariable=self.quality_var,
                                    values=self.video_qualities,
                                    state="readonly",
                                    width=25)
        quality_combo.grid(row=0, column=3, sticky=tk.W)
        
        # Formato
        ttk.Label(options_grid, text="Formato:", font=("Segoe UI", 10)).grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.format_var = tk.StringVar(value="MP4 (H.264)")
        self.format_combo = ttk.Combobox(options_grid,
                                        textvariable=self.format_var,
                                        values=list(self.video_formats.keys()),
                                        state="readonly",
                                        width=20)
        self.format_combo.grid(row=1, column=1, sticky=tk.W, padx=(0, 20), pady=(10, 0))
        
        # Carpeta de destino
        ttk.Label(options_grid, text="Destino:", font=("Segoe UI", 10)).grid(row=1, column=2, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        
        dest_frame = ttk.Frame(options_grid)
        dest_frame.grid(row=1, column=3, sticky=tk.W+tk.E, pady=(10, 0))
        
        self.download_path = tk.StringVar(value=self.config.get("download_path", 
                                                               os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader")))
        self.path_label = ttk.Label(dest_frame, 
                                   text=self.download_path.get(),
                                   font=("Segoe UI", 9),
                                   relief=tk.SUNKEN,
                                   padding=5,
                                   width=40,
                                   anchor=tk.W)
        self.path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(dest_frame,
                  text="📂",
                  command=self.select_download_folder,
                  width=3).pack(side=tk.LEFT, padx=(5, 0))
        
        # Frame de información del video
        self.info_frame = ttk.LabelFrame(main_frame, text="📊 Información del contenido", padding=15)
        self.info_frame.pack(fill=tk.X, pady=(0, 15))
        
        info_container = ttk.Frame(self.info_frame)
        info_container.pack(fill=tk.X)
        
        # Columna de información
        info_col = ttk.Frame(info_container)
        info_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.title_label = ttk.Label(info_col, text="📌 Título: --", font=("Segoe UI", 10), anchor=tk.W)
        self.title_label.pack(anchor=tk.W, pady=2)
        
        self.duration_label = ttk.Label(info_col, text="⏱️ Duración: --", font=("Segoe UI", 10), anchor=tk.W)
        self.duration_label.pack(anchor=tk.W, pady=2)
        
        self.views_label = ttk.Label(info_col, text="👁️ Vistas: --", font=("Segoe UI", 10), anchor=tk.W)
        self.views_label.pack(anchor=tk.W, pady=2)
        
        self.channel_label = ttk.Label(info_col, text="👤 Canal: --", font=("Segoe UI", 10), anchor=tk.W)
        self.channel_label.pack(anchor=tk.W, pady=2)
        
        # Columna de miniatura
        thumb_col = ttk.Frame(info_container)
        thumb_col.pack(side=tk.RIGHT, padx=(20, 0))
        
        self.thumbnail_label = ttk.Label(thumb_col, text="🎬", font=("Segoe UI", 40))
        self.thumbnail_label.pack()
        
        # Frame de progreso
        progress_frame = ttk.LabelFrame(main_frame, text="📈 Progreso de descarga", padding=15)
        progress_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Barra de progreso principal
        self.progress_bar = ttk.Progressbar(progress_frame,
                                          variable=self.progress_var,
                                          style="Custom.Horizontal.TProgressbar",
                                          length=100)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Información de progreso
        progress_info = ttk.Frame(progress_frame)
        progress_info.pack(fill=tk.X)
        
        self.status_label = ttk.Label(progress_info,
                                     textvariable=self.status_var,
                                     font=("Segoe UI", 10, "bold"))
        self.status_label.pack(anchor=tk.W, pady=2)
        
        self.speed_label = ttk.Label(progress_info,
                                    textvariable=self.download_speed_var,
                                    font=("Segoe UI", 9))
        self.speed_label.pack(anchor=tk.W, pady=1)
        
        self.time_label = ttk.Label(progress_info,
                                   textvariable=self.time_remaining_var,
                                   font=("Segoe UI", 9))
        self.time_label.pack(anchor=tk.W, pady=1)
        
        self.file_label = ttk.Label(progress_info,
                                   textvariable=self.current_file_var,
                                   font=("Segoe UI", 9))
        self.file_label.pack(anchor=tk.W, pady=1)
        
        # Botones de control
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Botón de descarga
        self.download_btn = ttk.Button(buttons_frame,
                                      text="⬇️ Descargar ahora",
                                      command=self.start_download,
                                      style="Accent.TButton",
                                      width=20)
        self.download_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón para agregar a cola
        self.queue_btn = ttk.Button(buttons_frame,
                                   text="📋 Agregar a cola",
                                   command=self.add_to_queue,
                                   width=20)
        self.queue_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón de cancelar
        self.cancel_btn = ttk.Button(buttons_frame,
                                    text="❌ Cancelar",
                                    command=self.cancel_download,
                                    state=tk.DISABLED,
                                    width=20)
        self.cancel_btn.pack(side=tk.LEFT, padx=10)
        
        # Botón de previsualización
        self.preview_btn = ttk.Button(buttons_frame,
                                     text="🎥 Previsualizar",
                                     command=self.preview_content,
                                     state=tk.DISABLED,
                                     width=20)
        self.preview_btn.pack(side=tk.RIGHT)
        
        # Panel de cola de descargas
        queue_frame = ttk.LabelFrame(main_frame, text="📋 Cola de descargas", padding=15)
        queue_frame.pack(fill=tk.BOTH, expand=True)
        
        # Lista de cola
        columns = ("#", "Plataforma", "Título", "Estado")
        self.queue_tree = ttk.Treeview(queue_frame, columns=columns, show="headings", height=4)
        
        for col in columns:
            self.queue_tree.heading(col, text=col)
            self.queue_tree.column(col, width=100)
            
        self.queue_tree.column("#", width=50)
        self.queue_tree.column("Plataforma", width=100)
        self.queue_tree.column("Título", width=300)
        self.queue_tree.column("Estado", width=100)
        
        scrollbar = ttk.Scrollbar(queue_frame, orient=tk.VERTICAL, command=self.queue_tree.yview)
        self.queue_tree.configure(yscrollcommand=scrollbar.set)
        
        self.queue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Botones de control de cola
        queue_buttons = ttk.Frame(queue_frame)
        queue_buttons.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
        ttk.Button(queue_buttons,
                  text="▶️ Iniciar cola",
                  command=self.start_queue,
                  width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(queue_buttons,
                  text="⏸️ Pausar cola",
                  command=self.pause_queue,
                  width=15).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(queue_buttons,
                  text="🗑️ Limpiar cola",
                  command=self.clear_queue,
                  width=15).pack(side=tk.LEFT, padx=2)

    def setup_convert_tab(self):
        """Configura la pestaña de conversión"""
        main_frame = ttk.Frame(self.convert_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame,
                 text="🔄 Conversor de Formatos",
                 style="Title.TLabel").pack(anchor=tk.W, pady=(0, 20))
        
        # Frame de selección de archivos
        select_frame = ttk.LabelFrame(main_frame, text="📁 Seleccionar archivo", padding=15)
        select_frame.pack(fill=tk.X, pady=(0, 15))
        
        file_container = ttk.Frame(select_frame)
        file_container.pack(fill=tk.X)
        
        self.convert_file_var = tk.StringVar()
        ttk.Entry(file_container,
                 textvariable=self.convert_file_var,
                 font=("Segoe UI", 11),
                 width=50).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        
        ttk.Button(file_container,
                  text="📂 Buscar",
                  command=self.select_file_to_convert,
                  width=15).pack(side=tk.RIGHT)
        
        # Frame de opciones de conversión
        convert_frame = ttk.LabelFrame(main_frame, text="⚙️ Opciones de conversión", padding=15)
        convert_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Formato de origen
        ttk.Label(convert_frame, text="Formato original:", font=("Segoe UI", 10)).pack(anchor=tk.W)
        self.source_format_var = tk.StringVar()
        ttk.Label(convert_frame,
                 textvariable=self.source_format_var,
                 font=("Segoe UI", 9),
                 relief=tk.SUNKEN,
                 padding=5).pack(fill=tk.X, pady=(0, 10))
        
        # Formato de destino
        ttk.Label(convert_frame, text="Convertir a:", font=("Segoe UI", 10)).pack(anchor=tk.W)
        
        format_container = ttk.Frame(convert_frame)
        format_container.pack(fill=tk.X, pady=(0, 10))
        
        # Video formats
        ttk.Label(format_container, text="Video:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
        self.convert_video_format = tk.StringVar(value="MP4")
        video_combo = ttk.Combobox(format_container,
                                  textvariable=self.convert_video_format,
                                  values=list(self.video_formats.keys()),
                                  state="readonly",
                                  width=20)
        video_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Audio formats
        ttk.Label(format_container, text="Audio:", font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 10))
        self.convert_audio_format = tk.StringVar(value="MP3")
        audio_combo = ttk.Combobox(format_container,
                                  textvariable=self.convert_audio_format,
                                  values=list(self.audio_formats.keys()),
                                  state="readonly",
                                  width=20)
        audio_combo.pack(side=tk.LEFT)
        
        # Calidad de conversión
        ttk.Label(convert_frame, text="Calidad:", font=("Segoe UI", 10)).pack(anchor=tk.W)
        self.convert_quality_var = tk.StringVar(value="Alta (Original)")
        quality_combo = ttk.Combobox(convert_frame,
                                    textvariable=self.convert_quality_var,
                                    values=["Alta (Original)", "Media", "Baja", "Personalizada"],
                                    state="readonly",
                                    width=30)
        quality_combo.pack(fill=tk.X, pady=(0, 15))
        
        # Botones de conversión
        button_frame = ttk.Frame(convert_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame,
                  text="🎬 Extraer audio",
                  command=self.extract_audio,
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame,
                  text="🎵 Convertir audio",
                  command=self.convert_audio,
                  width=20).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame,
                  text="🎥 Convertir video",
                  command=self.convert_video,
                  width=20).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(button_frame,
                  text="🔄 Batch convertir",
                  command=self.batch_convert,
                  width=20).pack(side=tk.RIGHT)

    def setup_history_tab(self):
        """Configura la pestaña de historial"""
        main_frame = ttk.Frame(self.history_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame,
                 text="📊 Historial de descargas",
                 style="Title.TLabel").pack(anchor=tk.W, pady=(0, 20))
        
        # Botones de control de historial
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Button(control_frame,
                  text="🔄 Actualizar",
                  command=self.refresh_history,
                  width=15).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(control_frame,
                  text="🗑️ Limpiar historial",
                  command=self.clear_history,
                  width=15).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame,
                  text="📊 Exportar CSV",
                  command=self.export_history_csv,
                  width=15).pack(side=tk.LEFT, padx=10)
        
        ttk.Button(control_frame,
                  text="📈 Estadísticas",
                  command=self.show_statistics,
                  width=15).pack(side=tk.RIGHT)
        
        # Treeview para historial
        columns = ("Fecha", "Plataforma", "Título", "Formato", "Tamaño", "Estado")
        self.history_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.history_tree.heading(col, text=col)
            self.history_tree.column(col, width=120)
            
        self.history_tree.column("Título", width=250)
        self.history_tree.column("Fecha", width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        h_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.history_tree.xview)
        self.history_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        self.history_tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

    def setup_settings_tab(self):
        """Configura la pestaña de configuración"""
        main_frame = ttk.Frame(self.settings_tab)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Pestaña General
        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        
        # Pestaña Descargas
        downloads_tab = ttk.Frame(notebook)
        notebook.add(downloads_tab, text="Descargas")
        
        # Pestaña Avanzado
        advanced_tab = ttk.Frame(notebook)
        notebook.add(advanced_tab, text="Avanzado")
        
        self.setup_general_settings(general_tab)
        self.setup_download_settings(downloads_tab)
        self.setup_advanced_settings(advanced_tab)

    def setup_general_settings(self, parent):
        """Configuración general"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tema
        ttk.Label(frame, text="🎨 Tema visual:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        theme_container = ttk.Frame(frame)
        theme_container.pack(fill=tk.X, pady=(0, 15))
        
        for theme_name in self.themes.keys():
            rb = ttk.Radiobutton(theme_container,
                                text=theme_name,
                                value=theme_name,
                                variable=self.current_theme,
                                command=self.apply_theme)
            rb.pack(anchor=tk.W, pady=2)
        
        # Transparencia
        ttk.Label(frame, text="🔍 Transparencia:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        scale_frame = ttk.Frame(frame)
        scale_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Scale(scale_frame,
                 from_=0.3, to=1.0,
                 variable=self.transparency,
                 command=self.apply_transparency,
                 orient=tk.HORIZONTAL).pack(fill=tk.X)
        
        # Modo oscuro/claro
        ttk.Checkbutton(frame,
                       text="🌓 Modo oscuro",
                       variable=self.dark_mode,
                       command=self.toggle_dark_mode).pack(anchor=tk.W, pady=10)
        
        # Limpieza automática
        ttk.Label(frame, text="🧹 Limpieza automática:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.auto_clean_var = tk.BooleanVar(value=self.config.get("auto_clean", False))
        ttk.Checkbutton(frame,
                       text="Eliminar archivos temporales automáticamente",
                       variable=self.auto_clean_var).pack(anchor=tk.W, pady=2)
        
        self.clean_days_var = tk.IntVar(value=self.config.get("clean_days", 7))
        spin_frame = ttk.Frame(frame)
        spin_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(spin_frame, text="Mantener archivos por:").pack(side=tk.LEFT)
        ttk.Spinbox(spin_frame,
                   from_=1, to=30,
                   textvariable=self.clean_days_var,
                   width=5).pack(side=tk.LEFT, padx=(5, 0))
        ttk.Label(spin_frame, text="días").pack(side=tk.LEFT, padx=(5, 0))

    def setup_download_settings(self, parent):
        """Configuración de descargas"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Descargas simultáneas
        ttk.Label(frame, text="⚡ Descargas simultáneas:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        self.concurrent_downloads_var = tk.IntVar(value=self.config.get("concurrent_downloads", 3))
        spin_frame = ttk.Frame(frame)
        spin_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(spin_frame, text="Número máximo:").pack(side=tk.LEFT)
        ttk.Spinbox(spin_frame,
                   from_=1, to=10,
                   textvariable=self.concurrent_downloads_var,
                   width=5).pack(side=tk.LEFT, padx=5)
        
        # Velocidad de descarga
        ttk.Label(frame, text="📶 Límite de velocidad:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.speed_limit_var = tk.StringVar(value=self.config.get("speed_limit", "0"))
        speed_frame = ttk.Frame(frame)
        speed_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Entry(speed_frame,
                 textvariable=self.speed_limit_var,
                 width=10).pack(side=tk.LEFT)
        ttk.Label(speed_frame, text="KB/s (0 = ilimitado)").pack(side=tk.LEFT, padx=(5, 0))
        
        # Reintentos
        ttk.Label(frame, text="🔄 Reintentos de descarga:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.retry_count_var = tk.IntVar(value=self.config.get("retry_count", 3))
        retry_frame = ttk.Frame(frame)
        retry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(retry_frame, text="Número de reintentos:").pack(side=tk.LEFT)
        ttk.Spinbox(retry_frame,
                   from_=0, to=10,
                   textvariable=self.retry_count_var,
                   width=5).pack(side=tk.LEFT, padx=5)
        
        # Carpeta predeterminada
        ttk.Label(frame, text="📂 Carpeta de descargas:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        default_path_frame = ttk.Frame(frame)
        default_path_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.default_path_var = tk.StringVar(value=self.config.get("default_path", ""))
        ttk.Entry(default_path_frame,
                 textvariable=self.default_path_var,
                 width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(default_path_frame,
                  text="Examinar",
                  command=self.browse_default_path,
                  width=10).pack(side=tk.RIGHT)

    def setup_advanced_settings(self, parent):
        """Configuración avanzada"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Configuración de proxy
        ttk.Label(frame, text="🔗 Configuración de Proxy:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(0, 10))
        
        self.proxy_var = tk.StringVar(value=self.config.get("proxy", ""))
        ttk.Entry(frame,
                 textvariable=self.proxy_var,
                 width=50).pack(fill=tk.X, pady=(0, 10))
        ttk.Label(frame, text="Ejemplo: http://usuario:contraseña@proxy:puerto").pack(anchor=tk.W, pady=(0, 15))
        
        # Configuración de FFmpeg
        ttk.Label(frame, text="🎬 Ruta de FFmpeg:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        ffmpeg_frame = ttk.Frame(frame)
        ffmpeg_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.ffmpeg_path_var = tk.StringVar(value=self.config.get("ffmpeg_path", "ffmpeg"))
        ttk.Entry(ffmpeg_frame,
                 textvariable=self.ffmpeg_path_var,
                 width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(ffmpeg_frame,
                  text="Auto-detectar",
                  command=self.auto_detect_ffmpeg,
                  width=12).pack(side=tk.RIGHT)
        
        # Opciones avanzadas
        ttk.Label(frame, text="⚡ Opciones avanzadas:", font=("Segoe UI", 11, "bold")).pack(anchor=tk.W, pady=(10, 5))
        
        self.keep_temp_var = tk.BooleanVar(value=self.config.get("keep_temp", False))
        ttk.Checkbutton(frame,
                       text="Mantener archivos temporales",
                       variable=self.keep_temp_var).pack(anchor=tk.W, pady=2)
        
        self.skip_existing_var = tk.BooleanVar(value=self.config.get("skip_existing", True))
        ttk.Checkbutton(frame,
                       text="Saltar archivos existentes",
                       variable=self.skip_existing_var).pack(anchor=tk.W, pady=2)
        
        self.embed_metadata_var = tk.BooleanVar(value=self.config.get("embed_metadata", True))
        ttk.Checkbutton(frame,
                       text="Incrustar metadatos",
                       variable=self.embed_metadata_var).pack(anchor=tk.W, pady=2)
        
        # Botones de acción
        action_frame = ttk.Frame(frame)
        action_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(action_frame,
                  text="💾 Guardar configuración",
                  command=self.save_config,
                  style="Accent.TButton",
                  width=20).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(action_frame,
                  text="🔄 Restaurar predeterminados",
                  command=self.reset_settings,
                  width=20).pack(side=tk.LEFT)

    def setup_status_bar(self):
        """Configura la barra de estado"""
        status_bar = ttk.Frame(self.root, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Estado de conexión
        self.connection_status = ttk.Label(status_bar, text="🟢 En línea", font=("Segoe UI", 9))
        self.connection_status.pack(side=tk.LEFT, padx=10)
        
        # Espacio utilizado
        self.space_used = ttk.Label(status_bar, text="💾 Espacio libre: --", font=("Segoe UI", 9))
        self.space_used.pack(side=tk.LEFT, padx=10)
        
        # Descargas activas
        self.active_downloads_label = ttk.Label(status_bar, text="📥 Activas: 0", font=("Segoe UI", 9))
        self.active_downloads_label.pack(side=tk.LEFT, padx=10)
        
        # Versión
        version_text = f"{self.app_info['name']} v{self.app_info['version']}"
        ttk.Label(status_bar, text=version_text, font=("Segoe UI", 9)).pack(side=tk.RIGHT, padx=10)
        
        # Actualizar información de espacio
        self.update_space_info()

    # ========== FUNCIONALIDADES PRINCIPALES ==========

    def analyze_url(self, event=None):
        """Analiza la URL para detectar la plataforma"""
        url = self.url_var.get().strip()
        if not url:
            self.platform_indicator.config(text="🌐 Plataforma: --")
            return
            
        detected = False
        for platform_name, domains in self.supported_platforms.items():
            for domain in domains:
                if domain in url:
                    self.platform_indicator.config(text=f"🌐 Plataforma: {platform_name}")
                    detected = True
                    break
            if detected:
                break
                
        if not detected:
            self.platform_indicator.config(text="🌐 Plataforma: Desconocida")
            
        # Obtener información si la URL parece válida
        if "http" in url and len(url) > 20:
            self.get_url_info()

    def get_url_info(self):
        """Obtiene información de la URL"""
        url = self.url_var.get().strip()
        if not url:
            return
            
        def fetch_info():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'extract_flat': True,
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Actualizar UI en hilo principal
                    self.root.after(0, lambda: self.update_url_info(info))
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_error(f"Error obteniendo información: {str(e)}"))
                
        threading.Thread(target=fetch_info, daemon=True).start()

    def update_url_info(self, info):
        """Actualiza la información de la URL"""
        if not info:
            return
            
        # Título
        title = info.get('title', 'Sin título')
        if len(title) > 60:
            title = title[:57] + "..."
        self.title_label.config(text=f"📌 Título: {title}")
        
        # Duración
        duration = info.get('duration', 0)
        if duration:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            if hours > 0:
                duration_str = f"{hours}:{minutes:02d}:{seconds:02d}"
            else:
                duration_str = f"{minutes}:{seconds:02d}"
        else:
            duration_str = "Desconocida"
        self.duration_label.config(text=f"⏱️ Duración: {duration_str}")
        
        # Vistas
        views = info.get('view_count', 0)
        if views:
            if views >= 1000000:
                views_str = f"{views/1000000:.1f}M"
            elif views >= 1000:
                views_str = f"{views/1000:.1f}K"
            else:
                views_str = str(views)
        else:
            views_str = "Desconocidas"
        self.views_label.config(text=f"👁️ Vistas: {views_str}")
        
        # Canal
        uploader = info.get('uploader', 'Desconocido')
        self.channel_label.config(text=f"👤 Canal: {uploader}")
        
        # Miniatura
        thumbnail = info.get('thumbnail')
        if thumbnail:
            self.load_thumbnail(thumbnail)
            
        # Habilitar botón de previsualización
        self.preview_btn.config(state=tk.NORMAL)

    def load_thumbnail(self, url):
        """Carga la miniatura del video"""
        def fetch_thumbnail():
            try:
                response = requests.get(url, timeout=10)
                img_data = Image.open(BytesIO(response.content))
                img_data = img_data.resize((160, 90), Image.Resampling.LANCZOS)
                
                if self.dark_mode.get():
                    # Ajustar brillo para modo oscuro
                    img_data = img_data.point(lambda p: p * 0.8)
                    
                photo = ImageTk.PhotoImage(img_data)
                self.root.after(0, lambda: self.thumbnail_label.config(image=photo, text=""))
                self.root.after(0, lambda: setattr(self, 'thumbnail_image', photo))
            except:
                pass
                
        threading.Thread(target=fetch_thumbnail, daemon=True).start()

    def start_download(self):
        """Inicia una descarga"""
        url = self.url_var.get().strip()
        if not url:
            self.show_warning("Por favor, ingresa una URL válida")
            return
            
        self.add_download_to_queue(url, start_now=True)

    def add_to_queue(self):
        """Agrega una descarga a la cola"""
        url = self.url_var.get().strip()
        if not url:
            self.show_warning("Por favor, ingresa una URL válida")
            return
            
        self.add_download_to_queue(url, start_now=False)
        self.show_info("Descarga agregada a la cola")

    def add_download_to_queue(self, url, start_now=False):
        """Agrega una descarga a la cola interna"""
        download_item = {
            'url': url,
            'status': 'En cola' if not start_now else 'Iniciando',
            'added_time': datetime.now(),
            'format': self.format_var.get(),
            'quality': self.quality_var.get(),
            'type': self.content_type.get()
        }
        
        self.download_queue.put(download_item)
        
        # Actualizar UI de cola
        self.update_queue_display()
        
        # Iniciar descarga si se solicita
        if start_now and not self.is_downloading:
            self.process_next_download()

    def process_next_download(self):
        """Procesa la siguiente descarga en la cola"""
        if self.is_downloading or self.download_queue.empty():
            return
            
        self.is_downloading = True
        download_item = self.download_queue.get()
        
        # Actualizar estado
        download_item['status'] = 'Descargando'
        self.active_downloads.append(download_item)
        self.update_queue_display()
        
        # Configurar botones
        self.download_btn.config(state=tk.DISABLED)
        self.cancel_btn.config(state=tk.NORMAL)
        self.status_var.set("⬇️ Descargando...")
        
        # Iniciar descarga en hilo separado
        thread = threading.Thread(target=self.perform_download, args=(download_item,))
        thread.daemon = True
        thread.start()

    def perform_download(self, download_item):
        """Realiza la descarga"""
        try:
            # Configurar opciones de yt-dlp
            ydl_opts = self.get_ydl_options(download_item)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Hook de progreso
                def progress_hook(d):
                    if d['status'] == 'downloading':
                        # Calcular porcentaje
                        if 'total_bytes' in d and d['total_bytes']:
                            percent = (d['downloaded_bytes'] / d['total_bytes']) * 100
                            self.progress_var.set(percent)
                            
                            # Calcular velocidad
                            if '_speed_str' in d:
                                self.download_speed_var.set(f"Velocidad: {d['_speed_str']}")
                                
                            # Calcular tiempo restante
                            if '_eta_str' in d:
                                self.time_remaining_var.set(f"Tiempo restante: {d['_eta_str']}")
                                
                            # Actualizar nombre de archivo
                            if '_default_filename' in d:
                                filename = d['_default_filename']
                                self.current_file_var.set(f"Archivo: {filename}")
                                
                    elif d['status'] == 'finished':
                        self.progress_var.set(100)
                        self.status_var.set("✅ Descarga completada")
                        
                ydl_opts['progress_hooks'] = [progress_hook]
                
                # Extraer información y descargar
                info = ydl.extract_info(download_item['url'], download=True)
                
                # Actualizar historial
                self.add_to_history(info, download_item)
                
                # Actualizar UI
                self.root.after(0, self.download_completed)
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error en descarga: {str(e)}"))
            download_item['status'] = 'Error'
        finally:
            # Limpiar y procesar siguiente
            self.root.after(0, self.cleanup_download, download_item)

    def get_ydl_options(self, download_item):
        """Obtiene las opciones para yt-dlp"""
        format_code = self.get_format_code(download_item)
        
        opts = {
            'format': format_code,
            'outtmpl': os.path.join(self.download_path.get(), '%(title)s.%(ext)s'),
            'quiet': False,
            'no_warnings': True,
            'continuedl': True,
            'noprogress': False,
            'retries': self.retry_count_var.get(),
            'fragment_retries': 3,
            'skip_unavailable_fragments': True,
            'extract_flat': False,
            'writeinfojson': True,
            'writethumbnail': True,
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': ['es', 'en'],
            'embedsubtitles': True,
            'embedthumbnail': True,
            'embedmetadata': self.embed_metadata_var.get(),
            'postprocessors': [],
        }
        
        # Agregar postprocessors según el tipo
        if download_item['type'] == 'Solo Audio':
            opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': self.audio_formats.get(download_item['format'], 'mp3'),
                'preferredquality': '192',
            })
        elif 'mp3' in download_item['format'].lower():
            opts['postprocessors'].append({
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            })
            
        # Configurar proxy si existe
        proxy = self.proxy_var.get()
        if proxy:
            opts['proxy'] = proxy
            
        # Configurar límite de velocidad
        speed_limit = self.speed_limit_var.get()
        if speed_limit and speed_limit != "0":
            opts['ratelimit'] = int(speed_limit) * 1024
            
        return opts

    def get_format_code(self, download_item):
        """Obtiene el código de formato para yt-dlp"""
        quality = download_item['quality']
        content_type = download_item['type']
        
        if content_type == 'Solo Audio':
            return 'bestaudio/best'
            
        elif content_type == 'Solo Video':
            if quality == 'Mejor calidad disponible':
                return 'bestvideo'
            else:
                # Extraer resolución
                match = re.search(r'(\d+)p', quality)
                if match:
                    height = match.group(1)
                    return f'bestvideo[height<={height}]'
                else:
                    return 'bestvideo'
                    
        else:  # Video + Audio
            if quality == 'Mejor calidad disponible':
                return 'best'
            else:
                match = re.search(r'(\d+)p', quality)
                if match:
                    height = match.group(1)
                    return f'best[height<={height}]'
                else:
                    return 'best'

    def download_completed(self):
        """Llamado cuando se completa una descarga"""
        self.show_info("✅ Descarga completada exitosamente")
        self.refresh_history()

    def cleanup_download(self, download_item):
        """Limpia después de una descarga"""
        # Remover de activas
        if download_item in self.active_downloads:
            self.active_downloads.remove(download_item)
            
        # Actualizar UI
        self.update_queue_display()
        self.update_active_downloads_label()
        
        # Resetear controles
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.status_var.set("🟢 Listo para descargar")
        self.download_speed_var.set("Velocidad: --")
        self.time_remaining_var.set("Tiempo restante: --")
        self.current_file_var.set("Archivo: Ninguno")
        
        # Procesar siguiente descarga
        self.is_downloading = False
        self.process_next_download()

    # ========== FUNCIONALIDADES DE COLA ==========

    def start_queue(self):
        """Inicia el procesamiento de la cola"""
        if not self.download_queue.empty() and not self.is_downloading:
            self.process_next_download()

    def pause_queue(self):
        """Pausa la cola de descargas"""
        self.is_downloading = False
        self.status_var.set("⏸️ Cola pausada")

    def clear_queue(self):
        """Limpia la cola de descargas"""
        while not self.download_queue.empty():
            self.download_queue.get()
        self.update_queue_display()

    def update_queue_display(self):
        """Actualiza la visualización de la cola"""
        # Limpiar árbol
        for item in self.queue_tree.get_children():
            self.queue_tree.delete(item)
            
        # Agregar elementos en cola
        queue_items = list(self.download_queue.queue)
        for i, item in enumerate(queue_items, 1):
            platform = self.detect_platform(item['url'])
            self.queue_tree.insert("", "end", values=(
                i, platform, item['url'][:50] + "...", item['status']
            ))
            
        # Agregar descargas activas
        for item in self.active_downloads:
            platform = self.detect_platform(item['url'])
            self.queue_tree.insert("", "end", values=(
                "▶", platform, item['url'][:50] + "...", item['status']
            ))

    def detect_platform(self, url):
        """Detecta la plataforma de una URL"""
        for platform_name, domains in self.supported_platforms.items():
            for domain in domains:
                if domain in url:
                    return platform_name
        return "Desconocida"

    # ========== FUNCIONALIDADES DE CONVERSIÓN ==========

    def select_file_to_convert(self):
        """Selecciona un archivo para convertir"""
        filetypes = [
            ("Todos los archivos multimedia", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.webm;*.mp3;*.wav;*.flac;*.aac;*.m4a"),
            ("Videos", "*.mp4;*.mkv;*.avi;*.mov;*.flv;*.webm"),
            ("Audio", "*.mp3;*.wav;*.flac;*.aac;*.m4a;*.ogg"),
        ]
        
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo para convertir",
            filetypes=filetypes
        )
        
        if filename:
            self.convert_file_var.set(filename)
            self.detect_file_format(filename)

    def detect_file_format(self, filename):
        """Detecta el formato del archivo"""
        ext = os.path.splitext(filename)[1].lower().replace('.', '')
        self.source_format_var.set(ext.upper())
        
        # Actualizar opciones de conversión según el tipo
        if ext in ['mp4', 'mkv', 'avi', 'mov', 'flv', 'webm']:
            self.convert_video_format.set("MP4")
        elif ext in ['mp3', 'wav', 'flac', 'aac', 'm4a', 'ogg']:
            self.convert_audio_format.set("MP3")

    def extract_audio(self):
        """Extrae audio de un video"""
        input_file = self.convert_file_var.get()
        if not input_file or not os.path.exists(input_file):
            self.show_warning("Selecciona un archivo válido")
            return
            
        output_format = self.convert_audio_format.get()
        output_file = self.get_output_filename(input_file, output_format)
        
        # Ejecutar FFmpeg en hilo separado
        threading.Thread(
            target=self.run_ffmpeg_extract_audio,
            args=(input_file, output_file),
            daemon=True
        ).start()

    def run_ffmpeg_extract_audio(self, input_file, output_file):
        """Ejecuta FFmpeg para extraer audio"""
        try:
            cmd = [
                self.ffmpeg_path_var.get(),
                '-i', input_file,
                '-vn',  # No video
                '-acodec', 'libmp3lame',
                '-ab', '192k',
                '-ar', '44100',
                '-y',  # Sobrescribir
                output_file
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                self.root.after(0, lambda: self.show_info(f"Audio extraído: {output_file}"))
            else:
                self.root.after(0, lambda: self.show_error(f"Error: {stderr}"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error ejecutando FFmpeg: {str(e)}"))

    def convert_audio(self):
        """Convierte archivo de audio a otro formato"""
        input_file = self.convert_file_var.get()
        if not input_file or not os.path.exists(input_file):
            self.show_warning("Selecciona un archivo válido")
            return
            
        output_format = self.convert_audio_format.get()
        format_code = self.audio_formats.get(output_format, 'mp3')
        output_file = self.get_output_filename(input_file, format_code)
        
        self.show_info(f"Convirtiendo audio a {output_format}...")
        # Implementar conversión de audio

    def convert_video(self):
        """Convierte video a otro formato"""
        input_file = self.convert_file_var.get()
        if not input_file or not os.path.exists(input_file):
            self.show_warning("Selecciona un archivo válido")
            return
            
        output_format = self.convert_video_format.get()
        format_code = self.video_formats.get(output_format, 'mp4')
        output_file = self.get_output_filename(input_file, format_code)
        
        self.show_info(f"Convirtiendo video a {output_format}...")
        # Implementar conversión de video

    def batch_convert(self):
        """Conversión por lotes"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta con archivos")
        if not folder:
            return
            
        # Obtener todos los archivos multimedia
        media_files = []
        for ext in ['*.mp4', '*.mkv', '*.avi', '*.mov', '*.mp3', '*.wav', '*.flac']:
            media_files.extend(Path(folder).glob(ext))
            
        if not media_files:
            self.show_warning("No se encontraron archivos multimedia en la carpeta")
            return
            
        # Crear ventana de progreso de batch
        batch_window = tk.Toplevel(self.root)
        batch_window.title("Conversión por lotes")
        batch_window.geometry("400x300")
        
        ttk.Label(batch_window, text=f"Convirtiendo {len(media_files)} archivos...").pack(pady=20)
        
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(batch_window, variable=progress_var, maximum=len(media_files))
        progress_bar.pack(fill=tk.X, padx=20, pady=10)
        
        status_label = ttk.Label(batch_window, text="Preparando...")
        status_label.pack(pady=10)
        
        def process_batch():
            for i, file in enumerate(media_files, 1):
                status_label.config(text=f"Procesando: {file.name}")
                progress_var.set(i)
                batch_window.update()
                
                # Aquí iría la conversión real
                time.sleep(0.5)  # Simulación
                
            status_label.config(text="✅ Conversión completada")
            
        threading.Thread(target=process_batch, daemon=True).start()

    def get_output_filename(self, input_file, output_format):
        """Genera nombre de archivo de salida"""
        base = os.path.splitext(input_file)[0]
        return f"{base}_converted.{output_format}"

    # ========== FUNCIONALIDADES DE HISTORIAL ==========

    def load_download_history(self):
        """Carga el historial de descargas"""
        history_file = os.path.join(os.path.dirname(self.config_file), "download_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    self.download_history = json.load(f)
                self.refresh_history()
            except:
                self.download_history = []

    def save_download_history(self):
        """Guarda el historial de descargas"""
        history_file = os.path.join(os.path.dirname(self.config_file), "download_history.json")
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.download_history[-100:], f, indent=2, ensure_ascii=False)
        except:
            pass

    def add_to_history(self, info, download_item):
        """Agrega una descarga al historial"""
        history_entry = {
            'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'platform': self.detect_platform(download_item['url']),
            'title': info.get('title', 'Sin título'),
            'format': download_item['format'],
            'duration': info.get('duration', 0),
            'size': info.get('filesize', 0),
            'url': download_item['url'],
            'status': 'Completado'
        }
        
        self.download_history.append(history_entry)
        self.save_download_history()

    def refresh_history(self):
        """Actualiza la visualización del historial"""
        # Limpiar árbol
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
            
        # Agregar entradas más recientes primero
        for entry in reversed(self.download_history[-50:]):
            size = entry.get('size', 0)
            if size:
                if size >= 1024*1024*1024:
                    size_str = f"{size/(1024*1024*1024):.2f} GB"
                elif size >= 1024*1024:
                    size_str = f"{size/(1024*1024):.2f} MB"
                elif size >= 1024:
                    size_str = f"{size/1024:.2f} KB"
                else:
                    size_str = f"{size} B"
            else:
                size_str = "--"
                
            self.history_tree.insert("", "end", values=(
                entry['date'],
                entry['platform'],
                entry['title'][:40] + ("..." if len(entry['title']) > 40 else ""),
                entry['format'],
                size_str,
                entry['status']
            ))

    def clear_history(self):
        """Limpia el historial"""
        if messagebox.askyesno("Confirmar", "¿Eliminar todo el historial de descargas?"):
            self.download_history = []
            self.save_download_history()
            self.refresh_history()

    def export_history_csv(self):
        """Exporta el historial a CSV"""
        filename = filedialog.asksaveasfilename(
            title="Exportar historial",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                import csv
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Fecha', 'Plataforma', 'Título', 'Formato', 'Tamaño', 'Estado', 'URL'])
                    for entry in self.download_history:
                        writer.writerow([
                            entry['date'],
                            entry['platform'],
                            entry['title'],
                            entry['format'],
                            entry.get('size', ''),
                            entry['status'],
                            entry['url']
                        ])
                self.show_info(f"Historial exportado a {filename}")
            except Exception as e:
                self.show_error(f"Error exportando: {str(e)}")

    def show_statistics(self):
        """Muestra estadísticas de descargas"""
        if not self.download_history:
            self.show_info("No hay datos de descargas")
            return
            
        # Calcular estadísticas
        total_downloads = len(self.download_history)
        completed = sum(1 for d in self.download_history if d['status'] == 'Completado')
        platforms = {}
        
        for entry in self.download_history:
            platform = entry['platform']
            platforms[platform] = platforms.get(platform, 0) + 1
            
        # Crear ventana de estadísticas
        stats_window = tk.Toplevel(self.root)
        stats_window.title("Estadísticas de descargas")
        stats_window.geometry("400x500")
        
        main_frame = ttk.Frame(stats_window, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text="📊 Estadísticas", style="Title.TLabel").pack(pady=(0, 20))
        
        # Mostrar estadísticas
        stats_text = f"""
        📈 Resumen general:
        ───────────────────
        • Descargas totales: {total_downloads}
        • Completadas: {completed}
        • Fallidas: {total_downloads - completed}
        
        🌐 Plataformas más usadas:
        ─────────────────────────"""
        
        for platform, count in sorted(platforms.items(), key=lambda x: x[1], reverse=True)[:5]:
            stats_text += f"\n• {platform}: {count}"
            
        ttk.Label(main_frame, text=stats_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        ttk.Button(main_frame, text="Cerrar", command=stats_window.destroy).pack(pady=20)

    # ========== CONFIGURACIÓN ==========

    def load_config(self):
        """Carga la configuración"""
        default_config = {
            "download_path": os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader"),
            "theme": "🌙 Dark Matrix",
            "dark_mode": True,
            "transparency": 0.95,
            "concurrent_downloads": 3,
            "speed_limit": "0",
            "retry_count": 3,
            "proxy": "",
            "ffmpeg_path": "ffmpeg",
            "auto_clean": False,
            "clean_days": 7,
            "keep_temp": False,
            "skip_existing": True,
            "embed_metadata": True
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                # Actualizar con valores por defecto para nuevas opciones
                for key, value in default_config.items():
                    if key not in self.config:
                        self.config[key] = value
            else:
                self.config = default_config
                
        except:
            self.config = default_config

    def save_config(self):
        """Guarda la configuración"""
        try:
            # Actualizar configuración actual
            self.config.update({
                "theme": self.current_theme.get(),
                "dark_mode": self.dark_mode.get(),
                "transparency": self.transparency.get(),
                "download_path": self.download_path.get(),
                "concurrent_downloads": self.concurrent_downloads_var.get(),
                "speed_limit": self.speed_limit_var.get(),
                "retry_count": self.retry_count_var.get(),
                "proxy": self.proxy_var.get(),
                "ffmpeg_path": self.ffmpeg_path_var.get(),
                "auto_clean": self.auto_clean_var.get(),
                "clean_days": self.clean_days_var.get(),
                "keep_temp": self.keep_temp_var.get(),
                "skip_existing": self.skip_existing_var.get(),
                "embed_metadata": self.embed_metadata_var.get()
            })
            
            # Crear directorio si no existe
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            # Guardar archivo
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
                
            self.show_info("✅ Configuración guardada")
            
        except Exception as e:
            self.show_error(f"Error guardando configuración: {str(e)}")

    def reset_settings(self):
        """Restaura la configuración por defecto"""
        if messagebox.askyesno("Confirmar", "¿Restaurar configuración por defecto?"):
            default_config = {
                "download_path": os.path.join(os.path.expanduser("~"), "Downloads", "MediaDownloader"),
                "theme": "🌙 Dark Matrix",
                "dark_mode": True,
                "transparency": 0.95,
                "concurrent_downloads": 3,
                "speed_limit": "0",
                "retry_count": 3,
                "proxy": "",
                "ffmpeg_path": "ffmpeg",
                "auto_clean": False,
                "clean_days": 7,
                "keep_temp": False,
                "skip_existing": True,
                "embed_metadata": True
            }
            
            self.config = default_config
            self.apply_config()
            self.show_info("Configuración restaurada")

    def apply_config(self):
        """Aplica la configuración cargada"""
        # Aplicar valores de configuración
        self.current_theme.set(self.config.get("theme", "🌙 Dark Matrix"))
        self.dark_mode.set(self.config.get("dark_mode", True))
        self.transparency.set(self.config.get("transparency", 0.95))
        self.download_path.set(self.config.get("download_path", ""))
        self.concurrent_downloads_var.set(self.config.get("concurrent_downloads", 3))
        self.speed_limit_var.set(self.config.get("speed_limit", "0"))
        self.retry_count_var.set(self.config.get("retry_count", 3))
        self.proxy_var.set(self.config.get("proxy", ""))
        self.ffmpeg_path_var.set(self.config.get("ffmpeg_path", "ffmpeg"))
        self.auto_clean_var.set(self.config.get("auto_clean", False))
        self.clean_days_var.set(self.config.get("clean_days", 7))
        self.keep_temp_var.set(self.config.get("keep_temp", False))
        self.skip_existing_var.set(self.config.get("skip_existing", True))
        self.embed_metadata_var.set(self.config.get("embed_metadata", True))
        
        # Aplicar cambios visuales
        self.apply_theme()
        self.apply_transparency()
        self.toggle_dark_mode()

    def browse_default_path(self):
        """Selecciona la carpeta por defecto"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de descargas por defecto")
        if folder:
            self.default_path_var.set(folder)

    def auto_detect_ffmpeg(self):
        """Intenta detectar FFmpeg automáticamente"""
        possible_paths = [
            "ffmpeg",
            "ffmpeg.exe",
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.join(os.path.dirname(sys.executable), "ffmpeg.exe")
        ]
        
        for path in possible_paths:
            try:
                subprocess.run([path, '-version'], 
                             stdout=subprocess.DEVNULL, 
                             stderr=subprocess.DEVNULL)
                self.ffmpeg_path_var.set(path)
                self.show_info(f"FFmpeg detectado en: {path}")
                return
            except:
                continue
                
        self.show_warning("FFmpeg no encontrado. Por favor, especifica la ruta manualmente.")

    # ========== FUNCIONALIDADES DE INTERFAZ ==========

    def apply_theme(self):
        """Aplica el tema seleccionado"""
        theme_name = self.current_theme.get()
        theme_id = self.themes.get(theme_name, "equilux")
        
        try:
            self.root.set_theme(theme_id)
            
            # Configurar colores según el tema
            if "Dark" in theme_name or "Black" in theme_name:
                self.dark_mode.set(True)
            elif "Light" in theme_name or "White" in theme_name:
                self.dark_mode.set(False)
                
            self.toggle_dark_mode()
            
        except:
            pass

    def apply_transparency(self, *args):
        """Aplica la transparencia"""
        alpha = self.transparency.get()
        self.root.attributes('-alpha', alpha)

    def toggle_dark_mode(self):
        """Alterna entre modo oscuro y claro"""
        if self.dark_mode.get():
            self.style.configure(".", background="#1a1a1a", foreground="#ffffff")
            self.style.configure("TFrame", background="#1a1a1a")
            self.style.configure("TLabel", background="#1a1a1a", foreground="#ffffff")
            self.style.configure("TLabelframe", background="#2d2d2d", foreground="#ffffff")
            self.style.configure("TLabelframe.Label", background="#2d2d2d", foreground="#00ff88")
        else:
            self.style.configure(".", background="#f5f5f5", foreground="#000000")
            self.style.configure("TFrame", background="#f5f5f5")
            self.style.configure("TLabel", background="#f5f5f5", foreground="#000000")
            self.style.configure("TLabelframe", background="#e0e0e0", foreground="#000000")
            self.style.configure("TLabelframe.Label", background="#e0e0e0", foreground="#007acc")

    def select_download_folder(self):
        """Selecciona la carpeta de descargas"""
        folder = filedialog.askdirectory(title="Seleccionar carpeta de descargas")
        if folder:
            self.download_path.set(folder)
            self.path_label.config(text=folder)

    def update_format_options(self, event=None):
        """Actualiza las opciones de formato según el tipo de contenido"""
        content_type = self.content_type.get()
        
        if content_type == "Solo Audio":
            self.format_combo.config(values=list(self.audio_formats.keys()))
            self.format_var.set("MP3 (128kbps)")
        else:
            self.format_combo.config(values=list(self.video_formats.keys()))
            self.format_var.set("MP4 (H.264)")

    def preview_content(self):
        """Previsualiza el contenido"""
        url = self.url_var.get().strip()
        if not url:
            return
            
        # Crear ventana de previsualización
        preview_window = tk.Toplevel(self.root)
        preview_window.title("Previsualización")
        preview_window.geometry("800x500")
        
        try:
            # Inicializar VLC
            vlc_instance = vlc.Instance('--no-xlib')
            player = vlc_instance.media_player_new()
            
            # Crear frame para el video
            video_frame = ttk.Frame(preview_window)
            video_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Canvas para el video
            canvas = tk.Canvas(video_frame, bg='black')
            canvas.pack(fill=tk.BOTH, expand=True)
            
            # Configurar player
            if platform.system() == 'Windows':
                player.set_hwnd(canvas.winfo_id())
            else:
                player.set_xwindow(canvas.winfo_id())
                
            # Cargar media
            media = vlc_instance.media_new(url)
            player.set_media(media)
            
            # Controles
            controls_frame = ttk.Frame(preview_window)
            controls_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            ttk.Button(controls_frame, text="▶️", 
                      command=player.play).pack(side=tk.LEFT, padx=2)
            ttk.Button(controls_frame, text="⏸️", 
                      command=player.pause).pack(side=tk.LEFT, padx=2)
            ttk.Button(controls_frame, text="⏹️", 
                      command=player.stop).pack(side=tk.LEFT, padx=2)
            ttk.Button(controls_frame, text="🔊 +", 
                      command=lambda: player.audio_set_volume(min(100, player.audio_get_volume() + 10))).pack(side=tk.LEFT, padx=2)
            ttk.Button(controls_frame, text="🔊 -", 
                      command=lambda: player.audio_set_volume(max(0, player.audio_get_volume() - 10))).pack(side=tk.LEFT, padx=2)
            
            # Reproducir automáticamente
            player.play()
            
        except Exception as e:
            self.show_error(f"No se puede previsualizar: {str(e)}")
            preview_window.destroy()

    def update_space_info(self):
        """Actualiza información de espacio en disco"""
        try:
            if os.path.exists(self.download_path.get()):
                stat = shutil.disk_usage(self.download_path.get())
                free_gb = stat.free / (1024**3)
                self.space_used.config(text=f"💾 Libre: {free_gb:.1f} GB")
        except:
            pass
            
        # Actualizar cada 30 segundos
        self.root.after(30000, self.update_space_info)

    def update_active_downloads_label(self):
        """Actualiza la etiqueta de descargas activas"""
        count = len(self.active_downloads)
        self.active_downloads_label.config(text=f"📥 Activas: {count}")

    def monitor_downloads(self):
        """Monitoriza el estado de las descargas"""
        self.update_active_downloads_label()
        self.root.after(1000, self.monitor_downloads)

    # ========== FUNCIONES DE UTILIDAD ==========

    def paste_url(self):
        """Pega URL desde portapapeles"""
        try:
            clipboard = self.root.clipboard_get()
            self.url_var.set(clipboard)
            self.analyze_url()
        except:
            pass

    def clear_url(self):
        """Limpia la URL"""
        self.url_var.set("")
        self.platform_indicator.config(text="🌐 Plataforma: --")
        self.title_label.config(text="📌 Título: --")
        self.duration_label.config(text="⏱️ Duración: --")
        self.views_label.config(text="👁️ Vistas: --")
        self.channel_label.config(text="👤 Canal: --")
        self.thumbnail_label.config(image="", text="🎬")
        self.preview_btn.config(state=tk.DISABLED)

    def cancel_download(self):
        """Cancela la descarga actual"""
        self.cancel_flag = True
        self.status_var.set("❌ Descarga cancelada")
        self.is_downloading = False

    # ========== MENSAJES Y DIÁLOGOS ==========

    def show_info(self, message):
        """Muestra mensaje informativo"""
        messagebox.showinfo("Información", message)

    def show_warning(self, message):
        """Muestra advertencia"""
        messagebox.showwarning("Advertencia", message)

    def show_error(self, message):
        """Muestra error"""
        messagebox.showerror("Error", message)

    def show_about(self):
        """Muestra información sobre la aplicación"""
        about_text = f"""
{self.app_info['name']} v{self.app_info['version']}

{self.app_info['description']}

👤 Desarrollador: {self.app_info['author']}
🎮 Nickname: {self.app_info['nickname']}
📧 Contacto: {self.app_info['email']}
🌐 Website: {self.app_info['website']}

© {self.app_info['year']} - Todos los derechos reservados

Este software es proporcionado "tal cual" sin garantías de ningún tipo.
        """
        
        about_window = tk.Toplevel(self.root)
        about_window.title("Acerca de")
        about_window.geometry("500x400")
        
        main_frame = ttk.Frame(about_window, padding=30)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(main_frame, text=self.app_info['name'], 
                 font=("Segoe UI", 18, "bold")).pack(pady=(0, 10))
        
        ttk.Label(main_frame, text=f"Versión {self.app_info['version']}",
                 font=("Segoe UI", 12)).pack(pady=(0, 20))
        
        ttk.Label(main_frame, text=about_text,
                 justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        ttk.Button(main_frame, text="Cerrar",
                  command=about_window.destroy).pack(pady=20)

    # ========== MÉTODOS NECESARIOS ==========

    def update_progress(self, percentage, status_text):
        """Actualiza el progreso"""
        self.progress_var.set(percentage)
        self.status_var.set(status_text)

    def reset_gui(self):
        """Resetea la GUI"""
        self.download_btn.config(state=tk.NORMAL)
        self.cancel_btn.config(state=tk.DISABLED)
        self.is_downloading = False

def main():
    """Función principal"""
    # Verificar dependencias
    try:
        import yt_dlp
        import ttkthemes
    except ImportError as e:
        print(f"Error: Falta dependencia - {e}")
        print("Instala con: pip install yt-dlp ttkthemes Pillow python-vlc")
        return
        
    # Crear ventana principal
    root = ThemedTk(theme="equilux")
    
    # Configurar icono si existe
    try:
        root.iconbitmap("icon.ico")
    except:
        pass
        
    # Crear aplicación
    app = ModernDownloadManager(root)
    
    # Menú principal
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # Menú Archivo
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Archivo", menu=file_menu)
    file_menu.add_command(label="Nueva descarga", command=lambda: app.notebook.select(0))
    file_menu.add_command(label="Abrir carpeta de descargas", command=app.select_download_folder)
    file_menu.add_separator()
    file_menu.add_command(label="Salir", command=root.quit)
    
    # Menú Herramientas
    tools_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Herramientas", menu=tools_menu)
    tools_menu.add_command(label="Conversor", command=lambda: app.notebook.select(1))
    tools_menu.add_command(label="Historial", command=lambda: app.notebook.select(2))
    tools_menu.add_command(label="Configuración", command=lambda: app.notebook.select(3))
    
    # Menú Ayuda
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Ayuda", menu=help_menu)
    help_menu.add_command(label="Acerca de", command=app.show_about)
    help_menu.add_command(label="Documentación", command=lambda: webbrowser.open("https://github.com"))
    help_menu.add_separator()
    help_menu.add_command(label="Verificar actualizaciones")
    
    # Ejecutar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
