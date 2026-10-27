"""Execute the existing notebook in a fresh kernel using this Python environment."""

import argparse
import json
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--phase', type=int, choices=[6, 7, 8, 9], default=9, help='Current authorized phase validation record')
    args = parser.parse_args()
    path = ROOT / 'notebooks/analysis.ipynb'
    notebook = nbformat.read(path, as_version=4)
    for cell in notebook.cells:
        if cell.cell_type == 'code':
            cell.outputs = []; cell.execution_count = None
    with tempfile.TemporaryDirectory(prefix='food-demand-kernel-') as directory:
        spec = Path(directory) / 'food-demand'
        spec.mkdir()
        (spec / 'kernel.json').write_text(json.dumps({'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                                                    'display_name': 'Food demand project Python', 'language': 'python'}))
        manager = KernelManager(kernel_name='food-demand', kernel_spec_manager=KernelSpecManager(kernel_dirs=[directory]))
        client = NotebookClient(notebook, km=manager, timeout=300, allow_errors=False,
                                resources={'metadata': {'path': str(ROOT)}})
        try:
            client.execute()
        finally:
            if manager.has_kernel:
                manager.shutdown_kernel(now=True)
    nbformat.validate(notebook)
    code = [cell for cell in notebook.cells if cell.cell_type == 'code']
    assert all(cell.execution_count is not None for cell in code)
    assert not [o for cell in code for o in cell.outputs if o.output_type == 'error']
    expected_images = 6 if args.phase >= 9 else 5
    assert sum('image/png' in output.get('data', {}) for cell in code for output in cell.outputs) == expected_images, 'Expected charts must be embedded'
    nbformat.write(notebook, path)
    result = {'status': 'passed', 'fresh_kernel': True, 'code_cells_executed': len(code),
              'error_outputs': 0, 'image_outputs': sum('image/png' in output.get('data', {}) for cell in code for output in cell.outputs),
              'nbformat_validation': 'passed', 'python': sys.version.split()[0]}
    (ROOT / f'docs/phase{args.phase}_notebook_validation.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
