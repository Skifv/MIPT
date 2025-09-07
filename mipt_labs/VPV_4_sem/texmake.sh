FILEPATH=$1
DIR=$(dirname "$FILEPATH")
FILEFULL=$(basename "$FILEPATH")
FILENAME="${FILEFULL%.*}"
FILEEXT="${FILEFULL##*.}"
# Checking that (path to) file we got is not a (path to) directory
if [[ ! -f "$FILEPATH" ]]
then echo "$FILEPATH is not a file"; exit;
fi
if [[ $FILEEXT != "tex" ]]
then echo "$FILEFULL is not a TeX file"; exit;
fi
cd "$DIR"
PDFLATEX="pdflatex -interaction=nonstopmode"
BIBTEX="bibtex8 --wolfgang"
BAD_EXTENSIONS="aux toc out bbl log"
$PDFLATEX "$FILENAME.tex" | $BIBTEX "$FILENAME.aux" | $PDFLATEX "$FILENAME.tex"  $PDFLATEX "$FILENAME.tex"
if [[ $? -ne 0 ]]
then rm -f "$FILENAME.pdf"
fi
# Moving LaTeX log file to temp dir. We may need it for debugging. 
if [[ -f "$FILENAME.log" ]]
then mv -f "$FILENAME.log" "/tmp/$FILENAME.log"
fi
# Moving BibTex log file to temp dir. We may need it for debugging. 
if [[ -f "$FILENAME.blg" ]]
then mv -f "$FILENAME.blg" "/tmp/$FILENAME.blg"
fi
for ext in $BAD_EXTENSIONS; do
	rm -f *.$ext 
done