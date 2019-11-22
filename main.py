from dotenv import load_dotenv
from github import Github
import os
from base64 import b64decode
import time
from tqdm import tqdm

load_dotenv()
g = Github(os.getenv("ACCESS_TOKEN"))

# reads in which repos to skip
with open("already_made_issues.txt") as f:
    made_issue = f.readlines()
with open("excluded_repos.txt") as f:
    made_issue += f.readlines()
made_issue = [x.strip() for x in made_issue]

# reads in the list of strings to use in the github search
with open("search_strings.txt") as f:
    querys = f.readlines()

# reads in the text to make an issue with
# the first line of the issue is the title, all other lines are the body
with open("issue.txt") as f:
    issue = f.readlines()

suspect_repos = {}
for line in querys:
    if line.strip() == "":
        continue
    query = f'"{line.strip()}" in:file'
    print("Searching:", line.strip())

    results = g.search_code(query)

    for result in tqdm(results, total=results.totalCount, ncols=50, unit="files"):
        name = result.repository.full_name

        if f"{name}".strip() in made_issue:
            continue

        if name not in suspect_repos.keys():
            suspect_repos[name] = [0, result.repository]
        suspect_repos[name][0] += 1

        # must sleep to avoid rait limiting, make this number larger if you continue to hit rate limits
        time.sleep(0.5)


index = 0
for repo in suspect_repos:
    index += 1
    print(f"{index}: {repo}")


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

    if f"{repo}".strip() in made_issue:
        print(f"{index}: Skiping {repo}, issue was made or excluded in the past")
        continue

    with open("already_made_issues.txt", "a") as myfile:
        myfile.write(f"{repo}\n")
    print(f"{index}: Making issue for: {repo}")

    print(issue[0])
    print()
    print("".join(issue[1:]))

    # must sleep to avoid rait limiting, make this number larger if you continue to hit rate limits
    time.sleep(2)
