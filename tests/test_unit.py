import pytest
from unittest.mock import patch, MagicMock
import os
import sys

# Adiciona o diretório 'api' ao sys.path para que possamos importar 'index'
# Isso é necessário porque o arquivo de teste está em uma pasta diferente
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../api')))

# Importa as funções que queremos testar do seu arquivo index.py
# Certifique-se de que os nomes das funções correspondem aos do seu index.py
from index import preprocess_text, classify_email_simulated, generate_response_openai, app # Assumindo que essas são suas funções

# --- Testes para preprocess_text ---
def test_preprocess_text_lowercase():
    """Testa se o texto é convertido para minúsculas."""
    assert preprocess_text("Hello World!") == "hello world!"
    assert preprocess_text("PYTHON") == "python"

def test_preprocess_text_strip_whitespace():
    """Testa se espaços em branco extras são removidos."""
    assert preprocess_text("  leading and trailing  ") == "leading and trailing"
    assert preprocess_text("  multiple   spaces  ") == "multiple spaces"

def test_preprocess_text_empty_string():
    """Testa o comportamento com string vazia."""
    assert preprocess_text("") == ""

def test_preprocess_text_with_numbers_and_symbols():
    """Testa o comportamento com números e símbolos."""
    assert preprocess_text("Email 123!@#$") == "email 123!@#$"

# --- Testes para classify_email_simulated ---
def test_classify_email_simulated_produtivo():
    """Testa a classificação para um e-mail produtivo."""
    email_content = "preciso de ajuda com o sistema"
    assert classify_email_simulated(email_content) == "Produtivo"

def test_classify_email_simulated_improdutivo():
    """Testa a classificação para um e-mail improdutivo."""
    email_content = "obrigado pelo feedback"
    assert classify_email_simulated(email_content) == "Improdutivo"

def test_classify_email_simulated_mixed_content_produtivo():
    """Testa a classificação com conteúdo misto que deve ser produtivo."""
    email_content = "Olá, recebi seu e-mail de agradecimento, mas ainda preciso daquela funcionalidade."
    assert classify_email_simulated(email_content) == "Produtivo"

def test_classify_email_simulated_mixed_content_improdutivo():
    """Testa a classificação com conteúdo misto que deve ser improdutivo."""
    email_content = "Parabéns pelo projeto! Muito bom. Sem mais, obrigado."
    assert classify_email_simulated(email_content) == "Improdutivo"

def test_classify_email_simulated_empty_content():
    """Testa a classificação com conteúdo vazio."""
    assert classify_email_simulated("") == "Improdutivo" # Ou "Não Classificado" dependendo da sua lógica

# --- Testes para generate_response_openai (com Mocking) ---

# Usamos @patch para substituir 'openai.OpenAI' por um mock durante o teste
@patch('openai.OpenAI')
def test_generate_response_openai_produtivo(mock_openai_class):
    """
    Testa a geração de resposta para um e-mail produtivo,
    simulando a resposta da API da OpenAI.
    """
    # Configura o mock para retornar um objeto que simula a resposta da API
    mock_client_instance = mock_openai_class.return_value # Retorna a instância do cliente OpenAI
    mock_chat_completion = MagicMock() # Cria um mock para o resultado da chamada chat.completions.create
    mock_chat_completion.choices[0].message.content = "Resposta sugerida para produtivo."
    mock_client_instance.chat.completions.create.return_value = mock_chat_completion

    email_content = "Preciso de suporte técnico urgente."
    classification = "Produtivo"
    expected_response = "Resposta sugerida para produtivo."

    response = generate_response_openai(email_content, classification)

    assert response == expected_response
    # Verifica se a API da OpenAI foi chamada com os argumentos corretos
    mock_client_instance.chat.completions.create.assert_called_once()
    args, kwargs = mock_client_instance.chat.completions.create.call_args
    assert "messages" in kwargs
    assert "Produtivo" in kwargs["messages"][1]["content"] # Verifica se a classificação está no prompt

