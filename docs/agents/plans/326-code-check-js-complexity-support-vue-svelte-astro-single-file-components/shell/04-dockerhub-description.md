# Docker Hub description and header comments

In `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` (around line 34, where it
says files with an unsupported extension are refused):

- add `.vue`, `.svelte` and `.astro` to the accepted extensions;
- add a short "Single-file components" paragraph: only the script blocks (and
  the Astro frontmatter) are analysed, line numbers are the original ones, a
  component with no script is OK 0, and an unknown `lang` or an unterminated
  frontmatter is a parse error.

Update `DOCKERHUB_SHORT_DESCRIPTION.txt` only if it lists extensions.

## Files to Change
- `docker/js_complexity/DOCKERHUB_DESCRIPTION.md` — the SFC support.
- `docker/js_complexity/DOCKERHUB_SHORT_DESCRIPTION.txt` — only if it lists
  extensions.
