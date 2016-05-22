base := Beeminder_Sync
version := $(shell sed -n '/^\# Version: /p' <$(base).py | awk '{print $$3}')

default: $(base) ui

$(base):
	touch $@.zip
	rm $@.zip
	zip $@.zip $@.py beetime/*py
	mv $@.zip $@-$(version).zip


ui:
	pyuic4 beetime/settings_layout.ui >beetime/settings_layout.py
