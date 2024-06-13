from typing import Optional
from supabase import create_client
from django.core.files.storage import Storage
from AcampsBK import settings
from mimetypes import guess_type
from tabulate import tabulate
import requests

from . import ConfigurationError, APIResponseError

class SupabaseStorage(Storage):
    def __init__(self, bucket_name=settings.BUCKET_NAME, **kwargs):
        # Start client
        self.bucket_name = bucket_name

        self.supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.storage_client = self.supabase.storage.from_(self.bucket_name)

    def _open(self, name, mode="rb"):
        # Implement the method to open a file from Supsabase
        pass

    def _save(self, name, content):
        # Implement the method to save a file to Supabase
        content_file = content.file
        content_file.seek(0)  # Move the file pointer to the beginning
        content_bytes = content_file.read()
        mime = guess_type(name, strict=False)[0]
        data = self.supabase.storage.from_(self.bucket_name).upload(
            name, content_bytes, {"content-type": mime, "upsert": "true"}
        )
        return data.json()["Key"]  # name/path of the file

    def exists(self, name):
        # Implement the method to check if a file exists in Supabase
        pass

    def url(self, name):
        # Implement the method to return the URL for a file in Supabase
        handled_name = name.replace(f'{settings.BUCKET_NAME}/', '', 1)
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{settings.BUCKET_NAME}/{handled_name}"

class VercelBlobStorage(Storage):
    def __init__(self):
        self.DEFAULT_PAGE_SIZE = 100
        self.DEFAULT_CACHE_AGE = 365 * 24 * 60 * 60 # 1 Year

    def _coercel_bool(self, value):
        return str(int(bool(value)))

    def _handle_response(self, response: requests.Response):
        if str(response.status_code) == "200":
            return response.json()
        raise APIResponseError(f"Algo de errado não está certo: {response.json()}")

    def dump_headers(self, options: Optional[dict], headers: dict):
        if options is None:
            options = {}
        if options.get("debug", False):
            print(tabulate([(k, v) for k, v in headers.items()]))

    def guess_mime_type(self, url):
        return guess_type(url, strict=False)[0]

    def get_token(self, options: dict):
        _tkn = options.get("token", settings.VERCEL_BLOB_READ_WRITE_TOKEN)        
        if not _tkn:
            raise ConfigurationError("Vercel's BLOB_RW_TOKEN is not set")
        return _tkn

    def put(self, pathname: str, body: bytes, options: Optional[dict] = None):
        _opts = dict(options) if options else dict()
        headers = {
            "access": "public",
            "authorization": f"Bearer {self.get_token(_opts)}",
            "x-api-version": settings.VERCEL_BLOLB_API_VERSION,
            "x-content-type": self.guess_mime_type(pathname),
            "x-cache-control-max-age": _opts.get(
                "cacheControlMaxAge", str(self.DEFAULT_CACHE_AGE)
            ),
            "x-add-random-suffix": "false",
        }
        self.dump_headers(options, headers)
        _resp = requests.put(
            f"{settings.VERCEL_API_URL}/{pathname}",
            data=body,
            headers=headers
        )
        return self._handle_response(_resp)

    def _save(self, name, content, options: Optional[dict] = None):
        content_file = content.file
        content_file.seek(0)
        content_bytes = content_file.read()
        data = self.put(name, content_bytes, options)
        return data["url"]

    def list(self, options: Optional[dict] = None):
        _opts = dict(options) if options else dict()
        headers = {
            "authorization": f"Bearer {self.get_token(_opts)}",
            "limit": _opts.get("limit", str(self.DEFAULT_PAGE_SIZE)),
        }
        if "prefix" in _opts:
            headers["prefix"] = _opts["prefix"]
        if "cursor" in _opts:
            headers["cursor"] = _opts["cursor"]
        if "mode" in _opts:
            headers["mode"] = _opts["mode"]

        self.dump_headers(options, headers)
        _resp = requests.get(
            f"{settings.VERCEL_API_URL}",
            headers=headers,
        )
        return self._handle_response(_resp)

    def exists(self, name: str) -> bool:
        pass
    
    def url(self, name: str | None) -> str:
        return name

    def delete(self, name: str) -> None:
        pass
