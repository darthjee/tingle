# frozen_string_literal: true

# Second of two classes sharing the same method body.
class OrderTotal
  def total(lines)
    sum = 0
    lines.each do |line|
      next if line[:skip]

      amount = line[:price] * line[:quantity]
      amount -= line[:discount] if line[:discount]
      sum += amount
    end
    sum.round(2)
  end
end
