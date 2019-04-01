all: timetable pdf

csv: timetable

timetable:
	./create_csv.py

pdf: timetable
	latexrun timetable.tex

export: all
	cp timetable.pdf revision.csv ..

clean:                                  
	rm -rf latex.out
	rm revision.csv
	rm timetable.pdf
