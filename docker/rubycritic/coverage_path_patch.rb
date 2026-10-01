# frozen_string_literal: true

# Preloaded (RUBYOPT=-r<this file>) by entrypoint.rb when it runs RubyCritic.
#
# RubyCritic 5.0.0 parses --coverage-path but drops it in
# Cli::Options::Argv#to_h, so its coverage analyser (analysers/coverage.rb)
# falls back to ./coverage, i.e. /src/coverage. When the analysed project has
# a coverage/.resultset.json, SimpleCov then opens .resultset.json.lock with
# "w+", which raises Errno::EROFS on the read-only /src mount.
#
# This patch forwards --coverage-path into RubyCritic's config. It does
# nothing when the flag isn't passed. Drop it once RubyCritic's Argv#to_h
# includes coverage_path upstream.

require "rubycritic/cli/options/argv"

RubyCritic::Cli::Options::Argv.prepend(Module.new do
  def to_h
    hash = super
    return hash if @coverage_path.nil?

    hash.merge(coverage_path: @coverage_path)
  end
end)
