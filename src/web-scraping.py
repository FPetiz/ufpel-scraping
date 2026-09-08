from bs4 import BeautifulSoup
import requests
import pandas as pd
from pathlib import Path

url_geral = "https://institucional.ufpel.edu.br"
url_unidade = "https://institucional.ufpel.edu.br/unidades/id/443"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

session = requests.Session()
session.headers.update(headers)
response = session.get(url_unidade)
soup = BeautifulSoup(response.content, "html.parser")

graduacoes = soup.find(id="graduacao")
links_cursos = graduacoes.find_all("a", href=True) if graduacoes else []

turmas = []
projetos = []
professores_processados = set()

# print(f"Links de graduação encontrados: {len(links_cursos)}")

for link in links_cursos:
    href = link["href"]
    if not href.startswith("/cursos/cod/"):
        continue

    nome_curso = link.text.strip()
    curso_url = url_geral + href

    # print(f"Curso: {nome_curso}")

    curso_response = session.get(curso_url, headers=headers)
    curso_soup = BeautifulSoup(curso_response.content, "html.parser")

    # =================================================================
    # PARTE I - Turmas Ofertadas -> Professor -> Vagas -> Matriculados
    # =================================================================
    secao_turmas = curso_soup.find(id="turmas")
    if secao_turmas:
        tabelas = secao_turmas.find_all("table", class_="tabela-dados")
        for tabela in tabelas:
            for linha in tabela.find_all("tr"):
                colunas = linha.find_all("td")
                if len(colunas) >= 4:
                    tag_a = colunas[0].find("a")
                    disciplina = tag_a.text.strip() if tag_a else colunas[0].get_text(strip=True)

                    span_prof = colunas[0].find("span", class_="tabela-detalhe-info")
                    professor = span_prof.text.replace("Professor responsável pela turma:", "").strip() if span_prof else "Não informado"

                    vagas = colunas[2].text.strip()
                    matriculados = colunas[3].text.strip()

                    turmas.append({
                        "Curso": nome_curso,
                        "Disciplina": disciplina,
                        "Professor": professor,
                        "Vagas Ofertadas": vagas,
                        "N Alunos Matriculados": matriculados
                    })

    # =================================================================
    # PARTE II - Computação -> Professores CDTec -> Projetos Ativos
    # =================================================================
    if "Computa" in nome_curso:
        # print(f"Extraindo professores e projetos do CDTec em: {nome_curso}")
        secao_profs = curso_soup.find(id="professores")

        if secao_profs:
            for a_prof in secao_profs.find_all("a", href=True):
                href_prof = a_prof["href"]

                if "/servidores/id/" in href_prof:
                    nome_prof = a_prof.get_text(strip=True).replace("Centro de Desenvolvimento Tecnológico", "").strip()
                    
                    if not nome_prof:
                        continue

                    prof_url = url_geral + href_prof

                    if prof_url in professores_processados:
                        continue

                    linha_tr = a_prof.find_parent("tr")
                    if linha_tr and "Centro de Desenvolvimento Tecnológico" in linha_tr.get_text():
                        professores_processados.add(prof_url)
                        # print(f"- Lendo projetos de: {nome_prof}")

                        prof_res = session.get(prof_url, headers=headers)
                        prof_soup = BeautifulSoup(prof_res.content, "html.parser")

                        secao_projetos = prof_soup.find(id="projetos")
                        if not secao_projetos:
                            continue

                        projs_prof_processados = set()
                        for a_proj in secao_projetos.find_all("a", href=True):
                            href_proj = a_proj["href"]
                            if href_proj.startswith("/projetos/id/"):
                                proj_url_detalhe = url_geral + href_proj

                                if proj_url_detalhe in projs_prof_processados:
                                    continue

                                tr_proj = a_proj.find_parent("tr")
                                if tr_proj and "finalizado" in tr_proj.get("class", []):
                                    continue

                                projs_prof_processados.add(proj_url_detalhe)
                                titulo_proj = a_proj.get_text(strip=True)

                                proj_res = session.get(proj_url_detalhe, headers=headers)
                                proj_soup = BeautifulSoup(proj_res.content, "html.parser")

                                resumo = "Sem resumo disponível"
                                labels = proj_soup.find_all("div", class_="ficha-label")
                                for lbl in labels:
                                    if "Resumo" in lbl.text:
                                        campo = lbl.find_next_sibling("div", class_="ficha-campo")
                                        if campo:
                                            resumo = campo.get_text(strip=True)
                                            break

                                projetos.append({
                                    "Curso": nome_curso,
                                    "Professor": nome_prof,
                                    "Projeto": titulo_proj,
                                    "Resumo": resumo
                                })

# =================================================================
#  RESULTADOS
# =================================================================
df_turmas = pd.DataFrame(turmas)
print("\n" + "="*40)
print("     RESUMO DA EXTRAÇÃO - PARTE I")
print("="*40)
print(df_turmas.info())

BASE_DIR = Path(__file__).resolve().parent.parent
pasta = BASE_DIR / "data" / "output"
pasta.mkdir(parents=True, exist_ok=True)

caminho_csv = pasta / "projetos_computacao.csv"
df_projetos = pd.DataFrame(projetos)
df_projetos.to_csv(caminho_csv, index=False, encoding="utf-8-sig")

print("\n" + "="*40)
print("     RESUMO DA EXTRAÇÃO - PARTE II")
print("="*40)
print(f"Total de projetos salvos no CSV: {len(projetos)}")
if not df_projetos.empty:
    print("\nPrimeiros projetos capturados:")
    print(df_projetos[["Professor", "Projeto"]].head(10))