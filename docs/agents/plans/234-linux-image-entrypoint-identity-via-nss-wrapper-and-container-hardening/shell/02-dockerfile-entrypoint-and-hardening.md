# Wire the entrypoint and hardening into the Dockerfile
Update `shell/linux/Dockerfile` (final stage only):

- Add `libnss-wrapper=<version>` to the pinned apt list, pinned against `UBUNTU_SNAPSHOT`. Put it in a sensible group, for example a new `# identity` comment group, and keep the list alphabetised within that group.
- Add `COPY --chmod=0755 shell/linux/entrypoint.sh /usr/local/bin/tingle-entrypoint`. The build context is the repo root.
- In the user-creation `RUN`, after `useradd`:
  - `mkdir -p /home/tingle/.ssh`;
  - `chmod 1777 /home/tingle /home/tingle/.ssh`;
  - `find / -xdev -perm /6000 -type f -exec chmod a-s {} +`.

  This must run as root, before `USER tingle`, and after every apt install and `COPY`, so that no setuid or setgid binary is left in the image.
- After `USER tingle`: `ENTRYPOINT ["/usr/local/bin/tingle-entrypoint"]` and `CMD ["bash"]`. Setting `ENTRYPOINT` clears the `CMD` inherited from ubuntu, so the explicit `CMD` is required.
- Update the header comment:
  - add `libnss-wrapper` and the entrypoint to the contents;
  - replace the "No CMD/ENTRYPOINT is set" paragraph with the entrypoint's role: identity for a foreign uid, `HOME`, the ssh wrapper, and the default `bash`;
  - describe the hardening (no setuid or setgid binaries, read-only `/etc/passwd`, `no-new-privileges` set by `docker_run`).

## Files to Change
- `shell/linux/Dockerfile`: new package, entrypoint `COPY`, permissions, setuid/setgid strip, `ENTRYPOINT`/`CMD`, header comment.
