#!/bin/sh
PRODUCTNAME='collective.portlet.contact'
I18NDOMAIN=$PRODUCTNAME

# Synchronise the .pot with the templates.
i18ndude rebuild-pot --pot locales/${PRODUCTNAME}.pot --merge locales/manual.pot --create ${I18NDOMAIN} .

# Synchronise the resulting .pot with the .po files
for po in locales/*/LC_MESSAGES/${I18NDOMAIN}.po; do
    i18ndude sync --pot locales/${I18NDOMAIN}.pot $po
done

# Manually recompile a po file: 
#     msgfmt -o domain.mo domain.po
# End all po files:
#    for po in $(find . -path '*/LC_MESSAGES/*.po'); do
#        msgfmt -o ${po/%po/mo} $po;
#    done
