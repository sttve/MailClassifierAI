# api/index.py
import os
from flask import Flask, render_template, request, jsonify
import PyPDF2
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do .env para a execução local
# Na Vercel, as variáveis de ambiente são configuradas diretamente no painel
load_dotenv()

app = Flask(__name__,
            template_folder=os.path.join(os.getcwd(), 'templates'),
            static_folder=os.path.join(os.getcwd(), 'static')) # Certifique-se que o Flask encontre as pastas

# --- Configuração da Chave da OpenAI ---
try:
    openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    if not openai_client.api_key:
        raise ValueError("OPENAI_API_KEY não configurada. Configure no Vercel Dashboard ou .env localmente.")
except Exception as e:
    print(f"Erro ao inicializar cliente OpenAI: {e}. Certifique-se de que OPENAI_API_KEY está configurada.")
    openai_client = None

# --- Funções do seu app.py ---
def preprocess_text(text):
    return text.lower()

def classify_email_simulated(text):
    productive_keywords = ["solicitação", "dúvida", "suporte", "atualização", "urgente", "problema", "bug"]
    for keyword in productive_keywords:
        if keyword in text:
            return "Produtivo"
    return "Improdutivo"

def generate_openai_response(category, email_content):
    if openai_client is None:
        return "Erro: Chave da OpenAI não configurada. Não foi possível gerar a resposta."

    if category == "Produtivo":
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
        max_tokens = 150
    elif category == "Improdutivo":
        prompt_text = f"""
        Você é um assistente de e-mail prestativo. Baseado no seguinte e-mail classificado como 'Improdutivo',
        gere uma resposta curta, cordial e informal que seja um simples agradecimento ou reconhecimento.
        Não inclua saudações iniciais como "Prezado(a)" e nem despedidas como "Atenciosamente".
        Apenas o corpo da resposta.

        Email:
        "{email_content}"

        Resposta:
        """
        max_tokens = 80
    else:
        return "Não foi possível gerar uma resposta para esta categoria."

    try:
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente de e-mail profissional e prestativo."},
                {"role": "user", "content": prompt_text}
            ],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Erro ao comunicar com a OpenAI: {e}"

# --- Rotas da Aplicação Flask ---

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

    preprocessed_text = preprocess_text(email_content)
    class_label = classify_email_simulated(preprocessed_text)
    suggested_response = generate_openai_response(class_label, email_content)

    return jsonify({
        "category": class_label,
        "suggested_response": suggested_response
    })

# --- Importante para a Vercel ---
# A Vercel espera uma variável `app` ou `application` para WSGI/ASGI
# O Gunicorn (que a Vercel usa internamente) vai procurar por esta variável.
# Certifique-se de que esta linha está no final do seu api/index.py
from werkzeug.serving import run_simple
if __name__ == '__main__':
    # Para testes locais diretamente via python api/index.py
    # A Vercel não usará este bloco
    app.run(debug=True)