import os
import random
import webbrowser
import spotipy
import spotipy.util as util
import spacy
import speech_recognition as sr
import pyttsx3
from datetime import datetime

scope = "user-read-playback-state,user-modify-playback-state"
username = "Lucas Daniel"
client_id = "599d97ecf88d4f1296c66ba3c107a6cd"
client_secret = "be984ae0f6e94c5ba84852f71ced7bee"
redirect_uri = "http://localhost:8888/callback"

token = util.prompt_for_user_token(username, scope, client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

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

agenda.carregar_agenda('C:\\Users\\ld388\\OneDrive\\Desktop\\Ipanema\\Agenda.txt')
agenda.carregar_anotacoes('C:\\Users\\ld388\\OneDrive\\Desktop\\Ipanema\\Anotacoes.txt')

def marcar_compromisso():
    data = input("Digite a data do compromisso (DD/MM/AAAA): ")
    compromisso = input("Digite o compromisso: ")
    agenda.adicionar_compromisso(data, compromisso)
    agenda.salvar_agenda('C:\\Users\\ld388\\OneDrive\\Desktop\\Ipanema\\Agenda.txt')
    print("Compromisso marcado com sucesso!")

def mostrar_compromissos():
    mes = int(input("Digite o número do mês: "))
    ano = int(input("Digite o ano: "))
    compromissos_mes = agenda.get_compromissos_mes(mes, ano)
    if compromissos_mes:
        print(f"Compromissos para o mês {mes}/{ano}:")
        for data, compromissos in compromissos_mes.items():
            print(f"Data: {data}")
            for compromisso in compromissos:
                print("-", compromisso)
    else:
        print("Nenhum compromisso marcado para este mês.")

def fazer_anotacao():
    titulo = input("Digite o título da anotação: ")
    conteudo = input("Digite o conteúdo da anotação: ")
    agenda.adicionar_anotacao(titulo, conteudo)
    agenda.salvar_anotacoes('C:\\Users\\ld388\\OneDrive\\Desktop\\Ipanema\\Anotacoes.txt')
    print("Anotação salva com sucesso!")

def mostrar_anotacoes():
    anotacoes = agenda.get_anotacoes()
    if anotacoes:
        print("Anotações disponíveis:")
        for i, (titulo, conteudo) in enumerate(anotacoes.items(), 1):
            print(f"{i}. {titulo}")
        print("0. Voltar")
        
        opcao = int(input("Escolha uma anotação para ler (digite o número correspondente): "))
        
        if opcao == 0:
            return
        
        if opcao > 0 and opcao <= len(anotacoes):
            titulo = list(anotacoes.keys())[opcao - 1]
            print(f"Anotação: {titulo}")
            print(anotacoes[titulo])
        else:
            print("Opção inválida.")
    else:
        print("Nenhuma anotação encontrada.")

def mostrar_anotacao_especifica():
    anotacoes = agenda.get_anotacoes()
    if anotacoes:
        mostrar_anotacoes()
        num = int(input("Digite o número da anotação que deseja ver: "))
        titulo = list(anotacoes.keys())[num - 1]
        print(f"\n--- {titulo} ---")
        print(anotacoes[titulo])
    else:
        print("Nenhuma anotação encontrada.")

def contar_piada():
    piadas = [
        "Por que o pombo não bate asa? Porque ele já é bom!",
        "Qual é o rei dos queijos? O reiqueijão!",
        "Qual é o cúmulo da rapidez? Fechar os olhos antes de aparecer a foto!",
        "Por que o elefante não pega fogo? Porque ele já é cinza!",
        "Por que o jacaré tirou o jacarezinho da escola? Porque ele réptil!"
    ]
    piada_escolhida = random.choice(piadas)
    print("\nAqui está uma piada para você:")
    print(piada_escolhida)

def fazer_pesquisa():
    pesquisa = input("Digite o que você deseja pesquisar: ")
    url = f"https://www.google.com/search?q={pesquisa}"
    webbrowser.open(url)

def fazer_pesquisa_por_voz():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    engine.say("O que você deseja pesquisar?")
    engine.runAndWait()
    try:
        with sr.Microphone() as source:
            print("Ouvindo...")
            audio = recognizer.listen(source)
        pesquisa = recognizer.recognize_google(audio, language='pt-BR')
        print("Você disse:", pesquisa)
        url = f"https://www.google.com/search?q={pesquisa}"
        webbrowser.open(url)
    except sr.UnknownValueError:
        print("Desculpe, não consegui entender o áudio.")
    except sr.RequestError as e:
        print("Erro ao acessar o serviço de reconhecimento de fala; {0}".format(e))
    except KeyboardInterrupt:
        print("Pesquisa por voz cancelada.")

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

def dialogo_por_voz():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    engine.say("Olá! Como posso ajudar?")
    engine.runAndWait()
    while True:
        try:
            with sr.Microphone() as source:
                print("Ouvindo...")
                audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language='pt-BR').lower()  
            print("Você disse:", text)

            doc = nlp(text)
            verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]
            
            if any(keyword in text for keyword in ["Ipanema encerrar", "Ipanema pare de falar", "Ipanema pare"]):
                print("Encerrando o chat por voz...")
                engine.say("Encerrando o chat por voz.")
                engine.runAndWait()
                break
            if "marcar compromisso" in text:
                marcar_compromisso()
            elif "mostrar compromissos" in text:
                mostrar_compromissos()
            elif "fazer anotação" in text:
                fazer_anotacao()
            elif "mostrar anotações" in text:
                mostrar_anotacoes()
            elif "mostrar anotação" in text and any(char.isdigit() for char in text):
                mostrar_anotacao_especifica()
            elif "abrir spotify" in text:
                abrir_spotify()
            elif "pesquisar" in text:
                fazer_pesquisa_por_voz()
            elif "contar piada" in text:
                contar_piada()
            elif "spotify" in text:
                spotify_menu_por_voz()
            engine.say("Você disse: " + text)
            engine.runAndWait()
        except sr.UnknownValueError:
            print("Desculpe, não consegui entender o áudio. Pode repetir?")
            engine.say("Desculpe, não consegui entender o áudio. Pode repetir?")
            engine.runAndWait()
        except sr.RequestError as e:
            print("Erro ao acessar o serviço de reconhecimento de fala; {0}".format(e))
            engine.say("Erro ao acessar o serviço de reconhecimento de fala.")
            engine.runAndWait()
        except KeyboardInterrupt:
            print("Encerrando o diálogo por voz...")
            engine.say("Encerrando o diálogo por voz.")
            engine.runAndWait()
            break

