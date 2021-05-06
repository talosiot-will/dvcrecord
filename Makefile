SRC = $(wildcard ./*.ipynb)
SHELL=/bin/bash -o pipefail

it: 
	. .venv/bin/activate && nbdev_read_nbs
	. .venv/bin/activate && nbdev_build_lib
	. .venv/bin/activate && nbdev_clean_nbs
	git status

test:
	. .venv/bin/activate && nbdev_test_nbs

readme:
	. .venv/bin/activate && nbdev_build_docs
	touch docs

clean:
	rm -rf dist

github:
	act -P ubuntu-latest=wgathright/github_workflow_tester

env:
	virtualenv .venv -p python3.8 --prompt "[$(shell basename "`pwd`")] "
	. .venv/bin/activate && pip install jupyter jupyterlab nbdev
	. .venv/bin/activate && pip install -e .

server:
	. .venv/bin/activate && jupyter lab --ip 0.0.0.0

