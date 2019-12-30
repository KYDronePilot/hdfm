# Commands for building HDFM PyInstaller bundles

PYINSTALLER=venv/bin/pyinstaller
MACOS_SPEC=utils/pyinstaller_mac.spec

include .env
export $(shell sed 's/=.*//' .env)

clean:
	rm -rf build/ dist/

build-macos: clean
	PYTHONPATH=src $(PYINSTALLER) --windowed \
		$(MACOS_SPEC)
	# Replace Tcl version per https://github.com/pyinstaller/pyinstaller/issues/3820
	perl -i -pe's/package require -exact Tcl ([0-9]+\.){2}[0-9]+/package require -exact Tcl 8.5.9/g' \
		dist/HDFM.app/Contents/MacOS/tcl/init.tcl
