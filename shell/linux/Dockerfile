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
        coreutils=9.4-3ubuntu6.3 \
        findutils=4.9.0-5build1 \
        grep=3.11-4build1 \
        sed=4.9-2ubuntu0.24.04.1 \
        gawk=1:5.2.1-2ubuntu0.1 \
        tar=1.35+dfsg-3ubuntu0.4 \
        diffutils=1:3.10-1ubuntu0.1 \
    && rm -rf /var/lib/apt/lists/*

RUN userdel --remove ubuntu 2>/dev/null; \
    useradd --create-home --uid 1000 tingle
USER tingle
