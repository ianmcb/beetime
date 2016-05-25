base := Beeminder_Sync
git := /home/jan/beetime-git
module := beetime
lasttemp := /tmp/Anki.last
settings := settings_layout
version := $(shell sed -n '/^\# Version: /p' <$(base).py | awk '{print $$3}')

Anki.last := $(shell cat "$(lasttemp)")

.PHONY: temp test retest

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

retest: ui |
	anki -b "$(Anki.last)"

temp:
	$(eval Anki.temp = $(shell mktemp -d /tmp/Anki.XXXXXXXXXX))
	mkdir "$(Anki.temp)/addons"
	ln -s -t "$(Anki.temp)/addons/" "$(git)/$(base).py" "$(git)/$(module)"
	@echo "$(Anki.temp)" > "$(lasttemp)"
