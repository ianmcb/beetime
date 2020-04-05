base := Beeminder_Sync

default: $(base)

$(base): clean ui
	zip -jr beetime.ankiaddon beetime

ui:
	pyuic5 resources/layout/config.ui > beetime/config_layout.py

clean:
	rm -f beetime.ankiaddon
	rm -f beetime/config_layout.py
