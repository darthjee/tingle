# frozen_string_literal: true

# A method with an unclosed parameter list.
class Broken
  def call(first, second
    first + second
  end
end