def spotify_menu_por_voz():
    recognizer = sr.Recognizer()
    engine = pyttsx3.init()
    engine.say("O que você deseja fazer no Spotify?")
    engine.runAndWait()
    while True:
        try:
            with sr.Microphone() as source:
                print("Ouvindo...")
                audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio, language='pt-BR').lower()  
            print("Você disse:", text)

            doc = nlp(text)
            verbs = [token.lemma_ for token in doc if token.pos_ == "VERB"]


            if any(verb in ["abrir"] for verb in verbs):
                abrir_spotify()
                break
            elif any(keyword in text for keyword in ["voltar para o começo", "voltar"]) or "spotify" in text:
                print("Voltando para o início do menu do Spotify...")
                engine.say("Voltando para o início do menu do Spotify.")
                engine.runAndWait()
                return
            else:
                print("Comando não reconhecido. Por favor, repita.")
                engine.say("Comando não reconhecido. Por favor, repita.")
                engine.runAndWait()
        except sr.UnknownValueError:
            print("Desculpe, não consegui entender o áudio. Pode repetir?")
            engine.say("Desculpe, não consegui entender o áudio. Pode repetir?")
            engine.runAndWait()
        except KeyboardInterrupt:
            print("Encerrando o menu do Spotify...")
            engine.say("Encerrando o menu do Spotify.")
            engine.runAndWait()
            break

def menu_spotify():
    print("\nMenu Spotify:")
    print("1. Abrir Spotify")
    print("2. Pausar música")
    print("3. Continuar música")
    print("4. Próxima música")
    print("5. Música anterior")
    print("6. Voltar para o menu principal")
    opcao_spotify = input("\nEscolha uma opção: ")
    if opcao_spotify == "1":
        abrir_spotify()
    elif opcao_spotify == "2":
        pausar_musica()
    elif opcao_spotify == "3":
        continuar_musica()
    elif opcao_spotify == "4":
        colocar_proxima_musica()
    elif opcao_spotify == "5":
        colocar_musica_anterior()
    elif opcao_spotify == "6":
        return
    else:
        print("Opção inválida. Por favor, escolha uma opção válida.")

def main():
    while True:
        print("\nMenu Principal:")
        print("1. Agenda")
        print("2. Anotações")
        print("3. Contar piada")
        print("4. Pesquisar")
        print("5. Menu Spotify")
        print("6. Diálogo por voz")
        print("7. Sair")
        opcao = input("\nEscolha uma opção: ")
        if opcao == "1":
            print("\nMenu Agenda:")
            print("1. Marcar compromisso")
            print("2. Mostrar compromissos")
            opcao_agenda = input("\nEscolha uma opção: ")
            if opcao_agenda == "1":
                marcar_compromisso()
            elif opcao_agenda == "2":
                mostrar_compromissos()
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")
        elif opcao == "2":
            print("\nMenu Anotações:")
            print("1. Fazer anotação")
            print("2. Mostrar anotações")
            opcao_anotacoes = input("\nEscolha uma opção: ")
            if opcao_anotacoes == "1":
                fazer_anotacao()
            elif opcao_anotacoes == "2":
                print("\nMenu Mostrar Anotações:")
                print("1. Mostrar todas as anotações")
                print("2. Mostrar anotação específica")
                opcao_mostrar_anotacoes = input("\nEscolha uma opção: ")
                if opcao_mostrar_anotacoes == "1":
                    mostrar_anotacoes()
                elif opcao_mostrar_anotacoes == "2":
                    mostrar_anotacao_especifica()
                else:
                    print("Opção inválida. Por favor, escolha uma opção válida.")
            else:
                print("Opção inválida. Por favor, escolha uma opção válida.")
        elif opcao == "3":
            contar_piada()
        elif opcao == "4":
            fazer_pesquisa()
        elif opcao == "5":
            menu_spotify()
        elif opcao == "6":
            dialogo_por_voz()
        elif opcao == "7":
            print("Saindo do programa...")
            break
        else:
            print("Opção inválida. Por favor, escolha uma opção válida.")

if __name__ == "__main__":
    main()