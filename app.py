import os

from dotenv import load_dotenv
load_dotenv()

# Carrega as variáveis do .env

try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Erro ao inicializar cliente OpenAI: {e}. Certifique-se de que OPENAI_API_KEY está configurada.")
    openai_client = None
from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import PyPDF2
from io import BytesIO

# Importar o cliente da OpenAI
from openai import OpenAI

app = Flask(__name__)

# --- Configuração da Chave da OpenAI ---
# É FUNDAMENTAL que você configure sua chave de API da OpenAI como uma variável de ambiente.
# Exemplo (no terminal antes de rodar o app):
# export OPENAI_API_KEY="sua_chave_aqui" (Linux/macOS)
# $env:OPENAI_API_KEY="sua_chave_aqui" (PowerShell)
# set OPENAI_API_KEY=sua_chave_aqui (CMD)
# Ou use um arquivo .env com a biblioteca python-dotenv (recomendado para desenvolvimento local)

try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
except Exception as e:
    print(f"Erro ao inicializar cliente OpenAI: {e}. Certifique-se de que OPENAI_API_KEY está configurada.")
    openai_client = None
    # Define como None se a chave não for encontrada

# --- Configuração do Modelo de Classificação ---
# Função de pré-processamento (simplificada para o exemplo)
def preprocess_text(text):
    return text.lower() # Apenas para o exemplo, sem pré-processamento real avançado

# Função de classificação (simulada)
def classify_email_simulated(text):
    productive_keywords = ["solicitação", "dúvida", "suporte", "atualização", "urgente", "problema", "bug"]
    for keyword in productive_keywords:
        if keyword in text:
            return "Produtivo"
    return "Improdutivo"

# Função para gerar resposta usando OpenAI
def generate_openai_response(category, email_content):
    if openai_client is None:
        return "Erro: Chave da OpenAI não configurada. Não foi possível gerar a resposta."

    if category == "Produtivo":
        # Prompt para email produtivo: solicitação, suporte, etc.
        prompt_text = f"""
        Você é um assistente de e-mail prestativo. Baseado no seguinte e-mail classificado como 'Produtivo',
        gere uma resposta formal, educada e concisa que confirme o recebimento, agradeça o contato e
        informe que a solicitação está sendo analisada ou que em breve entrarão em contato com uma atualização.
        Não inclua saudações iniciais como "Prezado(a)" e nem despedidas como "Atenciosamente".
        Apenas o corpo da resposta.

        Email:
        "{email_content}"

        Resposta:
        """
        max_tokens = 150 # Mais tokens para respostas mais elaboradas
    elif category == "Improdutivo":
        # Prompt para email improdutivo: agradecimentos, felicitações, etc.
        prompt_text = f"""
        Você é um assistente de e-mail prestativo. Baseado no seguinte e-mail classificado como 'Improdutivo',
        gere uma resposta curta, cordial e informal que seja um simples agradecimento ou reconhecimento.
        Não inclua saudações iniciais como "Prezado(a)" e nem despedidas como "Atenciosamente".
        Apenas o corpo da resposta.

        Email:
        "{email_content}"

        Resposta:
        """
        max_tokens = 80 # Menos tokens para respostas curtas
    else:
        return "Não foi possível gerar uma resposta para esta categoria."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",  # Ou "gpt-4" para resultados ainda melhores
            messages=[
                {"role": "system", "content": "Você é um assistente de e-mail profissional e prestativo."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=max_tokens,
            temperature=0.7, # Controla a criatividade (0.0 a 1.0)
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao comunicar com a OpenAI: {e}"

# --- Rotas da Aplicação ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_email', methods=['POST'])
def process_email():
    email_content = ""

    if 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        if file.filename.endswith('.txt'):
            email_content = file.read().decode('utf-8')
        elif file.filename.endswith('.pdf'):
            try:
                pdf_reader = PyPDF2.PdfReader(BytesIO(file.read()))
                for page in pdf_reader.pages:
                    email_content += page.extract_text() or ""
            except Exception as e:
                return jsonify({"error": f"Erro ao ler PDF: {e}"}), 400
        else:
            return jsonify({"error": "Formato de arquivo não suportado. Use .txt ou .pdf."}), 400
    elif 'email_text' in request.form:
        email_content = request.form['email_text']
    else:
        return jsonify({"error": "Nenhum arquivo ou texto foi fornecido."}), 400

    if not email_content.strip():
        return jsonify({"error": "O conteúdo do email está vazio."}), 400

    # Pré-processamento
    preprocessed_text = preprocess_text(email_content)

    # Classificação (mantendo a simulação ou integrando um modelo HF para classificação)
    class_label = classify_email_simulated(preprocessed_text)

    # Geração de resposta utilizando OpenAI
    suggested_response = generate_openai_response(class_label, email_content)

    return jsonify({
        "category": class_label,
        "suggested_response": suggested_response
    })

if __name__ == '__main__':
    app.run(debug=True)