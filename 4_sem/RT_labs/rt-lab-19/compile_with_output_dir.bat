@echo off
echo Компиляция документа LaTeX с перенаправлением временных файлов...

REM Создаем директорию temp, если она не существует
if not exist temp mkdir temp

REM Компилируем документ с перенаправлением вывода в директорию temp
pdflatex -output-directory=temp main.tex
pdflatex -output-directory=temp main.tex

REM Копируем готовый PDF из директории temp в корневую директорию
copy /Y temp\main.pdf main.pdf

echo Компиляция завершена! PDF-файл готов. 