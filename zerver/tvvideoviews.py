from typing import Dict, List, Optional

from django.conf import settings
from django.http import (
    FileResponse, Http404, HttpResponse, HttpResponseNotModified, HttpRequest,
)

from django.utils.http import http_date, parse_http_date
from django.core.exceptions import PermissionDenied
from zerver.decorator import REQ, has_request_variables, zulip_login_required, require_non_guest_user
from zerver.models import UserProfile
from zerver.lib.user_groups import get_user_groups
from pathlib import Path
import mimetypes
import os
from django_sendfile import sendfile

@zulip_login_required
def authenticated_media_view(
    request: HttpRequest,
    group_path: str,
    path: str
):
  user = request.user
  groups = {g.name.lower().replace(' ', '-') for g in get_user_groups(user)}
  if group_path not in groups:
    raise PermissionDenied
  document_root = Path(settings.LOCAL_UPLOADS_DIR) / "files" / "media"
  fullpath = document_root / group_path / path  # safe join?

  if fullpath.is_dir():
    raise Http404("Directory indexes are not allowed here.")
  if not fullpath.exists():
    raise Http404('"%(path)s" does not exist' % {'path': fullpath})

  content_type, encoding = mimetypes.guess_type(str(fullpath))
  content_type = content_type or 'application/octet-stream'

  response = sendfile(
    request, fullpath, attachment=False, mimetype=content_type, encoding=encoding
  )
  return response
