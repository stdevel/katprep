#Makefile friendly inspired by https://gist.github.com/bertvv/e77e3a5d24d8c2a9bcc4

#source and output directory
source := src
output := man
output_rst := ../source

#all Markdown files in source directory are considered
sources := $(wildcard $(source)/*.md)

#convert the list of source files (Markdown files in directory src/)
#into a list of output files (GZIPs in man/ directory)
objects := $(patsubst %.md,%.gz,$(subst $(source),$(output),$(sources)))
#convert the list of source files (Markdown files in directory src/)
#into a list of output files (rst files)
objects_rst := $(patsubst %.md,%.rst,$(subst $(source),$(output_rst),$(sources)))

#default make target
all: $(objects) $(objects_rst)
#all: $(objects)

#recipe for converting markdown to manpage and gzipping it afterwards
$(output)/%.gz: $(source)/%.md
	pandoc $< -s -t man | gzip -f > $@

#recipe for also exporting to markdown and copying it to the main documentation
$(output_rst)/%.rst: $(source)/%.md
	pandoc $< --from=markdown -t rst --output $@

.PHONY : clean

#clean _all_ the rubbish
clean:
	rm -f $(output)/*.gz
	rm -f $(output_rst)/*.1.rst
	rm -f $(output_rst)/*.5.rst
