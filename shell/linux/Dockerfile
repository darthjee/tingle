# GNU toolbox image for the `tingle linux` command.
#
# Provides a baseline of GNU coreutils, findutils, grep, sed, gawk, tar and
# diffutils, running as a non-root user (uid 1000) so files touched through
# a volume mount are owned correctly on the host.
#
# No CMD/ENTRYPOINT is set — every subcommand supplies its own command via
# `docker run <image> <cmd> <args...>`.
FROM ubuntu:24.04

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        coreutils \
        findutils \
        grep \
        sed \
        gawk \
        tar \
        diffutils \
    && rm -rf /var/lib/apt/lists/*

RUN userdel --remove ubuntu 2>/dev/null; \
    useradd --create-home --uid 1000 tingle
USER tingle
