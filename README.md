# ☁️ SkillBridge AI (100% Cloud – OpenAI)

API em **FastAPI** que roda **100% na nuvem** usando **OpenAI** para gerar conteúdo profissional
em **HTML pronto para WebView ou navegador**, focado em:

- **Planos de requalificação / carreira**;
- **Currículos profissionais em HTML** a partir de dados brutos;
- **Currículos DEMO** (perfis fictícios) para testes e demonstrações;
- **Explicações humanizadas** em tom de coach/mentor sobre planos e decisões de carreira.

Nenhum modelo local é necessário: toda a inteligência vem da API da OpenAI.

---

## 🎯 Visão geral da arquitetura

Esta API segue um fluxo simples e poderoso:

1. O cliente (mobile ou web) envia um **JSON** com as informações principais (perfil, dados do currículo ou contexto);
2. A API chama a **OpenAI** com prompts bem estruturados, pedindo **respostas em formato estrito** (Markdown ou JSON);
3. Quando necessário, a resposta em JSON é carregada em modelos Pydantic internos e convertida para um objeto de domínio
   (por exemplo, `CvStructured`);
4. Esse objeto é convertido em **Markdown semântico** (títulos, listas, seções);
5. O Markdown é renderizado em um **HTML moderno e pronto para impressão / WebView**, com estilos CSS embutidos.

Resultado: o front-end não precisa se preocupar com layout do plano/currículo/explicação,
basta abrir o HTML retornado em uma WebView ou aba do navegador.

---

## 📁 Endpoints principais

A API expõe os seguintes endpoints:

### `POST /gen/plan` – Plano de requalificação em HTML

Gera um **plano de requalificação / desenvolvimento de carreira** a partir de:

- Soft skills atuais;
- Hard skills atuais;
- Objetivo profissional;
- Horas disponíveis por semana;
- Idioma desejado (ex.: `pt-BR`, `en-US`).

O retorno é um **HTML completo**, ideal para ser exibido em uma WebView.

---

### `POST /gen/cv/html` – Currículo em HTML com dados reais

Recebe um corpo JSON com:

- `idioma`: idioma desejado do currículo (ex.: `pt-BR`);
- `dados`: objeto livre contendo nome, idade, contatos, escolaridade, skills, etc.

A API:

1. Usa a OpenAI para transformar `dados` em um currículo **estruturado** (`CvStructured`);
2. Constrói um currículo em **Markdown** a partir desse modelo;
3. Converte o Markdown para **HTML responsivo**, com tipografia e estilo prontos para impressão/WebView.

Esse é o endpoint principal para o app SkillBridge Mobile.

---

### `POST /gen/cv/html/demo` – Currículo DEMO em HTML

Gera um currículo **exemplo (fictício)**, útil para:

- Testar o fluxo do app sem depender de dados reais;
- Validar templates de WebView;
- Apresentar demonstrações da funcionalidade.

Parâmetros principais:

- `idioma`: idioma do currículo de exemplo (ex.: `pt-BR`);
- `tipoPerfil`: tipo do perfil fictício (ex.: `primeiro_emprego`, `estudante`, `profissional_experiente`).

Internamente, o endpoint monta um conjunto de dados base de exemplo,
passa pelo mesmo fluxo de geração estruturada e retorna o HTML final.

---

### `POST /gen/explain/html` – Explicação humanizada em HTML

Recebe um JSON com:

- `idioma`: idioma desejado (ex.: `pt-BR`);
- `contexto`: objeto livre com informações sobre o plano/decisão (tipo, resumo, perfil etc.).

A API pede para a OpenAI agir como um **coach empático**, retornando:

- Uma explicação em linguagem acessível;
- Sugestões práticas (ex.: 3 ações concretas).

Em seguida, a explicação é incorporada em um pequeno Markdown e convertida para **HTML**
com título e formatação amigável.

---

### `GET /health` – Healthcheck simples

Retorna um JSON com o status básico da API:

```json
{
  "status": "ok",
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

Útil para verificações de disponibilidade e automação de monitoramento.

---

## 🔧 Tecnologias utilizadas

- **Python 3.10+** (recomendado);
- **FastAPI** – framework web;
- **Uvicorn** – servidor ASGI para subir a API;
- **Pydantic** – modelos de entrada/saída e validações;
- **python-dotenv** – leitura do arquivo `.env` para carregar variáveis de ambiente;
- **OpenAI Python SDK** – comunicação com a API da OpenAI;
- **markdown2** – conversão de Markdown para HTML.

---

## ✅ Como rodar o projeto localmente

### 1. Criar e ativar o ambiente virtual

Na raiz do projeto (onde está o `main.py`):

```bash
python -m venv .venv

# Linux / Mac
. .venv/bin/activate

# Windows (PowerShell)
# .venv\Scripts\Activate.ps1
```

---

### 2. Instalar as dependências

Se houver um `requirements.txt`, use:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Ou, instalando os pacotes principais manualmente:

```bash
pip install fastapi uvicorn python-dotenv openai markdown2
```

> Outros pacotes (como `pydantic`) são trazidos automaticamente com o FastAPI.

---

### 3. Configurar variáveis de ambiente (.env)

Crie um arquivo `.env` na **mesma pasta do `main.py`** com:

```env
OPENAI_API_KEY=sk-xxxxxx_sua_chave_aqui
OPENAI_MODEL=gpt-4o-mini
```

- `OPENAI_API_KEY` é **obrigatório**. Se não estiver definido, a aplicação levanta um `RuntimeError` na inicialização.
- `OPENAI_MODEL` é opcional; se não informado, o código usa `gpt-4o-mini` como padrão.

---

### 4. Subir o servidor FastAPI com Uvicorn

Ainda na raiz do projeto:

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

A API ficará disponível em:

- Documentação interativa (Swagger UI): <http://localhost:8080/docs>
- Healthcheck: <http://localhost:8080/health>

---

## 🧪 Exemplos de uso (curl)

Os exemplos abaixo usam `curl`.  
No **Windows PowerShell**, lembre-se de trocar aspas simples `'` por aspas duplas `"` e ajustar escapes se necessário.

