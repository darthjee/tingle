"use strict";

// Fatal entrypoint error. `status` is the process exit status (1 unless a
// tool's own non-zero status is passed through).
class EntrypointError extends Error {
  constructor(message, status = 1) {
    super(message);
    this.name = "EntrypointError";
    this.status = status;
  }
}

module.exports = { EntrypointError };
