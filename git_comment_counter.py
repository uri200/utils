#!/usr/bin/env python  

import subprocess
import collections
import operator

OWNER = "magma"
REPO = "magma"
PRSTART = 7789
PREND = 10971


def findCommentsAndCount(prOrIssue, freq):
    cmd = "gh api graphql --paginate " \
      "-F owner='{}' -F name='{}' -F prOrIssue='{}' -f query='".format(
    OWNER, REPO, prOrIssue
    )
    cmd = cmd + """
query($name: String!, $owner: String!, $prOrIssue: Int!) {
  repository(owner: $owner, name: $name) {
    pullRequest: issueOrPullRequest(number: $prOrIssue) {
      __typename
      ... on PullRequest {
        reviewThreads(first: 100) {
          edges {
            node {
              comments(first: 100) {
                nodes {
                  author {
                    login
                  }
                  createdAt
                }
              }
            }
          }
          pageInfo {
            hasNextPage
            endCursor
          }
        }
        comments(first: 100) {
          nodes {
            author {
              login
            }
            createdAt
          }
        }
      }
      ... on Issue {
        id
        comments(first: 100) {
          nodes {
            author {
              login
            }
            createdAt
          }
        }
      }
    }
  }
}' | python -m json.tool | grep login | cut -d ':' -f 2 | awk '{$1=$1;print}' |
sort -n | uniq -c
"""

    res = subprocess.check_output(cmd, shell=True)
    #print(res)

    for element in res.splitlines():
        split_elements = element.strip().split(" ")
        if len(split_elements) != 2: continue
        key = split_elements[1]
        val = int(split_elements[0])
        freq[key]+=val


freq = collections.defaultdict(int)

for pr in range(PRSTART, PREND):
    findCommentsAndCount(pr, freq)
    if pr%10 == 0:
        print("{}".format(pr))
print("Done\n\n")

sorted_x = sorted(freq.items(), key=operator.itemgetter(1))
for element in sorted_x:
    print element
