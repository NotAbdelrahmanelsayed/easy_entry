import re
from urllib.parse import urlparse

import frappe
import requests

# Image extensions we accept from a remote link; anything else is skipped
# (e.g. Google/Jumia search result pages that aren't direct image URLs).
ALLOWED_CONTENT_TYPES = {
	"image/jpeg": "jpg",
	"image/png": "png",
	"image/webp": "webp",
	"image/gif": "gif",
}
MAX_DOWNLOAD_BYTES = 10 * 1024 * 1024  # 10 MB


def rehost_if_remote_url(doc, method=None):
	"""Download File docs pointed at an external image link and re-host the
	bytes on this server, instead of just proxying the remote URL.

	Frappe's own File.before_insert leaves file_url pointing at the external
	host whenever it looks like a URL (see File.is_remote_file) — it never
	downloads it. That means a File "attached by link" from Google/Jumia goes
	dead the moment the seller removes or renames that image upstream. This
	hook runs right after that core before_insert and, for external image
	links, pulls the bytes down and writes them through the normal
	File.save_file() path so the doc ends up backed by our own storage.
	"""
	if doc.is_folder or not doc.file_url or not doc.is_remote_file:
		return

	if not _is_external_url(doc.file_url):
		return

	try:
		content, extension = _download_image(doc.file_url)
	except Exception:
		frappe.log_error(
			title="Failed to re-host remote image",
			message=frappe.get_traceback(),
		)
		return

	doc.file_name = _build_filename(doc, extension)
	doc.file_url = ""
	doc.content = content
	doc.decode = False

	doc.save_file(content=content)
	doc.flags.new_file = True
	frappe.db.after_rollback.add(doc.on_rollback)


def _is_external_url(file_url):
	parsed = urlparse(file_url)
	if parsed.scheme not in ("http", "https"):
		return False
	site_host = urlparse(frappe.utils.get_url()).netloc
	return parsed.netloc != site_host


def _download_image(url):
	# A default python-requests UA is blocked by some image hosts (e.g. Wikimedia).
	headers = {"User-Agent": "Mozilla/5.0 (compatible; frappe-image-rehost/1.0)"}
	response = requests.get(url, timeout=10, stream=True, headers=headers)
	response.raise_for_status()

	content_type = response.headers.get("Content-Type", "").split(";")[0].strip().lower()
	extension = ALLOWED_CONTENT_TYPES.get(content_type)
	if not extension:
		frappe.throw(f"Unsupported or non-image content type for remote file: {content_type or 'unknown'}")

	content = response.raw.read(MAX_DOWNLOAD_BYTES + 1, decode_content=True)
	if len(content) > MAX_DOWNLOAD_BYTES:
		frappe.throw("Remote image exceeds the 10 MB download limit")

	return content, extension


def _build_filename(doc, extension):
	base = re.sub(r"[^A-Za-z0-9_-]+", "-", doc.file_name or "remote-image").strip("-") or "remote-image"
	base = re.sub(r"\.[A-Za-z0-9]+$", "", base)
	return f"{base}.{extension}"
