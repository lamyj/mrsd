SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

all: html

html: Makefile 
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

flash/empty.png flash/pulse.png &: flash/figures.py
	cd $$(dirname $<) && python3 $$(basename $<)

flash_figures: flash/empty.png flash/pulse.png

multiecho/single_echo.png multiecho/multiecho.png multiecho/final.png &: multiecho/figures.py
	cd $$(dirname $<) && python3 $$(basename $<)

multiecho_figures: multiecho/single_echo.png

html: flash_figures multiecho_figures
