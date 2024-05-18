import React, { useEffect, useState } from 'react';
import { View, Text, TextInput, Button, ScrollView } from 'react-native';
import Voice from 'react-native-voice';
import Tts from 'react-native-tts';
import RNFS from 'react-native-fs';
import SpotifyAPI from 'react-native-spotify-api';

const spotifyConfig = {
  clientId: '599d97ecf88d4f1296c66ba3c107a6cd',
  clientSecret: 'be984ae0f6e94c5ba84852f71ced7bee',
  redirectUri: 'yourapp://callback',
};

const spotifyApi = new SpotifyAPI(spotifyConfig);

const App = () => {
  const [compromissos, setCompromissos] = useState({});
  const [anotacoes, setAnotacoes] = useState({});
  const [voiceInput, setVoiceInput] = useState('');
  const [isListening, setIsListening] = useState(false);

  useEffect(() => {
    Voice.onSpeechResults = onSpeechResults;
    return () => {
      Voice.destroy().then(Voice.removeAllListeners);
    };
  }, []);

  const onSpeechResults = (event) => {
    setVoiceInput(event.value[0]);
    processVoiceCommand(event.value[0]);
  };

  const startListening = () => {
    Voice.start('pt-BR');
    setIsListening(true);
  };

  const stopListening = () => {
    Voice.stop();
    setIsListening(false);
  };

  const processVoiceCommand = (command) => {
    Tts.speak('Você disse: ' + command);
    // Process commands and call respective functions
  };

  const adicionarCompromisso = (data, compromisso) => {
    const updatedCompromissos = { ...compromissos };
    if (updatedCompromissos[data]) {
      updatedCompromissos[data].push(compromisso);
    } else {
      updatedCompromissos[data] = [compromisso];
    }
    setCompromissos(updatedCompromissos);
    salvarAgenda(updatedCompromissos);
  };

  const adicionarAnotacao = (titulo, conteudo) => {
    const updatedAnotacoes = { ...anotacoes, [titulo]: conteudo };
    setAnotacoes(updatedAnotacoes);
    salvarAnotacoes(updatedAnotacoes);
  };

  const salvarAgenda = async (agenda) => {
    const path = RNFS.DocumentDirectoryPath + '/Agenda.txt';
    let data = '';
    for (let date in agenda) {
      for (let compromisso of agenda[date]) {
        data += `${date},${compromisso}\n`;
      }
    }
    await RNFS.writeFile(path, data, 'utf8');
  };

  const carregarAgenda = async () => {
    const path = RNFS.DocumentDirectoryPath + '/Agenda.txt';
    if (await RNFS.exists(path)) {
      const data = await RNFS.readFile(path, 'utf8');
      const lines = data.split('\n');
      const loadedCompromissos = {};
      for (let line of lines) {
        if (line.trim()) {
          const [date, compromisso] = line.split(',', 1);
          if (loadedCompromissos[date]) {
            loadedCompromissos[date].push(compromisso);
          } else {
            loadedCompromissos[date] = [compromisso];
          }
        }
      }
      setCompromissos(loadedCompromissos);
    }
  };

  const salvarAnotacoes = async (anotacoes) => {
    const path = RNFS.DocumentDirectoryPath + '/Anotacoes.txt';
    let data = '';
    for (let titulo in anotacoes) {
      data += `${titulo}\n${anotacoes[titulo]}\n---\n`;
    }
    await RNFS.writeFile(path, data, 'utf8');
  };

  const carregarAnotacoes = async () => {
    const path = RNFS.DocumentDirectoryPath + '/Anotacoes.txt';
    if (await RNFS.exists(path)) {
      const data = await RNFS.readFile(path, 'utf8');
      const lines = data.split('\n');
      const loadedAnotacoes = {};
      for (let i = 0; i < lines.length; i += 3) {
        const titulo = lines[i].trim();
        const conteudo = lines[i + 1].trim();
        loadedAnotacoes[titulo] = conteudo;
      }
      setAnotacoes(loadedAnotacoes);
    }
  };

  const marcarCompromisso = () => {
    // Function to mark a commitment using input fields
  };

  const mostrarCompromissos = () => {
    // Function to show commitments
  };

  const fazerAnotacao = () => {
    // Function to make a note using input fields
  };

  const mostrarAnotacoes = () => {
    // Function to show notes
  };

  const contarPiada = () => {
    const piadas = [
      "Por que o pombo não bate asa? Porque ele já é bom!",
      "Qual é o rei dos queijos? O reiqueijão!",
      "Qual é o cúmulo da rapidez? Fechar os olhos antes de aparecer a foto!",
      "Por que o elefante não pega fogo? Porque ele já é cinza!",
      "Por que o jacaré tirou o jacarezinho da escola? Porque ele réptil!"
    ];
    const piadaEscolhida = piadas[Math.floor(Math.random() * piadas.length)];
    Tts.speak(piadaEscolhida);
  };

  const abrirSpotify = async () => {
    try {
      await spotifyApi.login();
    } catch (error) {
      console.error('Error logging into Spotify:', error);
    }
  };

  const continuarMusica = async () => {
    await spotifyApi.play();
  };

  const pausarMusica = async () => {
    await spotifyApi.pause();
  };

  const colocarMusicaAnterior = async () => {
    await spotifyApi.previous();
  };

  const colocarProximaMusica = async () => {
    await spotifyApi.next();
  };

  const fazerPesquisa = (pesquisa) => {
    const url = `https://www.google.com/search?q=${pesquisa}`;
    Linking.openURL(url);
  };

  const menuSpotify = () => {
    // Function to handle Spotify menu actions
  };

  return (
    <ScrollView>
      <View style={{ padding: 20 }}>
        <Text>Menu Principal</Text>
        <Button title="Marcar Compromisso" onPress={marcarCompromisso} />
        <Button title="Mostrar Compromissos" onPress={mostrarCompromissos} />
        <Button title="Fazer Anotação" onPress={fazerAnotacao} />
        <Button title="Mostrar Anotações" onPress={mostrarAnotacoes} />
        <Button title="Contar Piada" onPress={contarPiada} />
        <Button title="Pesquisar" onPress={() => fazerPesquisa('example search')} />
        <Button title="Menu Spotify" onPress={menuSpotify} />
        <Button title={isListening ? "Parar de Ouvir" : "Ouvir Comando de Voz"} onPress={isListening ? stopListening : startListening} />
      </View>
    </ScrollView>
  );
};

export default App;
