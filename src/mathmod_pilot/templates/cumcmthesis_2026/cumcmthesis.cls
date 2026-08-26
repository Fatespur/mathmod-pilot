\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\ProvidesClass{cumcmthesis}
              [2026/01/01 v3.2 CUMCM Anonymous Standard LaTeX Template]

\newif\if@mcm@bwprint\@mcm@bwprintfalse
\newif\if@mcm@preface\@mcm@prefacefalse

\DeclareOption{colorprint}{\@mcm@bwprintfalse}
\DeclareOption{bwprint}{\@mcm@bwprinttrue}
\DeclareOption{withpreface}{\@mcm@prefacetrue}
\DeclareOption{withoutpreface}{\@mcm@prefacefalse}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{ctexart}}
\ProcessOptions\relax

\LoadClass[a4paper,12pt,UTF8,fontset=windows]{ctexart}

\RequirePackage{geometry}
\geometry{top=2.5cm,bottom=2.5cm,left=2.5cm,right=2.5cm}

\RequirePackage{fontspec}
\setmainfont{Times New Roman}
\setsansfont{Arial}
\setmonofont{Consolas}

\setCJKmainfont[AutoFakeBold=true]{SimSun}
\setCJKsansfont[AutoFakeBold=true]{SimHei}
\setCJKmonofont{SimSun}

\RequirePackage{amsmath,amssymb,amsfonts,bm}
\RequirePackage{graphicx}
\RequirePackage{booktabs}
\RequirePackage{array}
\RequirePackage{longtable}
\RequirePackage{tabularx}
\RequirePackage{float}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage{cite}
\RequirePackage{fancyhdr}
\RequirePackage{xcolor}
\RequirePackage{enumitem}
\RequirePackage{hyperref}

\hypersetup{
    colorlinks=true,
    linkcolor=black,
    citecolor=blue,
    urlcolor=blue
}

% 页面与行距规范：小四号（12pt），1.25 倍行距，段首缩进 2 字符
\linespread{1.25}
\setlength{\parindent}{2em}
\setlength{\parskip}{0pt}
\setlength{\headheight}{15pt}
\addtolength{\topmargin}{-3pt}

% 页眉页脚规范：匿名提交版页脚居中阿拉伯数字页码
\pagestyle{fancy}
\fancyhf{}
\fancyhead[C]{\small\songti 全国大学生数学建模竞赛参赛论文}
\fancyfoot[C]{\small\thepage}
\renewcommand{\headrulewidth}{0.4pt}
\renewcommand{\footrulewidth}{0pt}

% 标题格式定制：一级标题四号黑体，二级标题小四黑体，三级标题小四黑体
\ctexset{
    section = {
        format = \zihao{4}\heiti\raggedright,
        name = {,、},
        number = \chinese{section},
        beforeskip = 0.8em,
        afterskip = 0.5em
    },
    subsection = {
        format = \zihao{-4}\heiti\raggedright,
        beforeskip = 0.6em,
        afterskip = 0.4em
    },
    subsubsection = {
        format = \zihao{-4}\heiti\raggedright,
        beforeskip = 0.5em,
        afterskip = 0.3em
    }
}

% 图表题注格式：五号居中
\captionsetup{
    font = small,
    labelsep = quad,
    skip = 6pt
}

\newcommand\mcm@tokens@keywords{}
\newcommand\keywords[1]{\renewcommand\mcm@tokens@keywords{#1}}

% 摘要环境定制：紧凑优雅，消除多余过大空白
\renewenvironment{abstract}{%
    \thispagestyle{fancy}
    \begin{center}
        {\zihao{3}\heiti\bfseries \@title \par}
        \vspace{0.6em}
        {\zihao{4}\heiti\bfseries 摘\quad 要}
    \end{center}
    \vspace{0.4em}
    \zihao{-4}\songti
}{%
    \par\vspace{0.8em}
    \noindent{\zihao{-4}\heiti\bfseries 关键词：}{\zihao{-4}\songti\mcm@tokens@keywords}
    \par\vspace{1.2em}
}

\endinput
