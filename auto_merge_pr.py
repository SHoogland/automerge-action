#!/usr/bin/env python
# -*- encoding: utf-8

import json
import os
import requests

def create_session(github_token):
    sess = requests.Session()
    sess.headers = {
        "Accept": "; ".join([
            "application/vnd.github.v3+json",
            "application/vnd.github.antiope-preview+json",
        ]),
        "Authorization": f"token {github_token}",
        "User-Agent": f"GitHub Actions script in {__file__}"
    }

    def raise_for_status(resp, *args, **kwargs):
        try:
            resp.raise_for_status()
        except Exception:
            print(resp.text)
            sys.exit("Error: Invalid repo, token or network issue!")

    sess.hooks["response"].append(raise_for_status)
    return sess


if __name__ == "__main__":
    event_path = os.environ["GITHUB_EVENT_PATH"]
    event_data = json.load(open(event_path))

    check_suite = event_data["check_suite"]

    if check_suite["status"] != "completed":
        print(f"*** Check suite has not completed")
        sys.exit(78)

    if check_suite["conclusion"] != "success":
        print(f"*** Check suite has not succeeded")
        sys.exit(1)

    assert len(check_suite["pull_requests"]) == 1
    pull_request = check_suite["pull_requests"][0]
    pr_number = pull_request["number"]
    pr_src = pull_request["head"]["ref"]
    pr_dst = pull_request["base"]["ref"]

    print(f"*** Checking pull request #{pr_number}: {pr_src} ~> {pr_dst}")

    github_token = os.environ["GITHUB_TOKEN"]

    sess = create_session(github_token)

    pr_data = sess.get(pull_request["url"]).json()

    pr_title = pr_data["title"]
    print(f"*** Title of PR is {pr_title!r}")

    pr_user = pr_data["user"]["login"]
    print(f"*** This pull request was opened by {pr_user}")
    if pr_user != "dependabot":
        print("*** This pull request was opened by somebody who isn't dependabot")
        quit()

    print("*** This pull request is ready to be merged.")
    merge_url = pull_request["url"] + "/merge"
    sess.put(merge_url)

    print("*** Cleaning up pull request branch")
    pr_ref = pr_data["head"]["ref"]
    api_base_url = pr_data["base"]["repo"]["url"]
    ref_url = f"{api_base_url}/git/refs/heads/{pr_ref}"
    sess.delete(ref_url)
