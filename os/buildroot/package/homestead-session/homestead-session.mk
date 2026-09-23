# Homestead session package — installs init, session, Python userspace.
HOMESTEAD_SESSION_VERSION = 0.1.0
HOMESTEAD_SESSION_SITE = $(BR2_EXTERNAL_HOMESTEAD_PATH)/../../..
HOMESTEAD_SESSION_SITE_METHOD = local

define HOMESTEAD_SESSION_INSTALL_TARGET_CMDS
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_HOMESTEAD_PATH)/../../init/homestead-init \
		$(TARGET_DIR)/sbin/init
	$(INSTALL) -D -m 0755 $(BR2_EXTERNAL_HOMESTEAD_PATH)/../../init/homestead-session \
		$(TARGET_DIR)/usr/bin/homestead-session
	mkdir -p $(TARGET_DIR)/usr/lib/homestead $(TARGET_DIR)/usr/lib/homestead-tests
	cp -r $(BR2_EXTERNAL_HOMESTEAD_PATH)/../../../src/homestead/* \
		$(TARGET_DIR)/usr/lib/homestead/
	cp $(BR2_EXTERNAL_HOMESTEAD_PATH)/../../../tests/test_homestead.py \
		$(TARGET_DIR)/usr/lib/homestead-tests/
endef

$(eval $(generic-package))
