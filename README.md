# 📧 Classificador de E-mails com IA e Sugestão de Respostas

Este projeto é uma aplicação web simples desenvolvida em **Python (Flask)** que utiliza **Inteligência Artificial** para classificar e-mails em categorias "Produtivo" ou "Improdutivo" e, em seguida, sugerir respostas automáticas personalizadas. A inteligência de geração de respostas é **powered by OpenAI GPT-3.5 Turbo**.

-----

## ✨ **Funcionalidades**

  * **Interface Web Intuitiva:** Um formulário HTML permite o upload de arquivos `.txt` ou `.pdf` ou a inserção direta do conteúdo do e-mail.
  * **Classificação de E-mails:** Categoriza e-mails em:
      * **Produtivo:** E-mails que exigem ação ou resposta (ex: solicitações, dúvidas, suporte técnico).
      * **Improdutivo:** E-mails que não demandam ação imediata (ex: agradecimentos, felicitações).
  * **Geração de Respostas Automáticas Inteligentes:** Utiliza a **API da OpenAI (GPT-3.5 Turbo)** para gerar sugestões de respostas contextuais, fluentes e adequadas à categoria identificada do e-mail, otimizando seu tempo de resposta.
  * **Processamento de Arquivos:** Capacidade de extrair texto de arquivos `.txt` e `.pdf` para análise.
  * **Pré-processamento Básico:** Realiza um pré-processamento simples do texto para normalização antes da análise.

-----

## 🛠️ **Tecnologias Utilizadas**

  * **Backend:**
      * **Python:** Linguagem de programação principal.
      * **Flask:** Microframework web para Python.
      * **OpenAI API:** Principal motor para a **geração de respostas automáticas (GPT-3.5 Turbo)**.
      * **PyPDF2:** Para extração de texto de arquivos PDF.
      * **Gunicorn:** Servidor WSGI utilizado para servir a aplicação Flask em ambiente de produção (Vercel).
      * **python-dotenv:** Para carregamento de variáveis de ambiente em desenvolvimento local.
  * **Frontend:**
      * **HTML:** Estrutura da interface.
      * **CSS:** Estilização básica para uma boa experiência visual.
      * **JavaScript (Fetch API):** Para comunicação assíncrona com o backend e exibição dinâmica dos resultados.
  * **Deploy:**
      * **Vercel:** Plataforma de deploy que hospeda a aplicação como uma *Serverless Function*.

-----

## 🚀 **Como Rodar o Projeto Localmente**

Siga os passos abaixo para configurar e executar a aplicação em sua máquina.

### **Pré-requisitos**

  * **Python 3.8+** (Recomenda-se Python 3.10 para compatibilidade com Vercel)
  * **Git**
  * **Chave de API da OpenAI:** Essencial para a funcionalidade de geração de respostas. Obtenha uma em [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys).

### **Passos para Configuração**

1.  **Clone o repositório:**

    ```bash
    git clone https://github.com/SEU_USUARIO_GITHUB/SEU_REPOSITORIO.git
    cd SEU_REPOSITORIO
    ```

    (Substitua `SEU_USUARIO_GITHUB` e `SEU_REPOSITORIO` pelos seus dados reais do GitHub).

2.  **Crie e ative um ambiente virtual (altamente recomendado):**

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

    Crie um arquivo chamado `.env` na **raiz do projeto** (na mesma pasta de `vercel.json`) com o seguinte conteúdo:

    ```
    OPENAI_API_KEY="sua_chave_secreta_da_openai_aqui"
    ```

    **Importante:** Substitua `"sua_chave_secreta_da_openai_aqui"` pela sua chave real da OpenAI. **Garanta que o arquivo `.env` esteja listado no seu `.gitignore` para evitar que sua chave seja enviada para o repositório público\!**

5.  **Execute a aplicação Flask:**

    ```bash
    python api/index.py
    ```

6.  **Acesse a aplicação:**
    Abra seu navegador e acesse: `http://127.0.0.1:5000/`

-----

## ☁️ **Deploy na Vercel**

Esta aplicação está configurada para ser facilmente implantada na Vercel como uma *Serverless Function*.

### **Estrutura de Pastas para Deploy**

Para que a Vercel detecte e faça o deploy corretamente, o código Flask principal foi movido para `api/index.py`, e os arquivos de template e estáticos são referenciados de lá. A estrutura esperada é:

```
seu_projeto/
├── api/
│   └── index.py  # Ponto de entrada da aplicação Flask na Vercel
├── templates/
│   └── index.html
├── static/
│   └── style.css
├── requirements.txt
├── vercel.json     # Configurações de build e rotas da Vercel
└── .gitignore
```

### **Passos para o Deploy na Vercel**

