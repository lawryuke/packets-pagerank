\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{includes}[2026/07/18 Custom class]
\LoadClass[12pt, a4paper]{article}

% ── Paquetes ────────────────────────────────────────────────
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}
\RequirePackage[spanish]{babel}
\RequirePackage{lmodern}
\RequirePackage{geometry}
\geometry{top=2.5cm, bottom=2.5cm, left=3cm, right=2.5cm}

\RequirePackage{amsmath, amssymb, amsthm}
\RequirePackage{mathtools}
\RequirePackage{bm}
\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{longtable}
\RequirePackage{multirow}
\RequirePackage{graphicx}
\RequirePackage{float}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage{tikz}
\usetikzlibrary{arrows.meta, positioning, shapes.geometric, calc}
\RequirePackage{pgfplots}
\pgfplotsset{compat=1.18}
\RequirePackage{algorithm}
\RequirePackage{algpseudocode}
\RequirePackage{listings}
\RequirePackage{xcolor}
\RequirePackage{hyperref}
\hypersetup{
    colorlinks=false, % TRUE si quieres enlaces de color, FALSE si quieres cuadros alrededor
    linkcolor=blue!60!black,
    citecolor=green!50!black,
    urlcolor=cyan!70!black
}
\RequirePackage{csquotes}

% APA format
% \RequirePackage[backend=biber, style=apa, sorting=nyt]{biblatex}

% IEEE format 
\RequirePackage[backend=biber, style=ieee]{biblatex}

\addbibresource{referencias.bib}
\RequirePackage{setspace}
\onehalfspacing

\RequirePackage{parskip}
\setlength{\parskip}{6pt}
\RequirePackage{enumitem}

% ── Entornos matemáticos ────────────────────────────────────
\theoremstyle{definition}
\newtheorem{definicion}{Definición}[section]
\newtheorem{proposicion}{Proposición}[section]
\newtheorem{teorema}{Teorema}[section]
\newtheorem{ejemplo}{Ejemplo}[section]

% ── Colores para código ─────────────────────────────────────
\lstdefinestyle{pythonstyle}{
    backgroundcolor=\color{gray!8},
    commentstyle=\color{green!45!black},
    keywordstyle=\color{blue!70!black}\bfseries,
    stringstyle=\color{red!60!black},
    basicstyle=\ttfamily\small,
    breaklines=true,
    numbers=left,
    numberstyle=\tiny\color{gray},
    frame=single,
    language=Python,
    showstringspaces=false
}
\lstset{
	literate={á}{{\'a}}1 {é}{{\'e}}1 {í}{{\'i}}1 {ó}{{\'o}}1 {ú}{{\'u}}1
	{Á}{{\'A}}1 {É}{{\'E}}1 {Í}{{\'I}}1 {Ó}{{\'O}}1 {Ú}{{\'U}}1
	{ñ}{{\~n}}1 {Ñ}{{\~N}}1
}
