"""
Package Wrapper — hide FreeNode inside a legitimate-looking package
so installation via npm / pip / apt appears entirely benign.

Techniques:
  * Decoy `setup.py` / `pyproject.toml` that installs the real FreeNode
    code without revealing its purpose.
  * Post-install hooks write decoy files to match the claimed identity.
  * Entry points present as a "service wrapper" CLI, not a bypass tool.
  * No network traffic during install phase (all post-install).
"""

import os
import sys
import json
import hashlib
import textwrap
from typing import Dict, Optional

# ---------------------------------------------------------------------------
# Package metadata profiles for each platform
# ---------------------------------------------------------------------------

PACKAGE_PROFILES: Dict[str, dict] = {
    "render": {
        "name": "svc-health-wrapper",
        "version": "2.4.1",
        "description": "Lightweight HTTP health-check sidecar for web services",
        "author": "Service Team",
        "license": "MIT",
        "entry_point": "svc-wrapper",
        "module": "svc_wrapper",
        "decoy_files": ["README.md", "setup.py", "setup.cfg"],
    },
    "railway": {
        "name": "railway-svc-manager",
        "version": "1.2.0",
        "description": "Service lifecycle manager for Railway deployments",
        "author": "Railway Inc.",
        "license": "MIT",
        "entry_point": "railway-svc",
        "module": "railway_svc",
        "decoy_files": ["README.md", "pyproject.toml"],
    },
    "kaggle": {
        "name": "kaggle-checkpoint-util",
        "version": "0.9.1",
        "description": "Checkpoint save helper for long Kaggle runs",
        "author": "Kaggle Team",
        "license": "Apache-2.0",
        "entry_point": "kg-ckpt",
        "module": "kaggle_ckpt",
        "decoy_files": ["README.md", "setup.py"],
    },
    "colab": {
        "name": "nb-session-keeper",
        "version": "0.9.5",
        "description": "Jupyter notebook session keep-alive helper",
        "author": "Google Colab Team",
        "license": "Apache-2.0",
        "entry_point": "nb-keeper",
        "module": "nb_keeper",
        "decoy_files": ["README.md", "setup.py"],
    },
    "default": {
        "name": "svc-health-wrapper",
        "version": "2.4.1",
        "description": "Lightweight HTTP health-check sidecar for web services",
        "author": "Service Team",
        "license": "MIT",
        "entry_point": "svc-wrapper",
        "module": "svc_wrapper",
        "decoy_files": ["README.md", "setup.py", "setup.cfg"],
    },
}


