"""One-time bootstrap: creates the user/workspace/account the M2 Dify
candidate's Start form asks for. Run once (idempotent -- safe to re-run,
returns the same ids). Prints the workspace_id / account_id to paste into
the Dify Start form.

Usage (from a container on docker_default, or anywhere that can reach the
M2 API base URL):
    python3 bootstrap_demo_workspace.py [API_BASE]
"""

import sys

import httpx

API_BASE = sys.argv[1] if len(sys.argv) > 1 else "http://diyu-m2-app:8000"


def main():
    with httpx.Client(base_url=API_BASE, timeout=10.0) as client:
        user = client.post(
            "/users", json={"external_ref": "founder-dify-candidate-demo", "display_name": "Founder (Dify candidate demo)"}
        ).json()
        actor_ref = user["external_ref"]
        ws = client.post(
            "/workspaces",
            json={"name": "M2 Dify Candidate Demo Workspace", "kind": "personal", "owner_user_id": user["id"]},
        ).json()
        # every workspace-scoped call requires X-Actor-Ref -- the workspace
        # owner (this user) is the only member who can call it right after
        # create_workspace.
        account = client.post(
            f"/workspaces/{ws['id']}/accounts",
            json={"platform": "test-platform", "handle": "m2-candidate-demo-account"},
            headers={"X-Actor-Ref": actor_ref},
        ).json()

    print("actor_ref:    ", actor_ref)
    print("user_id:      ", user["id"])
    print("workspace_id: ", ws["id"])
    print("account_id:   ", account["id"])
    print()
    print("Paste actor_ref, workspace_id and account_id into the Dify Start form.")


if __name__ == "__main__":
    main()
