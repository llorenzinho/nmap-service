from concurrent.futures import ThreadPoolExecutor, as_completed

from invoke.context import Context
from invoke.tasks import task


def format_block(c: Context, target: str):
    c.run(f"echo Formatting {target}")
    c.run(f"poetry run autoflake {target}")
    c.run(f"poetry run isort {target} --settings-path pyproject.toml")
    c.run(f"poetry run black {target} --config pyproject.toml")


@task
def swag(c: Context):
    """Run formatters and linters."""
    blocks = [
        "tasks.py",
        "src/nmap_service",
        "tests",
    ]
    errors = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(format_block, c, path): path for path in blocks}

        for future in as_completed(futures):
            path = futures[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error while formatting {path}: {e}")
                errors.append(path)


@task
def bump(c: Context):
    c.run("poetry run cz bump --changelog --yes")
