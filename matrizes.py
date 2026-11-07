# -*- coding: utf-8 -*-
"""
MATRIZES: A ARQUITETURA DOS DADOS
Projeto Extensionista e Integrador - Analise e Desenvolvimento de Software (ADS)

Como executar no VS Code (terminal):
    pip install flask
    python app.py
Depois abra http://127.0.0.1:5000 no navegador.
"""
from fractions import Fraction
from flask import Flask, request, render_template_string
from markupsafe import Markup, escape

app = Flask(__name__)
AUTORES = "Israel Dias,Davi Evangelista, Elyas Douglas, Antonio Rosa, Higo Yves"  # <- edite: nomes do grupo
MAX = 6                  # tamanho maximo das matrizes (6x6)


# ====================== UTILIDADES ======================
def fmt(x):
    if isinstance(x, str):
        return x
    x = Fraction(x)
    return str(x.numerator) if x.denominator == 1 else f"{x.numerator}/{x.denominator}"


def par(x):
    s = fmt(x)
    return f"({s})" if s[0] == "-" or "/" in s else s


def num(t, onde):
    t = str(t).strip().replace(",", ".") or "0"
    try:
        if len(t) > 15:
            raise ValueError
        return Fraction(t)
    except (ValueError, ZeroDivisionError):
        raise ValueError(f"Valor inválido em {onde}: '{t}'. Use inteiros, decimais (2,5) ou frações (1/2).")


def ler(v, nome):
    return [[num(x, f"{nome}[{i+1}][{j+1}]") for j, x in enumerate(r)] for i, r in enumerate(v)]


def T(M):
    return [list(r) for r in zip(*M)]


def menor(M, i, j):
    return [r[:j] + r[j + 1:] for k, r in enumerate(M) if k != i]


def prod(A, B):
    return [[sum(a * b for a, b in zip(r, c)) for c in zip(*B)] for r in A]


def det(M):  # eliminação de Gauss (valor de referência/verificação)
    A = [r[:] for r in M]
    d = Fraction(1)
    for c in range(len(A)):
        p = next((r for r in range(c, len(A)) if A[r][c] != 0), None)
        if p is None:
            return Fraction(0)
        if p != c:
            A[c], A[p] = A[p], A[c]
            d = -d
        d *= A[c][c]
        for r in range(c + 1, len(A)):
            f = A[r][c] / A[c][c]
            A[r] = [a - f * b for a, b in zip(A[r], A[c])]
    return d


# ====================== HTML DAS MATRIZES ======================
def mat(M, nome="", diag=False, marca=()):
    n = len(M)
    quad = n == len(M[0])
    linhas = ""
    for i, r in enumerate(M):
        tds = ""
        for j, x in enumerate(r):
            c = []
            if diag and quad and i == j:
                c.append("dp")
            if diag and quad and i + j == n - 1:
                c.append("ds")
            if (i, j) in marca:
                c.append("mk")
            tds += f'<td class="{" ".join(c)}">{escape(fmt(x))}</td>'
        linhas += f"<tr>{tds}</tr>"
    nm = f'<b class="nm">{escape(nome)}</b>' if nome else ""
    return Markup(f'<span class="mw">{nm}<span class="cb"><table>{linhas}</table></span></span>')


def html(itens):
    o = []
    for it in itens:
        k = it[0]
        if k == "m":
            o.append(str(mat(*it[1:])))
        elif k == "op":
            o.append(f'<span class="op">{escape(it[1])}</span>')
        elif k == "h":
            o.append(f"<h4>{escape(it[1])}</h4>")
        elif k == "p":
            o.append(f"<p>{escape(it[1])}</p>")
        elif k == "eq":
            o.append(f'<pre class="eq">{escape(it[1])}</pre>')
        elif k == "res":
            o.append(f'<div class="res">{escape(it[1])}</div>')
    return "".join(o)


app.jinja_env.globals["mat"] = mat


