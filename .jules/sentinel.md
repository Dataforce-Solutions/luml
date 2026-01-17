## 2024-05-22 - [Broken Access Control in Invite Acceptance]
**Vulnerability:** Found that `accept_invite` and `reject_invite` did not verify if the current user was the intended recipient of the invitation. Any user could accept or reject any invite if they knew the invite ID.
**Learning:** Checking for "authentication" is not enough. You must always verify "authorization" (permission to act on a specific resource). Just because `request.user` exists doesn't mean they own the invite.
**Prevention:** Always verify ownership of resources before performing actions. Pass the authenticated user's identity (ID, email) to the service layer and validate it against the resource being accessed.
