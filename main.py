import os
import re
import logging
from typing import List, Optional, Dict, Any

from dotenv import load_dotenv  # para ler o .env

from fastapi import (
    FastAPI,
    HTTPException,
)
from fastapi.responses import HTMLResponse

from pydantic import BaseModel, Field

# OpenAI (cloud)
from openai import OpenAI

# ================= Config =================

# Carrega variáveis do arquivo .env (na mesma pasta do main.py)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

if not OPENAI_API_KEY:
    raise RuntimeError("Defina OPENAI_API_KEY no ambiente (.env).")

# Logger padrão do Uvicorn
logger = logging.getLogger("uvicorn.error")

client = OpenAI(api_key=OPENAI_API_KEY)

app = FastAPI(
    title="SkillBridge AI (100% Cloud – OpenAI)",
    version="2.2.0",
    description="API em nuvem usando OpenAI para IA Generativa."
)

# ================= Models =================


class Perfil(BaseModel):
    softSkills: List[str] = Field(
        default_factory=list,
        description="Soft skills principais da pessoa (comunicação, organização, etc.)",
    )
    hardSkills: List[str] = Field(
        default_factory=list,
        description="Hard skills atuais (lógica, Excel, programação, etc.).",
    )
    objetivo: Optional[str] = Field(
        default="não informado",
        description="Objetivo profissional (ex.: conseguir primeiro emprego em TI).",
    )
    disponibilidadeSemanalHoras: Optional[int] = Field(
        default=4,
        description="Horas disponíveis por semana para estudar/desenvolver carreira.",
    )


class PlanRequest(BaseModel):
    perfil: Perfil
    idioma: Optional[str] = Field(
        default="pt-BR",
        description="Idioma do plano gerado (ex.: pt-BR, en-US).",
    )

    class Config:
        schema_extra = {
            "example": {
                "perfil": {
                    "softSkills": [
                        "comunicação",
                        "organização",
                        "vontade de aprender"
                    ],
                    "hardSkills": [
                        "informática básica",
                        "lógica de programação",
                        "HTML e CSS básicos"
                    ],
                    "objetivo": "Conseguir o primeiro emprego na área de tecnologia como estagiário.",
                    "disponibilidadeSemanalHoras": 10
                },
                "idioma": "pt-BR"
            }
        }


class CvRequest(BaseModel):
    dados: Dict[str, Any] = Field(
        description="Dados brutos do currículo (nome, idade, contatos, experiências, etc.)."
    )
    idioma: Optional[str] = Field(
        default="pt-BR",
        description="Idioma do currículo gerado (ex.: pt-BR, en-US).",
    )

    class Config:
        schema_extra = {
            "example": {
                "idioma": "pt-BR",
                "dados": {
                    "nome": "Gabrielly Rodrigues de Almeida",
                    "idade": 17,
                    "titulo": "Estudante de Ensino Médio em busca do primeiro emprego",
                    "resumo": "Estudante dedicada, com boa comunicação e vontade de aprender, buscando oportunidade como jovem aprendiz ou auxiliar administrativo.",
                    "contatos": {
                        "email": "gabrielly@example.com",
                        "telefone": "(11) 98928-4959",
                        "cidade": "São Paulo",
                        "estado": "SP",
                        "pais": "Brasil",
                        "linkedin": "https://linkedin.com/in/gabrielly-rodrigues"
                    },
                    "experiencias": [],
                    "escolaridade": [
                        {
                            "curso": "Ensino Médio",
                            "instituicao": "E.E. Imâncio Montero",
                            "inicio": "2023",
                            "fim": "2025",
                            "status": "Cursando",
                            "destaque": "Participação em projetos escolares e feiras de ciências."
                        }
                    ],
                    "softSkills": [
                        "responsabilidade",
                        "organização",
                        "trabalho em equipe"
                    ],
                    "hardSkills": [
                        "informática básica (Word, Excel, Internet)",
                        "digitação",
                        "atendimento ao público"
                    ],
                    "idiomas": ["Português (nativo)"],
                    "interesses": [
                        "Administração",
                        "Atendimento ao cliente",
                        "Tecnologia"
                    ],
                    "disponbilidade": "Período da tarde",
                    "pretensao": "Primeira oportunidade profissional (jovem aprendiz/auxiliar)."
                }
            }
        }


