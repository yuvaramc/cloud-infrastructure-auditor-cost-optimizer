from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_application_packages_exist():
    required_packages = [
        "app",
        "app/cli",
        "app/auth",
        "app/audit",
        "app/reporting",
        "app/cleanup",
        "app/core",
        "app/providers",
        "app/providers/aws",
        "app/providers/gcp",
    ]

    for package in required_packages:
        package_path = PROJECT_ROOT / package
        assert package_path.is_dir(), f"Missing package directory: {package}"
        assert (package_path / "__init__.py").is_file(), (
            f"Missing __init__.py: {package}"
        )


def test_required_project_directories_exist():
    required_directories = [
        "tests",
        "docs",
    ]

    for directory in required_directories:
        assert (PROJECT_ROOT / directory).is_dir(), (
            f"Missing project directory: {directory}"
        )


def test_project_configuration_exists():
    assert (PROJECT_ROOT / "pyproject.toml").is_file()
    assert (PROJECT_ROOT / "README.md").is_file()