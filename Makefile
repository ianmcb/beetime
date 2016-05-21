version := $(shell sed -n '/^\# Version: /p' <Beeminder_Time_Sync.py | awk '{print $$3}')

default: ui
	touch Beeminder_Time_Sync.zip
	rm Beeminder_Time_Sync.zip
	zip Beeminder_Time_Sync.zip Beeminder_Time_Sync.py beetime/*py
	cp Beeminder_Time_Sync.zip Beeminder_Time_Sync-$(version).zip

ui:
	pyuic4 beetime/beeminder_settings_layout.ui >beetime/beeminder_settings_layout.py
