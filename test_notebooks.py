import os
import subprocess
import tempfile

import nbformat
import glob
import pytest

def _notebook_run(path):
    """Execute a notebook via nbconvert and collect output.
       :returns (parsed nb object, execution errors)
    """
    dirname, __ = os.path.split(path)
    os.chdir(dirname)
    with tempfile.NamedTemporaryFile(suffix=".ipynb") as fout:
        args = ["jupyter", "nbconvert", "--to", "notebook", "--execute",
          "--ExecutePreprocessor.timeout=60",
          "--output", fout.name, path]
        subprocess.check_call(args)

        fout.flush()
        nb = nbformat.read(fout.name, nbformat.current_nbformat)

    errors = [output for cell in nb.cells if "outputs" in cell
                     for output in cell["outputs"]\
                     if output.output_type == "error"]

    return nb, errors

notebooks = glob.glob('*.ipynb')

@pytest.fixture(params=notebooks)
def all_notebooks(request):
    return os.path.abspath(request.param)

def check(notebook):
    nb, errors = _notebook_run(os.path.abspath(notebook))
    assert errors == []

def test_notebooks(all_notebooks):
    check(all_notebooks)
