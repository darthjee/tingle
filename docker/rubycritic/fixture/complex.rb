# frozen_string_literal: true

# One method with nested conditionals, loops and a case.
class Classifier
  def classify(items, mode)
    results = []
    items.each do |item|
      if item.nil?
        results << :missing
        next
      end

      case mode
      when :strict
        if item.respond_to?(:valid?) && item.valid?
          item.parts.each do |part|
            if part.size > 10
              results << :large
            elsif part.size > 5
              results << :medium
            else
              results << :small
            end
          end
        else
          results << :invalid
        end
      when :loose
        while item.pending?
          item.step!
          results << :stepped unless item.quiet?
        end
      when :counted
        item.count.times do |index|
          if index.zero?
            results << :first
          elsif index.even?
            results << (index > 100 ? :big_even : :even)
          else
            results << (index > 100 ? :big_odd : :odd)
          end
        end
      when :tagged
        item.tags.each do |tag|
          until tag.resolved?
            tag.resolve!
            results << tag.name.to_sym if tag.named? && !tag.hidden?
          end
        end
      else
        results << (item.to_s.empty? ? :blank : :other)
      end
    end
    results.compact.uniq.sort_by(&:to_s)
  end
end
