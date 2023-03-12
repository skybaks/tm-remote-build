import zipfile
import os
import logging
import pathlib

logger = logging.getLogger(__name__)


def zip_plugin(start_dir, target_dir, plugin_id) -> str:
    if not os.path.isdir(start_dir):
        logger.error("Input directory is not a valid path: " + str(start_dir))
        return ""
    if not os.path.isfile(os.path.join(start_dir, "info.toml")):
        logger.error("info.toml not found at input path")
        return ""

    if not os.path.isdir(target_dir):
        pathlib.Path(target_dir).mkdir(parents=True, exist_ok=True)

    outfile_path = os.path.join(target_dir, "%s.op" % (plugin_id,))

    if os.path.isfile(outfile_path):
        os.remove(outfile_path)

    with zipfile.ZipFile(outfile_path, "w", zipfile.ZIP_DEFLATED) as plugin_zip_file:
        for root, dirs, files in os.walk(start_dir, topdown=True):
            dirs[:] = [d for d in dirs if d not in [".git", ".vscode", ".build"]]
            for file in files:
                plugin_zip_file.write(
                    os.path.join(root, file),
                    os.path.relpath(os.path.join(root, file), start_dir),
                )
    if os.path.isfile(outfile_path):
        return outfile_path
    return ""
