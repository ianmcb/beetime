base := Beeminder_Sync
version := $(shell sed -n '/^\# Version: /p' <$(base).py | awk '{print $$3}')

default: $(base)

$(base): ui
	touch $@.zip
	rm $@.zip
	zip $@.zip $@.py beetime/*py
	mv $@.zip $@-$(version).zip


ui:
	pyuic5 beetime/resources/layout/settings.ui >beetime/settings_layout.py