class ExplainRequest(BaseModel):
    contexto: Dict[str, Any]
    idioma: Optional[str] = "pt-BR"

    class Config:
        schema_extra = {
            "example": {
                "idioma": "pt-BR",
                "contexto": {
                    "tipo": "plano_requalificacao",
                    "resumo": "Plano foca em lógica de programação, fundamentos web e hábitos de estudo diários.",
                    "perfil": {
                        "nome": "Rafael",
                        "objetivo": "Migrar de atendimento ao cliente para área de desenvolvimento de software."
                    }
                }
            }
        }


# ---------- MODELOS CV ESTRUTURADO ----------

class CvContato(BaseModel):
    email: Optional[str] = None
    telefone: Optional[str] = None
    linkedin: Optional[str] = None
    github: Optional[str] = None
    site: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    pais: Optional[str] = None


class CvExperiencia(BaseModel):
    cargo: str
    empresa: str
    inicio: str
    fim: Optional[str] = "Atual"
    local: Optional[str] = None
    responsabilidades: List[str] = Field(default_factory=list)
    conquistas: List[str] = Field(default_factory=list)


class CvEducacao(BaseModel):
    curso: str
    instituicao: str
    inicio: str
    fim: Optional[str] = None
    status: Optional[str] = None  # Concluído/Cursando
    destaque: Optional[str] = None


class CvCertificacao(BaseModel):
    nome: str
    orgao: Optional[str] = None
    ano: Optional[str] = None
    id_credencial: Optional[str] = None
    url_credencial: Optional[str] = None


class CvProjeto(BaseModel):
    nome: str
    descricao: Optional[str] = None
    stack: List[str] = Field(default_factory=list)
    link: Optional[str] = None
    impacto: Optional[str] = None


class CvStructured(BaseModel):
    nome: str
    idade: int
    titulo: Optional[str] = None
    resumo: str
    contatos: CvContato = Field(default_factory=CvContato)

    experiencias: List[CvExperiencia] = Field(min_items=1)
    escolaridade: List[CvEducacao] = Field(min_items=1)

    objetivo: Optional[str] = None
    softSkills: List[str] = Field(default_factory=list)
    hardSkills: List[str] = Field(default_factory=list)
    idiomas: List[str] = Field(default_factory=list)
    certificacoes: List[CvCertificacao] = Field(default_factory=list)
    projetos: List[CvProjeto] = Field(default_factory=list)
    interesses: List[str] = Field(default_factory=list)
    disponbilidade: Optional[str] = None
    pretensao: Optional[str] = None


class CvStructuredResponse(BaseModel):
    cv: CvStructured
    modelo: str


class DemoCvRequest(BaseModel):
    """
    Body da versão DEMO (currículo exemplo / aleatório).
    """
    idioma: Optional[str] = Field(
        default="pt-BR",
        description="Idioma do currículo exemplo (ex.: pt-BR, en-US).",
    )
    tipoPerfil: Optional[str] = Field(
        default="profissional_experiente",
        description="Tipo de perfil de exemplo: 'primeiro_emprego', 'estudante', 'profissional_experiente'.",
    )

    class Config:
        schema_extra = {
            "example": {
                "idioma": "pt-BR",
                "tipoPerfil": "primeiro_emprego"
            }
        }


# ================= Helpers =================

def chat(system_prompt: str, user_prompt: str, model: str = OPENAI_MODEL, temperature: float = 0.2) -> str:
    """
    Helper central para chamadas de chat na OpenAI.
    """
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature
        )
        return (resp.choices[0].message.content or "").strip()
    except Exception as e:
        raise HTTPException(500, f"OpenAI error: {e}")


