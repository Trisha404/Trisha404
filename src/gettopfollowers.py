"""
   Copyright 2020 Yufan You <https://github.com/ouuan>

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and limitations under the License.
"""

import requests
import sys
import re

if __name__ == "__main__":
    assert(len(sys.argv) == 4)
    handle = sys.argv[1]
    token = sys.argv[2]
    readmePath = sys.argv[3]

    headers = {
        "Accept": "application/vnd.github.v3+json",
        "Authorization": f"token {token}"
    }

    followers = []

    for i in range(1, 100000):
        page = requests.get(f"https://api.github.com/users/{handle}/followers?page={i}&per_page=100", headers = headers).json()
        if len(page) == 0:
            break
        for follower in page:
            info = requests.get(follower["url"], headers = headers).json()
            if info["following"] > 5000 and info["public_repos"] < 50:
                print(f"Ignored: https://github.com/{info['login']} with {info['followers']} followers and {info['following']} following")
                continue
            followers.append((info["followers"], info["login"], info["id"], info["name"] if info["name"] else info["login"]))
            print(followers[-1])

    followers.sort(reverse = True)

    html = "<table>\n"

    for i in range(min(len(followers), 14)):
        login = followers[i][1]
        id = followers[i][2]
        name = followers[i][3]
        if i % 7 == 0:
            if i != 0:
                html += "  </tr>\n"
            html += "  <tr>\n"
        html += f'''    <td align="center">
      <a href="https://github.com/{login}">
        <img src="https://avatars2.githubusercontent.com/u/{id}" width="100px;" alt="{login}"/>
      </a>
      <br />
      <a href="https://github.com/{login}">{name}</a>
    </td>
'''

    html += "  </tr>\n</table>"

    with open(readmePath, "r") as readme:
        content = readme.read()

    newContent = re.sub(r"(?<=<!\-\-START_SECTION:top\-followers\-\->)[\s\S]*(?=<!\-\-END_SECTION:top\-followers\-\->)", f"\n{html}\n", content)

    with open(readmePath, "w") as readme:
        readme.write(newContent)
Go back to your README.md file.
Add the following section to your README.md file; you can give whatever title you want. Just make sure that you use <!--START_SECTION:top-followers—> <!--END_SECTION:top-followers—> in your readme. The workflow will replace this comment with the actual blog post list:
# My followers
<!--START_SECTION:top-followers--> 
<!--END_SECTION:top-followers-->
Go back to the **.github** folder.
Create a new file named topFollowers.yml with the following contents inside the workflows folder:
name: Get Top Followers

on:
  push:
    branches:
      - master
  schedule:
    - cron: '0 20 * * *'

jobs:
  top-followers:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup python
        uses: actions/setup-python@v2
        with:
          python-version: 3.8
      - name: Install requests
        run: pip install requests
      - name: Update README
        run: python src/getTopFollowers.py ${{ github.repository_owner }} ${{ secrets.GITHUB_TOKEN }} README.md
      - name: Commit changes
        run: |
          git config --local user.email "action@github.com"
          git config --local user.name "GitHub Action"
          git add -A
          git diff-index --quiet HEAD || git commit -m "Update top followers"
      - name: Pull changes
        run: git pull -r
      - name: Push changes
        uses: ad-m/github-push-action@master
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