@patch('openai.OpenAI')
def test_generate_response_openai_improdutivo(mock_openai_class):
    """
    Testa a geração de resposta para um e-mail improdutivo,
    simulando a resposta da API da OpenAI.
    """
    mock_client_instance = mock_openai_class.return_value
    mock_chat_completion = MagicMock()
    mock_chat_completion.choices[0].message.content = "Resposta sugerida para improdutivo."
    mock_client_instance.chat.completions.create.return_value = mock_chat_completion

    email_content = "Obrigado pelo convite!"
    classification = "Improdutivo"
    expected_response = "Resposta sugerida para improdutivo."

    response = generate_response_openai(email_content, classification)

    assert response == expected_response
    mock_client_instance.chat.completions.create.assert_called_once()
    args, kwargs = mock_client_instance.chat.completions.create.call_args
    assert "messages" in kwargs
    assert "Improdutivo" in kwargs["messages"][1]["content"] # Verifica se a classificação está no prompt

@patch('openai.OpenAI')
def test_generate_response_openai_api_error(mock_openai_class):
    """
    Testa o tratamento de erro na geração de resposta da OpenAI.
    """
    mock_client_instance = mock_openai_class.return_value
    # Simula uma exceção da API da OpenAI
    mock_client_instance.chat.completions.create.side_effect = Exception("Erro da API OpenAI")

    email_content = "Teste de erro."
    classification = "Produtivo"
    expected_response_part = "Erro ao gerar resposta" # Parte da mensagem de erro esperada

    response = generate_response_openai(email_content, classification)

    assert expected_response_part in response
    mock_client_instance.chat.completions.create.assert_called_once()

# --- Teste de Integração Básico para a Rota Flask (Opcional aqui, mas bom para integração) ---
# Se você quiser testar as rotas Flask, precisará do cliente de teste do Flask
# from index import app # Já importado acima

@pytest.fixture
def client():
    """Configura um cliente de teste Flask."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@patch('index.generate_response_openai') # Mocka a função de chamada à OpenAI
@patch('index.classify_email_simulated') # Mocka a função de classificação
@patch('index.extract_text_from_pdf') # Mocka a função de extração de PDF
def test_process_email_route_text_input(mock_extract_pdf, mock_classify, mock_generate_response, client):
    """Testa a rota /process_email com entrada de texto."""
    mock_classify.return_value = "Produtivo"
    mock_generate_response.return_value = "Resposta mockada para o teste."
    mock_extract_pdf.return_value = "Conteúdo do PDF mockado." # Não deve ser chamado para texto

    response = client.post('/process_email', json={
        'email_content': 'Este é um email de teste.'
    })

    assert response.status_code == 200
    data = response.get_json()
    assert data['classification'] == 'Produtivo'
    assert data['suggested_response'] == 'Resposta mockada para o teste.'
    mock_classify.assert_called_once_with("este é um email de teste.")
    mock_generate_response.assert_called_once_with("Este é um email de teste.", "Produtivo")
    mock_extract_pdf.assert_not_called() # Garante que não chamou a extração de PDF

@patch('index.generate_response_openai')
@patch('index.classify_email_simulated')
@patch('index.extract_text_from_pdf')
def test_process_email_route_pdf_input(mock_extract_pdf, mock_classify, mock_generate_response, client):
    """Testa a rota /process_email com upload de PDF."""
    mock_extract_pdf.return_value = "Conteúdo do PDF mockado."
    mock_classify.return_value = "Improdutivo"
    mock_generate_response.return_value = "Resposta mockada para o PDF."

    # Cria um arquivo mock para simular o upload
    from io import BytesIO
    mock_pdf_file = BytesIO(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 0>>endobj\nxref\n0 3\n0000000000 65535 f\n0000000009 00000 n\n0000000055 00000 n\ntrailer<</Size 3/Root 1 0 R>>startxref\n104\n%%EOF")

    response = client.post('/process_email', data={
        'email_file': (mock_pdf_file, 'test.pdf')
    }, content_type='multipart/form-data')

    assert response.status_code == 200
    data = response.get_json()
    assert data['classification'] == 'Improdutivo'
    assert data['suggested_response'] == 'Resposta mockada para o PDF.'
    mock_extract_pdf.assert_called_once() # Verifica se a extração de PDF foi chamada
    mock_classify.assert_called_once_with("conteúdo do pdf mockado.")
    mock_generate_response.assert_called_once_with("Conteúdo do PDF mockado.", "Improdutivo")