# ====================== CLASSIFICAÇÃO E DIAGONAIS ======================
def tipos(A):
    m, n = len(A), len(A[0])
    t = []
    if m == n == 1:
        t.append("unitária (1×1)")
    elif m == 1:
        t.append("linha")
    elif n == 1:
        t.append("coluna")
    if all(x == 0 for r in A for x in r):
        t.append("nula")
    if m == n:
        t.append("quadrada")
        if all(A[i][j] == 0 for i in range(m) for j in range(n) if i != j):
            t.append("diagonal")
            if all(A[i][i] == 1 for i in range(n)):
                t.append("identidade")
        if all(A[i][j] == 0 for i in range(m) for j in range(i)):
            t.append("triangular superior")
        if all(A[i][j] == 0 for i in range(m) for j in range(i + 1, n)):
            t.append("triangular inferior")
        if A == T(A):
            t.append("simétrica")
    return t


def diag_itens(A):
    n = len(A)
    P = [A[i][i] for i in range(n)]
    S = [A[i][n - 1 - i] for i in range(n)]
    soma = lambda v: " + ".join(par(x) for x in v) + f" = {fmt(sum(v))}"
    it = [("m", A, "A", True),
          ("p", "Diagonal principal (i = j) em azul; diagonal secundária (i + j = n + 1) em dourado."),
          ("eq", "Diagonal principal:  " + soma(P) + "\nDiagonal secundária: " + soma(S)),
          ("res", f"Soma da diagonal principal = {fmt(sum(P))}   |   Soma da diagonal secundária = {fmt(sum(S))}")]
    if n % 2:
        it.append(("p", "Como n é ímpar, o elemento central pertence às duas diagonais."))
    return it


def analise(A):
    m, n = len(A), len(A[0])
    S = [("Informações gerais", [
        ("m", A, "A", m == n),
        ("p", f"Ordem: {m}×{n} ({m} linha(s), {n} coluna(s), {m*n} elementos)."),
        ("p", "Classificação: " + (", ".join(tipos(A)) or "matriz retangular comum") + ".")])]
    S.append(("Soma das diagonais", diag_itens(A) if m == n else
              [("p", "Diagonais principal e secundária só existem em matrizes quadradas (m = n).")]))
    S.append(("Transposta e oposta", [("m", A, "A"), ("op", "→ Aᵗ ="), ("m", T(A), "Aᵗ"),
                                      ("op", "   −A ="), ("m", [[-x for x in r] for r in A], "−A")]))
    return S


# ====================== DETERMINANTES ======================
def laplace(M):
    n = len(M)
    cand = [(sum(x == 0 for x in M[i]), "linha", i) for i in range(n)] + \
           [(sum(M[i][j] == 0 for i in range(n)), "coluna", j) for j in range(n)]
    z, t, k = max(cand, key=lambda c: c[0])
    marca = [(k, j) for j in range(n)] if t == "linha" else [(i, k) for i in range(n)]
    I = [("p", f"Teorema de Laplace: det(A) = soma de aij·Cij ao longo de qualquer fila, com cofator "
               f"Cij = (−1)^(i+j)·Dij (Dij = determinante do menor). Escolhemos a {t} {k+1}, que tem {z} zero(s)."),
         ("m", M, "A", False, marca)]
    tot, termos = Fraction(0), []
    for q in range(n):
        i, j = (k, q) if t == "linha" else (q, k)
        a, c = M[i][j], f"{i+1}{j+1}"
        if a == 0:
            I.append(("eq", f"a{c} = 0  →  termo nulo"))
            termos.append("0")
            continue
        D = det(menor(M, i, j))
        s = -1 if (i + j) % 2 else 1
        C = s * D
        tot += a * C
        I += [("h", f"Termo a{c} = {fmt(a)}"), ("m", menor(M, i, j), f"D{c}"),
              ("eq", f"D{c} = {fmt(D)}\nC{c} = ({s:+d})·{par(D)} = {fmt(C)}\n"
                     f"a{c}·C{c} = {par(a)}·{par(C)} = {fmt(a * C)}")]
        termos.append(par(a * C))
    I.append(("res", "det(A) = " + " + ".join(termos) + f" = {fmt(tot)}"))
    return tot, I