1.  **Crie uma Conta Vercel:** Se ainda não tiver, registre-se em [vercel.com](https://vercel.com/).

2.  **Conecte seu Repositório Git:** No painel da Vercel, importe seu repositório GitHub.

3.  **Configure as Variáveis de Ambiente:** Durante a configuração do projeto na Vercel, vá em "Environment Variables" e adicione:

      * **Name:** `OPENAI_API_KEY`
      * **Value:** `SUA_CHAVE_SECRETA_DA_OPENAI_AQUI`
      * Esta etapa é **CRÍTICA** para que a funcionalidade da OpenAI funcione em produção, pois a Vercel não lê o arquivo `.env`.

4.  **Configure as Regras de Build e Rotas:** O arquivo `vercel.json` na raiz do seu projeto já contém as configurações necessárias para a Vercel construir o projeto Python, servir os arquivos estáticos e rotear as requisições para a *serverless function* Flask.

    ```json
    {
      "version": 2,
      "builds": [
        {
          "src": "api/index.py",
          "use": "@vercel/python",
          "config": {
            "maxLambdaSize": "15mb",
            "runtime": "python3.10"
          }
        },
        {
          "src": "index.html",
          "use": "@vercel/static"
        },
        {
          "src": "static/**",
          "use": "@vercel/static"
        }
      ],
      "routes": [
        {
          "src": "/static/(.*)",
          "dest": "/static/$1"
        },
        {
          "src": "/(.*)",
          "dest": "/api/index.py"
        }
      ],
      "installCommand": "pip install -r requirements.txt"
    }
    ```

5.  **Inicie o Deploy:** Após configurar as variáveis de ambiente, clique em "Deploy". A Vercel fará o restante, e você receberá uma URL para sua aplicação online quando o processo for concluído.

-----

## 💡 **Como Funciona a Classificação e Resposta Detalhadamente**

  * **Classificação (Simulada):** Atualmente, a categorização entre "Produtivo" e "Improdutivo" é baseada na detecção de palavras-chave predefinidas no conteúdo do e-mail (ex: "solicitação", "dúvida", "suporte" indicam um e-mail "Produtivo"). Embora eficaz para demonstração, esta abordagem pode ser expandida com um modelo de NLP treinado para maior precisão em cenários reais.
  * **Geração de Resposta (OpenAI - GPT-3.5 Turbo):**
    1.  O conteúdo do e-mail e sua categoria (Produtivo/Improdutivo) são enviados como parte de um **prompt** estruturado para a API da OpenAI.
    2.  Modelos como o `gpt-3.5-turbo` analisam o prompt e o contexto do e-mail.
    3.  Com base em instruções claras no prompt (ex: "seja formal e conciso para emails produtivos", "seja curto e cordial para improdutivos"), a OpenAI gera uma sugestão de resposta que é então exibida na interface web.
    4.  A API é configurada para otimizar o comprimento e o tom da resposta, fornecendo um ponto de partida útil para o usuário.

-----

## ⏭️ **Próximos Passos e Melhorias Potenciais**

  * **Classificação Aprimorada:** Treinar um modelo de classificação de texto (ex: com Hugging Face Transformers) utilizando um dataset real de e-mails rotulados para alcançar maior precisão e robustez na categorização.
  * **Pré-processamento Avançado:** Integrar bibliotecas de NLP como `NLTK` ou `SpaCy` para um pré-processamento mais sofisticado do texto (remoção de *stopwords*, lematização/stemming, reconhecimento de entidades nomeadas), o que pode melhorar a performance dos modelos de IA.
  * **Interface do Usuário (UX):**
      * Adicionar funcionalidade de arrastar e soltar arquivos para um upload mais fluido.
      * Melhorar o feedback visual ao usuário durante o processamento (ex: barra de progresso mais detalhada).
      * Implementar um histórico de e-mails processados e suas respectivas respostas.
  * **Personalização:** Permitir que o usuário defina ou ajuste palavras-chave e regras de classificação, ou personalize os prompts de resposta para a OpenAI.
  * **Integração com Contas de E-mail:** Desenvolver funcionalidades para que a aplicação possa ler e-mails diretamente de uma caixa de entrada (ex: Gmail, Outlook) após a devida autenticação e autorização.
  * **Autenticação e Segurança:** Para um ambiente de produção mais robusto, adicionar um sistema de autenticação de usuário e implementar medidas de segurança adicionais para a API e os dados.

-----

## 🤝 **Contribuição**

Sinta-se à vontade para contribuir com este projeto\!

1.  Faça um *fork* do repositório.
2.  Crie uma *branch* para sua funcionalidade (`git checkout -b minha-nova-funcionalidade`).
3.  Faça suas alterações e *commit* (`git commit -m 'Adiciona nova funcionalidade X'`).
4.  Envie para sua *branch* (`git push origin minha-nova-funcionalidade`).
5.  Abra um *Pull Request* detalhando suas mudanças.

-----

## 📄 **Licença**

Este projeto está sob a licença [MIT License](https://www.google.com/search?q=LICENSE).

-----
