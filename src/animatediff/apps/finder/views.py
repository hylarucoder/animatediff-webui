import os
from typing import Optional

import pydantic as pt
from fastapi import APIRouter
from starlette.responses import FileResponse

from animatediff.consts import path_mgr
from animatediff.exceptions import ApiException

bp = APIRouter(prefix="/api/finder")

Q = [
    "index",
    # op
    "newfolder",
    "newfile",
    "download",
    "rename",
    "move",
    "delete",
    "upload",
    "archive",
    "unarchive",
    "preview",
    "save",
    "search",
]


class FileMetadata(pt.BaseModel):
    type: str
    path: str
    visibility: str
    last_modified: int
    extra_metadata: list = pt.Field([])
    basename: str
    extension: str = pt.Field(default="")
    storage: str
    file_size: int | None = None
    mime_type: str | None = None


MIME_TYPES = {
    "txt": "text/plain",
    "pdf": "application/pdf",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "gif": "image/gif",
    "html": "text/html",
    "css": "text/css",
    "js": "application/javascript",
    "json": "application/json",
    "xml": "application/xml",
    # 更多的映射可以根据需要添加
}


def get_mime_type(extension: str) -> Optional[str]:
    return MIME_TYPES.get(extension.lower())


class VFinder:
    def __init__(self, storage_root: str):
        self.storage_root = storage_root

    def list_files(self, directory: str) -> list[FileMetadata]:
        full_path = os.path.join(self.storage_root, directory)
        files = []
        for entry in os.scandir(full_path):
            file_data = {
                "type": "dir" if entry.is_dir() else "file",
                "path": f"local://{entry.path.replace(self.storage_root, '').lstrip('/')}",
                "visibility": "public",
                "last_modified": int(entry.stat().st_mtime),
                "basename": entry.name,
                "storage": "local",
            }

            if not entry.is_dir():
                ext = os.path.splitext(entry.name)[1].lstrip(".")
                file_data.update({"file_size": entry.stat().st_size, "extension": ext, "mime_type": get_mime_type(ext)})

            # Validate and create a Pydantic model for the file data
            files.append(FileMetadata(**file_data))

        sorted_files = sorted(files, key=lambda file: file.basename.lower())
        return sorted_files


def format_fs_protocol(path: str, adapter="local"):
    if not path.startswith(f"{adapter}://"):
        return f"{adapter}://{path}"
    return path


def clean_fs_protocol(path: str, adapter="local"):
    return path.replace(f"{adapter}://", "")


@bp.get("")
def index(q: str, path: str = "", adapter="local"):
    if q not in Q:
        raise ApiException("q not in Q")
    # read only
    # ['index', 'download', 'preview', 'search'];
    v_finder = VFinder(str(path_mgr.projects))
    if q == "index":
        path = clean_fs_protocol(path)
        return {
            "adapter": adapter,
            "storages": ["local", "media"],
            "dirname": f"{adapter}://{path}",
            "files": v_finder.list_files(path),
        }
    if q == "preview":
        """ 请求什么文件, 返回什么结果 """
        path = clean_fs_protocol(path)
        return FileResponse(path_mgr.projects / path)
