const { isLuhnValid } = require("./luhn");

const CARD_NUMBER_PATTERN = /^\d{13,19}$/;

function validate(cardNumber) {
  if (typeof cardNumber !== "string") {
    return { valid: false, reason: "invalid_format", last4: null, bin: null };
  }

  const normalized = cardNumber.replace(/[\s-]/g, "");

  if (!CARD_NUMBER_PATTERN.test(normalized)) {
    return { valid: false, reason: "invalid_format", last4: null, bin: null };
  }

  if (!isLuhnValid(normalized)) {
    return { valid: false, reason: "invalid_card", last4: null, bin: null };
  }

  return {
    valid: true,
    reason: null,
    last4: normalized.slice(-4),
    bin: normalized.slice(0, 6),
  };
}

module.exports = { validate };
