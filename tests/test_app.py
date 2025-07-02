import sys
import os
# Adiciona o diretório pai (raiz do projeto) ao sys.path
# Isso permite que 'api' seja importado como um pacote
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from api.index import app, db, User, login_manager  # Importe o que for necessário do seu index.py
from werkzeug.security import generate_password_hash
from flask.testing import FlaskClient


# Fixture para configurar um cliente de teste Flask
@pytest.fixture
def client():
    # Configura o app para testes (usa DB em memória para o teste)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Garante DB em memória para testes
    app.config['SECRET_KEY'] = 'test_secret_key'  # Chave secreta para testes

    # Cria o contexto da aplicação para configurar o DB e o Flask-Login
    with app.app_context():
        db.create_all()  # Cria as tabelas para cada teste que usar esta fixture
        # Cria um usuário de teste que estará disponível para todos os testes que usarem esta fixture
        # user = User(username='testuser')
        # user.set_password('testpassword')
        # db.session.add(user)
        # db.session.commit()

        test_client = app.test_client()
        yield test_client  # Retorna o cliente de teste para os testes

        # Cleanup: Remova os dados do DB após o teste (opcional, já que é em memória)
        db.session.remove()
        db.drop_all()


# --- Testes de Autenticação ---
def test_register_new_user(client: FlaskClient):
    """Testa o registro bem-sucedido de um novo usuário."""
    response = client.post('/register', data={
        'username': 'newuser',
        'password': 'newpassword123'
    }, follow_redirects=True)
    assert b"Conta criada com sucesso! Faa o login." in response.data  # Verifica mensagem flash
    assert response.status_code == 200  # Redirecionou e carregou a página

    with app.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.check_password('newpassword123')


def test_register_existing_user(client: FlaskClient):
    """Testa o registro com um nome de usuário já existente."""
    with app.app_context():
        existing_user = User(username='existinguser')
        existing_user.set_password('pass123')
        db.session.add(existing_user)
        db.session.commit()

    response = client.post('/register', data={
        'username': 'existinguser',
        'password': 'anotherpassword'
    }, follow_redirects=True)
    assert b"Nome de usurio j existe." in response.data  # Verifica mensagem flash
    assert response.status_code == 200


def test_login_valid_credentials(client: FlaskClient):
    """Testa o login com credenciais válidas."""
    with app.app_context():
        user = User(username='validuser')
        user.set_password('validpass')
        db.session.add(user)
        db.session.commit()

    response = client.post('/login', data={
        'username': 'validuser',
        'password': 'validpass'
    }, follow_redirects=True)
    assert b"Login realizado com sucesso!" in response.data
    # Verifica se o usuario foi redirecionado para a pagina principal
    assert b"Classificador de E-mails com IA" in response.data


def test_login_invalid_credentials(client: FlaskClient):
    """Testa o login com credenciais inválidas."""
    response = client.post('/login', data={
        'username': 'nonexistent',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    assert b"Login ou senha invlidos." in response.data
    assert b"Login - Classificador de E-mails com IA" in response.data  # Continua na tela de login


def test_access_protected_route_not_logged_in(client: FlaskClient):
    """Testa acesso a rota protegida sem login (deve redirecionar para login)."""
    response = client.get('/', follow_redirects=False)  # Não seguir redirecionamento para verificar o status
    assert response.status_code == 302  # Deve redirecionar
    assert '/login' in response.headers['Location']  # Verifica o destino do redirecionamento


def test_access_protected_route_logged_in(client: FlaskClient):
    """Testa acesso a rota protegida estando logado."""
    # Primeiro faz login
    with app.app_context():
        user = User(username='loggedinuser')
        user.set_password('securepass')
        db.session.add(user)
        db.session.commit()

    # Cria uma sessão de teste com login
    with client.session_transaction() as sess:
        from flask_login import login_user
        with app.app_context():
            # Força o login do usuário para a sessão de teste
            # Isso simula um login bem sucedido para o cliente de teste
            login_user(User.query.filter_by(username='loggedinuser').first())

    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b"Classificador de E-mails com IA" in response.data
    assert b"Ol, loggedinuser!" in response.data  # Verifica se o nome do usuário logado aparece


def test_logout(client: FlaskClient):
    """Testa a funcionalidade de logout."""
    # Primeiro, registre e faça login um usuário para ter uma sessão ativa
    with app.app_context():
        user = User(username='logoutuser')
        user.set_password('logoutpass')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as sess:
        from flask_login import login_user
        with app.app_context():
            login_user(User.query.filter_by(username='logoutuser').first())

    # Agora, faz o logout
    response = client.get('/logout', follow_redirects=True)
    assert b"Voc foi desconectado." in response.data
    assert b"Login - Classificador de E-mails com IA" in response.data  # Redirecionou para login

    # Verifica se a rota protegida não pode mais ser acessada
    response_after_logout = client.get('/', follow_redirects=False)
    assert response_after_logout.status_code == 302
    assert '/login' in response_after_logout.headers['Location']


# Exemplo de como testar /process_email (requer login)
def test_process_email_requires_login(client: FlaskClient):
    """Testa que /process_email exige login."""
    response = client.post('/process_email', data={'email_text': 'test'}, follow_redirects=False)
    assert response.status_code == 302  # Deve redirecionar para login
    assert '/login' in response.headers['Location']


def test_process_email_logged_in(client: FlaskClient):
    """Testa o processamento de email quando logado."""
    # Primeiro, login
    with app.app_context():
        user = User(username='procuser')
        user.set_password('procpass')
        db.session.add(user)
        db.session.commit()

    with client.session_transaction() as sess:
        from flask_login import login_user
        with app.app_context():
            login_user(User.query.filter_by(username='procuser').first())

    # Agora, processa o email
    response = client.post('/process_email', json={'email_text': 'Este e-mail é um teste de problema.'})
    assert response.status_code == 200
    data = response.get_json()
    assert 'category' in data
    assert 'suggested_response' in data
    assert data['category'] == 'Produtivo'  # Espera-se que seja Produtivo com base nas suas palavras-chave
    assert isinstance(data['suggested_response'], str)