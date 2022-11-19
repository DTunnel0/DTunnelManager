run:
	python3 -m app

clean:
	@echo 'Cleaning up...'
	rm -rf build dist *.egg-info *.spec

build:
	$(MAKE) clean
	@echo 'Building...'
	pyinstaller --onefile --windowed --name=vps main.py 1>/dev/null 2>&1