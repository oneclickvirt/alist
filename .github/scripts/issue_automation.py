"""Small REST replacement for the unavailable issues-helper action."""
import datetime
import json
import os
import urllib.error
import urllib.parse
import urllib.request

repo = os.environ['GITHUB_REPOSITORY']
event = json.load(open(os.environ['GITHUB_EVENT_PATH']))
action = os.environ['ISSUE_ACTION']

def call(path, method='GET', body=None):
    req = urllib.request.Request('https://api.github.com/repos/' + repo + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Authorization': 'Bearer ' + os.environ['ISSUE_TOKEN'], 'Accept': 'application/vnd.github+json', 'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        data = response.read()
    return json.loads(data) if data else None

def close(issue):
    body = os.environ.get('ISSUE_BODY', '').replace('{user}', issue['user']['login'])
    if body:
        call('/issues/' + str(issue['number']) + '/comments', 'POST', {'body': body})
    call('/issues/' + str(issue['number']), 'PATCH', {'state': 'closed', 'state_reason': os.environ.get('ISSUE_CLOSE_REASON', 'completed')})

if action == 'close-issues':
    cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=int(os.environ['ISSUE_INACTIVE_DAYS']))
    labels = urllib.parse.quote(os.environ.get('ISSUE_LABELS', ''), safe='')
    for page in range(1, 101):
        issues = call('/issues?state=open&labels=' + labels + '&per_page=100&page=' + str(page))
        for issue in issues:
            if 'pull_request' not in issue and datetime.datetime.fromisoformat(issue['updated_at'].replace('Z', '+00:00')) < cutoff:
                close(issue)
        if len(issues) < 100:
            break
else:
    issue = event['issue']
    prefix = '/issues/' + str(issue['number'])
    if action == 'create-comment':
        body = os.environ['ISSUE_BODY'].replace('{user}', issue['user']['login'])
        call(prefix + '/comments', 'POST', {'body': body})
    elif action == 'close-issue':
        call(prefix, 'PATCH', {'state': 'closed', 'state_reason': os.environ.get('ISSUE_CLOSE_REASON', 'completed')})
    elif action == 'remove-labels':
        current = {label['name'] for label in issue.get('labels', [])}
        for label in os.environ['ISSUE_LABELS'].split(','):
            if label.strip() in current:
                call(prefix + '/labels/' + urllib.parse.quote(label.strip(), safe=''), 'DELETE')
    else:
        raise ValueError('Unsupported issue action')
