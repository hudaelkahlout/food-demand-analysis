"""Execute the Phase 10 notebook with a fresh project-local Python kernel."""
from pathlib import Path
import json
import sys
import tempfile
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager
ROOT=Path(__file__).resolve().parents[1]

def main():
    path=ROOT/'notebooks/machine_learning.ipynb'; nb=nbformat.read(path,as_version=4)
    for c in nb.cells:
        if c.cell_type=='code': c.outputs=[]; c.execution_count=None
    with tempfile.TemporaryDirectory(prefix='food-ml-kernel-') as folder:
        spec=Path(folder)/'food-ml'; spec.mkdir()
        (spec/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],display_name='Food demand Python',language='python')))
        km=KernelManager(kernel_name='food-ml',kernel_spec_manager=KernelSpecManager(kernel_dirs=[folder]))
        try:
            NotebookClient(nb,km=km,timeout=1800,allow_errors=False,resources={'metadata':{'path':str(ROOT)}}).execute()
        finally:
            if km.has_kernel: km.shutdown_kernel(now=True)
    nbformat.validate(nb)
    code=[c for c in nb.cells if c.cell_type=='code']
    assert all(c.execution_count is not None for c in code)
    assert not [o for c in code for o in c.outputs if o.output_type=='error']
    nbformat.write(nb,path)
    result=dict(status='passed',fresh_kernel=True,code_cells_executed=len(code),error_outputs=0,nbformat_validation='passed')
    (ROOT/'docs/phase10_notebook_validation.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