def chio(M):
    A = [r[:] for r in M]
    n = len(A)
    f = Fraction(1)
    I = [("p", "Regra de Chió: se a11 = 1, det(A) = det(B), com B de ordem n−1 e bij = aij − ai1·a1j "
               "(retira-se a 1ª linha e a 1ª coluna e, de cada elemento restante, subtrai-se o produto "
               "dos elementos que ficam no início da sua linha e da sua coluna).")]
    while n > 2:
        pos = next(((i, j) for i in range(n) for j in range(n) if A[i][j] == 1), None) or \
              next(((i, j) for i in range(n) for j in range(n) if A[i][j] != 0), None)
        if pos is None:
            return Fraction(0), I + [("res", "Todos os elementos são 0 → det(A) = 0")]
        i, j = pos
        if i:
            A[0], A[i] = A[i], A[0]
            f = -f
            I.append(("p", f"Troca L1 ↔ L{i+1}: o determinante muda de sinal."))
        if j:
            for r in A:
                r[0], r[j] = r[j], r[0]
            f = -f
            I.append(("p", f"Troca C1 ↔ C{j+1}: o determinante muda de sinal."))
        p = A[0][0]
        if p != 1:
            A[0] = [x / p for x in A[0]]
            f *= p
            I.append(("p", f"a11 = {fmt(p)} ≠ 1: dividimos a 1ª linha por {fmt(p)} e multiplicamos o determinante por {fmt(p)}."))
        B = [[A[r][c] - A[r][0] * A[0][c] for c in range(1, n)] for r in range(1, n)]
        I += [("h", f"Redução de ordem {n} → {n-1}"),
              ("m", A, "A", False, [(0, c) for c in range(n)] + [(r, 0) for r in range(1, n)]),
              ("op", "⟹"), ("m", B, "B"),
              ("eq", f"b11 = a22 − a21·a12 = {fmt(A[1][1])} − {par(A[1][0])}·{par(A[0][1])} = {fmt(B[0][0])}\n"
                     f"Fator acumulado: {fmt(f)}")]
        A, n = B, n - 1
    d2 = A[0][0] * A[1][1] - A[0][1] * A[1][0]
    d = f * d2
    I += [("h", "Matriz 2×2 final"), ("m", A, "A"),
          ("eq", f"det = {par(A[0][0])}·{par(A[1][1])} − {par(A[0][1])}·{par(A[1][0])} = {fmt(d2)}"),
          ("res", (f"det(A) = {par(f)} · {par(d2)} = {fmt(d)}" if f != 1 else f"det(A) = {fmt(d)}"))]
    return d, I


def jacobi(M):
    A = [r[:] for r in M]
    n = len(A)
    s = 1
    I = [("p", "Teorema de Jacobi: somar a uma fila um múltiplo de outra fila paralela NÃO altera o determinante. "
               "Usamos isso para zerar tudo abaixo da diagonal principal (matriz triangular); "
               "então det(A) = produto dos elementos da diagonal."), ("m", A, "A")]
    for c in range(n - 1):
        ops = []
        if A[c][c] == 0:
            p = next((r for r in range(c + 1, n) if A[r][c] != 0), None)
            if p is None:
                return Fraction(0), I + [("res", f"Coluna {c+1} sem pivô → det(A) = 0")]
            A[c], A[p] = A[p], A[c]
            s = -s
            ops.append(f"L{c+1} ↔ L{p+1}  (troca de filas: o sinal do determinante inverte)")
        for r in range(c + 1, n):
            if A[r][c] != 0:
                k = A[r][c] / A[c][c]
                A[r] = [a - k * b for a, b in zip(A[r], A[c])]
                ops.append(f"L{r+1} ← L{r+1} − ({fmt(k)})·L{c+1}")
        I += [("h", f"Zerar a coluna {c+1}"), ("eq", "\n".join(ops) or "Já há zeros abaixo do pivô."),
              ("m", A, "A'", False, [(r, c) for r in range(c + 1, n)])]
    d = Fraction(s)
    for i in range(n):
        d *= A[i][i]
    I.append(("res", "det(A) = " + ("(−1)·" if s < 0 else "") + "·".join(par(A[i][i]) for i in range(n)) + f" = {fmt(d)}"))
    return d, I


