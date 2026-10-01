# frozen_string_literal: true

# Entrypoint of the tingle_rubycritic image (`tingle code_check rubycritic`).
#
# Usage (inside the container, working directory /src):
#   printf '%s\n' app/a.rb lib/b.rb | ruby /opt/tingle_rubycritic/entrypoint.rb
#
# Input:  stdin, one file path per line, relative to the working directory.
#         Blank lines are ignored; duplicates are kept once, at their first
#         position. Arguments are ignored.
# Output: stdout, exactly one JSON object followed by "\n": RubyCritic's
#         report.json plus a top-level "parse_errors" key. Everything else
#         (RubyCritic's own stdout and stderr included) goes to stderr.
# Exit:   0 when the JSON was printed; RubyCritic's status when it fails;
#         1 on any other failure (one-line reason on stderr).
#
# Files RubyCritic 5.0.0 can't parse would abort the whole run (Reek raises on
# the first syntax error), so every path is pre-parsed with Reek's own parser
# first. Failures go to "parse_errors" and are not passed to RubyCritic.
#
# Dependencies: the locked bundle (rubycritic 5.0.0, reek) from
# /opt/tingle_rubycritic/Gemfile.lock.
#
# Contract: docs/agents/specs/code_check/rubycritic/image.md (section 4).

# Real stdout, written to once at the very end. Anything printed through
# $stdout before that (warnings, library output) goes to stderr instead.
OUTPUT = $stdout.dup
$stdout = $stderr

require "bundler/setup"
require "fileutils"
require "json"
require "reek"
require "set"

REPORT_DIR = "/tmp/out"
REPORT_PATH = File.join(REPORT_DIR, "report.json")

def fail_with(reason, status = 1)
  warn("tingle_rubycritic: #{reason.to_s.lines.first.to_s.strip}")
  exit(status)
end

def read_paths
  data = $stdin.binmode.read
  seen = Set.new
  data.split("\n".b).each_with_object([]) do |line, paths|
    next if line.strip.empty?

    path = line.force_encoding(Encoding::UTF_8)
    paths << path if seen.add?(path)
  end
end

def pre_parse(paths)
  parse_errors = []
  survivors = paths.select do |path|
    Reek::Source::SourceCode.new(source: File.read(path), origin: path).syntax_tree
    true
  rescue StandardError, ScriptError => e
    parse_errors << { "path" => path, "message" => e.message.to_s.lines.first.to_s.strip }
    false
  end
  [survivors, parse_errors]
end

def run_rubycritic(paths)
  FileUtils.rm_rf(REPORT_DIR)
  command = ["bundle", "exec", "rubycritic", "--format", "json", "--no-browser", "-p", REPORT_DIR, *paths]
  system(*command, out: $stderr, err: $stderr)
  status = $?
  fail_with("could not run rubycritic") if status.nil?
  return if status.success?

  code = status.exitstatus
  fail_with("rubycritic exited with status #{code || status}", code.nil? || code.zero? ? 1 : code)
end

def read_report
  fail_with("#{REPORT_PATH} is missing") unless File.file?(REPORT_PATH)

  report = JSON.parse(File.read(REPORT_PATH))
  fail_with("#{REPORT_PATH} is not a JSON object") unless report.is_a?(Hash)

  report
rescue JSON::ParserError => e
  fail_with("#{REPORT_PATH} is not valid JSON: #{e.message}")
end

def emit(object)
  OUTPUT.write(JSON.generate(object), "\n")
  OUTPUT.flush
end

begin
  survivors, parse_errors = pre_parse(read_paths)

  if survivors.empty?
    emit("metadata" => nil, "analysed_modules" => [], "score" => nil, "parse_errors" => parse_errors)
    exit(0)
  end

  run_rubycritic(survivors)
  report = read_report
  report["parse_errors"] = parse_errors
  emit(report)
  exit(0)
rescue SystemExit
  raise
rescue Exception => e # rubocop:disable Lint/RescueException
  fail_with("#{e.class}: #{e.message}")
end
