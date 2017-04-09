sorted-clusters.txt: tokens.csv
	./cluster.py | sort > $@

tokens.csv:
	./count.py

