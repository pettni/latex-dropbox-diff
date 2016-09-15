import os
from subprocess import call


def run_latexdiff(file1_content, file2_content):
    # Create temporary files

    def write_to_file(file_content, file_name):
        f = open(file_name, 'w')
        f.write(file_content)
        f.close()

    write_to_file(file1_content, 'f1temp.tex')
    write_to_file(file2_content, 'f2temp.tex')

    with open('diff.tex', "w") as outfile:
        call(["/Library/TeX/texbin/latexdiff", "f1temp.tex", "f2temp.tex"],
             stdout=outfile)

    os.remove('f1temp.tex')
    os.remove('f2temp.tex')

    # Compile it
    call(["latexmk", "-cd", "-e", "-f", "-pdf", "-interaction=nonstopmode",
          "-synctex=1", "diff.tex"])

    # If successful, open pdf
    call(["open", "diff.pdf"])
