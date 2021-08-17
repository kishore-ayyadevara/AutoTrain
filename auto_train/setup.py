import os
from torch_snippets.paths import writelines
from torch_snippets.registry import *
import typer

app = typer.Typer()

bash_file = '''
git clone https://github.com/rwightman/pytorch-image-models timm
export BASE_DATA_DIR=BASE_DATA_DIRECTORY
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=True

trap cleanup INT
cleanup() {
    echo "Killing label studio"
    kill "$label_studio_pid"
    echo "Killing label studio ml"
    kill "$label_studio_ml_pid"
}

label-studio &
label_studio_pid=$!
echo "Label Studio lauched @ $label_studio_pid"
label-studio-ml init APP_NAME --script SCRIPT_PATH
label-studio-ml start ./APP_NAME
label_studio_ml_pid=$!
echo "Label Studio ML lauched @ $label_studio_ml_pid"

wait
'''

@app.command()
def main(config_path='config.ini'):
    config = Config().from_disk(config_path)
    config = AttrDict(config)
    file = (bash_file
        .replace('BASE_DATA_DIRECTORY', config.label_studio.base_data_dir)
        .replace('APP_NAME', config.label_studio_ml.app_name)
        .replace('SCRIPT_PATH', config.label_studio_ml.script_path)
    )
    file = [l for l in file.splitlines() if l.strip()!='']
    writelines(file, 'setup.sh')

if __name__ == '__main__':
    app()
