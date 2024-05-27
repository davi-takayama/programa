# TCC

---

## Descrição

Este repositório contém o código fonte do Trabalho de Conclusão de Curso (TCC) do curso de Engenharia de Software da Universidade Tecnológica Federal do Paraná (UTFPR) - Campus Dois Vizinhos. O trabalho tem como título "desenvolvimento de uma aplicação gamificada para educação musical", desenvolvida por Davi Takayama e orientada pela professora Dra. Simone de Sousa Borges

---

## Tecnologias

- [Python](https://www.python.org/)
- [Pygame](https://www.pygame.org/)

---

## Instalação

A versão do Python utilizada no projeto é a 3.11.9 por conta da compatibilidade de uma das dependências do projeto. Para instalar as dependências do projeto, execute o comando abaixo:

```bash
git clone https://github.com/davi-takayama/tcc
cd tcc
pip install -r requirements.txt
```

Para executar o projeto, basta executar o comando `python main.py` com o terminal aberto no diretorio raiz.

---

## Estrutura

O projeto está estruturado da seguinte forma:

> 📁 assets - arquivos de áudio e imagens
> 📂 src - todo o código fonte da aplicação
>> 📂 render - parte do código responsável pelas telas e componentes
>>> 📂 menu - tela de navegação da aplicação
>>>> 📂 mod_x - módulos de cada uma das partes do programa
>>>>> 📄 challenge
>>>>> 📄 explanation
>>>>> 📄 layout
>>>>
>>>> 📄 [main_menu](src/render/menu/main_menu.py) - gerencia e exibe as informações do módulo atualmente aberto
>>>> 📄 [top_menu](src/render/menu/top_menu.py) - componente do menu que exibe o progresso geral de todos os módulos
>>>
>>> 📄 [intro_scr](src//render/intro_scr.py) - exibida na primeira vez abrindo a aplicação
>>> 📄 [staff](src/render/staff.py) - componente que exibe a pauta da partitura (usado em diversas telas)
>>
>> 📂 utils - funções e classes utilitárias
>>> 📂 audioinput - arquivos usados para identificar as notas pela frequência do microfone
>>>> 📄 [audio_analyzer](src/utils/audioinput/audio_analyzer.py) - classe que identifica as notas de acordo com a frequência
>>>> 📄 [threading_helper](src/utils/audioinput/threading_helper.py) - thread auxiliar que guarda um buffer para o arquivo acima
>>>
>>> 📂 save_operations
>>>> 📄 [check_save_exists](src/utils/save_operations/check_save_exists.py) - arquivo que verifica os dados existentes
>>>> 📄 [create_save](src/utils/save_operations/create_save.py) - função que cria dados designado
>>>> 📄 [read_save](src/utils/save_operations/read_save.py) - classes que mapeiam (leitura e escrita) dos dados
>>>> 📄 [save](src/utils/save_operations/save.json) - template dos dados
>>>
>>> 📄 [bottom_screen_button](src/utils/bottom_screen_button.py) - devolve um botão no canto inferior direito
>>> 📄 [button](src/utils/button.py) - classe do objeto de botão
>>> 📄 [challenge_model](src/utils/challenge_model.py) - classe abstrata de desafio
>>> 📄 [image_rescaler](src/utils/image_rescaler.py) - funções de reescalar uma imagem proporcionalmente
>>> 📄 [metronome](src/utils/metronome.py) - thread que inicia um metrônomo
>>> 📄 [module_model](src/utils/module_model.py) - classe abstrata do layout de um módulo
>>> 📄 [note_renderer](src/utils/note_renderer.py) - renderiza as notas e pausas
>>> 📄 [renderable](src/utils/renderable.py) - classe abstrata de todos os componentes visuais
>>> 📄 [root_dir](src/utils/root_dir.py) - devolve o diretório raiz da aplicação
>>
>> 📄 [state_handler](src/state_handler.py) - gerencia o estado da aplicação para definir telas e ações
>
> 📄 [main](main.py) - arquivo principal que inicia a aplicação (chama o gerenciador de estados)

A aplicação faz uso da arquitetura de estados para gerenciar as telas e ações do usuário. Cada módulo é uma tela diferente e possui um arquivo de layout, ao menos uma explicação e um tipo de desafio referente ao conteúdo da explicação.

---

## Conteúdos

### Módulo 1

O primeiro módulo é uma introdução à leitura de partituras. O usuário é apresentado à pauta e às notas musicais. O desafio é identificar as notas musicais na pauta.

Na primeira explicação são apresentadas as notas de cada linha e espaço da pauta (as notas naturais) e como lembrar seus respectivos nomes

Já na segunda explicação, são apresentadas as notas não naturais (acidentadas)

No desafio deve-se identificar as notas musicais na pauta. O usuário deve clicar na nota correspondente à que está sendo tocada.

Do segundo em diante, deve ser usado um instrumento para tocar a nota que está sendo pedida.

### Módulo 2

O segundo módulo é uma introdução ao ritmo. O usuário é apresentado ao conceito de compasso e à duração das notas. Inicialmente são apresentadas as figuras de tempo e suas respectivas durações, assim como sua relação com as assinaturas de tempo. Em seguida, são apresentadas as pausas e suas durações.

O primeiro desafio consiste em identificar a duração de um conjunto de notas e dar outro conjunto com tempo equivalente. O segundo repete o conceito do primeiro, mas com a adição das figuras de pausa. O terceiro mistura notas e pausas e pede uma sequência de notas e pausas com tempo equivalente.

Do quarto em diante, assumindo que o usuário esteja familiarizado com as figuras, é usado novamente um instrumento para que a relação entre as figuras e a duração real delas seja mais clara.

---

## Elementos da gamificação

- Pontuação: cada nível conta com uma pontuação máxima que pode ser alcançada. A pontuação é baseada na quantidade de acertos e erros do usuário.

- Níveis: cada módulo é um nível diferente. O usuário deve completar o módulo para avançar para o próximo.

- Recompensas: ao completar um módulo, o usuário recebe uma recompensa. A recompensa é uma estrela exibida em vazio no menu principal. Ao completar um módulo com a pontuação perfeita, a estrela é preenchida.

- Conquistas/divisas: ao completar um módulo com a pontuação perfeita, o usuário recebe um marco. O marco é uma estrela preenchida exibida no menu principal. Ao completar todos os módulos com a pontuação perfeita, o usuário recebe um marco especial daquele módulo.

- feedback: durante cada desafio de um capítulo, o usuário recebe o feedback sobre sua resposta para que seja compreendida a ação realizada por ele.

- progresso: no menu, são exibidas algumas informações, como número de capítulos completados, número de capítulos com pontuação perfeita e uma barra de progresso geral

- objetivos definidos: cada módulo tem um objetivo claro e definido, que é apresentado ao usuário no início e durante do módulo