def clean_markdown(md: str) -> str:
    md = md.replace("```markdown", "").replace("```", "")
    md = md.replace("\\n", "\n")
    return md.strip()


# ---------- RENDERIZADORES ----------

def render_markdown(cv: CvStructured) -> str:
    """
    Monta um currículo em Markdown a partir da estrutura CvStructured.
    Depois isso é convertido para HTML.
    """
    linhas = []
    titulo = f"# {cv.nome}"
    if cv.titulo:
        titulo += f" — {cv.titulo}"
    linhas.append(titulo)
    linhas.append("")
    linhas.append(cv.resumo.strip())
    linhas.append("")

    # contatos
    c = cv.contatos
    contatos_line = []
    for label, v in [
        ("📧", c.email),
        ("📱", c.telefone),
        ("🔗 LinkedIn", c.linkedin),
        ("💻 GitHub", c.github),
        ("🌐", c.site),
        ("📍", ", ".join([x for x in [c.cidade, c.estado, c.pais] if x]))
    ]:
        if v:
            contatos_line.append(f"{label}: {v}")
    if contatos_line:
        linhas.append("**Contatos**: " + " | ".join(contatos_line))
        linhas.append("")

    if cv.objetivo:
        linhas.append("## Objetivo")
        linhas.append(cv.objetivo.strip())
        linhas.append("")

    if cv.hardSkills or cv.softSkills:
        linhas.append("## Skills")
        if cv.hardSkills:
            linhas.append(f"- **Hard**: {', '.join(cv.hardSkills)}")
        if cv.softSkills:
            linhas.append(f"- **Soft**: {', '.join(cv.softSkills)}")
        linhas.append("")

    if cv.experiencias:
        linhas.append("## Experiências")
        for e in cv.experiencias:
            linhas.append(f"### {e.cargo} — {e.empresa} ({e.inicio} • {e.fim})")
            if e.local:
                linhas.append(f"*{e.local}*")
            for r in e.responsabilidades:
                linhas.append(f"- {r}")
            for g in e.conquistas:
                linhas.append(f"- 🏆 {g}")
            linhas.append("")
    if cv.escolaridade:
        linhas.append("## Escolaridade")
        for ed in cv.escolaridade:
            fim = f" • {ed.fim}" if ed.fim else ""
            status = f" — *{ed.status}*" if ed.status else ""
            linhas.append(f"- **{ed.curso}**, {ed.instituicao} ({ed.inicio}{fim}){status}")
            if ed.destaque:
                linhas.append(f"  - {ed.destaque}")
        linhas.append("")
    if cv.certificacoes:
        linhas.append("## Certificações")
        for cert in cv.certificacoes:
            base = f"- {cert.nome}"
            if cert.orgao:
                base += f" — {cert.orgao}"
            if cert.ano:
                base += f" ({cert.ano})"
            if cert.url_credencial:
                base += f" — {cert.url_credencial}"
            linhas.append(base)
        linhas.append("")
    if cv.projetos:
        linhas.append("## Projetos")
        for p in cv.projetos:
            base = f"### {p.nome}"
            if p.link:
                base += f" — {p.link}"
            linhas.append(base)
            if p.descricao:
                linhas.append(f"- {p.descricao}")
            if p.stack:
                linhas.append(f"- Stack: {', '.join(p.stack)}")
            if p.impacto:
                linhas.append(f"- Impacto: {p.impacto}")
            linhas.append("")
    if cv.idiomas:
        linhas.append("## Idiomas")
        linhas.append(", ".join(cv.idiomas))
        linhas.append("")
    if cv.pretensao or cv.disponbilidade or cv.interesses:
        linhas.append("## Informações Adicionais")
        if cv.disponbilidade:
            linhas.append(f"- Disponibilidade: {cv.disponbilidade}")
        if cv.pretensao:
            linhas.append(f"- Pretensão: {cv.pretensao}")
        if cv.interesses:
            linhas.append(f"- Interesses: {', '.join(cv.interesses)}")
        linhas.append("")

    return "\n".join(linhas).strip()


