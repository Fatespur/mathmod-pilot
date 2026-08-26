@echo off
chcp 65001 > nul
echo === 正在编译 2026 CUMCM LaTeX 论文模板 ===
xelatex -interaction=nonstopmode template_2026.tex
bibtex template_2026
xelatex -interaction=nonstopmode template_2026.tex
xelatex -interaction=nonstopmode template_2026.tex
echo === 编译完成，生成 template_2026.pdf ===
pause
