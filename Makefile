help:
	# release: 发布
	# clean: 清除缓存

release:
	rm -rf build dist
	python setup.py sdist
	twine upload dist/*

clean:
	rm -rf build dist
	rm -rf __pycache__
	rm -rf iydon/__pycache__
	rm -rf iydon.egg-info
