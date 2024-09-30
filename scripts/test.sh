docker run --rm -it \
	-e DJANGO_SETTINGS_MODULE='test_settings' \
	-v $PWD/fields_of_gold:/code/fields_of_gold \
	fields-of-gold python -m django test fields_of_gold
