"""Hatch build hook that bundles the WebUI and nujinagent skill documentation.

Triggered automatically by `python -m build` (and any other hatch-driven build)
so published wheels and sdists ship a fresh webui without requiring developers
to remember `cd webui && bun run build` beforehand. Documentation from docs/ is
copied into the nujinagent-document skill on every build, including editable installs.

WebUI behavior:

- Skips for editable installs (`pip install -e .`). Editable mode is for Python
  development; webui contributors use `cd webui && bun run dev` (Vite HMR) and
  do not need a packaged `dist/`.
- No-op when `webui/package.json` is absent (e.g. installing from an sdist that
  already contains a prebuilt `nujinagent/web/dist/`).
- Skips when `NUJINAGENT_SKIP_WEBUI_BUILD=1` is set.
- Reuses `nujinagent/web/dist/` only when it is already fresh, unless
  `NUJINAGENT_FORCE_WEBUI_BUILD=1` is set.
- Uses `bun` when available, otherwise falls back to `npm`, or provisions Bun
  when neither is available. Bun builds use `--bun` so Node is not required.
"""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from types import ModuleType

from hatchling.builders.hooks.plugin.interface import BuildHookInterface

_PROJECT_ROOT = Path(__file__).resolve().parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))


def _load_webui_build_module() -> ModuleType:
    from nujinagent.webui import build as webui_build

    return webui_build


class WebUIBuildHook(BuildHookInterface):
    PLUGIN_NAME = "webui-build"

    def initialize(self, version: str, build_data: dict) -> None:
        root = Path(self.root)
        docs_dir = root / "docs"
        references_dir = root / "nujinagent" / "skills" / "nujinagent-document" / "references"
        if not (docs_dir / "README.md").is_file():
            raise RuntimeError("[nujinagent-document] docs/README.md is required to bundle documentation")
        # Refresh generated files without removing directories that Windows
        # editors or file watchers may hold open during editable installs.
        current_docs: set[Path] = set()
        for source in docs_dir.rglob("*.md"):
            relative = source.relative_to(docs_dir)
            if relative.parts[0] in {"plans", "superpowers"}:
                continue
            current_docs.add(relative)
            destination = references_dir / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
        for generated in references_dir.rglob("*.md"):
            if generated.relative_to(references_dir) not in current_docs:
                generated.unlink()
        build_data.setdefault("artifacts", []).append(
            "nujinagent/skills/nujinagent-document/references/**/*.md"
        )

        # Bundle nujinSkills from pinned GitHub release if not already present (e.g. dev symlink)
        nujinskills_dir = root / "nujinagent" / "skills" / "nujinskills"
        if not nujinskills_dir.exists():
            import os
            import tarfile
            import tempfile
            import urllib.request

            tag = os.environ.get("NUJINSKILLS_VERSION", "v1.0.0")
            url = f"https://github.com/nujinAI/nujinSkills/archive/refs/tags/{tag}.tar.gz"
            try:
                with tempfile.TemporaryDirectory() as tmpdir:
                    tar_path = Path(tmpdir) / "nujinskills.tar.gz"
                    urllib.request.urlretrieve(url, tar_path)
                    with tarfile.open(tar_path, "r:gz") as tar:
                        tar.extractall(tmpdir)
                    extracted = next(Path(tmpdir).glob("nujinSkills-*"), None)
                    if extracted and extracted.is_dir():
                        shutil.copytree(extracted, nujinskills_dir)
                        self.app.display_info(f"[nujinskills] bundled {tag} from GitHub")
            except Exception as exc:
                self.app.display_warning(f"[nujinskills] skipped remote fetch ({exc})")
        if nujinskills_dir.exists():
            build_data.setdefault("artifacts", []).append("nujinagent/skills/nujinskills/**/*")
        webui_dir = root / "webui"
        package_json = webui_dir / "package.json"
        dist_dir = root / "nujinagent" / "web" / "dist"
        index_html = dist_dir / "index.html"

        # `pip install -e .` builds an editable wheel; skip the (slow) webui
        # bundle since editable installs target Python development and webui
        # work uses `bun run dev` instead.
        if self.target_name == "wheel" and version == "editable":
            self.app.display_info(
                "[webui-build] skipped for editable install "
                "(use `cd webui && bun run build` to bundle webui manually)"
            )
            return

        from nujinagent.build_info import read_commit

        commit = read_commit(root)
        if commit:
            commit_file = root / "nujinagent" / "_build_commit.txt"
            commit_file.write_text(commit + "\n", encoding="utf-8")
            build_data.setdefault("force_include", {})[str(commit_file)] = "nujinagent/_build_commit.txt"

        if os.environ.get("NUJINAGENT_SKIP_WEBUI_BUILD") == "1":
            self.app.display_info("[webui-build] skipped via NUJINAGENT_SKIP_WEBUI_BUILD=1")
            return

        if not package_json.is_file():
            self.app.display_info(
                "[webui-build] no webui/ source tree, assuming prebuilt nujinagent/web/dist/"
            )
            return

        webui_build = _load_webui_build_module()
        status = webui_build.inspect_webui_bundle(source_dir=webui_dir, dist_dir=dist_dir)
        force = os.environ.get("NUJINAGENT_FORCE_WEBUI_BUILD") == "1"
        if not status.needs_build and not force:
            self.app.display_info(
                f"[webui-build] reusing existing build at {dist_dir} "
                "(already fresh; set NUJINAGENT_FORCE_WEBUI_BUILD=1 to rebuild)"
            )
            return

        if status.needs_build and not force:
            self.app.display_info(
                f"[webui-build] {webui_build.describe_webui_bundle_status(status)}"
            )

        try:
            webui_build.build_webui_bundle(
                source_dir=webui_dir,
                dist_dir=dist_dir,
                output=self.app.display_info,
            )
        except webui_build.WebUIBuildError as exc:
            raise RuntimeError(
                "[webui-build] "
                f"{exc}. Install `bun` or `npm`, or set NUJINAGENT_SKIP_WEBUI_BUILD=1 to bypass."
            ) from exc

        if not index_html.is_file():
            raise RuntimeError(
                f"[webui-build] build finished but {index_html} is missing; "
                "check webui/vite.config.ts outDir."
            )
        self.app.display_info(f"[webui-build] webui ready at {dist_dir}")
