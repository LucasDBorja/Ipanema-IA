import os
import random
import webbrowser
import spotipy
import spotipy.util as util
import spacy
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import tkinter as tk
from tkinter import messagebox, simpledialog
import requests

# Variáveis da API de Pesquisa Personalizada do Google
GOOGLE_API_KEY = 'AIzaSyA5RBLA9Aq3AYD2SUxSiythUg6VCMW2_yI'
SEARCH_ENGINE_ID = 'e127997aced3a4a6c'

scope = "user-read-playback-state,user-modify-playback-state"
username = "Lucas Daniel"
client_id = "599d97ecf88d4f1296c66ba3c107a6cd"
client_secret = "be984ae0f6e94c5ba84852f71ced7bee"
redirect_uri = "http://localhost:8888/callback"

token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Erro ao obter token de acesso do Spotify. Verifique suas credenciais e tente novamente.")

recognizer = sr.Recognizer()
nlp = spacy.load("pt_core_news_sm")

class Agenda:
    def __init__(self):
        self.compromissos = {}
        self.anotacoes = {}

    def adicionar_compromisso(self, data, compromisso):
        if data in self.compromissos:
            self.compromissos[data].append(compromisso)
        else:
            self.compromissos[data] = [compromisso]

    def adicionar_anotacao(self, titulo, conteudo):
        self.anotacoes[titulo] = conteudo

    def get_compromissos(self, data):
        return self.compromissos.get(data, [])

    def get_anotacoes(self):
        return self.anotacoes

    def get_compromissos_mes(self, mes, ano):
        compromissos_mes = {}
        for data, compromissos in self.compromissos.items():
            data_obj = datetime.strptime(data, "%d/%m/%Y")
            if data_obj.month == mes and data_obj.year == ano:
                compromissos_mes[data] = compromissos
        return compromissos_mes

    def salvar_agenda(self, filename):
        with open(filename, 'w') as file:
            for data, compromissos in self.compromissos.items():
                for compromisso in compromissos:
                    file.write(f"{data},{compromisso}\n")

    def carregar_agenda(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                for line in file:
                    data, compromisso = line.strip().split(',', 1)
                    self.adicionar_compromisso(data, compromisso)

    def salvar_anotacoes(self, filename):
        with open(filename, 'w') as file:
            for titulo, conteudo in self.anotacoes.items():
                file.write(f"{titulo}\n{conteudo}\n---\n")

    def carregar_anotacoes(self, filename):
        if os.path.exists(filename):
            with open(filename, 'r') as file:
                lines = file.readlines()
                for i in range(0, len(lines), 3):
                    titulo = lines[i].strip()
                    conteudo = lines[i+1].strip()
                    self.adicionar_anotacao(titulo, conteudo)

agenda = Agenda()

agenda.carregar_agenda('agenda.txt')
agenda.carregar_anotacoes('anotacoes.txt')

def marcar_compromisso():
    data = simpledialog.askstring("Marcar Compromisso", "Digite a data do compromisso (DD/MM/AAAA):")
    compromisso = simpledialog.askstring("Marcar Compromisso", "Digite o compromisso:")
    agenda.adicionar_compromisso(data, compromisso)
    agenda.salvar_agenda('agenda.txt')
    messagebox.showinfo("Sucesso", "Compromisso marcado com sucesso!")

def mostrar_compromissos():
    mes = simpledialog.askinteger("Mostrar Compromissos", "Digite o número do mês:")
    ano = simpledialog.askinteger("Mostrar Compromissos", "Digite o ano:")
    compromissos_mes = agenda.get_compromissos_mes(mes, ano)
    if compromissos_mes:
        compromissos_str = f"Compromissos para o mês {mes}/{ano}:\n"
        for data, compromissos in compromissos_mes.items():
            compromissos_str += f"Data: {data}\n"
            for compromisso in compromissos:
                compromissos_str += f"- {compromisso}\n"
        messagebox.showinfo("Compromissos", compromissos_str)
    else:
        messagebox.showinfo("Compromissos", "Nenhum compromisso marcado para este mês.")

def fazer_anotacao():
    titulo = simpledialog.askstring("Fazer Anotação", "Digite o título da anotação:")
    conteudo = simpledialog.askstring("Fazer Anotação", "Digite o conteúdo da anotação:")
    agenda.adicionar_anotacao(titulo, conteudo)
    agenda.salvar_anotacoes('anotacoes.txt')
    messagebox.showinfo("Sucesso", "Anotação salva com sucesso!")

def mostrar_anotacoes():
    anotacoes = agenda.get_anotacoes()
    if anotacoes:
        anotacoes_str = "Anotações disponíveis:\n"
        for i, (titulo, conteudo) in enumerate(anotacoes.items(), 1):
            anotacoes_str += f"{i}. {titulo}\n"
        anotacoes_str += "0. Voltar"
        
        opcao = simpledialog.askinteger("Mostrar Anotações", anotacoes_str)
        
        if opcao == 0:
            return
        
        if opcao > 0 and opcao <= len(anotacoes):
            titulo = list(anotacoes.keys())[opcao - 1]
            messagebox.showinfo("Anotação", f"{titulo}\n{anotacoes[titulo]}")
        else:
            messagebox.showerror("Erro", "Opção inválida.")
    else:
        messagebox.showinfo("Anotações", "Nenhuma anotação encontrada.")

def contar_piada():
    piadas = [
        "Por que o pombo não bate asa? Porque ele já é bom!",
        "Qual é o rei dos queijos? O reiqueijão!",
        "Qual é o cúmulo da rapidez? Fechar os olhos antes de aparecer a foto!",
        "Por que o elefante não pega fogo? Porque ele já é cinza!",
        "Por que o jacaré tirou o jacarezinho da escola? Porque ele réptil!"
    ]
    piada_escolhida = random.choice(piadas)
    messagebox.showinfo("Piada", piada_escolhida)

def fazer_pesquisa():
    pesquisa = simpledialog.askstring("Fazer Pesquisa", "Digite o que você deseja pesquisar:")
    if pesquisa:
        resultados = realizar_pesquisa_google(pesquisa)
        if resultados:
            resultados_str = "\n".join(f"{i+1}. {res['title']} ({res['link']})" for i, res in enumerate(resultados))
            messagebox.showinfo("Resultados da Pesquisa", f"Resultados para '{pesquisa}':\n\n{resultados_str}")
        else:
            messagebox.showinfo("Resultados da Pesquisa", "Nenhum resultado encontrado.")

def realizar_pesquisa_google(query):
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}"
    response = requests.get(url)
    if response.status_code == 200:
        results = response.json().get("items", [])
        return [{"title": item["title"], "link": item["link"]} for item in results]
    else:
        print("Erro na pesquisa:", response.status_code)
        return []

