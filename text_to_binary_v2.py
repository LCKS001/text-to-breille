import cv2
import pytesseract
import serial
import time
import os
import sys
import numpy as np
from PIL import Image
import fitz
import argparse

DEFAULT_TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
DEFAULT_SERIAL_PORT = "COM24"
DEFAULT_BAUD_RATE = 9600
DEFAULT_LANG = 'por'

class TextToBinarySender:

    def __init__(self, tesseract_cmd, serial_port, baud_rate, lang):
        self.tesseract_cmd = tesseract_cmd
        self.serial_port = serial_port
        self.baud_rate = baud_rate
        self.lang = lang
        self.serial_conn = None

        if not os.path.exists(self.tesseract_cmd):
            raise FileNotFoundError(f"Tesseract não encontrado em: {self.tesseract_cmd}. Verifique o caminho.")
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_cmd

    def connect_serial(self):
        if self.serial_conn and self.serial_conn.is_open:
            print("Já conectado à porta serial.")
            return True
        try:
            print(f"Conectando a {self.serial_port} a {self.baud_rate} baud...")
            self.serial_conn = serial.Serial(self.serial_port, self.baud_rate, timeout=2)
            time.sleep(2)
            print("Conectado com sucesso.")
            return True
        except serial.SerialException as e:
            print(f"Erro ao conectar à porta serial {self.serial_port}: {e}")
            self.serial_conn = None
            return False

    def text_to_binary_string(self, text):
        if not text:
            return ""
        return ' '.join(format(ord(char), '08b') for char in text)

    def load_and_preprocess_image(self, file_path):
        print(f"Carregando e pré-processando: {file_path}")
        try:
            if file_path.lower().endswith('.pdf'):
                with fitz.open(file_path) as doc:
                    if not doc.page_count > 0:
                        print("Erro: PDF sem páginas.")
                        return None
                    page = doc.load_page(0)
                    pix = page.get_pixmap()
                    img_pil = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                    img_cv = cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)
            else:
                img_cv = cv2.imread(file_path)
                if img_cv is None:
                    print(f"Erro: Não foi possível carregar a imagem ou formato inválido: {file_path}")
                    return None

            gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            print("Pré-processamento concluído.")
            return thresh

        except fitz.fitz.FileNotFoundError:
             print(f"Erro: Arquivo PDF não encontrado: {file_path}")
             return None
        except Exception as e:
            print(f"Erro inesperado ao carregar/pré-processar a imagem: {e}")
            return None

    def extract_text_from_image(self, img):
        if img is None:
            return None
        print(f"Extraindo texto com Tesseract (idioma: {self.lang})...")
        try:
            text = pytesseract.image_to_string(img, lang=self.lang)
            extracted_text = text.strip()
            if not extracted_text:
                 print("Aviso: Nenhum texto detectado pelo Tesseract.")
            else:
                 print("Texto extraído com sucesso.")
            return extracted_text
        except pytesseract.TesseractNotFoundError:
            print(f"Erro: Executável do Tesseract não encontrado ou não está no PATH.")
            return None
        except Exception as e:
            print(f"Erro durante a extração de texto pelo Tesseract: {e}")
            return None

    def send_to_arduino(self, data_string):
        if not data_string:
            print("Nenhum dado para enviar.")
            return False
            
        if not self.serial_conn or not self.serial_conn.is_open:
            print("Conexão serial não está aberta. Tentando reconectar...")
            if not self.connect_serial():
                return False

        try:
            print(f"Enviando dados para {self.serial_port}: {len(data_string)} caracteres")
            self.serial_conn.write(data_string.encode('utf-8') + b'\n')
            print("Dados enviados.")
            return True
        except serial.SerialTimeoutException:
            print("Erro: Timeout ao escrever na porta serial.")
            return False
        except serial.SerialException as e:
            print(f"Erro de comunicação serial: {e}")
            return False
        except Exception as e:
             print(f"Erro inesperado ao enviar dados: {e}")
             return False

    def process_file(self, file_path):
        if not os.path.exists(file_path):
            print(f"Erro: Arquivo de entrada não encontrado: {file_path}")
            return False

        processed_img = self.load_and_preprocess_image(file_path)
        if processed_img is None:
            return False

        text = self.extract_text_from_image(processed_img)
        if text is None:
            return False

        binary_string = self.text_to_binary_string(text)
        print(f"\n--- Resultados ---")
        print(f"Texto Original: {text}")
        print(f"Representação Binária (String): {binary_string}")
        print(f"----------------\n")

        if not self.connect_serial():
             return False
             
        return self.send_to_arduino(binary_string)

    def close_connection(self):
        if self.serial_conn and self.serial_conn.is_open:
            print(f"Fechando conexão com {self.serial_port}.")
            self.serial_conn.close()
            self.serial_conn = None

    def __del__(self):
        self.close_connection()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Lê texto de uma imagem/PDF, converte para binário e envia via serial.")
    parser.add_argument("file_path", help="Caminho para o arquivo de imagem (jpg, png, etc.) ou PDF.")
    parser.add_argument("-t", "--tesseract", default=DEFAULT_TESSERACT_CMD, help=f"Caminho para o executável tesseract.exe (Padrão: {DEFAULT_TESSERACT_CMD})")
    parser.add_argument("-p", "--port", default=DEFAULT_SERIAL_PORT, help=f"Porta serial para comunicação com Arduino (Padrão: {DEFAULT_SERIAL_PORT})")
    parser.add_argument("-b", "--baud", type=int, default=DEFAULT_BAUD_RATE, help=f"Baud rate da comunicação serial (Padrão: {DEFAULT_BAUD_RATE})")
    parser.add_argument("-l", "--lang", default=DEFAULT_LANG, help=f"Idioma para o Tesseract OCR (Padrão: {DEFAULT_LANG})")

    args = parser.parse_args()

    try:
        sender = TextToBinarySender(
            tesseract_cmd=args.tesseract,
            serial_port=args.port,
            baud_rate=args.baud,
            lang=args.lang
        )
        success = sender.process_file(args.file_path)
        
        if success:
            print("\nProcesso concluído com sucesso.")
        else:
            print("\nProcesso concluído com erros.")
            sys.exit(1)
            
    except FileNotFoundError as e:
        print(f"Erro de configuração: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Erro inesperado na execução principal: {e}")
        sys.exit(1)
    finally:
        if 'sender' in locals() and sender:
             sender.close_connection()

