# Technical Overview

## Languages & Frameworks

- **Python 3.12**: Primary language for agent development.
- **MDX/Next.js**: Used for the documentation site, enabling interactive and easily maintainable guides and references.

## Key Libraries

- **uagents**: Framework for building autonomous agents, handling messaging, protocols, and agent lifecycle.
- **fastapi**: (Planned/optional) For building REST APIs or agent endpoints if needed in future extensions.
- **next-docs**: (Previously used) For documentation site structure and navigation.

## Development Setup

- **Python Environment**: Use Python 3.12. Install dependencies via `pip install -r requirements.txt`.
- **Docs Site**: MDX/Next.js files are located in `docs/pages/`. To run the docs site, use the standard Next.js workflow (e.g., `npm install` and `npm run dev` if a package.json is present).
- **Agents**: Each agent is a standalone Python script in the `agents/` directory. Run agents individually for local testing.

## Design Patterns

- **Modular Design**: Agents are implemented as independent modules, each with clear responsibilities.
- **Separation of Concerns**: Documentation, agent logic, and (future) backend services are kept in separate directories.
- **Extensibility**: The project structure allows for easy addition of new agents, documentation, or backend components.
- **Documentation-Driven Development**: Guides and references are maintained alongside code to ensure up-to-date onboarding and usage instructions.

## Additional Notes

- The project is designed for rapid prototyping and hackathon-style iteration.
- Future improvements may include more advanced backend integration, persistent storage, and automated testing.