def inversa(A):
    n = len(A)
    d = det(A)
    I = [("m", A, "A"), ("p", "A⁻¹ = (1/det A)·adj(A), com adj(A) = (matriz dos cofatores)ᵀ. Só existe se det(A) ≠ 0."),
         ("eq", f"det(A) = {fmt(d)}")]
    if d == 0:
        return I + [("res", "det(A) = 0 → A não é inversível (matriz singular).")]
    cof = [[(-1) ** (i + j) * det(menor(A, i, j)) for j in range(n)] for i in range(n)]
    inv = [[x / d for x in r] for r in T(cof)]
    ok = prod(A, inv) == [[Fraction(int(i == j)) for j in range(n)] for i in range(n)]
    return I + [("m", cof, "Cof(A)"), ("op", "→ transposta →"), ("m", T(cof), "adj(A)"), ("op", "÷ det →"),
                ("m", inv, "A⁻¹"), ("res", "Verificação A · A⁻¹ = I " + ("✓" if ok else "✗"))]


# ====================== EXECUÇÃO DAS OPERAÇÕES ======================
OPS = [("analise", "Análise completa (ordem, tipo, diagonais, transposta, oposta)", 0, 0),
       ("diag", "Soma das diagonais principal e secundária", 0, 0),
       ("det_todos", "Determinante: Laplace + Chió + Jacobi (comparar)", 0, 0),
       ("det_laplace", "Determinante: Teorema de Laplace", 0, 0),
       ("det_chio", "Determinante: Regra de Chió", 0, 0),
       ("det_jacobi", "Determinante: Teorema de Jacobi", 0, 0),
       ("inversa", "Matriz inversa", 0, 0),
       ("soma", "Soma A + B", 1, 0), ("sub", "Subtração A − B", 1, 0),
       ("produto", "Produto A · B", 1, 0), ("escalar", "Multiplicação por escalar k · A", 0, 1)]
METODOS = {"det_laplace": ("Teorema de Laplace", laplace), "det_chio": ("Regra de Chió", chio),
           "det_jacobi": ("Teorema de Jacobi", jacobi)}


def executar(e):
    op, A = e["op"], ler(e["A"], "A")
    m, n = len(A), len(A[0])
    if op in ("diag", "inversa") or op.startswith("det"):
        if m != n:
            raise ValueError(f"Esta operação exige matriz quadrada (m = n); sua matriz A é {m}×{n}.")
    if op == "analise":
        return analise(A)
    if op == "diag":
        return [("Soma das diagonais", diag_itens(A))]
    if op == "inversa":
        return [("Matriz inversa", inversa(A))]
    if op.startswith("det"):
        if n == 1:
            return [("Determinante", [("res", f"det(A) = {fmt(A[0][0])}")])]
        sel = list(METODOS.values()) if op == "det_todos" else [METODOS[op]]
        S, vals = [], []
        for titulo, f in sel:
            d, I = f(A)
            vals.append(d)
            S.append((titulo, I))
        chk = det(A)
        ok = all(v == chk for v in vals)
        S.insert(0, ("Resultado", [("m", A, "A", True), ("res", f"det(A) = {fmt(chk)}"),
                                   ("p", ("Todos os métodos coincidem com a verificação por eliminação de Gauss ✓"
                                          if ok else "Atenção: divergência entre os métodos!"))]))
        return S
    if op == "escalar":
        k = num(e["k"], "k")
        C = [[k * x for x in r] for r in A]
        return [("Multiplicação por escalar", [("eq", f"k = {fmt(k)}   →   cij = k · aij"), ("m", A, "A"),
                                               ("op", f"{par(k)} · A ="), ("m", C, "C")])]
    B = ler(e["B"], "B")
    p, q = len(B), len(B[0])
    if op == "produto":
        if n != p:
            raise ValueError(f"Não existe A·B: o nº de colunas de A ({n}) deve ser igual ao nº de linhas de B ({p}).")
        C = prod(A, B)
        lin = [f"c{i+1}{j+1} = " + " + ".join(f"({fmt(A[i][k])}·{fmt(B[k][j])})" for k in range(n)) +
               f" = {fmt(C[i][j])}" for i in range(m) for j in range(q)]
        return [("Produto A · B", [("p", f"A é {m}×{n} e B é {p}×{q}  →  C = A·B é {m}×{q}."),
                                   ("m", A, "A"), ("op", "·"), ("m", B, "B"), ("op", "="), ("m", C, "C"),
                                   ("eq", "\n".join(lin[:25]))])]
    if (m, n) != (p, q):
        raise ValueError(f"Só é possível somar/subtrair matrizes de mesma ordem: A é {m}×{n} e B é {p}×{q}.")
    s = 1 if op == "soma" else -1
    sy = "+" if s == 1 else "−"
    C = [[a + s * b for a, b in zip(r1, r2)] for r1, r2 in zip(A, B)]
    lin = [f"c{i+1}{j+1} = {fmt(A[i][j])} {sy} {par(B[i][j])} = {fmt(C[i][j])}" for i in range(m) for j in range(n)]
    return [("Soma" if s == 1 else "Subtração", [("m", A, "A"), ("op", sy), ("m", B, "B"), ("op", "="),
                                                  ("m", C, "C"), ("eq", "\n".join(lin[:25]))])]


