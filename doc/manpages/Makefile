#Makefile friendly inspired by https://gist.github.com/bertvv/e77e3a5d24d8c2a9bcc4

#source and output directory
source := src
output := man

#all Markdown files in source directory are considered
sources := $(wildcard $(source)/*.md)

#convert the list of source files (Markdown files in directory src/)
#into a list of output files (GZIPs in man/ directory)
objects := $(patsubst %.md,%.gz,$(subst $(source),$(output),$(sources)))

#default make target
all: $(objects)

#recipe for converting markdown to manpage and gzipping it afterwards
$(output)/%.gz: $(source)/%.md
	pandoc $< -s -t man | gzip -f > $@

.PHONY : clean

#clean _all_ the rubbish
clean:
	rm -f $(output)/*.gz
