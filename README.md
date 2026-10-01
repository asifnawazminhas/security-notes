# Asif's Security Notes

A practical cybersecurity knowledge base covering penetration testing, red teaming, operating system security, source code review, purple teaming and vulnerability research.

**Read the notes:** [notes.asifnawazminhas.com](https://notes.asifnawazminhas.com/)

Built with MkDocs Material, the site connects assessment methodology, detailed technical notes, tool guidance and quick reference cheatsheets.

## Approach

The notes follow a consistent assessment model:

**Observation -> Candidate -> Validation -> Evidence -> Security Conclusion**

A tool result, unusual response or potentially dangerous permission is a starting point for investigation. A finding needs supporting evidence, relevant prerequisites and a clearly explained security consequence.

Practical notes aim to answer five questions:

1. **When does it apply?** Identify the relevant environment, access level and prerequisites.
2. **What should I do?** Choose a focused inspection or validation step.
3. **What should I expect?** Understand the expected behaviour and useful evidence.
4. **What does it mean?** Separate confirmed behaviour from assumptions and limitations.
5. **What follows?** Decide whether to investigate further, document, remediate or retest.

## Explore the Knowledge Base

| Section | Focus |
| --- | --- |
| [Web Application Security](docs/web/index.md) | Reconnaissance, authentication, authorisation, application behaviour, APIs and vulnerability validation |
| [Source Code Review](docs/source-code-review/index.md) | Entry points, data flow, security controls, source-to-sink analysis and static analysis |
| [Active Directory](docs/active-directory/index.md) | Identity, authentication, permissions, certificate services, delegation, trusts and attack paths |
| [Windows](docs/windows/index.md) | Host enumeration, services, scheduled tasks, permissions, credentials and security controls |
| [Linux](docs/linux/index.md) | Host enumeration, services, scheduled jobs, sudo, SUID/SGID, capabilities and security controls |
| [PrivEsc Explorer](docs/privesc/index.md) | Windows and Linux privilege escalation candidates, prerequisites and validation guidance |
| [Red Teaming](docs/red-teaming/index.md) | Engagement methodology, infrastructure, operational planning, attack paths and reporting |
| [Purple Teaming](docs/purple-teaming/index.md) | Collaborative exercises, detection engineering, knowledge transfer and continuous validation |
| [Vulnerability Research](docs/vulnerability-research/index.md) | Attack surface analysis, debugging, fuzzing, crash analysis, patch diffing and disclosure |
| [Tools](docs/tools/index.md) | Tool selection, practical usage and interpretation of results |
| [Cheatsheets](docs/cheatsheets/index.md) | Quick references for commands, testing workflows and common assessment tasks |

## Where to Start

- **Assessing a web application?** Start with [Web Application Security](docs/web/index.md) and use the [Cheatsheets](docs/cheatsheets/index.md) for quick reference.
- **Reviewing an application repository?** Start with [Source Code Review](docs/source-code-review/index.md).
- **Working from an existing host session?** Start with [Windows](docs/windows/index.md) or [Linux](docs/linux/index.md), then investigate relevant candidates in [PrivEsc Explorer](docs/privesc/index.md).
- **Investigating domain attack paths?** Start with [Active Directory](docs/active-directory/index.md).
- **Planning an engagement or exercise?** Start with [Red Teaming](docs/red-teaming/index.md) or [Purple Teaming](docs/purple-teaming/index.md).
- **Investigating a suspected software vulnerability?** Start with [Vulnerability Research](docs/vulnerability-research/index.md).

## How the Sections Fit Together

| Layer | Purpose |
| --- | --- |
| Landing pages | Orient the reader and route them to relevant topics |
| Detailed notes | Explain mechanisms, prerequisites, validation, interpretation and follow-up |
| Tools | Explain how tools support a particular assessment question |
| Cheatsheets | Provide compact reminders during practical work |
| PrivEsc Explorer | Help investigate privilege escalation candidates and their requirements |

Use the detailed notes to understand the technique, the tool pages to support the investigation, and the cheatsheets when you need a concise reminder.

## Local Build

In an existing Codespaces checkout with the project virtual environment configured:

```bash
cd /workspaces/security-notes
source .venv/bin/activate
mkdocs build
```

To preview the site while editing:

```bash
mkdocs serve
```

Open or forward the address reported by MkDocs.

## Repository Structure

```text
security-notes/
├── docs/          # Markdown notes, site assets and custom styling
├── mkdocs.yml     # Site configuration and navigation
└── README.md      # Project overview
```

The published site is the primary reading experience. Some features, including Material cards, admonitions and interactive components, may display differently when viewed directly on GitHub.

## Corrections and Suggestions

Corrections, broken link reports and suggestions are welcome through repository issues or pull requests.

For technical corrections, include:

- The affected page.
- The behaviour or statement that needs correcting.
- Relevant platform, tool or version details.
- Supporting documentation or a reproducible example.
- A proposed correction, where possible.

Do not include credentials, tokens, personal information or confidential assessment evidence.

For documentation changes:

- Link to existing Markdown source files using relative paths.
- Keep commands and examples consistent with their stated prerequisites.
- Distinguish observations, candidate paths and validated findings.
- Prefer authoritative references for technical claims.
- Build the site and resolve any new warnings before submitting.

## Responsible Use

These notes are intended for authorised security assessments, defensive validation, lab research and education.

Examples require adaptation to the target environment and agreed scope. Commands can change system state or expose sensitive information, so understand their behaviour before using them.

## Author

Maintained by [Asif Nawaz Minhas](https://github.com/asifnawazminhas).
