import logging
logger = logging.getLogger(__name__)

import json
import toml
from pathlib import Path
from typing import Union

def save_dictionary_to_json(save_path: Union[str, Path], dictionary: dict, filename: str):
    if filename.split(".")[-1] != "json":
        filename = f"{filename}.json"
    json_file_path = Path(save_path) / filename
    json_file_path.write_text(json.dumps(dictionary, indent=4))
    logger.info(f"Saved dictionary {filename} as json to: {json_file_path}")

def save_dictionaries_to_toml(input_dictionaries: dict, output_file_path: Path):
    with open(output_file_path, "w") as toml_file:
        toml_file.write(toml.dumps(input_dictionaries))