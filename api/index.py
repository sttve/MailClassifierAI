from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import os
import PyPDF2
from openai import OpenAI

# --- Configuração do Flask ---
app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', 'sua_chave_secreta_padrao_muito_segura')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' # Mantenha o DB em memória
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


# --- Configuração OpenAI (já existente) ---
openai_api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

# --- Modelo de Usuário para o Banco de Dados ---
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"User('{self.username}')"

with app.app_context():
    db.create_all() # <-- Isso garante que as tabelas sejam criadas na inicialização da função serverless
    # Opcional: Criar um usuário admin na inicialização do DB em memória (para testes)
    # Note: Este usuário será recriado a cada nova instância da função na Vercel
    if not User.query.filter_by(username='admin').first(): # Sempre true em uma nova instância
        admin_user = User(username='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        db.session.commit()
        print("Usuário 'admin' criado na memória para testes.") # Isso aparecerá nos logs da Vercel

# --- Callback para Flask-Login ---
@login_manager.user_loader
def load_user(user_id):
    """
    Função que recarrega o objeto User a partir do ID do usuário armazenado na sessão.
    Essencial para o Flask-Login.
    """
    return db.session.get(User, int(user_id))  # Usa db.session.get para Python 3.9+ e SQLAlchemy 1.4+


# --- Funções de Processamento (já existentes) ---
def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page_num in range(len(reader.pages)):
            text += reader.pages[page_num].extract_text() or ""
        return text.strip()
    except Exception as e:
        app.logger.error(f"Erro ao extrair texto do PDF: {e}")  # Usar logger para erros
        raise ValueError("Erro ao processar o arquivo PDF.")


def preprocess_text(text):
    return text.lower().strip()


def classify_email_simulated(email_content):
    # Exemplo simples de classificação por palavras-chave
    email_content_lower = email_content.lower()

    # Palavras-chave para "Produtivo"
    productive_keywords = ['urgente', 'problema', 'ajuda', 'suporte', 'defeito', 'bug', 'erro', 'falha', 'solicitação',
                           'atraso', 'cancelar', 'reembolso', 'devolução', 'dúvida', 'questão', 'impedimento',
                           'urgência', 'chamado', 'incidente']

    # Palavras-chave para "Improdutivo"
    improductive_keywords = ['obrigado', 'feedback', 'parabéns', 'ótimo', 'excelente', 'legal', 'bem', 'concluído',
                             'finalizado', 'perfeito', 'ótima', 'agradeço', 'convite', 'newsletter', 'marketing',
                             'promoção', 'feliz', 'boas notícias', 'sucesso', 'informação', 'atualização']

    for keyword in productive_keywords:
        if keyword in email_content_lower:
            return "Produtivo"

    for keyword in improductive_keywords:
        if keyword in email_content_lower:
            return "Improdutivo"

    return "Improdutivo"  # Default para improdutivo se não houver palavras-chave claras


def generate_openai_response(classification, email_content):
    prompt = f"Você é um assistente de e-mail. Crie uma resposta formal e concisa para um e-mail classificado como '{classification}'. O conteúdo do e-mail original é: '{email_content}'. Se a classificação for 'Produtivo', a resposta deve ser resolutiva ou de encaminhamento. Se for 'Improdutivo', a resposta deve ser de agradecimento ou confirmação."

    messages = [
        {"role": "system", "content": "Você é um assistente prestativo para responder e-mails."},
        {"role": "user", "content": prompt}
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # ou "gpt-4o", "gpt-4-turbo"
            messages=messages,
            temperature=0.7,
            max_tokens=200  # Aumentei um pouco para respostas potencialmente mais longas
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Registre o erro para depuração
        app.logger.error(f"Erro na API OpenAI: {e}")
        return "Erro ao gerar resposta com a OpenAI. Por favor, tente novamente mais tarde."


# --- Rotas Existentes (modificadas) ---

@app.route('/')
def index():
    # A rota principal agora exige login
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('index.html')


@app.route('/process_email', methods=['POST'])
@login_required  # Protege esta rota, só usuários logados podem acessá-la
def process_email():
    email_content = ""
    if 'email_text' in request.form and request.form['email_text'].strip():
        email_content = request.form['email_text'].strip()
    elif 'file' in request.files and request.files['file'].filename != '':
        file = request.files['file']
        filename = file.filename
        if filename.endswith('.txt'):
            email_content = file.read().decode('utf-8').strip()
        elif filename.endswith('.pdf'):
            try:
                email_content = extract_text_from_pdf(file)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
        else:
            return jsonify({'error': 'Formato de arquivo não suportado. Use .txt ou .pdf.'}), 400

    if not email_content:
        return jsonify({'error': 'Nenhum conteúdo de e-mail válido foi fornecido.'}), 400

    preprocessed_content = preprocess_text(email_content)
    classification = classify_email_simulated(preprocessed_content)
    suggested_response = generate_openai_response(classification, email_content)

    return jsonify({
        'category': classification,
        'suggested_response': suggested_response
    })


# --- Novas Rotas de Autenticação ---

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Já logado, redireciona para a página principal

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Login realizado com sucesso!', 'success')
            next_page = request.args.get(
                'next')  # Pega a URL que o usuário tentou acessar antes de ser redirecionado para o login
            return redirect(next_page or url_for('index'))
        else:
            flash('Login ou senha inválidos.', 'danger')
    return render_template('login.html')  # Você precisará criar este template


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # Já logado, redireciona para a página principal

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Validação básica
        if not username or not password:
            flash('Nome de usuário e senha são obrigatórios.', 'danger')
            return render_template('register.html')
        if len(username) < 3 or len(password) < 6:
            flash('Nome de usuário deve ter no mínimo 3 caracteres e senha no mínimo 6.', 'danger')
            return render_template('register.html')

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('Nome de usuário já existe. Por favor, escolha outro.', 'danger')
        else:
            new_user = User(username=username)
            new_user.set_password(password)  # Hash da senha
            db.session.add(new_user)
            db.session.commit()
            flash('Conta criada com sucesso! Faça o login.', 'success')
            return redirect(url_for('login'))
    return render_template('register.html')  # Você precisará criar este template


@app.route('/logout')
@login_required  # Só permite logout se o usuário estiver logado
def logout():
    logout_user()
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    # O db.create_all() já foi chamado acima. Pode deixar aqui para garantir, mas não é estritamente necessário.
    # Se quiser testar o admin em memória localmente, pode deixar este bloco.
    print("Iniciando aplicação Flask localmente.")
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 8080))