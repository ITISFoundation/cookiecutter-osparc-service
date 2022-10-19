#
# CONVENTIONS:
#
# - targets shall be ordered such that help list rensembles a typical workflow, e.g. 'make devenv tests'
# - add doc to relevant targets
# - internal targets shall start with '.'
# - KISS
#
SHELL = /bin/bash
.DEFAULT_GOAL := help

OUTPUT_DIR = $(CURDIR)/.output
TEMPLATE = $(CURDIR)
VERSION := $(shell cat VERSION)

#-----------------------------------
.PHONY: devenv
.venv:
	@python3 --version
	python3 -m venv $@
	# upgrading package managers
	$@/bin/pip install --upgrade \
		pip \
		wheel \
		setuptools

requirements.txt: requirements.in
	# freezes requirements
	.venv/bin/pip-compile --upgrade --build-isolation --output-file $@ $(word2, $^)

devenv: .venv  ## create a python virtual environment with tools to dev, run and tests cookie-cutter
	# installing extra tools
	@$</bin/pip3 install -r requirements.txt
	# your dev environment contains
	@$</bin/pip3 list
	@echo "To activate the virtual environment, run 'source $</bin/activate'"


.PHONY: tests
tests: ## tests backed cookie
	@pytest -vv \
		--basetemp=$(CURDIR)/tmp \
		--exitfirst \
		--failed-first \
		--durations=0 \
		--pdb \
		$(CURDIR)/tests


#-----------------------------------
.PHONY: play

$(OUTPUT_DIR):
	# creating $@
	@mkdir -p $@

define cookiecutterrc =
$(shell find $(OUTPUT_DIR) -name ".cookiecutterrc" 2>/dev/null | tail -n 1 )
endef


play: $(OUTPUT_DIR) ## runs cookiecutter into output folder
ifeq (,$(cookiecutterrc))
	# baking cookie $(TEMPLATE) onto $<
	@cookiecutter --output-dir "$<" "$(TEMPLATE)"
else
	# replaying cookie-cutter using $(cookiecutterrc)
	@cookiecutter --no-input -f \
		--config-file="$(cookiecutterrc)"  \
		--output-dir="$<" "$(TEMPLATE)"
endif
	@echo "To see generated code, lauch 'code $(OUTPUT_DIR)'"



.PHONY: version-patch version-minor version-major
version-patch version-minor version-major: ## commits version as patch (bug fixes not affecting the API), minor/minor (backwards-compatible/INcompatible API addition or changes)
	# upgrades as $(subst version-,,$@) version, commits and tags
	@bump2version --verbose  --list $(subst version-,,$@)


#-----------------------------------
.PHONY: help
# thanks to https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help: ## this colorful help
	@echo "Recipes for '$(notdir $(CURDIR))':"
	@echo ""
	@awk --posix 'BEGIN {FS = ":.*?## "} /^[[:alpha:][:space:]_-]+:.*?## / {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""

git_clean_args = -dxf --exclude=.vscode/ --exclude=.venv/ --exclude=.python

.PHONY: clean clean-force
clean: ## cleans all unversioned files in project and temp files create by this makefile
	# Cleaning unversioned
	@git clean -n $(git_clean_args)
	@echo -n "Are you sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@echo -n "$(shell whoami), are you REALLY sure? [y/N] " && read ans && [ $${ans:-N} = y ]
	@git clean $(git_clean_args)
	-rm -rf $(OUTPUT_DIR)

clean-force: clean
	# removing .venv
	-@rm -rf .venv


.PHONY: info
info: ## displays info about the scope
	# python
	@echo $(shell which python)
	@python --version
	@echo $(shell which pip)




# RELEASE -------------------------------------------------------------------------------

prod_prefix := v
_git_get_current_branch = $(shell git rev-parse --abbrev-ref HEAD)

# NOTE: be careful that GNU Make replaces newlines with space which is why this command cannot work using a Make function
_url_encoded_title = $(VERSION)
_url_encoded_tag = $(prod_prefix)$(VERSION)
_url_encoded_target = $(if $(git_sha),$(git_sha),$(if $(findstring -hotfix, $@),$(_git_get_current_branch),master))
_prettify_logs = $$(git log \
		$$(git describe --match="$(prod_prefix)*" --abbrev=0 --tags)..$(if $(git_sha),$(git_sha),HEAD) \
		--pretty=format:"- %s")
define _url_encoded_logs
$(shell \
	scripts/url-encoder.bash \
	"$(_prettify_logs)"\
)
endef
_git_get_repo_orga_name = $(shell git config --get remote.origin.url | \
							grep --perl-regexp --only-matching "((?<=git@github\.com:)|(?<=https:\/\/github\.com\/))(.*?)(?=.git)")

.PHONY: .check-master-branch
.check-master-branch:
	@if [ "$(_git_get_current_branch)" != "master" ]; then\
		echo -e "\e[91mcurrent branch is not master branch."; exit 1;\
	fi

.PHONY: release
release pre-release: .check-master-branch ## Creates github release link. Usage: make release-prod git_sha=optional
	# ensure tags are up-to-date
	@git pull --tags
	@echo -e "\e[33mOpen the following link to create a release:";
	@echo -e "\e[32mhttps://github.com/$(_git_get_repo_orga_name)/releases/new?prerelease=$(if $(findstring pre-, $@),1,0)&target=$(_url_encoded_target)&tag=$(_url_encoded_tag)&title=$(_url_encoded_title)&body=$(_url_encoded_logs)";
	@echo -e "\e[33mOr open the following link to create a release and paste the logs:";
	@echo -e "\e[32mhttps://github.com/$(_git_get_repo_orga_name)/releases/new?prerelease=$(if $(findstring pre-, $@),1,0)&target=$(_url_encoded_target)&tag=$(_url_encoded_tag)&title=$(_url_encoded_title)";
	@echo -e "\e[34m$(_prettify_logs)"
