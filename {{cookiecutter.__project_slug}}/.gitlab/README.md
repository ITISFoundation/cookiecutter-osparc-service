# Gitlab

add the following in your __gitlab-ci.yml__ file:

```yaml
include:
  - local: '/services/{{ cookiecutter.__project_slug }}/.gitlab/gitlab-ci.yml'
```