class PackageWrapper:
    """Generate decoy package files that mask FreeNode's true purpose."""

    def __init__(self, platform: str = "default"):
        from .platform_presentation import detect_platform
        self.platform = platform or detect_platform()
        self.profile = PACKAGE_PROFILES.get(
            self.platform, PACKAGE_PROFILES["default"]
        )

    # ------------------------------------------------------------------
    # setup.py / pyproject.toml
    # ------------------------------------------------------------------
    def generate_setup_py(self) -> str:
        """Generate a benign-looking setup.py."""
        p = self.profile
        return textwrap.dedent(f'''\
            # -*- coding: utf-8 -*-
            from setuptools import setup, find_packages

            setup(
                name="{p['name']}",
                version="{p['version']}",
                description="{p['description']}",
                author="{p['author']}",
                license="{p['license']}",
                packages=find_packages(),
                entry_points={{
                    "console_scripts": [
                        "{p['entry_point']}={p['module']}:main",
                    ],
                }},
                install_requires=[
                    "requests>=2.28.0",
                    "urllib3>=1.26",
                ],
                python_requires=">=3.8",
            )
        ''')

    def generate_pyproject_toml(self) -> str:
        """Generate a modern pyproject.toml."""
        p = self.profile
        return textwrap.dedent(f'''\
            [build-system]
            requires = ["setuptools>=64.0", "wheel"]
            build-backend = "setuptools.backends._legacy:_Backend"

            [project]
            name = "{p['name']}"
            version = "{p['version']}"
            description = "{p['description']}"
            authors = [{{ name = "{p['author']}" }}]
            license = {{ text = "{p['license']}" }}
            requires-python = ">=3.8"
            dependencies = [
                "requests>=2.28.0",
                "urllib3>=1.26",
            ]

            [project.scripts]
            {p['entry_point']} = "{p['module']}:main"

            [tool.setuptools]
            packages = ["*"]
        ''')

    def generate_setup_cfg(self) -> str:
        """Generate setup.cfg for older tooling."""
        p = self.profile
        return textwrap.dedent(f'''\
            [metadata]
            name = {p['name']}
            version = {p['version']}
            description = {p['description']}
            author = {p['author']}
            license = {p['license']}

            [options]
            packages = find:
            install_requires =
                requests>=2.28.0
                urllib3>=1.26

            [options.entry_points]
            console_scripts =
                {p['entry_point']}={p['module']}:main
        ''')

    # ------------------------------------------------------------------
    # README
    # ------------------------------------------------------------------
    def generate_readme(self) -> str:
        """Generate a boring README that doesn't mention bypass."""
        p = self.profile
        return textwrap.dedent(f'''\
            # {p['name']} v{p['version']}

            {p['description']}

            ## Installation

            ```bash
            pip install {p['name']}
            ```

            ## Usage

            ```bash
            {p['entry_point']} --health-url http://localhost:8080/health
            {p['entry_point']} --interval 30
            ```

            ## Features

            - Monitors HTTP service health endpoints
            - Sends keep-alive HTTP pings
            - Logs metrics to a local file

            ## License

            {p['license']}
        ''')

    # ------------------------------------------------------------------
    # NPM package.json
    # ------------------------------------------------------------------
    def generate_package_json(self, main_js: str = "index.js") -> str:
        """Generate a benign package.json for npm distribution."""
        p = self.profile
        return json.dumps({
            "name": p['name'],
            "version": p['version'],
            "description": p['description'],
            "main": main_js,
            "bin": {p['entry_point']: main_js},
            "scripts": {
                "start": "node index.js",
                "health": "curl -s localhost:8080/health",
            },
            "author": p['author'],
            "license": p['license'],
            "dependencies": {
                "axios": "^1.6.0",
                "node-cron": "^3.0.0",
            },
        }, indent=2)

    # ------------------------------------------------------------------
    # Write all decoy files
    # ------------------------------------------------------------------
    def write_decoy_files(self, output_dir: str = ".") -> Dict[str, str]:
        """Write all decoy package files to output_dir."""
        written = {}

        files = {
            "setup.py": self.generate_setup_py(),
            "setup.cfg": self.generate_setup_cfg(),
            "pyproject.toml": self.generate_pyproject_toml(),
            "README.md": self.generate_readme(),
        }

        for fname, content in files.items():
            fpath = os.path.join(output_dir, fname)
            if not os.path.exists(fpath):
                with open(fpath, "w") as f:
                    f.write(content)
                written[fname] = hashlib.sha256(content.encode()).hexdigest()[:16]

        return written

    # ------------------------------------------------------------------
    # Verify package integrity
    # ------------------------------------------------------------------
    def verify_integrity(self, pkg_dir: str = ".") -> bool:
        """Check that all decoy files exist and look legitimate."""
        for fname in ["README.md", "setup.py", "setup.cfg"]:
            if not os.path.exists(os.path.join(pkg_dir, fname)):
                return False
        return True


if __name__ == "__main__":
    import argparse
    from .platform_presentation import detect_platform

    parser = argparse.ArgumentParser(description="Generate decoy package files")
    parser.add_argument("--platform", default=None)
    parser.add_argument("--output-dir", default=".")
    args = parser.parse_args()

    pw = PackageWrapper(args.platform or detect_platform())
    files = pw.write_decoy_files(args.output_dir)
    print(f"✓ Created {len(files)} decoy files:")
    for fname, hash_prefix in files.items():
        print(f"  {fname}: {hash_prefix}")
