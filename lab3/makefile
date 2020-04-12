define generate_file
	@cat /dev/urandom | tr -dc 'a-zA-Z0-9' | fold -w $(1) | head -1
endef

test:
	$(call generate_file, 1023) > 1KB.txt
	$(call generate_file, 10239) > 10KB.txt
	$(call generate_file, 102399) > 100KB.txt
	$(call generate_file, 1048575) > 1MB.txt

	python3 test.py

