SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

html: Makefile flash/empty.png flash/pulse.png
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

flash/empty.png flash/pulse.png &: flash/figures.py
	cd $$(dirname $<) && python3 $$(basename $<)