def abrir_spotify():
    os.system("spotify")

def continuar_musica():
    sp.start_playback()

def pausar_musica():
    sp.pause_playback()

def colocar_musica_anterior():
    sp.previous_track()

def colocar_proxima_musica():
    sp.next_track()

def menu_spotify():
    spotify_menu = tk.Toplevel(root)
    spotify_menu.title("Menu Spotify")
    
    tk.Button(spotify_menu, text="Abrir Spotify", command=abrir_spotify).pack(pady=10)
    tk.Button(spotify_menu, text="Pausar Música", command=pausar_musica).pack(pady=10)
    tk.Button(spotify_menu, text="Continuar Música", command=continuar_musica).pack(pady=10)
    tk.Button(spotify_menu, text="Próxima Música", command=colocar_proxima_musica).pack(pady=10)
    tk.Button(spotify_menu, text="Música Anterior", command=colocar_musica_anterior).pack(pady=10)

is_dark_mode = False

def toggle_mode():
    global is_dark_mode
    is_dark_mode = not is_dark_mode
    apply_mode()

def apply_mode():
    bg_color = "black" if is_dark_mode else "white"
    fg_color = "white" if is_dark_mode else "black"
    root.configure(bg=bg_color)
    for widget in root.winfo_children():
        widget.configure(bg=bg_color, fg=fg_color)
    mode_button.configure(text="Modo Claro" if is_dark_mode else "Modo Escuro")

root = tk.Tk()
root.title("Menu Principal")
mode_button = tk.Button(root, text="Modo Escuro", command=toggle_mode)
mode_button.pack(pady=10)
tk.Button(root, text="Marcar Compromisso", command=marcar_compromisso).pack(pady=10)
tk.Button(root, text="Mostrar Compromissos", command=mostrar_compromissos).pack(pady=10)
tk.Button(root, text="Fazer Anotação", command=fazer_anotacao).pack(pady=10)
tk.Button(root, text="Mostrar Anotações", command=mostrar_anotacoes).pack(pady=10)
tk.Button(root, text="Contar Piada", command=contar_piada).pack(pady=10)
tk.Button(root, text="Fazer Pesquisa", command=fazer_pesquisa).pack(pady=10)
tk.Button(root, text="Controlar Spotify", command=menu_spotify).pack(pady=10)

apply_mode()
root.mainloop()