---

### 1️⃣ Healthcheck – `GET /health`

```bash
curl http://localhost:8080/health
```

Resposta esperada (exemplo):

```json
{
  "status": "ok",
  "provider": "openai",
  "model": "gpt-4o-mini"
}
```

---

### 2️⃣ Gerar plano de requalificação em HTML – `POST /gen/plan`

Exemplo de requisição, salvando o HTML em arquivo:

```bash
curl -s -X POST "http://localhost:8080/gen/plan"       -H "Content-Type: application/json"       -d '{
    "perfil": {
      "softSkills": ["comunicação", "organização"],
      "hardSkills": ["Excel", "SQL básico"],
      "objetivo": "Migrar para análise de dados",
      "disponibilidadeSemanalHoras": 8
    },
    "idioma": "pt-BR"
  }' > plano.html
```

Depois, abra `plano.html` no navegador ou em uma WebView.

---

### 3️⃣ Gerar currículo HTML com dados reais – `POST /gen/cv/html`

```bash
curl -s -X POST "http://localhost:8080/gen/cv/html"       -H "Content-Type: application/json"       -d '{
    "idioma": "pt-BR",
    "dados": {
      "nome": "Gabrielly Rodrigues de Almeida",
      "idade": 17,
      "titulo": "Estudante em busca do primeiro emprego",
      "resumo": "Estudante dedicada, com boa comunicação e vontade de aprender.",
      "contatos": {
        "email": "gabrielly@example.com",
        "telefone": "(11) 98928-4959",
        "cidade": "São Paulo",
        "estado": "SP",
        "pais": "Brasil"
      },
      "escolaridade": [
        {
          "curso": "Ensino Médio",
          "instituicao": "E.E. Imâncio Montero",
          "inicio": "2023",
          "fim": "2025",
          "status": "Cursando"
        }
      ],
      "softSkills": ["responsabilidade", "organização"],
      "hardSkills": ["informática básica (Word, Excel, Internet)"],
      "idiomas": ["Português (nativo)"],
      "interesses": ["Administração", "Atendimento ao cliente"]
    }
  }' > curriculo.html
```

Abra o arquivo `curriculo.html` no navegador para ver o currículo pronto.

> Caso `dados` esteja vazio ou não contenha pelo menos o campo `nome`, a API retorna um erro 400,
> pois o nome é obrigatório para montar o currículo.

---

### 4️⃣ Gerar currículo HTML DEMO – `POST /gen/cv/html/demo`

```bash
curl -s -X POST "http://localhost:8080/gen/cv/html/demo"       -H "Content-Type: application/json"       -d '{
    "idioma": "pt-BR",
    "tipoPerfil": "primeiro_emprego"
  }' > curriculo_demo.html
```

Depois, é só abrir `curriculo_demo.html` no navegador.

Esse endpoint é ideal para:

- Telas de demonstração;
- Ambientes de teste;
- Validar layout sem expor dados reais de usuários.

---

### 5️⃣ Gerar explicação humanizada em HTML – `POST /gen/explain/html`

```bash
curl -s -X POST "http://localhost:8080/gen/explain/html"       -H "Content-Type: application/json"       -d '{
    "idioma": "pt-BR",
    "contexto": {
      "tipo": "plano_requalificacao",
      "resumo": "Plano foca em lógica de programação e desenvolvimento web.",
      "perfil": {
        "nome": "Rafael",
        "objetivo": "Migrar de suporte técnico para desenvolvimento de software."
      }
    }
  }' > explicacao.html
```

Abra `explicacao.html` no navegador para visualizar o texto gerado em tom de coach,
com explicações e ações práticas sugeridas.

---

## 🔐 Boas práticas de uso

- **Não commitar** sua `OPENAI_API_KEY` em repositórios públicos;
- Se for enviar dados sensíveis (nomes reais, histórico de trabalho), considere:
  - Anonimizar parte dos campos;
  - Restringir o acesso à API e ao repositório;
- Monitorar:
  - **Consumo de tokens** na OpenAI;
  - **Latência** das respostas;
- Para uso em produção, recomenda-se:
  - Logs estruturados (JSON);
  - Monitoramento de erros e tempo de resposta;
  - Rate limiting e autenticação em cima desta API, se exposta externamente.

---

## ✅ Resumo

- Projeto: **SkillBridge AI (100% Cloud – OpenAI)**;
- Objetivo: gerar **HTML pronto** para planos, currículos e explicações;
- Entradas: **JSON simples** (perfil, dados de currículo, contexto);
- Saídas: **HTML bem formatado**, pronto para WebView ou navegador;
- Sem OCR, sem upload de arquivos, sem manipulação de imagens ou PDFs;
- Perfeito para integrar com o **SkillBridge Mobile** e outras aplicações web
  que precisam de conteúdo de carreira gerado por IA, com baixo acoplamento no front-end.
