base := Beeminder_Sync
git := /home/jan/beetime-git
module := beetime
settings := settings_layout
version := $(shell sed -n '/^\# Version: /p' <$(base).py | awk '{print $$3}')

.PHONY: test temp

default: zip

release: test zip

zip: $(base).zip
$(base).zip: ui
	touch "$@"
	rm "$@"
	zip "$@" "$(base).py" "$(module)"/*py
	mv "$@" "$(base)-$(version).zip"


ui: $(module)/$(settings).py
$(module)/$(settings).py: $(module)/$(settings).ui
	pyuic4 "$<" > "$@"

test: ui | temp
	anki -b "$(Anki.temp)"

temp:
	$(eval Anki.tmp = $(shell mktemp -d /tmp/Anki.XXXXXXXXXX))
	mkdir "$(Anki.tmp)/addons"
	ln -s -t "$(Anki.tmp)/addons/" "$(git)/$(base).py" "$(git)/$(module)"
