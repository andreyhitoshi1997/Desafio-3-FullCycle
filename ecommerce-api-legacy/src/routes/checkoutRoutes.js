const { Router } = require("express");
const { buildCheckoutHandler } = require("../controllers/checkoutController");

function createCheckoutRoutes(db) {
  const router = Router();
  router.post("/api/checkout", buildCheckoutHandler(db));
  return router;
}

module.exports = { createCheckoutRoutes };
