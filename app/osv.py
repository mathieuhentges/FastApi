import requests
import re

API_URL = "https://api.osv.dev/v1/"


def post_api(endpoint: str, data, params: dict = None, headers: dict = None):
    try:
        url = API_URL + endpoint
        response = requests.post(url, json=data, params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as exc:
        return {"error": f"HTTP error {response.status_code}: {response.text}"}
    except requests.RequestException as exc:
        return {"error": f"Request failed: {exc}"}


def format_requirements(requirements: str):
    queries = []
    requirements = requirements.split("\n")
    for requirement in requirements:
        if requirement.startswith('#'):
            continue
        else:
            package = re.split(r'[=<>~!]+', requirement, maxsplit=1)
            queries.append({
                "package": {"name": package[0].strip(), "ecosystem": "PyPI"},
                **({"version": package[1].strip()} if len(package) > 1 else {})
            })
    return {"queries": queries}


def get_dependency_vulnerability(dependency: str):
    reponse = post_api("query", {
        "package": {
            "name": dependency,
            "ecosystem": "PyPI"
        }
    })
    return reponse

