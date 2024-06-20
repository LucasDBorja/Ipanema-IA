import os
import random
import webbrowser
import requests
import tkinter as tk
from tkinter import simpledialog, messagebox, Menu
from datetime import datetime
import spotipy
import spotipy.util as util
import speech_recognition as sr
from PIL import Image, ImageTk
import pyttsx3
import spacy

GOOGLE_API_KEY = ''
SEARCH_ENGINE_ID = ''

scope = "user-read-playback-state,user-modify-playback-state"
username = ""
client_id = ""
client_secret = ""
redirect_uri = "http://localhost:8888/callback"

# Obtendo token de acesso do Spotify
token = util.prompt_for_user_token(username, scope, client_id, client_secret, redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Erro ao obter token de acesso do Spotify. Verifique suas credenciais e tente novamente.")

# Inicializando objetos necessários
recognizer = sr.Recognizer()
nlp = spacy.load("pt_core_news_sm")

# Classe para manipulação da agenda
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

# Carregando dados da agenda
agenda.carregar_agenda('agenda.txt')
agenda.carregar_anotacoes('anotacoes.txt')

# Funções para interação com o usuário
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
    termo = simpledialog.askstring("Fazer Pesquisa", "Digite o termo da pesquisa:")
    if termo:
        pesquisa_google(termo)

def pesquisa_google(termo):
    url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&q={termo}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        results = response.json().get('items', [])
        if results:
            resultados_str = "Resultados da pesquisa:\n"
            for result in results:
                titulo = result.get('title')
                link = result.get('link')
                resultados_str += f"- {titulo}: {link}\n"
            messagebox.showinfo("Resultados da Pesquisa", resultados_str)
        else:
            messagebox.showinfo("Resultados da Pesquisa", "Nenhum resultado encontrado para o termo especificado.")
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Erro na Pesquisa", f"Erro ao executar a pesquisa: {e}")

def abrir_spotify_local():
    global token, sp
    if token:
        spotify_path = r"C:\Users\ld388\AppData\Local\Microsoft\WindowsApps\SpotifyAB.SpotifyMusic_zpdnekdrzrea0\Spotify.exe"
        if os.path.exists(spotify_path):
            os.startfile(spotify_path)
        else:
            messagebox.showerror("Erro", "O aplicativo Spotify não está instalado no sistema.")
    else:
        messagebox.showerror("Erro", "Você não está autenticado no Spotify. Tente reiniciar o programa.")

def continuar_musica():
    if token:
        sp.start_playback()
        messagebox.showinfo("Sucesso", "Continuando música no Spotify.")
    else:
        messagebox.showerror("Erro", "Você não está autenticado no Spotify. Tente reiniciar o programa.")

def pausar_musica():
    if token:
        sp.pause_playback()
        messagebox.showinfo("Sucesso", "Pausando música no Spotify.")
    else:
        messagebox.showerror("Erro", "Você não está autenticado no Spotify. Tente reiniciar o programa.")

def pesquisar_musica():
    musica = simpledialog.askstring("Pesquisar Música", "Digite o nome da música:")
    if token and musica:
        results = sp.search(q=musica, limit=1)
        if results['tracks']['items']:
            track_uri = results['tracks']['items'][0]['uri']
            sp.start_playback(uris=[track_uri])
            messagebox.showinfo("Sucesso", f"Reproduzindo música: {musica}")
        else:
            messagebox.showerror("Erro", f"Nenhuma música encontrada com o nome '{musica}'.")
    elif not musica:
        messagebox.showerror("Erro", "Nenhum nome de música especificado.")
    else:
        messagebox.showerror("Erro", "Você não está autenticado no Spotify. Tente reiniciar o programa.")

def buscar_imagem():
    termo = simpledialog.askstring("Buscar Imagem", "Digite o termo para buscar imagem:")
    if termo:
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={SEARCH_ENGINE_ID}&searchType=image&q={termo}"
        try:
            response = requests.get(url)
            response.raise_for_status()
            results = response.json().get('items', [])
            if results:
                imagem_url = results[0]['link']
                exibir_imagem_url(imagem_url)
            else:
                messagebox.showinfo("Imagem", f"Nenhuma imagem encontrada para o termo '{termo}'.")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Erro na Busca de Imagem", f"Erro ao buscar imagem: {e}")
    else:
        messagebox.showerror("Erro na Busca de Imagem", "Nenhum termo especificado.")

def exibir_imagem_url(imagem_url):
    root = tk.Tk()
    root.title("Imagem")
    image_bytes = requests.get(imagem_url).content
    image = Image.open(io.BytesIO(image_bytes))
    photo = ImageTk.PhotoImage(image)
    label = tk.Label(root, image=photo)
    label.pack()
    root.mainloop()

def ouvir_microfone():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        messagebox.showinfo("Aviso", "Fale algo para ser reconhecido.")
        audio = recognizer.listen(source)

    try:
        frase = recognizer.recognize_google(audio, language='pt-BR')
        messagebox.showinfo("Reconhecimento de Voz", f"Frase reconhecida: {frase}")
        analisar_texto(frase)
    except sr.UnknownValueError:
        messagebox.showinfo("Reconhecimento de Voz", "Não foi possível reconhecer a fala.")
    except sr.RequestError as e:
        messagebox.showerror("Erro de Serviço", f"Erro ao reconhecer fala; {e}")

def analisar_texto(frase):
    doc = nlp(frase)
    entidades = [(ent.text, ent.label_) for ent in doc.ents]
    if entidades:
        entidades_str = "Entidades reconhecidas:\n"
        for entidade, tipo in entidades:
            entidades_str += f"{entidade} - {tipo}\n"
        messagebox.showinfo("Análise de Texto", entidades_str)
    else:
        messagebox.showinfo("Análise de Texto", "Nenhuma entidade reconhecida.")

def enviar_mensagem_chat():
    mensagem = entrada_texto.get("1.0",'end-1c')
    if mensagem.strip() == "":
        messagebox.showwarning("Aviso", "Você não pode enviar uma mensagem em branco.")
    else:
        caixa_texto.config(state=tk.NORMAL)
        caixa_texto.insert(tk.END, f"Você: {mensagem}\n")
        caixa_texto.config(state=tk.DISABLED)
        entrada_texto.delete("1.0", tk.END)
        responder_bot(mensagem)

def responder_bot(mensagem):
    respostas = [
        "Olá! Em que posso ajudar?",
        "Como posso ser útil hoje?",
        "Estou aqui para ajudar. O que você precisa?",
        "Pode contar comigo! O que deseja fazer?"
    ]
    resposta = random.choice(respostas)
    caixa_texto.config(state=tk.NORMAL)
    caixa_texto.insert(tk.END, f"Assistente: {resposta}\n")
    caixa_texto.config(state=tk.DISABLED)

# Configuração da interface gráfica
root = tk.Tk()
root.title("Assistente Virtual")

menu_bar = Menu(root)
root.config(menu=menu_bar)

agenda_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Agenda", menu=agenda_menu)
agenda_menu.add_command(label="Marcar Compromisso", command=marcar_compromisso)
agenda_menu.add_command(label="Mostrar Compromissos", command=mostrar_compromissos)

anotacoes_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Anotações", menu=anotacoes_menu)
anotacoes_menu.add_command(label="Fazer Anotação", command=fazer_anotacao)
anotacoes_menu.add_command(label="Mostrar Anotações", command=mostrar_anotacoes)

piadas_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Piadas", menu=piadas_menu)
piadas_menu.add_command(label="Contar Piada", command=contar_piada)

pesquisa_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Pesquisa", menu=pesquisa_menu)
pesquisa_menu.add_command(label="Fazer Pesquisa", command=fazer_pesquisa)

spotify_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Spotify", menu=spotify_menu)
spotify_menu.add_command(label="Abrir Spotify", command=abrir_spotify_local)
spotify_menu.add_command(label="Continuar Música", command=continuar_musica)
spotify_menu.add_command(label="Pausar Música", command=pausar_musica)
spotify_menu.add_command(label="Pesquisar Música", command=pesquisar_musica)

imagem_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Imagem", menu=imagem_menu)
imagem_menu.add_command(label="Buscar Imagem", command=buscar_imagem)

voz_menu = Menu(menu_bar, tearoff=0)
menu_bar.add_cascade(label="Voz", menu=voz_menu)
voz_menu.add_command(label="Ouvir Microfone", command=ouvir_microfone)

frame_chat = tk.Frame(root)
frame_chat.pack(pady=10)

caixa_texto = tk.Text(frame_chat, width=80, height=20)
caixa_texto.config(state=tk.DISABLED)
caixa_texto.pack()

scrollbar = tk.Scrollbar(frame_chat, command=caixa_texto.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

caixa_texto.config(yscrollcommand=scrollbar.set)

frame_entrada = tk.Frame(root)
frame_entrada.pack(pady=10)

entrada_texto = tk.Text(frame_entrada, width=60, height=3)
entrada_texto.pack()

botao_enviar = tk.Button(frame_entrada, text="Enviar", command=enviar_mensagem_chat)
botao_enviar.pack()

root.mainloop()
