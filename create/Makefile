all:
	./create_csv.py
	latexrun timetable.tex

export: all
	mv timetable.pdf revision.csv ..

clean:                                  
	rm -rf latex.out
	rm revision.csv
	rm timetable.pdf