# ====================== PÁGINAS ======================
BASE = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Matrizes: A Arquitetura dos Dados</title>
<style>
:root{--navy:#0d1b36;--ouro:#c9a84c;--azul:#6fb4e8;--papel:#f4f1ea}
*{box-sizing:border-box}body{margin:0;font:16px/1.6 system-ui,Segoe UI,Roboto,sans-serif;background:var(--papel);color:#16233f}
header{background:var(--navy);color:#fff;padding:.8rem 1.2rem;display:flex;flex-wrap:wrap;gap:1rem;align-items:center;justify-content:space-between}
header b{font-size:1.1rem;color:var(--ouro)}nav a{color:#dfe8fa;text-decoration:none;margin-left:1.2rem;padding-bottom:3px}
nav a.on{border-bottom:2px solid var(--ouro);color:#fff}
main{max-width:1000px;margin:0 auto;padding:1.2rem}footer{text-align:center;color:#667;padding:2rem 1rem;font-size:.9rem}
.hero{background:var(--navy);color:#fff;border-radius:16px;padding:2.2rem 1.5rem;text-align:center;margin-bottom:1.2rem}
.hero h1{margin:0 0 .3rem;font-size:clamp(1.6rem,5vw,2.6rem)}.hero p{margin:0 0 1rem;color:#b9c7e6}
.gr{display:inline-grid;grid-template-columns:repeat(3,22px);gap:6px;margin:.5rem 0 1rem}.gr i{height:22px;border:2px solid #dfe8fa}.gr i:nth-child(3){background:var(--ouro);border-color:var(--ouro)}
.btn{display:inline-block;background:var(--ouro);color:var(--navy);font-weight:700;border:0;border-radius:8px;padding:.6rem 1.2rem;text-decoration:none;cursor:pointer;font-size:1rem}
.btn.s{background:#e3e8f2;color:var(--navy);padding:.3rem .7rem;font-size:.85rem;font-weight:600}
.card{background:#fff;border:1px solid #dcd6c8;border-radius:14px;padding:1rem 1.3rem;margin:1rem 0;box-shadow:0 2px 8px rgba(13,27,54,.06)}
h2{color:var(--navy);margin:.2rem 0 .4rem}h3{color:var(--navy);margin:0 0 .5rem;border-bottom:3px solid var(--ouro);display:inline-block}h4{margin:1rem 0 .3rem;color:#2d5f8a}
.mw{display:inline-flex;align-items:center;gap:.4rem;margin:.3rem .5rem;vertical-align:middle}.nm{font:italic 700 1.2rem Georgia,serif}
.cb{position:relative;display:inline-block;padding:0 .7rem}.cb::before,.cb::after{content:"";position:absolute;top:0;bottom:0;width:.5rem;border:2.5px solid var(--navy)}
.cb::before{left:0;border-right:0}.cb::after{right:0;border-left:0}
.cb td{padding:.25rem .6rem;min-width:2.5rem;text-align:center;font:600 1rem ui-monospace,Consolas,monospace;border-radius:6px}
td.dp{background:rgba(111,180,232,.4)}td.ds{background:rgba(201,168,76,.45)}td.dp.ds{background:linear-gradient(135deg,rgba(111,180,232,.6) 50%,rgba(201,168,76,.65) 50%)}
td.mk{outline:2px dashed #c0392b;outline-offset:-2px}.op{font-size:1.2rem;font-weight:700;margin:0 .3rem;vertical-align:middle}
.eq{background:#0f1f3d;color:#e8eefc;border-radius:10px;padding:.7rem 1rem;overflow-x:auto;font:.95rem/1.5 ui-monospace,Consolas,monospace;margin:.5rem 0}
.res{background:var(--ouro);color:var(--navy);font-weight:700;border-radius:10px;padding:.7rem 1rem;margin:.6rem 0}
.err{background:#fde8e6;border:1px solid #c0392b;color:#7b1c12;padding:.8rem 1rem;border-radius:10px;margin:1rem 0}
.row{display:flex;flex-wrap:wrap;gap:1rem;align-items:flex-end}label{font-weight:600;font-size:.9rem}
select,input{font:inherit;padding:.35rem .5rem;border:1px solid #b9b2a0;border-radius:6px}
.grade input{width:4.2rem;text-align:center;margin:2px;padding:.3rem .2rem}.grade{overflow-x:auto;padding:.4rem 0}
table{border-collapse:collapse}.tb td,.tb th{border:1px solid #cfc8b8;padding:.4rem .7rem;text-align:left}.tb th{background:var(--navy);color:#fff}
.g2{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:1rem}
</style></head><body>
<header><b>▦ Matrizes: A Arquitetura dos Dados</b>
<nav><a href="/" class="{{'on' if ativo=='t'}}">Teoria</a><a href="/calculadora" class="{{'on' if ativo=='c'}}">Calculadora</a></nav></header>
<main>{{ corpo }}</main>
<footer>Matemática Aplicada · ADS — Análise e Desenvolvimento de Software<br>{{ autores }}</footer></body></html>"""

TEORIA = """
<div class="hero"><h1>Matrizes: A Arquitetura dos Dados</h1><p>Fundamentos, taxonomia e mecânica da álgebra matricial · Determinantes, Laplace, Jacobi e Chió</p>
<div class="gr"><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i><i></i></div><br><a class="btn" href="/calculadora">Abrir a calculadora →</a></div>

<div class="card"><h3>1. O que é uma matriz?</h3>
<p>Uma estrutura matemática disposta em tabela para organizar dados e facilitar a resolução de problemas. Uma matriz <b>A<sub>m×n</sub></b> tem
<b>m</b> linhas (horizontal) e <b>n</b> colunas (vertical). Cada elemento <b>a<sub>ij</sub></b> tem endereço: <b>i</b> = linha, <b>j</b> = coluna.</p>
{{ mat([[15,28,9],[81,54,7]],'A') }} <p>Ordem 2×3 e a<sub>21</sub> = 81. Lei de formação: se a<sub>ij</sub> = j² − 2i (2×2), então
a<sub>11</sub>=−1, a<sub>12</sub>=2, a<sub>21</sub>=−3, a<sub>22</sub>=0:</p>{{ mat([[-1,2],[-3,0]],'A') }}</div>

<div class="card"><h3>2. Tipos especiais e diagonais</h3>
<p><b>Linha</b> (1×n), <b>coluna</b> (m×1), <b>nula</b> (todos 0), <b>unitária</b> (1×1), <b>quadrada</b> (m = n), <b>diagonal</b> (fora da diagonal principal = 0),
<b>identidade</b> (diagonal = 1, resto 0) e <b>simétrica</b> (A = Aᵗ).</p>
<p>Na matriz quadrada, a <b style="color:#2d7ab8">diagonal principal</b> tem i = j e a <b style="color:#a8851f">diagonal secundária</b> tem i + j = n + 1.</p>
{{ mat([[2,-1,4],[0,7,-3],[5,1,9]],'A',True) }}
<p>Soma da principal: 2 + 7 + 9 = <b>18</b> · Soma da secundária: 4 + 7 + 5 = <b>16</b>.</p></div>

<div class="card"><h3>3. Operações e condições de existência</h3>
<table class="tb"><tr><th>Operação</th><th>Condição</th><th>Mecânica</th></tr>
<tr><td>Soma / subtração</td><td>Mesma ordem m×n</td><td>Elemento com elemento (c<sub>ij</sub> = a<sub>ij</sub> ± b<sub>ij</sub>)</td></tr>
<tr><td>Escalar k·A</td><td>Nenhuma</td><td>k multiplica todos os elementos</td></tr>
<tr><td>Produto A·B</td><td>Colunas de A = Linhas de B</td><td>Linha × coluna; resultado m×p</td></tr>
<tr><td>Transposta Aᵗ</td><td>Nenhuma</td><td>a<sub>ij</sub> vira a<sub>ji</sub> (linhas viram colunas)</td></tr>
<tr><td>Inversa A⁻¹</td><td>Quadrada com det ≠ 0</td><td>A · A⁻¹ = I</td></tr></table>
<p>Exemplo de produto: {{ mat([[2,1],[-1,3]],'A') }}·{{ mat([[3,0,5],[1,4,0]],'B') }}={{ mat([[7,4,10],[0,12,-5]],'C') }}, pois c<sub>11</sub> = 2·3 + 1·1 = 7.</p></div>

<div class="card"><h3>4. Determinantes</h3>
<p>O determinante existe só para matrizes quadradas. Em 2×2: det = a·d − b·c. Propriedades úteis: troca de duas filas inverte o sinal; fila de zeros ⇒ det = 0;
matriz triangular ⇒ det = produto da diagonal. Nos exemplos abaixo usamos:</p>{{ mat([[1,2,3],[0,4,5],[1,0,6]],'A') }} <b>det(A) = 22</b>

<h4>Teorema de Laplace</h4>
<p>O determinante é a soma dos elementos de uma fila multiplicados pelos seus cofatores C<sub>ij</sub> = (−1)<sup>i+j</sup>·D<sub>ij</sub>. Escolha a fila com mais zeros. Pela coluna 1:
det = 1·C<sub>11</sub> + 0·C<sub>21</sub> + 1·C<sub>31</sub> = 1·(+24) + 1·(−2) = <b>22</b>.</p>
<h4>Teorema de Jacobi</h4>
<p>Somar a uma fila um múltiplo de outra fila paralela não altera o determinante. Com L3 ← L3 − L1:</p>{{ mat([[1,2,3],[0,4,5],[0,-2,3]],"A'") }}
<p>det = 1·(4·3 − 5·(−2)) = <b>22</b>.</p>
<h4>Regra de Chió</h4>
<p>Se a<sub>11</sub> = 1: tira-se a 1ª linha e a 1ª coluna e faz-se b<sub>ij</sub> = a<sub>ij</sub> − a<sub>i1</sub>·a<sub>1j</sub>, obtendo uma matriz de ordem n−1 com o mesmo determinante:</p>
{{ mat([[4,5],[-2,3]],'B') }}<p>det(B) = 4·3 − 5·(−2) = <b>22</b>.</p></div>
"""

CALC = """
<h2>Calculadora de matrizes</h2>
<form method="post" class="card">
<div class="row"><div><label>Operação</label><br><select name="op" id="op" onchange="vis()">
{% for v,r,b,k in ops %}<option value="{{v}}" {{'selected' if v==estado.op}}>{{r}}</option>{% endfor %}</select></div>
<div id="boxK"><label>Escalar k</label><br><input name="k" value="{{estado.k}}" size="6"></div></div>
<div class="g2">
{% for X in ['A','B'] %}<div id="box{{X}}"><h4>Matriz {{X}}</h4>
<div class="row"><div><label>Linhas</label><br><select name="rows{{X}}" id="rows{{X}}" onchange="dim('{{X}}')">{% for v in range(1,7) %}<option {{'selected' if v==estado['rows'+X]}}>{{v}}</option>{% endfor %}</select></div>
<div><label>Colunas</label><br><select name="cols{{X}}" id="cols{{X}}" onchange="dim('{{X}}')">{% for v in range(1,7) %}<option {{'selected' if v==estado['cols'+X]}}>{{v}}</option>{% endfor %}</select></div></div>
<div class="grade"><span class="cb" id="g{{X}}"></span></div>
<button type="button" class="btn s" onclick="fill('{{X}}',()=>0)">Zerar</button>
<button type="button" class="btn s" onclick="fill('{{X}}',(i,j)=>i==j?1:0)">Identidade</button>
<button type="button" class="btn s" onclick="fill('{{X}}',()=>Math.floor(Math.random()*19)-9)">Aleatória</button></div>{% endfor %}
</div><p style="font-size:.85rem;color:#556">Aceita inteiros, decimais (2,5) e frações (1/2). Tamanho máximo 6×6.</p>
<button class="btn" type="submit">Calcular</button></form>
{% if erro %}<div class="err"><b>Atenção:</b> {{erro}}</div>{% endif %}
{% if resultado %}<div id="resultado">{{resultado}}</div>{% endif %}
<script>
const E={{estado|tojson}},OPS={{meta|tojson}};
function grade(X,R,C,V){const t=document.createElement('table');for(let i=0;i<R;i++){const r=t.insertRow();for(let j=0;j<C;j++){const n=document.createElement('input');n.name=X+'-'+i+'-'+j;n.value=(V[i]&&V[i][j]!=null)?V[i][j]:'0';r.insertCell().appendChild(n)}}const g=document.getElementById('g'+X);g.innerHTML='';g.appendChild(t)}
function ler(X){return [...document.querySelectorAll('#g'+X+' tr')].map(r=>[...r.querySelectorAll('input')].map(i=>i.value))}
function dim(X){grade(X,+document.getElementById('rows'+X).value,+document.getElementById('cols'+X).value,ler(X))}
function fill(X,f){const v=ler(X).map((r,i)=>r.map((_,j)=>f(i,j)));grade(X,v.length,v[0].length,v)}
function vis(){const o=OPS[document.getElementById('op').value];document.getElementById('boxB').style.display=o[0]?'':'none';document.getElementById('boxK').style.display=o[1]?'':'none'}
['A','B'].forEach(X=>grade(X,E['rows'+X],E['cols'+X],E[X]));vis();
const rs=document.getElementById('resultado');if(rs)rs.scrollIntoView({behavior:'smooth'});
</script>
"""


def pagina(ativo, corpo):
    return render_template_string(BASE, corpo=Markup(corpo), ativo=ativo, autores=AUTORES)


def estado_padrao():
    return {"rowsA": 3, "colsA": 3, "rowsB": 3, "colsB": 3, "op": "det_todos", "k": "2",
            "A": [["1", "2", "3"], ["0", "4", "5"], ["1", "0", "6"]],
            "B": [["2", "0", "1"], ["1", "3", "0"], ["0", "1", "4"]]}


def estado_form(f):
    def d(k):
        try:
            return max(1, min(MAX, int(f.get(k, 3))))
        except ValueError:
            return 3
    e = {}
    for X in "AB":
        R, C = d("rows" + X), d("cols" + X)
        e["rows" + X], e["cols" + X] = R, C
        e[X] = [[f.get(f"{X}-{i}-{j}", "0") for j in range(C)] for i in range(R)]
    e["op"], e["k"] = f.get("op", "analise"), f.get("k", "2")
    return e


@app.route("/")
def teoria():
    return pagina("t", render_template_string(TEORIA))


@app.route("/calculadora", methods=["GET", "POST"])
def calculadora():
    estado, resultado, erro = estado_padrao(), "", ""
    if request.method == "POST":
        estado = estado_form(request.form)
        try:
            secoes = executar(estado)
            resultado = Markup("".join(
                f'<section class="card"><h3>{escape(t)}</h3><div>{html(I)}</div></section>' for t, I in secoes))
        except ValueError as ex:
            erro = str(ex)
    meta = {v: [b, k] for v, _, b, k in OPS}
    return pagina("c", render_template_string(CALC, estado=estado, ops=OPS, meta=meta,
                                              resultado=resultado, erro=erro))


if __name__ == "__main__":
    app.run(debug=True)
