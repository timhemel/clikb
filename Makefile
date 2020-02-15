
.PHONY: test

test:
	python3 -m unittest discover -v  -p test_\*.py test

