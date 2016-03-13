PREFIX ?= /usr/local
BIN_DIR = $(PREFIX)/bin
LIB_DIR = $(PREFIX)/lib/python2.7/site-packages

SRC_DIR = $(CURDIR)/twnews_consumer
SECRETS_SRC = $(SRC_DIR)/secrets.py.gpg
SECRETS_DEST = $(SRC_DIR)/secrets.py

INSTALL_TARGETS = install-dir install-package clean

install: $(INSTALL_TARGETS)

install-dir:
	install -d $(PREFIX) $(BIN_DIR) $(LIB_DIR)

unpack-secrets:
	@if [ ! -f $(SECRETS_DEST) ]; then \
		gpg --decrypt $(SECRETS_SRC) 1> $(SECRETS_DEST); \
	fi

install-package: install-dir clean unpack-secrets
	PYTHONPATH=$(LIB_DIR) python setup.py test
	PYTHONPATH=$(LIB_DIR) python setup.py install --prefix=$(PREFIX)
	@echo 'twnews-consumer successfully installed'

clean:
	@find . -name \*.pyc -delete
	@rm -rf build dist twnews_consumer.egg-info