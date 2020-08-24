.PHONY: install_rain

## Install Rain on OSX
install_rain:
	mkdir -p rain_source
	wget https://github.com/aws-cloudformation/rain/releases/download/v0.7.2/rain-v0.7.2_osx-i386.zip -O rain_source/rain.zip
	unzip -o rain_source/rain.zip -d rain_source/
	cp rain_source/dist/rain-v0.7.2_osx-i386/rain /usr/local/bin/
	rm -rf ./rain_source
	@echo "Installation completed - rain"