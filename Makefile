# Commands for building HDFM PyInstaller bundles

PYINSTALLER=venv/bin/pyinstaller
MACOS_SPEC=utils/pyinstaller_mac.spec
UBUNTU_SPEC=utils/pyinstaller_ubuntu.spec
WINDOWS_SPEC=utils/pyinstaller_windows.spec

include .env
export $(shell sed 's/=.*//' .env)

install-ubuntu-requirements:
	sudo apt-get update
	sudo apt-get install -y python3-venv virtualenv python3-dev python3-tk tk8.6-dev tcl8.6-dev

install-ubuntu-mingw-requirements:
	sudo apt-get update
	sudo apt-get install -y git mingw-w64 cmake autoconf build-essential libtool

install-pip-requirements-ubuntu:
	venv/bin/pip install -r requirements.txt

install-pip-requirements-mac:
	venv/bin/pip install -r requirements.txt
	# Fix condition in PyInstaller tkinter hook per https://github.com/pyinstaller/pyinstaller/issues/3753
	perl -i -pe"s|if 'Library/Frameworks' in path_to_tcl|if 'Library/Frameworks' in path_to_tcl and 'Python' not in path_to_tcl|g" \
		venv/lib/python3.7/site-packages/PyInstaller/hooks/hook-_tkinter.py

install-pip-requirements-windows:
	.\venv\Scripts\pip.exe install -r requirements.txt

clean-nix:
	rm -rf build/ dist/

clean-windows:
	if exist .\build del .\build
	if exist .\dist del .\dist

create-venv-ubuntu: install-ubuntu-requirements
	@if ! [ -d "./venv/" ] ; then \
		virtualenv ./venv -p $(PYTHON); \
	fi

create-venv-windows:
	IF NOT EXIST ".\venv" ( \
		$(PYTHON) -m venv venv \
	)

create-venv-mac:
	@if ! [ -d "./venv/" ] ; then \
		$(PYTHON) -m venv ./venv/; \
	fi

build-macos: create-venv-mac install-pip-requirements-mac clean-nix
	PYTHONPATH=src $(PYINSTALLER) --windowed $(MACOS_SPEC)
	# Replace Tcl version per https://github.com/pyinstaller/pyinstaller/issues/3820
	perl -i -pe's/package require -exact Tcl ([0-9]+\.){2}[0-9]+/package require -exact Tcl 8.5.9/g' \
		dist/HDFM.app/Contents/MacOS/tcl/init.tcl

build-ubuntu: create-venv-ubuntu install-pip-requirements-ubuntu clean-nix
	PYTHONPATH=src $(PYINSTALLER) $(UBUNTU_SPEC)

build-windows: create-venv-windows install-pip-requirements-windows clean-windows
	set PYTHONPATH=src
	$(PYINSTALLER) $(WINDOWS_SPEC)
