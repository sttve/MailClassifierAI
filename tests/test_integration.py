import pytest
from unittest.mock import patch, MagicMock
import os
import sys
from io import BytesIO
import json  # Para lidar com JSON nas respostas

# Ajusta o sys.path para que possamos importar de 'api'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../api')))

# Importa a instância 'app' do Flask do seu arquivo 'index.py'
# E as outras funções que serão mockadas
from index import app, preprocess_text, classify_email_simulated, generate_openai_response


# --- Fixture para o Cliente de Teste Flask ---
@pytest.fixture
def client():
    """
    Configura um cliente de teste Flask para cada teste.
    Define o modo de teste para desabilitar erros de stack trace
    e outras configurações de produção.
    """
    app.config['TESTING'] = True
    # O cliente de teste é um context manager, então usamos 'with'
    with app.test_client() as client:
        yield client  # Retorna o cliente para o teste usar


# --- Teste da Rota Inicial (/) ---
def test_index_route(client):
    """
    Verifica se a rota raiz (/) carrega a página HTML corretamente.
    """
    response = client.get('/')
    assert response.status_code == 200
    assert b"An\xc3\xa1lise de E-mails Inteligente" in response.data  # Verifica uma parte do título HTML com acento
    assert b"Classificar e Sugerir Resposta" in response.data  # Verifica texto do botão


# --- Testes da Rota /process_email ---

# Usaremos @patch para simular o comportamento de funções internas
# e de módulos externos, como a OpenAI ou a leitura de PDF.
# Isso garante que estamos testando APENAS a lógica da rota,
# e não a dependência externa real (que seria testada em seus próprios unitários ou de integração específicos).

@patch('index.generate_openai_response')  # Simula a chamada à OpenAI
@patch('index.classify_email_simulated')  # Simula a classificação
@patch('index.PyPDF2.PdfReader')  # Simula a leitura de PDF
def test_process_email_route_with_text_input(mock_pdf_reader, mock_classify_email, mock_generate_response, client):
    """
    Testa a rota /process_email quando um texto de e-mail é fornecido.
    Verifica se as funções internas são chamadas corretamente e a resposta é válida.
    """
    # Define o que as funções mockadas devem retornar
    mock_classify_email.return_value = "Produtivo"
    mock_generate_response.return_value = "Sua solicitação está sendo analisada. Em breve retornaremos."

    email_test_content = "Olá, preciso de ajuda com o meu pedido #12345. Ele não chegou."

    # Faz a requisição POST simulada com dados de formulário (form)
    # Note que usamos 'data' e 'content_type' para simular um formulário HTML normal
    response = client.post('/process_email', data={
        'email_text': email_test_content
    })

    # Verifica o status HTTP da resposta
    assert response.status_code == 200

    # Converte a resposta JSON para um dicionário Python
    response_data = json.loads(response.data)

    # Verifica os dados no JSON da resposta
    assert response_data['category'] == "Produtivo"
    assert response_data['suggested_response'] == "Sua solicitação está sendo analisada. Em breve retornaremos."

    # Verifica se as funções internas foram chamadas conforme o esperado
    # Lembre-se que preprocess_text é chamada DENTRO de classify_email_simulated
    mock_classify_email.assert_called_once_with(preprocess_text(email_test_content))
    mock_generate_response.assert_called_once_with("Produtivo", email_test_content)
    # Assegura que PyPDF2 não foi chamado
    mock_pdf_reader.assert_not_called()