def markdown_to_html(md: str, title: str = "Currículo") -> str:
    import markdown2
    body = markdown2.markdown(
        md,
        extras=[
            "fenced-code-blocks",
            "tables",
            "break-on-newline",
            "strike",
            "smarty-pants",
            "toc",
        ],
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>{title}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
  :root {{
    --ink:#202124; --muted:#5f6368; --rule:#e6e6e6; --chip:#fafafa; --brand:#1a73e8;
  }}

  @page {{ size: A4; margin: 18mm 16mm; }}
  * {{ box-sizing: border-box; }}
  html, body {{ height:100%; }}
  body {{
    margin:0; color:var(--ink);
    font-family: Inter, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    line-height:1.42; font-size:11.5pt;
    -webkit-print-color-adjust: exact; print-color-adjust: exact;
    hyphens:auto;
  }}

  h1 {{ font-size:22pt; margin:0 0 6pt 0; font-weight:750; letter-spacing:.2px; }}
  h2 {{ font-size:14pt; margin:18pt 0 6pt; border-bottom:1px solid var(--rule); padding-bottom:2pt; }}
  h3 {{ font-size:12.5pt; margin:12pt 0 4pt; }}
  p  {{ margin:0 0 6pt; }}
  ul {{ margin:0 0 8pt 16pt; padding:0; }}
  li {{ margin:0 0 4pt 0; }}
  a  {{ color:var(--brand); text-decoration:none; word-break:break-word; }}

  .page {{ padding:18mm 16mm; }}
  .header {{
    display:grid; grid-template-columns: 1fr auto; gap:12pt; align-items:end; margin-bottom:10pt;
  }}
  .contacts {{ text-align:right; color:var(--muted); font-size:10pt; line-height:1.3; }}
  .contacts a {{ color:inherit; }}

  .meta {{ color:var(--muted); font-size:10pt; margin-bottom:10pt; }}

  .chips {{ margin:.5rem 0 0; }}
  .chips span {{
    display:inline-block; border:1px solid var(--rule); border-radius:14px;
    padding:2pt 8pt; margin:0 6pt 6pt 0; font-size:10pt; background:var(--chip);
  }}

  h2, h3 {{ page-break-after:avoid; page-break-inside:avoid; }}
  p, li {{ orphans:2; widows:2; }}
  .block {{ page-break-inside:avoid; }}

  .role {{ font-weight:650; }}
  .when, .place {{ color:var(--muted); font-size:10pt; }}

  @media (prefers-color-scheme: dark) {{
    :root {{ --ink:#e9eaed; --muted:#c2c5c9; --rule:#2b2d30; --chip:#1c1f23; }}
    body {{ background:#0f1113; }}
  }}
</style>
</head>
<body>
  <div class="page">
    {body}
  </div>
</body>
</html>"""


# ---------- LLM PARA JSON ESTRUTURADO (CV) ----------

def gen_structured_from_llm(body: CvRequest) -> CvStructured:
    """
    Usa a IA para transformar 'dados' em currículo estruturado.
    Regras:
    - 'dados' não pode ser vazio
    - precisa ter pelo menos 'nome'
    - resto (idade, curso, etc.) é opcional; a IA completa.
    """
    if not body.dados or not isinstance(body.dados, dict):
        raise HTTPException(
            status_code=400,
            detail="O campo 'dados' não pode estar vazio. Envie pelo menos o 'nome'.",
        )

    nome = str(body.dados.get("nome", "")).strip()
    if not nome:
        raise HTTPException(
            status_code=400,
            detail="Informe pelo menos o campo 'nome' em 'dados'.",
        )

    system = (
        "Você é um gerador de currículos profissionais. "
        "Responda ESTRITAMENTE em JSON válido UTF-8, sem cercas de código, no seguinte formato mínimo:\n"
        "{"
        "\"nome\":\"string\", \"idade\":int, \"titulo\":\"string?\", \"resumo\":\"string\","
        "\"contatos\": {"
            "\"email\":\"string?\",\"telefone\":\"string?\",\"linkedin\":\"string?\","
            "\"github\":\"string?\",\"site\":\"string?\",\"cidade\":\"string?\","
            "\"estado\":\"string?\",\"pais\":\"string?\""
        "},"
        "\"experiencias\":[{"
            "\"cargo\":\"string\","
            "\"empresa\":\"string\","
            "\"inicio\":\"MM/YYYY\","
            "\"fim\":\"MM/YYYY?\","
            "\"local\":\"string?\","
            "\"responsabilidades\":[\"...\"],"
            "\"conquistas\":[\"...\"]"
        "}],"
        "\"escolaridade\":[{"
            "\"curso\":\"string\","
            "\"instituicao\":\"string\","
            "\"inicio\":\"MM/YYYY\","
            "\"fim\":\"MM/YYYY?\","
            "\"status\":\"string?\","
            "\"destaque\":\"string?\""
        "}],"
        "\"objetivo\":\"string?\","
        "\"softSkills\":[\"...\"],"
        "\"hardSkills\":[\"...\"],"
        "\"idiomas\":[\"...\"],"
        "\"certificacoes\":[{"
            "\"nome\":\"string\","
            "\"orgao\":\"string?\","
            "\"ano\":\"YYYY?\","
            "\"id_credencial\":\"string?\","
            "\"url_credencial\":\"string?\""
        "}],"
        "\"projetos\":[{"
            "\"nome\":\"string\","
            "\"descricao\":\"string?\","
            "\"stack\":[\"...\"],"
            "\"link\":\"string?\","
            "\"impacto\":\"string?\""
        "}],"
        "\"interesses\":[\"...\"],"
        "\"disponbilidade\":\"string?\","
        "\"pretensao\":\"string?\""
        "}"
        " IMPORTANTÍSSIMO: todas as datas devem seguir o padrão brasileiro, NUNCA americano. "
        "Use sempre 'MM/YYYY' (por exemplo, '03/2024'), ou o texto 'Atual' para posições em andamento."
    )

    user = (
        f"Gere um currículo estruturado em {body.idioma} a partir destes dados "
        f"(campos ausentes podem ser completados ou adaptados por você): {body.dados}.\n"
        "Traga 2–4 responsabilidades e 1–2 conquistas mensuráveis por experiência. "
        "Use tom profissional e objetivo; evite adjetivos vazios; privilegie números e impacto."
    )
    txt = chat(system, user, model=OPENAI_MODEL, temperature=0.5)
    import json
    try:
        data = json.loads(txt)
        return CvStructured(**data)
    except Exception as e:
        raise HTTPException(
            500,
            f"Falha ao estruturar currículo: {e}. Resposta do modelo: {txt[:3000]}",
        )


# ================= Endpoints =================

@app.post(
    "/gen/plan",
    summary="Gera plano de requalificação em HTML (para WebView)",
    response_class=HTMLResponse,
)
def gen_plan(body: PlanRequest):
    """
    Gera um plano de requalificação / desenvolvimento de carreira
    em cima do perfil informado (soft/hard skills, objetivo, tempo disponível)
    e retorna um HTML pronto para renderizar em WebView.
    """
    system = (
        "Você é um mentor de carreira. "
        "Gere um plano de requalificação em MARKDOWN, bem organizado, SEM cercas ``` e sem JSON. "
        "Estruture o conteúdo com títulos e listas, seguindo este formato aproximado:\n\n"
        "# Plano de Requalificação\n"
        "## Visão Geral\n"
        "- Resuma o objetivo e o contexto da pessoa.\n\n"
        "## Trilhas de Desenvolvimento\n"
        "### Nome da trilha\n"
        "- Carga horária estimada: X horas\n"
        "- Etapa 1\n"
        "- Etapa 2\n"
        "...\n\n"
        "## Hábitos Recomendados\n"
        "- Hábito 1\n"
        "- Hábito 2\n\n"
        "Finalize com uma mensagem encorajadora curta."
    )

    user = (
        f"Gere o plano no idioma {body.idioma} para o perfil:\n"
        f"- soft skills: {body.perfil.softSkills}\n"
        f"- hard skills: {body.perfil.hardSkills}\n"
        f"- objetivo: {body.perfil.objetivo}\n"
        f"- horas disponíveis por semana: {body.perfil.disponibilidadeSemanalHoras}\n"
        "Use linguagem clara, prática e motivadora, focada em ações concretas."
    )

    md = chat(system, user, model=OPENAI_MODEL, temperature=0.3)
    md = clean_markdown(md)
    html = markdown_to_html(md, title="Plano de Requalificação – SkillBridge AI")
    return HTMLResponse(content=html, status_code=200)


# --------- HTML PRINCIPAL (dados do usuário) ---------

@app.post(
    "/gen/cv/html",
    summary="Gera currículo em HTML usando os dados informados",
    response_class=HTMLResponse,
)
def gen_cv_html(body: CvRequest):
    """
    Endpoint PRINCIPAL para o app mobile:
    - Recebe dados de currículo (CvRequest.dados) digitados pelo usuário
      (nome obrigatório, resto opcional).
    - Gera um HTML bonito de currículo.
    - O app pode renderizar esse HTML em uma WebView.
    """
    cv = gen_structured_from_llm(body)
    md = render_markdown(cv)
    html = markdown_to_html(md, title=f"Currículo — {cv.nome}")
    return HTMLResponse(content=html, status_code=200)


# --------- HTML DEMO (perfil aleatório / exemplo) ---------

@app.post(
    "/gen/cv/html/demo",
    summary="Gera currículo EXEMPLO em HTML (perfil aleatório)",
    response_class=HTMLResponse,
)
def gen_cv_html_demo(body: DemoCvRequest):
    """
    Versão DEMO:
    - Não depende de dados do usuário.
    - Gera um currículo de exemplo (perfil inventado) para testes / demonstração.
    """
    base_dados = {
        "nome": "João da Silva (Exemplo)",
        "titulo": "Profissional de Tecnologia",
        "resumo": (
            "Este é um perfil de exemplo gerado automaticamente para demonstração do SkillBridge AI. "
            "Use o endpoint /gen/cv/html com seus dados reais para obter um currículo personalizado."
        ),
        "tipoPerfil": body.tipoPerfil,
    }
    cv_request = CvRequest(dados=base_dados, idioma=body.idioma)
    cv = gen_structured_from_llm(cv_request)
    md = render_markdown(cv)
    html = markdown_to_html(md, title=f"Currículo — {cv.nome}")
    return HTMLResponse(content=html, status_code=200)


@app.post(
    "/gen/explain/html",
    summary="Gera explicação humanizada em HTML (coach)",
    response_class=HTMLResponse,
)
def gen_explain_html(body: ExplainRequest):
    """
    Versão em HTML da explicação humanizada.
    Ideal para usar em WebView no app mobile ou abrir direto no navegador.
    """
    system = "Você é um coach empático. Explique de forma positiva, com ações práticas."
    user = (
        f"Explique o contexto a seguir em {body.idioma}, com 3 ações práticas:\n"
        f"{body.contexto}"
    )
    txt = chat(system, user, model=OPENAI_MODEL, temperature=0.3)

    # monta um pequeno markdown usando o texto retornado
    md = (
        "# Explicação do plano\n\n"
        f"{txt.strip()}\n"
    )

    html = markdown_to_html(md, title="Explicação – SkillBridge AI")
    return HTMLResponse(content=html, status_code=200)


@app.get("/health", summary="Healthcheck simples")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "provider": "openai",
        "model": OPENAI_MODEL,
    }
