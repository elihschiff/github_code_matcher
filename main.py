from dotenv import load_dotenv
from github import Github
import os
from base64 import b64decode
import time
from tqdm import tqdm

load_dotenv()
g = Github(os.getenv("ACCESS_TOKEN"))

# reads in which repos to skip
# with open("already_made_issues.txt") as f:
#     made_issue = f.readlines()

excluded_repos = []
with open("excluded_repos.txt") as f:
    excluded_repos += f.readlines()
excluded_repos = [x.strip() for x in excluded_repos]

# reads in the list of strings to use in the github search
with open("search_strings.txt") as f:
    querys = f.readlines()

# reads in the text to make an issue with
# the first line of the issue is the title, all other lines are the body
with open("issue.txt") as f:
    issue = f.readlines()

suspect_repos = {}
for line in querys:
    if line.strip() == "" or line.strip().startswith("##"):
        continue
    query = f'"{line.strip()}" in:file'
    print("Searching:", line.strip())

    results = g.search_code(query)

    for result in tqdm(results, total=results.totalCount, ncols=50, unit="files"):
        name = result.repository.full_name

        if f"{name}".strip() in excluded_repos:
            continue

        if name not in suspect_repos.keys():
            suspect_repos[name] = [0, result.repository]
        suspect_repos[name][0] += 1

        # must sleep to avoid rait limiting, make this number larger if you continue to hit rate limits
        time.sleep(1.5)
    time.sleep(30)

index = 0
for repo in suspect_repos:
    index += 1
    print(f"{index}: https://github.com/{repo}")


print('==> Repos to exclude: (eg: "4", "1 2 3").')
repos_to_exclude = input("==> ").strip().split()
repos_to_exclude = [int(x) for x in repos_to_exclude]

index = 0
for repo in tqdm(suspect_repos, ncols=50, unit="repos"):
    index += 1

    if index in repos_to_exclude:
        with open("excluded_repos.txt", "a") as myfile:
            myfile.write(f"{repo}\n")
        print(f"{index}: Excluding {repo}")
        continue

    if f"{repo}".strip() in excluded_repos:
        print(f"{index}: Skiping {repo}, issue was excluded in the past")
        continue

    issue_user = "elihschiff"
    if suspect_repos[repo][1].get_issues(creator=issue_user).totalCount != 0:
        print(
            f"{index}: Skiping {repo}, issue already made by {issue_user} on this repo"
        )
        continue

    # with open("already_made_issues.txt", "a") as myfile:
    #     myfile.write(f"{repo}\n")

    # uncomment the next line only when you are ready to actually add issues
    # suspect_repos[repo][1].create_issue(title=issue[0], body="".join(issue[1:]))

    # must sleep to avoid rait limiting, make this number larger if you continue to hit rate limits
    time.sleep(10)
