FROM python:3-alpine

MAINTAINER Stephan Hoogland <stephan@shoogland.com>

LABEL "com.github.actions.name"="Auto-merge pull requests"
LABEL "com.github.actions.description"="Merge the pull request after the checks pass"
LABEL "com.github.actions.icon"="activity"
LABEL "com.github.actions.color"="green"

RUN pip3 install requests

COPY auto_merge_pr.py /
ENTRYPOINT ["python3", "/auto_merge_pr.py"]