@patch('index.generate_openai_response')
@patch('index.classify_email_simulated')
@patch('index.PyPDF2.PdfReader')
def test_process_email_route_with_pdf_upload(mock_pdf_reader, mock_classify_email, mock_generate_response, client):
    """
    Testa a rota /process_email quando um arquivo PDF é enviado.
    Simula a leitura do PDF e o fluxo de classificação/geração.
    """
    # Configura o mock do PdfReader para simular a extração de texto
    # Note que a mock_pdf_reader é a CLASSE, então precisamos mockar seu retorno de instância
    mock_pdf_instance = MagicMock()
    mock_pdf_reader.return_value = mock_pdf_instance
    mock_pdf_instance.pages = [MagicMock(), MagicMock()]  # Simula duas páginas
    mock_pdf_instance.pages[0].extract_text.return_value = "Conteúdo da primeira página."
    mock_pdf_instance.pages[
        1].extract_text.return_value = " Conteúdo da segunda página."  # Com espaço para testar strip no preprocess

    mock_classify_email.return_value = "Improdutivo"
    mock_generate_response.return_value = "Agradecemos o contato!"

    # Crie um arquivo BytesIO para simular um arquivo real
    # O conteúdo real não importa muito aqui, pois mockamos a leitura interna do PyPDF2
    dummy_pdf_file = BytesIO(b"dummy pdf content")
    dummy_pdf_file.name = 'test_email.pdf'  # Importante ter um nome de arquivo

    response = client.post(
        '/process_email',
        data={
            'file': (dummy_pdf_file, 'test_email.pdf')  # (conteúdo, nome do arquivo)
        },
        content_type='multipart/form-data'  # Tipo de conteúdo para upload de arquivo
    )

    assert response.status_code == 200
    response_data = json.loads(response.data)

    assert response_data['category'] == "Improdutivo"
    assert response_data['suggested_response'] == "Agradecemos o contato!"

    # Verifica se PyPDF2.PdfReader foi chamado e extraiu o texto
    mock_pdf_reader.assert_called_once()
    mock_pdf_instance.pages[0].extract_text.assert_called_once()
    mock_pdf_instance.pages[1].extract_text.assert_called_once()

    # Verifica se as funções de classificação e geração foram chamadas com o texto concatenado
    expected_full_pdf_text = "Conteúdo da primeira página. Conteúdo da segunda página."
    mock_classify_email.assert_called_once_with(preprocess_text(expected_full_pdf_text))
    mock_generate_response.assert_called_once_with("Improdutivo", expected_full_pdf_text)


@patch('index.generate_openai_response')
@patch('index.classify_email_simulated')
def test_process_email_route_no_input(mock_classify_email, mock_generate_response, client):
    """
    Testa a rota /process_email sem fornecer entrada de e-mail.
    Deve retornar um erro 400.
    """
    response = client.post('/process_email', data={})  # Requisição vazia

    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert "Nenhum arquivo ou texto foi fornecido." in response_data['error']

    # Garante que as funções de processamento não foram chamadas
    mock_classify_email.assert_not_called()
    mock_generate_response.assert_not_called()


@patch('index.generate_openai_response')
@patch('index.classify_email_simulated')
def test_process_email_route_empty_content(mock_classify_email, mock_generate_response, client):
    """
    Testa a rota /process_email com conteúdo de e-mail vazio (apenas espaços).
    """
    response = client.post('/process_email', data={'email_text': '   '})

    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert "O conteúdo do email está vazio." in response_data['error']

    mock_classify_email.assert_not_called()
    mock_generate_response.assert_not_called()


@patch('index.generate_openai_response')
@patch('index.classify_email_simulated')
def test_process_email_route_unsupported_file_type(mock_classify_email, mock_generate_response, client):
    """
    Testa o envio de um tipo de arquivo não suportado (ex: .jpg).
    """
    dummy_image_file = BytesIO(b"dummy image content")
    dummy_image_file.name = 'test_image.jpg'

    response = client.post(
        '/process_email',
        data={
            'file': (dummy_image_file, 'test_image.jpg')
        },
        content_type='multipart/form-data'
    )

    assert response.status_code == 400
    response_data = json.loads(response.data)
    assert "error" in response_data
    assert "Formato de arquivo não suportado. Use .txt ou .pdf." in response_data['error']

    mock_classify_email.assert_not_called()
    mock_generate_response.assert_not_called()

# Você pode adicionar mais testes de integração, como:
# - Testar a rota /process_email com upload de TXT
# - Testar cenários de erro na leitura de PDF (se PyPDF2 levantar exceção)
# - Testar cenários de erro na chamada à OpenAI (já coberto no unitário, mas pode ser verificado aqui se a rota lida bem com isso)