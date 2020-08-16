GLOBAL_DEPENCIES = Makefile *.py

all: build/plugin.video.needforponies.zip build/plugin.audio.needforponies.zip

build/plugin.video.needforponies.zip: $(GLOBAL_DEPENCIES) addon_video.xml plugin_param_video.py
	rm -rf tmp/plugin.video.needforponies
	rm -f tmp/plugin.video.needforponies.zip
	mkdir -p tmp/plugin.video.needforponies
	cp *.py tmp/plugin.video.needforponies
	cp addon_video.xml tmp/plugin.video.needforponies/addon.xml
	cp plugin_param_video.py tmp/plugin.video.needforponies/plugin_param.py
	cd tmp/; zip plugin.video.needforponies.zip -r plugin.video.needforponies
	mkdir -p build
	mv tmp/plugin.video.needforponies.zip build/plugin.video.needforponies.zip

build/plugin.audio.needforponies.zip: $(GLOBAL_DEPENCIES) addon_audio.xml plugin_param_audio.py
	rm -rf tmp/plugin.audio.needforponies
	rm -f tmp/plugin.audio.needforponies.zip
	mkdir -p tmp/plugin.audio.needforponies
	cp *.py tmp/plugin.audio.needforponies
	cp addon_audio.xml tmp/plugin.audio.needforponies/addon.xml
	cp plugin_param_audio.py tmp/plugin.audio.needforponies/plugin_param.py
	cd tmp/; zip plugin.audio.needforponies.zip -r plugin.audio.needforponies
	mkdir -p build
	mv tmp/plugin.audio.needforponies.zip build/plugin.audio.needforponies.zip

clean:
	rm -rf tmp build
