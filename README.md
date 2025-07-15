# README - Sistema de Conversão de Texto para Braille

## Visão Geral

Este projeto consiste em dois componentes principais:
1. Um script Python (`text_to_binary_v2.py`) que converte texto de imagens/PDFs para representação binária e envia via serial para um Arduino
2. Um sketch Arduino (`sketch_jun3a.ino`) que recebe os dados binários e controla servomotores para representar caracteres em Braille

O sistema permite converter texto de documentos ou imagens em saída física em Braille usando servomotores.

## Pré-requisitos

### Para o script Python:
- Python 3.x
- Bibliotecas Python:
  - OpenCV (`pip install opencv-python`)
  - PyTesseract (`pip install pytesseract`)
  - PySerial (`pip install pyserial`)
  - PyMuPDF (`pip install pymupdf`)
  - Pillow (`pip install pillow`)
  - NumPy (`pip install numpy`)
- Tesseract OCR instalado (caminho padrão: `C:\Program Files\Tesseract-OCR\tesseract.exe`)

### Para o Arduino:
- Placa Arduino (Uno, Mega ou similar)
- 6 servomotores
- Buzzer
- Bibliotecas:
  - Servo.h (incluída na IDE Arduino)

## Hardware necessário

- Arduino (Uno, Mega ou similar)
- 6 servomotores conectados aos pinos A0-A5
- Buzzer conectado ao pino 10
- Cabo USB para conexão serial

## Configuração do Arduino

1. Conecte os servomotores aos pinos A0-A5
2. Conecte o buzzer ao pino 10
3. Carregue o sketch `sketch_jun3a.ino` para o Arduino
4. Anote a porta serial utilizada (COMx no Windows, /dev/ttyACMx no Linux)

## Como executar

### Script Python:

```bash
python text_to_binary_v2.py caminho/para/arquivo [opções]
```

Opções disponíveis:
- `-t` ou `--tesseract`: Caminho para o executável do Tesseract (padrão: `C:\Program Files\Tesseract-OCR\tesseract.exe`)
- `-p` ou `--port`: Porta serial (padrão: COM24)
- `-b` ou `--baud`: Baud rate (padrão: 9600)
- `-l` ou `--lang`: Idioma para OCR (padrão: 'por' - português)

Exemplo:
```bash
python text_to_binary_v2.py documento.pdf -p COM3 -l eng
```

### Arduino:
O sketch Arduino deve ser carregado uma vez e ficará aguardando dados pela porta serial.

## Fluxo de Funcionamento

1. O Python lê um arquivo (imagem ou PDF)
2. Pré-processa a imagem (converte para escala de cinza e binariza)
3. Extrai texto usando Tesseract OCR
4. Converte o texto para representação binária (8 bits por caractere)
5. Envia a string binária via porta serial para o Arduino
6. O Arduino recebe os dados e:
   - Ativa os servomotores correspondentes aos pontos do Braille
   - Mantém cada caractere ativo por 2 segundos
   - Emite um beep ao final de cada caractere
   - Desativa todos os servos antes do próximo caractere

## Estrutura dos Códigos

### text_to_binary_v2.py

- `TextToBinarySender`: Classe principal que gerencia todo o processo
  - `connect_serial()`: Estabelece conexão com a porta serial
  - `text_to_binary_string()`: Converte texto para string binária
  - `load_and_preprocess_image()`: Carrega e pré-processa imagens/PDFs
  - `extract_text_from_image()`: Usa Tesseract para extrair texto de imagens
  - `send_to_arduino()`: Envia dados para o Arduino via serial
  - `process_file()`: Orquestra todo o processo de um arquivo

### sketch_jun3a.ino

- Configura 6 servomotores nos pinos A0-A5
- Configura um buzzer no pino 10
- `loop()` principal verifica por novos dados serial periodicamente
- `processBraille()`: Ativa os servos conforme os bits recebidos (1=90°, 0=0°)
  - Cada caractere é exibido por 2 segundos
  - Emite um beep de 200ms ao final de cada caractere
  - Pausa de 1 segundo entre caracteres

## Limitações e Melhorias Possíveis

1. O sistema atual converte texto para representação binária genérica, não para padrão Braille
2. O OCR pode ter dificuldades com fontes não padronizadas ou imagens de baixa qualidade
3. Melhorias possíveis:
   - Mapeamento direto para Braille (6 pontos) em vez de usar representação binária de 8 bits
   - Suporte a mais idiomas no OCR
   - Configuração mais flexível dos pinos e tempos

## Troubleshooting

- Verifique a porta serial correta no Python
- Confira se o Tesseract está instalado no caminho especificado
- Certifique-se que todos os servomotores estão conectados corretamente
- Se o Arduino não responder, reinicie a placa e verifique a conexão serial

## Licença

Este projeto está disponível sob licença MIT. Sinta-se livre para modificar e distribuir conforme necessário.
