# Release checklist

Use this checklist before publishing a public release.

## v0.1.0 public foundation

The first release should prove that the project is real, understandable, and safe to inspect publicly.

## Repository basics

- [ ] README explains the project clearly
- [ ] repository name matches the project focus
- [ ] license is included
- [ ] security policy is included
- [ ] contribution guide is included
- [ ] roadmap is included
- [ ] open issues describe planned work

## Documentation

- [ ] architecture document exists
- [ ] setup guide exists
- [ ] testing checklist exists
- [ ] Supabase setup docs exist
- [ ] n8n technical notes exist
- [ ] optional dashboard notes exist
- [ ] security and secrets guide exists

## Supabase

- [ ] public schema example exists
- [ ] schema uses placeholder defaults
- [ ] no real account names are included
- [ ] no real account IDs are included
- [ ] no real project URLs are included
- [ ] no real tokens or service keys are included

## n8n workflows

- [ ] webhook workflow template exists
- [ ] queue worker workflow template exists
- [ ] workflows are inactive by default
- [ ] all private credentials are removed
- [ ] all production metadata is removed
- [ ] no real account IDs are included
- [ ] no hardcoded private tokens are included
- [ ] every Supabase node uses placeholder credentials or user-owned credentials
- [ ] template README explains setup after import

## Optional dashboard

- [ ] dashboard is documented as optional
- [ ] raw private dashboard code is not published before sanitization
- [ ] hardcoded API keys are removed before any public dashboard release
- [ ] debug routes are documented as private/protected

## Safety review

Search the repository for these strings before release:

```text
token
secret
apikey
Authorization
Bearer
supabase.co
service_role
access_token
private
localhost
```

Review every match manually. Some words are expected in documentation, but no real private values should be present.

## Release notes draft

Suggested v0.1.0 title:

```text
v0.1.0 - Public foundation
```

Suggested release summary:

```text
Initial public foundation for a self-hosted Instagram comment-to-DM automation toolkit powered by n8n, Supabase and Meta APIs.

This release includes project documentation, security guidelines, Supabase schema example, setup guide, testing checklist, roadmap, and initial sanitized workflow templates.
```

## Before applying to any OSS support program

- [ ] repository is public
- [ ] README is clear and specific
- [ ] project purpose is obvious within 30 seconds
- [ ] workflow templates are visible
- [ ] setup docs are visible
- [ ] roadmap/issues show active maintenance
- [ ] no private secrets are exposed
- [ ] application story is honest about project size and current status
