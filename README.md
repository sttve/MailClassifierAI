# 📧 Classificador de E-mails com IA e Sugestão de Respostas

Este projeto é uma aplicação web simples desenvolvida em **Python (Flask)** que utiliza **Inteligência Artificial** para classificar e-mails em categorias "Produtivo" ou "Improdutivo" e, em seguida, sugerir respostas automáticas personalizadas. A inteligência de geração de respostas é powered by **OpenAI GPT-3.5 Turbo**.

---

## ✨ **Funcionalidades**

* **Interface Web Intuitiva:** Um formulário HTML permite o upload de arquivos `.txt` ou `.pdf` ou a inserção direta do conteúdo do e-mail.
* **Classificação de E-mails:** Categoriza e-mails em:
    * **Produtivo:** E-mails que exigem ação ou resposta (ex: solicitações, dúvidas, suporte técnico).
    * **Improdutivo:** E-mails que não demandam ação imediata (ex: agradecimentos, felicitações).
* **Geração de Respostas Automáticas:** Utiliza a API da **OpenAI (GPT-3.5 Turbo)** para gerar sugestões de respostas contextuais e adequadas à categoria do e-mail.
* **Pré-processamento Básico:** Realiza um pré-processamento simples do texto para normalização.

---

## 🛠️ **Tecnologias Utilizadas**

* **Backend:**
    * **Python:** Linguagem de programação principal.
    * **Flask:** Microframework web para Python.
    * **OpenAI API:** Para a geração de respostas automáticas (GPT-3.5 Turbo).
    * **PyPDF2:** Para extração de texto de arquivos PDF.
    * **Hugging Face Transformers (Opcional/Simulado):** Mencionado como opção para classificação ou modelos menores de geração, mas para este projeto a classificação é simplificada e a geração é via OpenAI.
* **Frontend:**
    * **HTML:** Estrutura da interface.
    * **CSS:** Estilização básica.
    * **JavaScript (Fetch API):** Para comunicação assíncrona com o backend.

---

## 🚀 **Como Rodar o Projeto Localmente**

Siga os passos abaixo para configurar e executar a aplicação em sua máquina.

### **Pré-requisitos**

* **Python 3.8+**
* **Git**
* **Chave de API da OpenAI:** Você precisará de uma chave válida para usar a funcionalidade de geração de respostas. Obtenha uma em [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### **Passos para Configuração**

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/SEU_USUARIO_GITHUB/SEU_REPOSITORIO.git](https://github.com/SEU_USUARIO_GITHUB/SEU_REPOSITORIO.git)
    cd SEU_REPOSITORIO
    ```
    (Substitua `SEU_USUARIO_GITHUB` e `SEU_REPOSITORIO` pelos seus dados).

2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows:
    .\venv\Scripts\activate
    # No macOS/Linux:
    source venv/bin/activate
    ```

3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure sua chave de API da OpenAI:**

    **Opção A: Variável de Ambiente (Recomendado para produção ou execução única)**
    * **No Linux/macOS:**
        ```bash
        export OPENAI_API_KEY="sua_chave_secreta_aqui"
        ```
    * **No Windows (CMD):**
        ```cmd
        set OPENAI_API_KEY=sua_chave_secreta_aqui
        ```
    * **No Windows (PowerShell):**
        ```powershell
        $env:OPENAI_API_KEY="sua_chave_secreta_aqui"
        ```
    Substitua `"sua_chave_secreta_aqui"` pela sua chave real da OpenAI.

    **Opção B: Arquivo `.env` (Recomendado para desenvolvimento local)**
    Crie um arquivo chamado `.env` na raiz do projeto (na mesma pasta de `app.py`) com o seguinte conteúdo:
    ```
    OPENAI_API_KEY="sua_chave_secreta_aqui"
    ```
    **Certifique-se de que o `.env` está no `.gitignore` para evitar que sua chave seja versionada!**

5.  **Execute a aplicação Flask:**
    ```bash
    python app.py
    ```

6.  **Acesse a aplicação:**
    Abra seu navegador e acesse: `http://127.0.0.1:5000/`

---

## 💡 **Como Funciona a Classificação e Resposta**

* **Classificação (Simulada):** Para simplificar o desafio, a categorização entre "Produtivo" e "Improdutivo" é baseada na presença de palavras-chave predefinidas no conteúdo do e-mail (ex: "solicitação", "dúvida" para produtivo). Em uma aplicação real, um modelo de NLP treinado seria utilizado para maior precisão.
* **Geração de Resposta (OpenAI):** Após a classificação, um `prompt` específico é enviado à API `gpt-3.5-turbo` da OpenAI, instruindo-a a gerar uma resposta adequada ao contexto e à categoria identificada. Prompts diferentes são usados para e-mails "Produtivos" (solicitando análise/retorno) e "Improdutivos" (apenas agradecimento).

---

## ⏭️ **Próximos Passos e Melhorias Potenciais**

* **Classificação Aprimorada:** Treinar um modelo de classificação de texto (ex: com Hugging Face Transformers) com um dataset real de e-mails rotulados para maior precisão.
* **Pré-processamento Avançado:** Integrar bibliotecas como `NLTK` ou `SpaCy` para remoção de *stopwords*, lematização/stemming, reconhecimento de entidades nomeadas, etc.
* **Interface do Usuário (UX):**
    * Adicionar funcionalidade de arrastar e soltar arquivos.
    * Melhorar o feedback visual durante o processamento.
    * Implementar um histórico de e-mails processados.
* **Personalização:** Permitir que o usuário defina regras ou adicione palavras-chave personalizadas para classificação.
* **Integração com Contas de E-mail:** Desenvolver funcionalidades para ler e-mails diretamente de uma caixa de entrada (ex: Gmail, Outlook) após autenticação.
* **Autenticação e Segurança:** Para um ambiente de produção, adicionar autenticação de usuário e outras medidas de segurança.

---

## 🤝 **Contribuição**

Sinta-se à vontade para contribuir com este projeto!

1.  Faça um *fork* do repositório.
2.  Crie uma *branch* para sua funcionalidade (`git checkout -b minha-nova-funcionalidade`).
3.  Faça suas alterações e *commit* (`git commit -m 'Adiciona nova funcionalidade X'`).
4.  Envie para sua *branch* (`git push origin minha-nova-funcionalidade`).
5.  Abra um *Pull Request*.

---

## 📄 **Licença**

Este projeto está sob a licença [MIT License](LICENSE).